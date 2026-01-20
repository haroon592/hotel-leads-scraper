#!/usr/bin/env python3
"""
Simple Zoho Refresh Token Generator
Run this to get your ZOHO_REFRESH_TOKEN
"""

import requests
import webbrowser
from urllib.parse import urlencode

print("="*70)
print("🔐 ZOHO CRM REFRESH TOKEN GENERATOR")
print("="*70)
print("\nYou already have:")
print("  ✓ Client ID: 1000.GIOV9I7GHETNSM5D0J1ZEVI0PCXNEQ")
print("  ✓ Client Secret: 465d7b5e5a4f4d83888db483eb4a3b5a67f08cab45")
print("\nNow let's get your Refresh Token...\n")
print("="*70)

# Your existing credentials
CLIENT_ID = "1000.GIOV9I7GHETNSM5D0J1ZEVI0PCXNEQ"
CLIENT_SECRET = "465d7b5e5a4f4d83888db483eb4a3b5a67f08cab45"
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL"

# Step 1: Generate authorization URL
print("\n📌 STEP 1: Get Authorization Code")
print("-" * 70)

auth_params = {
    'scope': SCOPE,
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'access_type': 'offline',
    'redirect_uri': REDIRECT_URI
}

auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(auth_params)}"

print("\n1️⃣  A browser window will open (or copy the URL below)")
print("\n" + "="*70)
print(auth_url)
print("="*70)

# Try to open browser automatically
try:
    webbrowser.open(auth_url)
    print("\n✓ Browser opened automatically")
except:
    print("\n⚠️  Please copy and paste the URL above into your browser")

print("\n2️⃣  In the browser:")
print("   • Login with: hello@centrox.ai / Hello101.!")
print("   • Click 'Accept' or 'Allow' to authorize")
print("\n3️⃣  After clicking Accept:")
print("   • The browser will try to load: http://localhost:8000/callback?code=...")
print("   • The page WON'T load (shows error) - THIS IS NORMAL!")
print("   • Look at the browser's ADDRESS BAR")
print("   • It should show: http://localhost:8000/callback?code=1000.xxxxx...")
print("   • Copy the ENTIRE URL from the address bar")

print("\n" + "="*70)
print("\n⚠️  IMPORTANT: Do NOT paste the authorization URL again!")
print("   You need the NEW URL that appears AFTER clicking Accept")
print("   It starts with: http://localhost:8000/callback?code=")
print("="*70)

# Step 2: Get the authorization code
print("\n📌 STEP 2: Enter the Redirect URL")
print("-" * 70)

redirect_url = input("\n📋 Paste the REDIRECT URL (starts with http://localhost:8000/callback): ").strip()

# Extract code from URL
try:
    if 'code=' in redirect_url:
        auth_code = redirect_url.split('code=')[1].split('&')[0]
        print(f"\n✓ Extracted authorization code: {auth_code[:20]}...\n")
    else:
        print("\n" + "="*70)
        print("❌ ERROR: No 'code=' found in URL")
        print("="*70)
        print("\n🤔 What you pasted:")
        print(f"   {redirect_url[:80]}...")
        print("\n✋ Common mistakes:")
        print("   1. You pasted the ORIGINAL authorization URL")
        print("   2. You didn't click 'Accept' in the browser yet")
        print("   3. You copied the URL before the redirect happened")
        print("\n✅ What you SHOULD paste:")
        print("   http://localhost:8000/callback?code=1000.xxxxxxxxxxxxx")
        print("\n📝 Steps to fix:")
        print("   1. Go to the browser window that opened")
        print("   2. Login if needed: hello@centrox.ai / Hello101.!")
        print("   3. Click 'Accept' or 'Allow'")
        print("   4. Wait for redirect (page will show error - that's OK!)")
        print("   5. Look at address bar - it should start with:")
        print("      http://localhost:8000/callback?code=")
        print("   6. Copy that ENTIRE URL and run this script again")
        print("="*70 + "\n")
        exit(1)
except Exception as e:
    print(f"\n❌ Error parsing URL: {e}")
    print("Make sure you copied the entire redirect URL!\n")
    exit(1)

# Step 3: Exchange code for refresh token
print("="*70)
print("\n📌 STEP 3: Getting Refresh Token")
print("-" * 70)

token_url = "https://accounts.zoho.com/oauth/v2/token"
token_params = {
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
}

print("\n⏳ Requesting tokens from Zoho...")

try:
    response = requests.post(token_url, params=token_params)
    response.raise_for_status()
    data = response.json()
    
    if 'refresh_token' in data:
        refresh_token = data['refresh_token']
        
        print("\n" + "="*70)
        print("🎉 SUCCESS! YOUR REFRESH TOKEN:")
        print("="*70)
        print(f"\n{refresh_token}\n")
        print("="*70)
        print("\n📝 NEXT STEP: Add this to your .env file")
        print("-" * 70)
        print("\nOpen .env file and update this line:")
        print(f"\nZOHO_REFRESH_TOKEN={refresh_token}\n")
        print("="*70)
        
        # Offer to update .env automatically
        update = input("\n❓ Would you like me to update .env automatically? (y/n): ").strip().lower()
        
        if update == 'y':
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                
                # Replace the empty refresh token line
                if 'ZOHO_REFRESH_TOKEN=' in env_content:
                    env_content = env_content.replace(
                        'ZOHO_REFRESH_TOKEN=',
                        f'ZOHO_REFRESH_TOKEN={refresh_token}'
                    )
                    
                    with open('.env', 'w') as f:
                        f.write(env_content)
                    
                    print("\n✅ .env file updated successfully!")
                    print("\n🚀 You're ready to run the scheduler!")
                    print("\nRun: python scheduler.py")
                else:
                    print("\n⚠️  Couldn't find ZOHO_REFRESH_TOKEN in .env")
                    print("Please add it manually.")
            except Exception as e:
                print(f"\n⚠️  Couldn't update .env automatically: {e}")
                print("Please update it manually.")
        else:
            print("\n👍 No problem! Just copy the token above to your .env file.")
        
        print("\n" + "="*70 + "\n")
        
    else:
        print("\n❌ Error: No refresh_token in response")
        print(f"Response: {data}")
        
except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n✨ Done!\n")
