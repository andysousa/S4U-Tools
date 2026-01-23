# Unlock IP Automation

A Python script to automate unlocking IP addresses on s4u.

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

## Configuration

### Base URL

The script **requires** the `S4U_BASE_URL` environment variable to be set. This specifies the base URL of the service you want to connect to.

**Set the base URL (required):**

**Linux/macOS:**
```bash
export S4U_BASE_URL="https://your-service-url.com"
python unlock_ip.py 192.168.1.1 --login
```

**Windows (Command Prompt):**
```cmd
set S4U_BASE_URL=https://your-service-url.com
python unlock_ip.py 192.168.1.1 --login
```

**Windows (PowerShell):**
```powershell
$env:S4U_BASE_URL="https://your-service-url.com"
python unlock_ip.py 192.168.1.1 --login
```

**Using a `.env` file (recommended):**

The script automatically loads `.env` files if `python-dotenv` is installed (included in requirements.txt).

Copy the example file and edit it with your values:
```bash
cp .env.example .env
# Then edit .env with your actual service URL
```

The `.env` file should contain:
```
S4U_BASE_URL=https://your-service-url.com
```

Then simply run the script - it will automatically load the `.env` file:
```bash
python unlock_ip.py 192.168.1.1 --login
```

**Alternative (without python-dotenv):** If you prefer not to use `python-dotenv`, you can manually load the `.env` file:
```bash
export $(cat .env | xargs)
python unlock_ip.py 192.168.1.1 --login
```

**Note:** The `.env` file is gitignored and won't be committed to version control.

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

You can also provide email and password as command-line arguments:
```bash
python unlock_ip.py 192.168.1.1 --login --email user@example.com --password yourpassword
```

Or provide just the email (password will be prompted):
```bash
python unlock_ip.py 192.168.1.1 --login --email user@example.com
```

You can also automatically detect and use your external IP address:
```bash
python unlock_ip.py --auto-ip --login --email user@example.com --password yourpassword
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

1. Open your browser and log into webpage
2. Open DevTools (F12 or Cmd+Option+I)
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click on **Cookies** > `[your base URL]` (or the URL set in `S4U_BASE_URL` environment variable)
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
- Make sure you're logged into s4u in your browser
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

This tool is not officially affiliated with s4u. Use at your own risk.