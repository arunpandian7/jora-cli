#!/usr/bin/env python3
"""
🃏 Jora Setup - Because Jira is a Joke!
Quick setup script that actually works (unlike Jira's setup process)
"""

import os


def setup():
    """Quick setup for Jira Manager"""
    print("🃏 Jora Setup - Because Jira is a Joke!")
    print("💫 Setting up something that actually works...")
    print("=" * 50)

    # Check if .env exists
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        overwrite = input("Do you want to reconfigure? (y/N): ").lower().strip()
        if overwrite != "y":
            print("Setup cancelled.")
            return

    # Get user input
    print("\n📝 Please provide your Jira credentials:")
    username = input("Jira Username/Email: ").strip()
    api_token = input("Jira API Token: ").strip()

    # Optional settings
    print("\n⚙️  Optional settings (press Enter to skip):")
    default_project = input("Default Project (e.g., ARTS): ").strip()
    default_assignee = input("Default Assignee (e.g., me): ").strip()

    # Create .env file
    env_content = f"""# Jira Configuration
JIRA_SERVER=https://your-jira-instance.example.com
JIRA_USERNAME={username}
JIRA_API_TOKEN={api_token}
"""

    if default_project:
        env_content += f"DEFAULT_PROJECT={default_project}\n"
    if default_assignee:
        env_content += f"DEFAULT_ASSIGNEE={default_assignee}\n"

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n✅ Configuration saved to .env")
    print("� You can now run Jora: uv run jira_manager.py")
    print("🔒 Note: .env file is secure and git-ignored (unlike Jira's security)")
    print("💫 Ready to make ticket management less painful!")


if __name__ == "__main__":
    setup()
