"""
Discord Account Creator
Uses Selenium to automate Discord account registration
"""

import os
import json
import time
import random
import string
import threading
from colorama import Fore, Style

# Try undetected-chromedriver first for better stealth
try:
    import undetected_chromedriver as uc
    UNDETECTED = True
except ImportError:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    UNDETECTED = False

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class DiscordAccountCreator:
    def __init__(self, proxy=None):
        self.accounts_file = "accounts/generated_accounts.json"
        os.makedirs("accounts", exist_ok=True)
        
        # Load existing accounts
        self.accounts = []
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, "r") as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = []

    def _generate_username(self):
        """Generate a realistic Discord username"""
        prefixes = ["xX", "Pro", "Cool", "Dark", "Neon", "Cyber", "Elite", "Shadow", 
                     "Frost", "Blaze", "Pixel", "Night", "Storm", "Venom", "Crypto"]
        suffixes = ["Wolf", "Phoenix", "Dragon", "Falcon", "Tiger", "Knight", "Ghost",
                     "Hawk", "Lynx", "Viper", "King", "Queen", "Ace", "Bolt", "Claw"]
        num = random.randint(100, 9999)
        return f"{random.choice(prefixes)}{random.choice(suffixes)}{num}"

    def _generate_dob(self):
        """Generate a valid date of birth"""
        year = random.randint(1990, 2005)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}", f"{day}", f"{year}"

    def _generate_password(self):
        """Generate a strong password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=14)) + "A1!"

    def create_account(self, headless=False):
        """Automate Discord account creation"""
        print(f"\n{Fore.CYAN}[*] Creating new Discord account...{Style.RESET_ALL}")

        username = self._generate_username()
        password = self._generate_password()
        month, day, year = self._generate_dob()

        print(f"    Username: {Fore.GREEN}{username}{Style.RESET_ALL}")
        print(f"    Password: {Fore.GREEN}{password}{Style.RESET_ALL}")
        print(f"    DOB: {month}/{day}/{year}")

        try:
            if UNDETECTED:
                options = uc.ChromeOptions()
                if headless:
                    options.headless = True
                driver = uc.Chrome(options=options)
            else:
                chrome_options = Options()
                if headless:
                    chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://discord.com/register")
            wait = WebDriverWait(driver, 15)
            time.sleep(2)

            # Fill username
            try:
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                username_field.clear()
                username_field.send_keys(username)
            except:
                print(f"{Fore.YELLOW}    ⚠ Could not fill username field{Style.RESET_ALL}")

            # Fill password
            try:
                password_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
                if password_fields:
                    password_fields[0].send_keys(password)
            except:
                pass

            # Fill DOB
            try:
                month_select = wait.until(EC.presence_of_element_located((By.NAME, "month")))
                month_select.send_keys(month)
                day_select = driver.find_element(By.NAME, "day")
                day_select.send_keys(day)
                year_select = driver.find_element(By.NAME, "year")
                year_select.send_keys(year)
            except:
                print(f"{Fore.YELLOW}    ⚠ Could not fill DOB fields (may need manual input){Style.RESET_ALL}")

            # Click continue
            try:
                continue_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                continue_btn.click()
            except:
                try:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if "continue" in btn.text.lower():
                            btn.click()
                            break
                except:
                    pass

            print(f"{Fore.YELLOW}    ⏳ Waiting for CAPTCHA... Please solve it manually in the browser.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    Or press Ctrl+C in terminal to cancel.{Style.RESET_ALL}")

            # Wait for navigation to complete (user solves captcha)
            time.sleep(5)
            
            # Wait for user to complete registration and get to the "What is your email?" screen
            # or the main Discord interface
            input(f"{Fore.CYAN}    📌 Press Enter AFTER you've completed the registration in the browser...{Style.RESET_ALL}")

            # Try to extract token from localStorage
            token = None
            try:
                token = driver.execute_script("""
                    var token = null;
                    for (var i = 0; i < localStorage.length; i++) {
                        var key = localStorage.key(i);
                        if (key && (key.includes('token') || key.includes('Token'))) {
                            try {
                                var val = localStorage.getItem(key);
                                if (val && val.length > 50) {
                                    token = val.replace(/['"]+/g, '');
                                    break;
                                }
                            } catch(e) {}
                        }
                    }
                    return token;
                """)
            except:
                pass

            # Alternative: check localStorage for discord tokens
            if not token:
                try:
                    # Common Discord token storage locations
                    token = driver.execute_script("""
                        try {
                            var t = window.__DISCORD_TOKEN__ || 
                                    localStorage.getItem('token') || 
                                    localStorage.getItem('discord_token');
                            // Check all localStorage entries
                            for(var i=0; i<localStorage.length; i++) {
                                var k = localStorage.key(i);
                                var v = localStorage.getItem(k);
                                if(v && v.length > 50 && v.startsWith('mfa.') || v.startsWith('OT') || v.includes('.')) {
                                    return v.replace(/"/g,'');
                                }
                            }
                        } catch(e) {}
                        return null;
                    """)
                except:
                    pass

            driver.quit()

            if token:
                account_info = {
                    "username": username,
                    "password": password,
                    "token": token,
                    "created_at": time.time(),
                    "dob": f"{month}/{day}/{year}"
                }
                self.accounts.append(account_info)

                with open(self.accounts_file, "w") as f:
                    json.dump(self.accounts, f, indent=2)

                print(f"{Fore.GREEN}✅ Account created successfully!{Style.RESET_ALL}")
                print(f"    Token: {Fore.CYAN}{token[:30]}...{Style.RESET_ALL}")
                return token
            else:
                print(f"{Fore.YELLOW}⚠ Account may have been created but couldn't extract token.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  You'll need to get the token manually and add it to .env{Style.RESET_ALL}")
                return None

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}🛑 Cancelled{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}❌ Error during account creation: {e}{Style.RESET_ALL}")
            return None


class AccountCreatorCLI:
    def run(self):
        creator = DiscordAccountCreator()
        
        print(f"\n{Fore.CYAN}━━━ Account Creation ━━━{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[1]{Style.RESET_ALL} Create 1 account")
        print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Create multiple accounts")
        print(f"{Fore.GREEN}[3]{Style.RESET_ALL} View saved tokens")
        print(f"{Fore.RED}[0]{Style.RESET_ALL} Back")
        
        choice = input(f"\n{Fore.CYAN}Select: {Style.RESET_ALL}").strip()
        
        if choice == "1":
            creator.create_account(headless=False)
        elif choice == "2":
            try:
                count = int(input("How many accounts? "))
                for i in range(count):
                    print(f"\n{Fore.CYAN}[Account {i+1}/{count}]{Style.RESET_ALL}")
                    creator.create_account(headless=False)
            except ValueError:
                print(f"{Fore.RED}Invalid number{Style.RESET_ALL}")
        elif choice == "3":
            if creator.accounts:
                print(f"\n{Fore.CYAN}Saved Accounts:{Style.RESET_ALL}")
                for i, acc in enumerate(creator.accounts, 1):
                    print(f"  {i}. {acc['username']} - Token: {acc['token'][:25]}...")
            else:
                print(f"{Fore.YELLOW}No accounts saved yet{Style.RESET_ALL}")
