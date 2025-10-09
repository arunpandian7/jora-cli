#!/usr/bin/env python3
"""
🃏 Jora Usage Examples - Because Jira is a Joke!
This script demonstrates how to use Jora programmatically
(You know, actually getting stuff done efficiently)
"""

from jira_manager import JoraManager


def example_usage():
    """Example of how to use JiraManager programmatically"""

    # Initialize Jora manager (the better way)
    jira_manager = JoraManager()

    # Connect (will prompt for credentials if not in .env)
    if not jira_manager.connect():
        print("Failed to connect to Jira")
        return

    # Example 1: Filter tickets for ARTS project, assigned to me
    print("\n🔍 Example 1: Filtering ARTS tickets assigned to me")
    issues = jira_manager.filter_tickets(
        project_name="ARTS", assignee="me", max_results=10
    )
    jira_manager.display_tickets(issues)

    # Example 2: Get details for a specific ticket
    print("\n📋 Example 2: Getting details for ARTS-3183")
    jira_manager.get_ticket_details("ARTS-3183")

    # Example 3: Filter by release
    print("\n🔍 Example 3: Filtering by release version")
    release_issues = jira_manager.filter_tickets(
        project_name="ARTS",
        release="v2.1.0",  # Replace with actual release name
    )
    jira_manager.display_tickets(release_issues)

    print("\n✅ Jora example completed! Use the interactive script for full functionality.")
    print("🃏 See how much better this is than using Jira's web interface? 😉")


if __name__ == "__main__":
    example_usage()
