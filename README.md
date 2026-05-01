# Discord Automation Bot

Automated Discord account creation + selfbot for server management, messaging, and reactions.

## ⚠️ Legal & Ethical Notice

**This tool is for educational and authorized testing purposes only.** Using selfbots violates Discord's Terms of Service and can result in account termination. Only use on servers you own or have explicit permission to test.

## Features

- 🤖 **Auto Account Creation** - Creates Discord accounts via Selenium browser automation
- 🔗 **Auto Join Server** - Automatically joins Discord servers via invite links
- 📋 **Channel Scanner** - Scans and categorizes channels (general, trading, chat, etc.)
- 💬 **Auto Messaging** - Sends messages to channels on a timer
- 👍 **Auto Reactions** - Adds emoji reactions to specified posts
- ⏰ **Scheduler** - Run automation only during specified hours
- 🛑 **Stop Mechanism** - Say `!stop` in DMs to halt all automation
- 🔧 **Fully Configurable** - All settings in `config.json`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and edit configuration
cp .env.example .env
# Edit .env with your settings

# 3. Run the bot
python main.py
