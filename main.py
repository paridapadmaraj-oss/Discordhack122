#!/usr/bin/env python3
"""
Discord Automation Bot
Main entry point with interactive CLI menu
"""

import os
import sys
import json
import asyncio
import threading
from colorama import init, Fore, Style
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════╗
║       DISCORD AUTOMATION BOT v1.0        ║
║     Auto Account Creator + Selfbot      ║
╚══════════════════════════════════════════╝
{Style.RESET_ALL}
"""


def print_menu():
    print(f"\n{Fore.YELLOW}━━━ MAIN MENU ━━━{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Create new Discord account(s)")
    print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Start bot (join server + automate)")
    print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Configure settings")
    print(f"{Fore.GREEN}[4]{Style.RESET_ALL} View saved accounts")
    print(f"{Fore.GREEN}[5]{Style.RESET_ALL} Start with full pipeline (create + run)")
    print(f"{Fore.RED}[0]{Style.RESET_ALL} Exit")
    print(f"{Fore.YELLOW}━━━━━━━━━━━━━━{Style.RESET_ALL}")


def configure_settings():
    """Interactive settings configuration"""
    config_path = "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    print(f"\n{Fore.CYAN}⚙️  Configuration Editor{Style.RESET_ALL}")
    
    invite = input(f"  Server invite link (e.g., https://discord.gg/...): ") or config["bot"]["join_server"]["invite_link"]
    config["bot"]["join_server"]["invite_link"] = invite

    post_link = input(f"  Post link for reactions (URL): ") or config["bot"]["actions"]["add_reactions"]["post_link"]
    config["bot"]["actions"]["add_reactions"]["post_link"] = post_link

    emojis_input = input(f"  Reaction emojis (comma-separated, e.g., 👍,🔥,💯): ")
    if emojis_input:
        config["bot"]["actions"]["add_reactions"]["emojis"] = [e.strip() for e in emojis_input.split(",")]

    messages_input = input(f"  Messages to send (comma-separated): ")
    if messages_input:
        config["bot"]["actions"]["send_messages"]["messages"] = [m.strip() for m in messages_input.split(",")]

    msg_interval = input(f"  Message interval in seconds [{config['bot']['actions']['send_messages']['interval_seconds']}]: ")
    if msg_interval:
        config["bot"]["actions"]["send_messages"]["interval_seconds"] = int(msg_interval)

    react_interval = input(f"  Reaction interval in seconds [{config['bot']['actions']['add_reactions']['interval_seconds']}]: ")
    if react_interval:
        config["bot"]["actions"]["add_reactions"]["interval_seconds"] = int(react_interval)

    scheduler = input(f"  Enable scheduler? (y/n): ").lower() == 'y'
    config["bot"]["scheduler"]["enabled"] = scheduler
    if scheduler:
        start = input(f"  Start time (HH:MM) [{config['bot']['scheduler']['start_time']}]: ")
        if start: config["bot"]["scheduler"]["start_time"] = start
        end = input(f"  End time (HH:MM) [{config['bot']['scheduler']['end_time']}]: ")
        if end: config["bot"]["scheduler"]["end_time"] = end

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"{Fore.GREEN}✅ Configuration saved!{Style.RESET_ALL}")


def show_accounts():
    """Display saved accounts"""
    accounts_file = "accounts/generated_accounts.json"
    if not os.path.exists(accounts_file):
        print(f"{Fore.YELLOW}No saved accounts found.{Style.RESET_ALL}")
        return
    
    with open(accounts_file, "r") as f:
        accounts = json.load(f)
    
    print(f"\n{Fore.CYAN}📋 Saved Accounts ({len(accounts)}){Style.RESET_ALL}")
    for i, acc in enumerate(accounts, 1):
        print(f"  {i}. {acc.get('username', 'N/A')} | Token: {acc.get('token', 'N/A')[:20]}...")
    print()


def run_account_creator():
    """Run the account creation module"""
    from account_creator import AccountCreatorCLI
    cli = AccountCreatorCLI()
    cli.run()


def run_bot():
    """Run the Discord selfbot"""
    print(f"\n{Fore.CYAN}🤖 Starting Discord bot...{Style.RESET_ALL}")
    
    # Load config
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Check for token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        # Try to load from saved accounts
        accounts_file = "accounts/generated_accounts.json"
        if os.path.exists(accounts_file):
            with open(accounts_file, "r") as f:
                accounts = json.load(f)
            if accounts:
                print(f"{Fore.GREEN}Using saved account token{Style.RESET_ALL}")
                token = accounts[-1].get("token")
    
    if not token:
        print(f"{Fore.RED}❌ No token found. Create an account first or set DISCORD_TOKEN in .env{Style.RESET_ALL}")
        return

    from bot_core import DiscordAutomationBot
    bot = DiscordAutomationBot(token, config)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Bot stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")


def full_pipeline():
    """Create account then immediately run the bot"""
    print(f"\n{Fore.CYAN}🔄 Full Pipeline: Create Account → Start Bot{Style.RESET_ALL}")
    run_account_creator()
    run_bot()


def main():
    print(BANNER)
    
    while True:
        print_menu()
        choice = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}").strip()
        
        if choice == "1":
            run_account_creator()
        elif choice == "2":
            run_bot()
        elif choice == "3":
            configure_settings()
        elif choice == "4":
            show_accounts()
        elif choice == "5":
            full_pipeline()
        elif choice == "0":
            print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid option{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
