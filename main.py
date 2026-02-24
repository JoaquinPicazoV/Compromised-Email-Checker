import subprocess
import sys

def ensure_dependencies():
    required = ["requests"]
    for package in required:
        try:
            __import__(package)
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
            except Exception as e:
                sys.exit(1)

import requests
import json
import re
import time

YELLOW = '\033[93m'
BOLD = '\033[1m'
CYAN = '\033[96m'
WHITE = "\033[97m"
GREEN = "\033[38;5;46m"
RED = "\033[31m"
RESET = '\033[0m'

def show_banner():
    print(f"{CYAN}{BOLD}Compromised Email Checker [CEC] - OSINT Breach Scanner{WHITE}")
    print(f"Powered by XposedOrNot API (Public)")

def loading_animation(seconds):
    print(f"\n{CYAN}{BOLD}[*] Searching for breaches... Please wait.{RESET}")
    bar_length = 40
    for i in range(bar_length + 1):
        percent = 100 * (i / bar_length)
        bar = '█' * i + '-' * (bar_length - i)
        sys.stdout.write(f'\r{WHITE}[{bar}] {percent:.1f}%')
        sys.stdout.flush()
        time.sleep(seconds / bar_length)
    print(f"\n{GREEN}{BOLD}Scan complete!{RESET}")

def show_disclaimer():
    print(f"\n{YELLOW}{BOLD}[!] LEGAL DISCLAIMER AND SCOPE LIMITATION{RESET}")
    print(f"{YELLOW}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{YELLOW}The results shown come from public sources (OSINT) and{RESET}")
    print(f"{YELLOW}third-party databases.{RESET}")
    print(f"{YELLOW}{RESET}")
    print(f"{YELLOW}A clean result does not guarantee absolute security, as{RESET}")
    print(f"{YELLOW}there may be recent or private breaches, or breaches on the Dark Web, that{RESET}")
    print(f"{YELLOW}have not yet been detected or indexed by this system.{RESET}")
    print(f"{YELLOW}──────────────────────────────────────────────────────────────────────{RESET}")

def is_valid_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def get_email():
    while True:
        email = input(f"{WHITE}{BOLD}Enter the email to investigate: {RESET}").strip()
        if not email:
            print(f"{RED}[!] Error: The email cannot be empty.{RESET}")
            continue
        if is_valid_email(email):
            return email
        else:
            print(f"{RED}[!] Error: Invalid email format. Please try again.{RESET}")

def search_databreach(email):
    url = f"https://api.xposedornot.com/v1/breach-analytics?email={email}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return {"ExposedBreaches": {"breaches_details": []}}
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 429:
            return {"error": "Too many requests. Please wait a moment before trying again."}
        elif status >= 500:
            return {"error": f"Server error ({status}). Please try again later."}
        else:
            return {"error": f"HTTP Error: {status}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except Exception as e:
        return {"error": str(e)}

def display_results(data):
    if not data:
        print(f"\n{RED}[!] Error: No data received from the API.{RESET}")
        return

    if isinstance(data, dict) and "error" in data:
        print(f"\n{RED}{BOLD}{'!'*80}{RESET}")
        print(f"{RED}{BOLD}{' ERROR DETECTED ':^80}{RESET}")
        print(f"{RED}{BOLD}{'!'*80}{RESET}")
        print(f"\n{WHITE}Details: {data['error']}{RESET}\n")
        return

    exposed_breaches = data.get("ExposedBreaches") or {}
    breaches = exposed_breaches.get("breaches_details") or []
    
    if not breaches:
        breaches_summary = data.get("BreachesSummary") or {}
        breaches = breaches_summary.get("site") or []
        if isinstance(breaches, str):
            breaches = [b.strip() for b in breaches.split(";") if b.strip()]
    
    if not breaches:
        print(f"{GREEN}{BOLD}\n{'-'*60}{RESET}")
        print(f"{GREEN}{BOLD}[OK] RESULT: No known leaks were found.{RESET}")
        print(f"{GREEN}{BOLD}{'-'*60}{RESET}")
        return

    print(f"\n{RED}{BOLD}{'#'*80}{RESET}")
    print(f"{RED}{BOLD}{'SECURITY REPORTS DETECTED':^80}{RESET}")
    print(f"{RED}{BOLD}{'#'*80}{RESET}\n")

    for breach in breaches:
        if isinstance(breach, dict):
            name = breach.get("breach", "Unknown")
            date = breach.get("xposed_date", "N/A")
            raw_data = breach.get("xposed_data", "Not specified")
            risk = breach.get("password_risk", "N/A").upper()
            reference = breach.get("references", "").strip()
            if not reference:
                reference = f"Not specified"
        else:
            name = str(breach)
            date = "Unknown"
            raw_data = "Not detailed in this report"
            risk = "PENDING"
            reference = f"Not specified"
    
        data_list = raw_data.replace(";", ", ")

        print(f"{RED}{BOLD}[!] SOURCE: {name}{RESET}")
        print(f"    {WHITE}Date: {date}{RESET}")
        print(f"    {WHITE}Password risk: {risk}{RESET}")
        print(f"    {WHITE}Data exposed: {data_list}{RESET}")
        print(f"    {WHITE}Reference: {reference}{RESET}")
        print(f"{YELLOW}{BOLD}{'-'*80}{RESET}")

if __name__ == "__main__": 
    ensure_dependencies()
    show_banner()
    show_disclaimer()   
    email = get_email()
    result = search_databreach(email)
    loading_animation(10)
    display_results(result)
