"""
Channel Scanner Module
Scans Discord servers and categorizes channels by type
"""

import discord
from colorama import Fore, Style


class ChannelScanner:
    def __init__(self, bot):
        self.bot = bot

    async def scan_all_guilds(self):
        """Scan all servers the account is in"""
        print(f"{Fore.CYAN}[*] Scanning all servers...{Style.RESET_ALL}")
        for guild in self.bot.guilds:
            print(f"  Server: {Fore.YELLOW}{guild.name}{Style.RESET_ALL} ({len(guild.channels)} channels)")
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    print(f"    📝 #{channel.name}")
                elif isinstance(channel, discord.VoiceChannel):
                    print(f"    🔊 #{channel.name}")
                elif isinstance(channel, discord.CategoryChannel):
                    print(f"    📁 {channel.name}")

    def categorize_channels(self, guild):
        """Categorize channels by their names/keywords"""
        categories = {
            "general": [],
            "trading": [],
            "chat": [],
            "announcements": [],
            "support": [],
            "voice": [],
            "other": []
        }

        keywords = {
            "general": ["general", "main", "lounge", "lobby", "public"],
            "trading": ["trade", "trading", "market", "exchange", "buy", "sell", "deal", "bazaar"],
            "chat": ["chat", "talk", "discussion", "conversation"],
            "announcements": ["announce", "news", "update", "notice", "log"],
            "support": ["support", "help", "ask", "question", "ticket"],
            "voice": ["voice", "vc", "audio", "talk"]
        }

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel):
                channel_name = channel.name.lower()
                categorized = False

                for cat_type, cat_keywords in keywords.items():
                    if any(kw in channel_name for kw in cat_keywords):
                        categories[cat_type].append(channel)
                        categorized = True
                        break

                if not categorized:
                    categories["other"].append(channel)

        return categories

    def get_channel_by_name(self, guild, name):
        """Find a channel by name"""
        for channel in guild.channels:
            if channel.name.lower() == name.lower():
                return channel
        return None
