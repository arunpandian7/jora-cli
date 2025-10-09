#!/usr/bin/env python3
"""
Enhanced API Token Test Script
Test different authentication methods for Jira
"""

import os
import requests
from dotenv import load_dotenv
import getpass
import base64
import json


def test_basic_auth():
    """Test with Basic Authentication (email + API token)"""
    load_dotenv()

    username = os.getenv("JIRA_USERNAME")
    api_token = os.getenv("JIRA_API_TOKEN")
    server_url = os.getenv("JIRA_SERVER")

    print(f"📧 Testing Basic Auth with: {username}")
    print(f"🔗 Server: {server_url}")

    credentials = f"{username}:{api_token}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    return test_endpoint(server_url, headers, "Basic Auth")


def test_bearer_token():
    """Test with Bearer Token (Personal Access Token)"""
    load_dotenv()

    api_token = os.getenv("JIRA_API_TOKEN")
    server_url = os.getenv("JIRA_SERVER")

    print(f"🎫 Testing Bearer Token")
    print(f"🔗 Server: {server_url}")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    return test_endpoint(server_url, headers, "Bearer Token")


def test_endpoint(server_url, headers, auth_method):
    """Test a specific endpoint with given headers"""
    try:
        # Test endpoint: get current user info
        response = requests.get(
            f"{server_url}/rest/api/2/myself",
            headers=headers,
            timeout=30,
            verify=True,
        )

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ {auth_method} - SUCCESS!")
            print(f"👤 Name: {user_info.get('displayName', 'Unknown')}")
            print(f"📧 Email: {user_info.get('emailAddress', 'Not available')}")
            print(f"🔑 Account ID: {user_info.get('accountId', 'Not available')}")
            return True

        elif response.status_code == 401:
            print(f"❌ {auth_method} - Authentication Failed (401)")
            print(f"🔍 Response: {response.text[:200]}")
            return False

        elif response.status_code == 403:
            print(f"❌ {auth_method} - Access Forbidden (403)")
            print(f"🔍 Response: {response.text[:200]}")
            return False

        else:
            print(f"❌ {auth_method} - Failed with status {response.status_code}")
            print(f"🔍 Response: {response.text[:200]}")
            return False

    except requests.exceptions.SSLError as e:
        print(f"🔒 SSL Error with {auth_method}: {str(e)}")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"🌐 Connection Error with {auth_method}: {str(e)}")
        return False

    except Exception as e:
        print(f"💥 Unexpected error with {auth_method}: {str(e)}")
        return False


def test_projects_access(server_url, headers):
    """Test access to projects"""
    try:
        print("\n🔍 Testing project access...")
        projects_response = requests.get(
            f"{server_url}/rest/api/2/project", headers=headers, timeout=30, verify=True
        )

        if projects_response.status_code == 200:
            projects = projects_response.json()
            print(f"📋 Found {len(projects)} accessible projects:")

            # Look for ARTS project specifically
            arts_project = None
            for project in projects:
                if project.get("key") == "ARTS":
                    arts_project = project
                    break

            if arts_project:
                print(f"🎯 ARTS Project Found: {arts_project.get('name', 'N/A')}")
            else:
                print("⚠️  ARTS project not found in accessible projects")

            # Show first few projects
            for project in projects[:5]:
                print(f"   • {project.get('key', 'N/A')}: {project.get('name', 'N/A')}")
            if len(projects) > 5:
                print(f"   ... and {len(projects) - 5} more")

        else:
            print(
                f"❌ Could not fetch projects (Status: {projects_response.status_code})"
            )
            print(f"🔍 Response: {projects_response.text[:200]}")

    except Exception as e:
        print(f"💥 Error testing projects: {str(e)}")


def main():
    """Main test function"""
    print("🧪 Enhanced Jira Authentication Test")
    print("=" * 40)

    # Load and display current config
    load_dotenv()
    username = os.getenv("JIRA_USERNAME")
    token = os.getenv("JIRA_API_TOKEN")
    server = os.getenv("JIRA_SERVER")

    print(f"📧 Username: {username}")
    print(f"🎫 Token: {token[:10]}...{token[-5:] if len(token) > 15 else token}")
    print(f"🌐 Server: {server}")
    print()

    # Test different authentication methods
    print("1️⃣ Testing Basic Authentication (Username + Token)...")
    basic_success = test_basic_auth()

    print("\n2️⃣ Testing Bearer Token (Personal Access Token)...")
    bearer_success = test_bearer_token()

    # If either method worked, test project access
    if basic_success:
        print("\n🎉 Basic Auth worked! Testing project access...")
        load_dotenv()
        username = os.getenv("JIRA_USERNAME")
        api_token = os.getenv("JIRA_API_TOKEN")
        server_url = os.getenv("JIRA_SERVER")

        credentials = f"{username}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
        }
        test_projects_access(server_url, headers)

    elif bearer_success:
        print("\n🎉 Bearer Token worked! Testing project access...")
        load_dotenv()
        api_token = os.getenv("JIRA_API_TOKEN")
        server_url = os.getenv("JIRA_SERVER")

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
        }
        test_projects_access(server_url, headers)

    else:
        print("\n❌ Both authentication methods failed!")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Verify your token is a valid Personal Access Token")
        print("2. Check if the token has expired")
        print("3. Ensure you have permissions to access Jira")
        print("4. Try regenerating the token")
        print("5. Contact your Jira administrator")


if __name__ == "__main__":
    main()
