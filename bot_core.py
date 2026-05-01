"""
Discord Automation Selfbot
Uses discord.py-self to automate Discord actions
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import time
import random
from colorama import Fore, Style

from modules.channel_scanner import ChannelScanner
from modules.message_sender import MessageSender
from modules.reaction_adder import ReactionAdder
from modules.scheduler import Scheduler


class DiscordAutomationBot:
    def __init__(self, token, config):
        self.token = token
        self.config = config
        self.running = False
        self.stop_keyword = config.get("stop_keyword", "!stop")

        # Setup intents for user account (selfbot)
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True

        self.bot = commands.Bot(
            command_prefix=".",
            self_bot=True,
            intents=intents,
            help_command=None
        )

        # Initialize modules
        self.channel_scanner = ChannelScanner(self.bot)
        self.message_sender = MessageSender(self.bot, config)
        self.reaction_adder = ReactionAdder(self.bot, config)
        self.scheduler = Scheduler(config)

        self._register_events()

    def _register_events(self):
        @self.bot.event
        async def on_ready():
            print(f"\n{Fore.GREEN}✅ Logged in as: {self.bot.user}{Style.RESET_ALL}")
            print(f"    User ID: {self.bot.user.id}")
            print(f"    Bot runtime starting...\n")
            
            self.running = True
            config = self.config

            # Auto-join server if invite link is configured
            invite_link = config["bot"]["join_server"].get("invite_link", "")
            if invite_link and config["bot"]["join_server"].get("auto_join", True):
                await self._join_server(invite_link)

            # Scan channels if configured
            if config["bot"]["channels"].get("scan_on_join", True):
                await self.channel_scanner.scan_all_guilds()

            # Start automated actions
            await self._start_automated_actions()

        @self.bot.event
        async def on_message(message):
            # Don't respond to ourselves
            if message.author == self.bot.user:
                return

            # Listen for stop command
            if message.content.lower() == self.stop_keyword.lower():
                if message.channel.type == discord.ChannelType.private:
                    await message.channel.send("🛑 Stopping automation...")
                    await self.stop()
                    return

            # Also check in DMs for control
            if isinstance(message.channel, discord.DMChannel):
                if message.content.lower() == "!status":
                    await message.channel.send(
                        f"✅ Bot is running\n"
                        f"  User: {self.bot.user}\n"
                        f"  Servers: {len(self.bot.guilds)}\n"
                        f"  Actions: {self.message_sender.active}/"
                        f"{self.reaction_adder.active}"
                    )

    async def _join_server(self, invite_link):
        """Join a Discord server via invite link"""
        print(f"{Fore.CYAN}[*] Joining server: {invite_link}{Style.RESET_ALL}")
        try:
            # Extract invite code from URL
            if "discord.gg/" in invite_link:
                code = invite_link.split("discord.gg/")[-1].split("/")[0].split("?")[0]
            elif "discord.com/invite/" in invite_link:
                code = invite_link.split("discord.com/invite/")[-1].split("/")[0].split("?")[0]
            else:
                code = invite_link.strip()

            invite = await self.bot.fetch_invite(code)
            await invite.guild.chunk()  # Load members
            
            # Join using the invite
            # Note: Selfbots join automatically when using an invite link
            # We'll use the HTTP API to accept the invite
            headers = {"Authorization": self.token}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(f"https://discord.com/api/v10/invites/{code}") as resp:
                    if resp.status == 200:
                        print(f"{Fore.GREEN}✅ Joined server: {invite.guild.name}{Style.RESET_ALL}")
                        return True
                    else:
                        data = await resp.json()
                        print(f"{Fore.RED}❌ Failed to join: {data.get('message', 'Unknown error')}{Style.RESET_ALL}")
                        return False
        except Exception as e:
            print(f"{Fore.RED}❌ Error joining server: {e}{Style.RESET_ALL}")
            return False

    async def _start_automated_actions(self):
        """Start all scheduled automated tasks"""
        print(f"{Fore.CYAN}[*] Starting automated actions...{Style.RESET_ALL}")

        # Channel scanning and categorization
        if self.config["bot"]["channels"]["categorize"]:
            print(f"{Fore.CYAN}[*] Categorizing channels...{Style.RESET_ALL}")
            for guild in self.bot.guilds:
                categories = self.channel_scanner.categorize_channels(guild)
                print(f"\n  {Fore.YELLOW}Server: {guild.name}{Style.RESET_ALL}")
                for cat_type, channels in categories.items():
                    if channels:
                        names = [c.name for c in channels[:5]]
                        print(f"    {cat_type}: {', '.join(names)}{'...' if len(channels) > 5 else ''}")

        # Start message sending loop
        if self.config["bot"]["actions"]["send_messages"]["enabled"]:
            self.message_sender.active = True
            asyncio.create_task(self._message_loop())
            print(f"{Fore.GREEN}  ✅ Message sender started{Style.RESET_ALL}")

        # Start reaction adding loop
        if self.config["bot"]["actions"]["add_reactions"]["enabled"]:
            self.reaction_adder.active = True
            asyncio.create_task(self._reaction_loop())
            print(f"{Fore.GREEN}  ✅ Reaction adder started{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}✅ All automation running! Say '{self.stop_keyword}' in DMs to stop.{Style.RESET_ALL}")

    async def _message_loop(self):
        """Background loop for sending messages"""
        config = self.config["bot"]["actions"]["send_messages"]
        interval = config.get("interval_seconds", 60)
        
        while self.running and self.message_sender.active:
            try:
                # Check if scheduler allows running
                if self.scheduler.enabled and not self.scheduler.should_run():
                    await asyncio.sleep(30)
                    continue

                await self.message_sender.send_to_targets()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"{Fore.RED}  ❌ Message loop error: {e}{Style.RESET_ALL}")
                await asyncio.sleep(10)

    async def _reaction_loop(self):
        """Background loop for adding reactions"""
        config = self.config["bot"]["actions"]["add_reactions"]
        interval = config.get("interval_seconds", 30)
        
        while self.running and self.reaction_adder.active:
            try:
                if self.scheduler.enabled and not self.scheduler.should_run():
                    await asyncio.sleep(30)
                    continue

                await self.reaction_adder.add_reactions_to_target()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"{Fore.RED}  ❌ Reaction loop error: {e}{Style.RESET_ALL}")
                await asyncio.sleep(10)

    async def stop(self):
        """Stop all automation"""
        print(f"\n{Fore.YELLOW}🛑 Stopping automation...{Style.RESET_ALL}")
        self.running = False
        self.message_sender.active = False
        self.reaction_adder.active = False
        await self.bot.close()
        print(f"{Fore.GREEN}✅ Automation stopped{Style.RESET_ALL}")

    async def run(self):
        """Start the bot"""
        await self.bot.start(self.token)
