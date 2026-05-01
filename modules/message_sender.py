"""
Message Sender Module
Sends automated messages to target channels
"""

import discord
import asyncio
import random
from colorama import Fore, Style


class MessageSender:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.active = False
        self.message_history = []

    async def send_to_targets(self):
        """Send messages to configured target channels"""
        if not self.active:
            return

        config = self.config["bot"]["actions"]["send_messages"]
        messages = config.get("messages", ["Hello!"])
        
        # Get target channels from config or auto-detect
        target_channels = await self._get_target_channels()

        for channel in target_channels:
            try:
                # Pick a message
                if config.get("random_order", True):
                    msg = random.choice(messages)
                else:
                    msg = messages[len(self.message_history) % len(messages)]

                # Send typing indicator first
                if self.config["bot"]["actions"]["typing_indicator"].get("enabled", False):
                    async with channel.typing():
                        duration = self.config["bot"]["actions"]["typing_indicator"].get("duration_seconds", 3)
                        await asyncio.sleep(duration)

                # Send the message
                sent = await channel.send(msg)
                self.message_history.append(msg)
                
                print(f"{Fore.GREEN}  ✅ Sent to #{channel.name}: '{msg}'{Style.RESET_ALL}")
                
                # Small delay between channels to avoid rate limits
                await asyncio.sleep(random.uniform(1, 3))

            except discord.Forbidden:
                print(f"{Fore.RED}  ❌ No permission to send in #{channel.name}{Style.RESET_ALL}")
            except discord.HTTPException as e:
                print(f"{Fore.RED}  ❌ HTTP error in #{channel.name}: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ❌ Error in #{channel.name}: {e}{Style.RESET_ALL}")

    async def _get_target_channels(self):
        """Get channels to send messages to"""
        config = self.config["bot"]["channels"]
        
        # If specific channel IDs are configured, use those
        if config.get("targets"):
            channels = []
            for channel_id in config["targets"]:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    channels.append(channel)
            if channels:
                return channels

        # Auto-detect: find general/trading channels
        channels = []
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    name = channel.name.lower()
                    if any(kw in name for kw in ["general", "chat", "trading", "lounge", "main"]):
                        channels.append(channel)
        
        return channels or []
