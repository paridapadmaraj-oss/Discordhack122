"""
Reaction Adder Module
Adds reactions/emojis to specified posts
"""

import discord
import asyncio
import re
import random
from colorama import Fore, Style


class ReactionAdder:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.active = False

    async def add_reactions_to_target(self):
        """Add reactions to target posts"""
        if not self.active:
            return

        config = self.config["bot"]["actions"]["add_reactions"]
        post_link = config.get("post_link", "")
        emojis = config.get("emojis", ["👍"])

        if not post_link:
            print(f"{Fore.YELLOW}  ⚠ No post link configured for reactions{Style.RESET_ALL}")
            return

        # Parse the post link to get guild, channel, and message IDs
        message = await self._resolve_message_from_link(post_link)
        
        if not message:
            print(f"{Fore.YELLOW}  ⚠ Could not resolve message from link: {post_link}{Style.RESET_ALL}")
            return

        for emoji in emojis:
            try:
                # Check if emoji is a custom emoji
                if emoji.startswith("<") and emoji.endswith(">"):
                    # Custom emoji format: <:name:id>
                    match = re.match(r"<a?:(\w+):(\d+)>", emoji)
                    if match:
                        emoji_id = int(match.group(2))
                        custom_emoji = discord.PartialEmoji(
                            name=match.group(1),
                            id=emoji_id,
                            animated=emoji.startswith("<a")
                        )
                        await message.add_reaction(custom_emoji)
                    else:
                        print(f"{Fore.YELLOW}  ⚠ Invalid custom emoji format: {emoji}{Style.RESET_ALL}")
                        continue
                else:
                    # Unicode emoji
                    await message.add_reaction(emoji)

                print(f"{Fore.GREEN}  ✅ Added reaction '{emoji}' to message{Style.RESET_ALL}")
                await asyncio.sleep(random.uniform(0.5, 2))  # Anti-rate-limit delay

            except discord.Forbidden:
                print(f"{Fore.RED}  ❌ No permission to add reactions{Style.RESET_ALL}")
            except discord.HTTPException as e:
                print(f"{Fore.RED}  ❌ HTTP error adding reaction: {e}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}  ❌ Error adding reaction '{emoji}': {e}{Style.RESET_ALL}")

    async def _resolve_message_from_link(self, link):
        """Resolve a Discord message link to a Message object"""
        # Format: https://discord.com/channels/guild_id/channel_id/message_id
        pattern = r"(?:discord\.com/channels|discord\.gg)/(\d+)/(\d+)/(\d+)"
        match = re.search(pattern, link)
        
        if not match:
            # Try alternate format: just channel_id/message_id
            pattern2 = r"/(\d+)/(\d+)$"
            match2 = re.search(pattern2, link)
            if match2:
                channel_id = int(match2.group(1))
                message_id = int(match2.group(2))
            else:
                return None
        else:
            channel_id = int(match.group(2))
            message_id = int(match.group(3))

        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                # Try fetching the channel
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except:
                    return None

            message = await channel.fetch_message(message_id)
            return message
        except Exception as e:
            print(f"{Fore.RED}  ❌ Error resolving message: {e}{Style.RESET_ALL}")
            return None
