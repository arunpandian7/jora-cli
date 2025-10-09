#!/usr/bin/env python3
"""
Quick API Token Test Script
Test your Jira API token before using the main application
"""

import os
import requests
from dotenv import load_dotenv
import getpass
import base64


def test_api_token():
    """Test Jira API token connectivity"""
    print("🧪 Jira API Token Test")
    print("=" * 30)

    # Load environment variables
    load_dotenv()

    # Get credentials
    username = os.getenv("JIRA_USERNAME") or input("Enter Jira username/email: ")
    api_token = os.getenv("JIRA_API_TOKEN") or getpass.getpass("Enter Jira API token: ")
    server_url = os.getenv("JIRA_SERVER") or "https://your-jira-instance.example.com"

    # Test with simple REST API call
    try:
        print(f"🔗 Testing connection to {server_url}...")

        # Create basic auth header
        credentials = f"{username}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Test endpoint: get current user info
        response = requests.get(
            f"{server_url}/rest/api/2/myself",
            headers=headers,
            timeout=30,
            verify=True,  # Set to False if SSL issues
        )

        if response.status_code == 200:
            user_info = response.json()
            print("✅ API Token Test PASSED!")
            print(f"👤 Logged in as: {user_info.get('displayName', 'Unknown')}")
            print(f"📧 Email: {user_info.get('emailAddress', 'Not available')}")
            print(f"🔑 Account ID: {user_info.get('accountId', 'Not available')}")

            # Test project access
            print("\n🔍 Testing project access...")
            projects_response = requests.get(
                f"{server_url}/rest/api/2/project",
                headers=headers,
                timeout=30,
                verify=True,
            )

            if projects_response.status_code == 200:
                projects = projects_response.json()
                print(f"📋 Found {len(projects)} accessible projects:")
                for project in projects[:5]:  # Show first 5 projects
                    print(
                        f"   • {project.get('key', 'N/A')}: {project.get('name', 'N/A')}"
                    )
                if len(projects) > 5:
                    print(f"   ... and {len(projects) - 5} more")
            else:
                print(
                    f"⚠️  Could not fetch projects (Status: {projects_response.status_code})"
                )

            return True

        elif response.status_code == 401:
            print("❌ API Token Test FAILED!")
            print("🔐 Authentication failed - check your username and API token")
            print("💡 Make sure you're using your email address as username")
            return False

        elif response.status_code == 403:
            print("❌ API Token Test FAILED!")
            print("🚫 Access forbidden - your account may not have permission")
            print("💡 Contact your Jira administrator for access")
            return False

        else:
            print(f"❌ API Token Test FAILED!")
            print(f"🌐 HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.SSLError:
        print("❌ SSL Certificate Error!")
        print("🔒 Try setting verify=False in the script temporarily")
        return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("🌐 Cannot reach the Jira server - check your network/VPN")
        return False

    except requests.exceptions.Timeout:
        print("❌ Connection Timeout!")
        print("⏱️  Server took too long to respond")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """Main test function"""
    success = test_api_token()

    if success:
        print("\n🎉 Your API token is working correctly!")
        print("✨ You can now use the main Jira Manager application")
        print("🚀 Run: uv run jira_manager.py")
    else:
        print("\n🔧 Troubleshooting steps:")
        print("1. Check API_TOKEN_GUIDE.md for token creation steps")
        print("2. Verify your email and token in .env file")
        print("3. Ensure you have access to the Jira instance")
        print("4. Contact IT if you need permissions")


if __name__ == "__main__":
    main()
