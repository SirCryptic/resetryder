# ResetRyder - Open Source Brute Force Password Reset Tool

This tool is a brute force password reset tool designed to exploit the vulnerability [CVE-2023-24080](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-24080). The vulnerability was discovered in the Chamberlain myQ v5.222.0.32277 app on iOS, but this tool should work for any web application that has a similar vulnerability. The tool was developed by [SirCryptic](https://github.com/SirCryptic) of the [NullSecurityTeam](https://github.com/NULL-Security-Team).

## Installation
1. Install the required Python packages: `requests` `argparse` `asyncio`.

## Example Usage
```
python3 resetryder.py -p passwords.txt -u usernames.txt -r https://example.com/resetpassword -x proxies.txt -a 3 -o 10 -c 10
```

The following arguments are required:
* `-p`: Path to the password list file.
* `-u`: Path to the username list file.
* `-r`: URL to the reset password endpoint.
* `-x`: Path to the SOCKS4 proxy list file.

The following arguments are optional:
* `-a`: Maximum number of retries for failed requests (default: 3).
* `-o`: Maximum timeout for requests in seconds (default: 10).
* `-c`: Maximum number of concurrent requests (default: 10).
* `-t`: Rate limiting time in seconds (default: 1).

## Disclaimer

The author of this script is not responsible for any damage caused by the use or misuse of this script. These PoCs are intended for educational and research purposes only, and should never be used to target or exploit systems without explicit permission from the owner.
