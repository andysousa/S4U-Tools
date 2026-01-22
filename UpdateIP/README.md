# Unlock IP Automation

A Python script to automate unlocking IP addresses on Seasons4U.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Installation

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4
```

## Usage

### Method 1: API Login (Recommended - No Browser Needed!)

```bash
python unlock_ip.py <IP_ADDRESS> --login
```

Example:
```bash
python unlock_ip.py 192.168.1.1 --login
```

This will prompt you for your email and password, then automatically:
- Authenticate via API
- Get your session cookie
- Unlock the IP address

You can also provide email as an argument:
```bash
python unlock_ip.py 192.168.1.1 --login --email user@example.com
```

### Method 2: Use Existing Session Cookie

```bash
python unlock_ip.py <IP_ADDRESS> --cookie "<COOKIE>"
```

Example:
```bash
python unlock_ip.py 192.168.1.1 --cookie ".AspNet.ApplicationCookie=YOUR_SESSION_COOKIE_VALUE_HERE"
```

### Getting Your Session Cookie (if needed)

1. Open your browser and log into Seasons4U
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click on **Cookies** > `https://seasons4u.com`
5. Find the cookie named `.AspNet.ApplicationCookie`
6. Copy its entire value

## How It Works

1. **GET** `/UnlockIp/Edit/558` to retrieve:
   - CSRF token (`__RequestVerificationToken`)
   - User ID
   - Current IP unlock ID

2. **POST** `/UnlockIp/Edit/558` with form data:
   - CSRF token
   - User ID
   - IP Unlock ID
   - New IP address

3. Server responds with a 302 redirect to `/UnlockIp` on success

## Error Handling

If you get authentication errors:
- Make sure you're logged into Seasons4U in your browser
- Copy the full session cookie value (it's very long)
- The cookie expires, so you may need to get a fresh one

## Security Note

- Never commit your session cookies to version control
- Session cookies are sensitive - treat them like passwords
- Consider using environment variables for cookies in production

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md) that all contributors are expected to follow.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Disclaimer

This tool is not officially affiliated with Seasons4U. Use at your own risk.