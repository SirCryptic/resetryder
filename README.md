# ResetRyder - Open Source Brute Force Password Reset Tool
This tool brute-forces password reset endpoints, targeting flaws like [CVE-2023-24080](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-24080) in Chamberlain myQ v5.222.0.32277 (iOS). Works on similar web apps. By [SirCryptic](https://github.com/SirCryptic) of [NullSecurityTeam](https://github.com/NULL-Security-Team).

## Installation
1. Install Python 3.7+ and packages: pip install aiohttp aiohttp_socks fake_useragent aiofiles PySocks
2. Use high-quality SOCKS4 proxies (e.g., paid providers, avoid free lists) for best results.

## Example Usage
```
python resetryder.py -p passwords.txt -u usernames.txt -r https://example.com/reset -x proxies.txt -a 3 -o 10 -c 10
```
Check target response (e.g., "Password updated") and update config.json's "success_indicators".
With CSRF token:
```
python resetryder.py -p passwords.txt -u usernames.txt -r https://example.com/reset -x proxies.txt --config config_with_csrf.json
```

The following arguments are required:
* `-p`: Path to the password list file.
* `-u`: Path to the username list file.
* `-r`: URL to the reset password endpoint.
* `-x`: Path to the SOCKS4 proxy list file.

The following arguments are optional:
* `-a`: Max retries for failed requests (default: 3).
* `-o`: Max timeout in seconds (default: 10).
* `-c`: Max concurrent requests (default: 10).
* `-t`: Rate limit in seconds (default: 1.0).
* `--config`: JSON config file (default: config.json).

## Notes
CAPTCHAs may block attempts—use a solver like 2Captcha (not included) or Selenium for automation. Edit config.json to add solver API keys when implemented.

## Disclaimer
Not responsible for misuse. For educational and authorized testing only. Illegal without permission (e.g., CFAA, Computer Misuse Act).
