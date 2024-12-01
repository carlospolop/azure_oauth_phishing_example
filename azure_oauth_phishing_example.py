from flask import Flask, request, session, render_template_string
import requests
import os
import argparse
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Parse CLI arguments
parser = argparse.ArgumentParser(description='Run the Flask app with Azure OAuth.')
parser.add_argument('--client-id', required=True, help='Azure Client ID')
parser.add_argument('--client-secret', required=True, help='Azure Client Secret')
parser.add_argument('--scopes', default="https://graph.microsoft.com/.default", help='Comma separated list of scopes. By default: https://graph.microsoft.com/.default')
parser.add_argument('--redir-url', default='http://localhost:8000/callback', help='URL for redirect. By default: http://localhost:8000/callback')
args = parser.parse_args()

# Configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ONLY for development
AZURE_CLIENT_ID = args.client_id
AZURE_CLIENT_SECRET = args.client_secret
REDIRECT_URI = args.redir_url
SCOPES = args.scopes.split(',')
AUTHORITY = "https://login.microsoftonline.com/common"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
AUTH_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"

# Sanitize scopes
SCOPES = list(set(SCOPES))  # Remove duplicates
SCOPES = [scope.strip() for scope in SCOPES if scope.strip()]  # Clean scopes

# Config app
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    authorization_url = (
        f"{AUTH_URL}?client_id={AZURE_CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&response_mode=query&scope={' '.join(SCOPES)}&state=random_state_string"
    )
    return render_template_string("""
    <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .button {
                    display: inline-block;
                    background: #0078d4;
                    color: white;
                    border-radius: 2px;
                    padding: 10px 20px;
                    font-size: 16px;
                    text-decoration: none;
                    -webkit-box-shadow: 0 3px 6px 0 #666;
                    box-shadow: 0 3px 6px 0 #666;
                }
                .button:hover {
                    background: #005a9e;
                }
                .button img {
                    vertical-align: middle;
                    margin-right: 8px;
                }
            </style>
        </head>
        <body>
            <a href="{{ authorization_url }}" class="button">
                <img src="https://www.microsoft.com/favicon.ico" alt="Microsoft logo">
                <b>Login with Microsoft</b>
            </a>
        </body>
    </html>
    """, authorization_url=authorization_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or state != "random_state_string":
        return "Invalid response!", 400

    # Exchange code for token
    token_response = requests.post(
        TOKEN_URL,
        data={
            "client_id": AZURE_CLIENT_ID,
            "scope": " ".join(SCOPES),
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "client_secret": AZURE_CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_response.status_code != 200:
        return f"Token exchange failed: {token_response.text}", 400

    token_data = token_response.json()
    session['token_data'] = token_data

    # Console output with colors
    print(f"{Fore.GREEN}Access Token: {Style.BRIGHT}{token_data.get('access_token')}")
    print(f"{Fore.BLUE}Refresh Token: {Style.BRIGHT}{token_data.get('refresh_token')}")

    # Return tokens with color coding in HTML
    return f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                .token {{
                    font-size: 16px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    word-break: break-all;
                }}
                .access-token {{
                    color: green;
                    background-color: #f0fdf4;
                }}
                .refresh-token {{
                    color: blue;
                    background-color: #e0f7ff;
                }}
            </style>
        </head>
        <body>
            <h2>OAuth Tokens</h2>
            <div class="token access-token">
                <strong>Access Token:</strong><br>
                {token_data.get('access_token')}
            </div>
            <div class="token refresh-token">
                <strong>Refresh Token:</strong><br>
                {token_data.get('refresh_token')}
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run('localhost', 8000)
