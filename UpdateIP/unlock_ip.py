#!/usr/bin/env python3
"""
Automate IP unlocking for s4u
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import getpass

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

# Configuration - Base URL from environment variable (required)
BASE_URL = os.environ.get('S4U_BASE_URL')
if not BASE_URL:
    print('❌ Error: S4U_BASE_URL environment variable is required')
    print('   Please set it before running the script:')
    print('   export S4U_BASE_URL="https://your-service-url.com"')
    sys.exit(1)

LOGIN_URL = f'{BASE_URL}/Account/Login'
EDIT_URL = f'{BASE_URL}/UnlockIp/Edit/558'

# Extract domain from BASE_URL for cookie setting
BASE_DOMAIN = urlparse(BASE_URL).netloc

# Create a session to maintain cookies
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Safari/605.1.15'
})


def login(username, password):
    """
    Login via API and get session cookie
    
    Args:
        username (str): Your username/email
        password (str): Your password
        
    Returns:
        str: Session cookie string (e.g., ".AspNet.ApplicationCookie=...")
    """
    try:
        print('🔐 Logging in...')
        
        # First, get the login page to extract CSRF token
        response = session.get(LOGIN_URL)
        response.raise_for_status()
        
        # Parse HTML to find CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if not csrf_input or not csrf_input.get('value'):
            raise ValueError('CSRF token not found on login page')
        
        csrf_token = csrf_input['value']
        
        # Prepare login form data (using Username field, not Email)
        login_data = {
            '__RequestVerificationToken': csrf_token,
            'Username': username,
            'Password': password
        }
        
        # Submit login (requests will automatically URL-encode the data)
        response = session.post(
            LOGIN_URL,
            data=login_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': LOGIN_URL,
                'Origin': BASE_URL
            },
            allow_redirects=False
        )
        
        # Check if login was successful (usually redirects to home/dashboard)
        if response.status_code in [200, 302]:
            # Extract the session cookie
            cookies = session.cookies
            
            # Look for the ASP.NET application cookie
            app_cookie = None
            for cookie in cookies:
                if cookie.name == '.AspNet.ApplicationCookie':
                    app_cookie = f"{cookie.name}={cookie.value}"
                    break
            
            if app_cookie:
                print('✅ Login successful!')
                return app_cookie
            else:
                # If we got redirected, login likely succeeded but cookie format might be different
                # Try to get it from the cookie jar
                if 'Location' in response.headers:
                    print('✅ Login successful (redirected)!')
                    # Return all cookies as a string
                    cookie_string = '; '.join([f"{c.name}={c.value}" for c in cookies])
                    return cookie_string
                else:
                    raise ValueError('Login may have failed - no session cookie found')
        else:
            # Check if there's an error message in the response
            soup = BeautifulSoup(response.text, 'html.parser')
            error_msg = soup.find('div', class_='validation-summary-errors')
            if error_msg:
                error_text = error_msg.get_text(strip=True)
                raise ValueError(f'Login failed: {error_text}')
            else:
                raise ValueError(f'Login failed with status code: {response.status_code}')
                
    except requests.exceptions.RequestException as e:
        print(f'❌ Network Error during login: {e}')
        raise
    except Exception as e:
        print(f'❌ Login Error: {e}')
        raise


def get_csrf_token():
    """Get the CSRF token from the edit page"""
    try:
        print('📥 Fetching edit page to get CSRF token...')
        
        response = session.get(EDIT_URL)
        response.raise_for_status()
        
        # Parse HTML to find CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
        
        if not csrf_input or not csrf_input.get('value'):
            raise ValueError('CSRF token not found in page')
        
        csrf_token = csrf_input['value']
        print('✅ CSRF token retrieved')
        return csrf_token
        
    except Exception as e:
        print(f'❌ Error getting CSRF token: {e}')
        raise


def get_user_info():
    """Get current user info from the page"""
    try:
        response = session.get(EDIT_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract UserId and IpUnlockId from hidden inputs
        user_id_input = soup.find('input', {'name': 'UserId'})
        ip_unlock_id_input = soup.find('input', {'name': 'IpUnlockId'})
        
        user_id = user_id_input['value'] if user_id_input else None
        ip_unlock_id = ip_unlock_id_input['value'] if ip_unlock_id_input else '558'
        
        return {'user_id': user_id, 'ip_unlock_id': ip_unlock_id}
        
    except Exception as e:
        print(f'❌ Error getting user info: {e}')
        raise


def get_external_ip():
    """
    Get your current external/public IP address
    
    Returns:
        str: Your external IP address
    """
    # Try multiple services in case one is down
    ip_services = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://ifconfig.me/ip',
        'https://api.ip.sb/ip'
    ]
    
    for service_url in ip_services:
        try:
            print(f'🌐 Detecting external IP address...')
            response = requests.get(service_url, timeout=5)
            response.raise_for_status()
            ip = response.text.strip()
            
            # Validate it looks like an IP address
            parts = ip.split('.')
            if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                print(f'✅ External IP detected: {ip}')
                return ip
            else:
                raise ValueError(f'Invalid IP format: {ip}')
                
        except Exception as e:
            print(f'⚠️  Failed to get IP from {service_url}: {e}')
            continue
    
    raise Exception('Could not detect external IP address from any service')


def unlock_ip(new_ip_address, session_cookie=None):
    """
    Update the unlocked IP address
    
    Args:
        new_ip_address (str): The IP address to unlock
        session_cookie (str): Optional session cookie (e.g., ".AspNet.ApplicationCookie=...")
    """
    try:
        print(f'🔓 Attempting to unlock IP: {new_ip_address}')
        
        # If session cookie provided, add it to the session
        if session_cookie:
            # Parse cookie string
            if '=' in session_cookie:
                cookie_name, cookie_value = session_cookie.split('=', 1)
                session.cookies.set(cookie_name, cookie_value, domain=BASE_DOMAIN)
            else:
                print('⚠️  Warning: Session cookie format may be incorrect')
        
        # Get CSRF token
        csrf_token = get_csrf_token()
        
        # Get user info
        user_info = get_user_info()
        user_id = user_info['user_id']
        ip_unlock_id = user_info['ip_unlock_id']
        
        if not user_id:
            raise ValueError('UserId not found. You may need to provide a session cookie.')
        
        # Prepare form data
        form_data = {
            '__RequestVerificationToken': csrf_token,
            'UserId': user_id,
            'IpUnlockId': ip_unlock_id,
            'Ip': new_ip_address,
            'action': ''
        }
        
        print('📤 Submitting IP unlock request...')
        print(f'   UserId: {user_id}')
        print(f'   IpUnlockId: {ip_unlock_id}')
        print(f'   IP: {new_ip_address}')
        
        # Submit the form
        response = session.post(
            EDIT_URL,
            data=form_data,
            headers={
                'Referer': EDIT_URL,
                'Origin': BASE_URL
            },
            allow_redirects=False  # Don't follow redirects automatically
        )
        
        # Check if we got redirected (302) which means success
        if response.status_code in [200, 302]:
            print('✅ IP unlock request submitted successfully!')
            print(f'   Status: {response.status_code}')
            
            if 'Location' in response.headers:
                print(f'   Redirected to: {response.headers["Location"]}')
            
            return {'success': True, 'status': response.status_code}
        else:
            raise Exception(f'Unexpected status code: {response.status_code}')
            
    except requests.exceptions.RequestException as e:
        print(f'❌ Network Error: {e}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'   Status: {e.response.status_code}')
            print(f'   Response: {e.response.text[:200]}')
        raise
    except Exception as e:
        print(f'❌ Error: {e}')
        raise


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print('Usage: python unlock_ip.py [IP_ADDRESS] [OPTIONS]')
        print('')
        print('Options:')
        print('  --auto-ip             Automatically detect and use external IP (default if no IP provided)')
        print('  --cookie <COOKIE>     Use existing session cookie')
        print('  --login               Login with email/password (interactive)')
        print('  --email <EMAIL>        Username/Email for login (use with --login)')
        print('  --password <PASSWORD>  Password for login (use with --login, no prompt)')
        print('')
        print('Examples:')
        print('  python unlock_ip.py --auto-ip --login')
        print('  python unlock_ip.py --auto-ip --login --email user@example.com --password mypass')
        print('  python unlock_ip.py 192.168.1.1 --cookie ".AspNet.ApplicationCookie=..."')
        print('  python unlock_ip.py 192.168.1.1 --login')
        print('')
        print('Note: If no IP address provided, --auto-ip is assumed.')
        sys.exit(1)
    
    ip_address = None
    session_cookie = None
    use_login = False
    email = None
    password = None
    auto_ip = False
    
    # Parse arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--cookie' and i + 1 < len(sys.argv):
            session_cookie = sys.argv[i + 1]
            i += 2
        elif arg == '--login':
            use_login = True
            i += 1
        elif arg == '--email' and i + 1 < len(sys.argv):
            email = sys.argv[i + 1]
            i += 2
        elif arg == '--password' and i + 1 < len(sys.argv):
            password = sys.argv[i + 1]
            i += 2
        elif arg == '--auto-ip':
            auto_ip = True
            i += 1
        elif not arg.startswith('--'):
            # This is likely the IP address
            ip_address = arg
            i += 1
        else:
            i += 1
    
    # If no IP provided, default to auto-detect
    if not ip_address:
        auto_ip = True
    
    # Get IP address
    if auto_ip:
        ip_address = get_external_ip()
    else:
        print(f'📌 Using provided IP: {ip_address}')
    
    try:
        # If login requested, authenticate first
        if use_login:
            if not email:
                email = input('Username/Email: ')
            if not password:
                password = getpass.getpass('Password: ')
            session_cookie = login(email, password)
            print('')
        
        # Unlock the IP
        print('')
        unlock_ip(ip_address, session_cookie)
        
    except KeyboardInterrupt:
        print('\n\n❌ Cancelled by user')
        sys.exit(1)
    except Exception as e:
        print('')
        print('💡 Tips:')
        print('   - Use --login to authenticate with email/password')
        print('   - Or get cookie from browser: DevTools > Application > Cookies')
        print('   - Look for: .AspNet.ApplicationCookie')
        sys.exit(1)


if __name__ == '__main__':
    main()
