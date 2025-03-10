# ResetRyder - Open Source Brute Force Password Reset Tool
This tool is a brute force password reset tool designed to exploit the vulnerability [CVE-2023-24080](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-24080). The vulnerability was discovered in the Chamberlain myQ v5.222.0.32277 app on iOS, but this tool works for any web application with a similar flaw. Developed by [SirCryptic](https://github.com/SirCryptic) of [NullSecurityTeam](https://github.com/NULL-Security-Team).

## Installation
1. Install the required Python packages: `aiohttp` `aiohttp_socks` `fake_useragent` `aiofiles` `PySocks`.
   Run: pip install aiohttp aiohttp_socks fake_useragent aiofiles PySocks

## Example Usage
python resetryder.py -p passwords.txt -u usernames.txt -r https://example.com/reset -x proxies.txt -a 3 -o 10 -c 10

The following arguments are required:
* `-p`: Path to the password list file.
* `-u`: Path to the username list file.
* `-r`: URL to the reset password endpoint.
* `-x`: Path to the SOCKS4 proxy list file.

The following arguments are optional:
* `-a`: Maximum number of retries for failed requests (default: 3).
* `-o`: Maximum timeout for requests in seconds (default: 10).
* `-c`: Maximum number of concurrent requests (default: 10).
* `-t`: Rate limiting time in seconds (default: 1.0).
* `--config`: Path to JSON config file (default: config.json).

## Disclaimer
The author of this script is not responsible for any damage caused by its use or misuse. This tool is for educational and research purposes only. Do not use it to target or exploit systems without explicit permission from the owner.
