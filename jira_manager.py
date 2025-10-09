#!/usr/bin/env python3
"""
Jira Manager Script
A Python script to connect to private Jira instance and manage tickets.
Features:
- Connect to private Jira instance
- Filter tickets by project name, release, and assignee
- Edit original estimate and work log
"""

import os
from typing import List, Optional
from jira import JIRA, Issue
from dotenv import load_dotenv
import getpass

# Load environment variables
load_dotenv()


class JiraManager:
    def __init__(self):
        self.jira = None
        self.server_url = "https://your-jira-instance.example.com"

    def connect(
        self, username: Optional[str] = None, api_token: Optional[str] = None
    ) -> bool:
        """Connect to Jira instance using Personal Access Token"""
        try:
            # Get credentials from environment or prompt user
            if not username:
                username = os.getenv("JIRA_USERNAME") or input(
                    "Enter Jira username/email: "
                )
            if not api_token:
                api_token = os.getenv("JIRA_API_TOKEN") or getpass.getpass(
                    "Enter Jira Personal Access Token: "
                )

            print("🔗 Connecting to Jira...")

            # Connect to Jira using Personal Access Token (Bearer auth)
            self.jira = JIRA(
                server=self.server_url,
                token_auth=api_token,  # Use token_auth for Bearer tokens
                options={
                    "verify": True,  # Set to False if you have SSL certificate issues
                    "server": self.server_url,
                },
            )

            # Test the connection
            current_user = self.jira.current_user()
            print(f"✅ Successfully connected to Jira: {self.server_url}")
            print(f"👤 Logged in as: {current_user}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect to Jira: {str(e)}")
            print("💡 Make sure your API token is valid and has the right permissions.")
            return False

    def filter_tickets(
        self,
        project_name: Optional[str] = None,
        release: Optional[str] = None,
        assignee: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Issue]:
        """Filter tickets based on project name, release, and assignee"""
        if not self.jira:
            print("❌ Not connected to Jira. Please connect first.")
            return []

        # Build JQL query
        jql_parts = []

        if project_name:
            jql_parts.append(f'project = "{project_name}"')

        if release:
            jql_parts.append(f'fixVersion = "{release}"')

        if assignee:
            if assignee.lower() == "me":
                jql_parts.append("assignee = currentUser()")
            else:
                jql_parts.append(f'assignee = "{assignee}"')

        jql = " AND ".join(jql_parts) if jql_parts else "project is not EMPTY"

        try:
            issues = self.jira.search_issues(jql, maxResults=max_results)
            print(f"🔍 Found {len(issues)} tickets matching criteria")
            return issues
        except Exception as e:
            print(f"❌ Error searching for tickets: {str(e)}")
            return []

    def display_tickets(self, issues: List[Issue]):
        """Display tickets in a formatted table"""
        if not issues:
            print("No tickets found.")
            return

        print("\n" + "=" * 120)
        print(
            f"{'Key':<15} {'Summary':<50} {'Status':<15} {'Assignee':<20} {'Original Estimate':<20}"
        )
        print("=" * 120)

        for issue in issues:
            key = issue.key
            summary = (
                (issue.fields.summary[:47] + "...")
                if len(issue.fields.summary) > 50
                else issue.fields.summary
            )
            status = issue.fields.status.name
            assignee = (
                issue.fields.assignee.displayName
                if issue.fields.assignee
                else "Unassigned"
            )
            original_estimate = self._format_time_estimate(
                issue.fields.timeoriginalestimate
            )

            print(
                f"{key:<15} {summary:<50} {status:<15} {assignee:<20} {original_estimate:<20}"
            )

        print("=" * 120 + "\n")

    def _format_time_estimate(self, seconds: Optional[int]) -> str:
        """Convert seconds to human readable format"""
        if not seconds:
            return "Not set"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def _parse_time_input(self, time_str: str) -> Optional[int]:
        """Parse time input (e.g., '2h 30m', '90m', '1.5h') to seconds"""
        if not time_str or time_str.lower() in ["none", "null", ""]:
            return None

        try:
            time_str = time_str.lower().strip()
            total_seconds = 0

            # Handle formats like '2h 30m', '2h30m'
            if "h" in time_str:
                parts = time_str.split("h")
                hours = float(parts[0].strip())
                total_seconds += hours * 3600

                if len(parts) > 1 and parts[1].strip():
                    minutes_part = parts[1].replace("m", "").strip()
                    if minutes_part:
                        minutes = float(minutes_part)
                        total_seconds += minutes * 60

            # Handle formats like '90m'
            elif "m" in time_str:
                minutes = float(time_str.replace("m", "").strip())
                total_seconds += minutes * 60

            # Handle plain numbers (assume hours)
            else:
                hours = float(time_str)
                total_seconds += hours * 3600

            return int(total_seconds)

        except ValueError:
            print(
                f"❌ Invalid time format: {time_str}. Use formats like '2h 30m', '90m', or '1.5h'"
            )
            return None

    def edit_original_estimate(self, issue_key: str):
        """Edit the original estimate of a ticket"""
        if not self.jira:
            print("❌ Not connected to Jira. Please connect first.")
            return

        try:
            issue = self.jira.issue(issue_key)
            current_estimate = self._format_time_estimate(
                issue.fields.timeoriginalestimate
            )

            print(
                f"\n📝 Editing original estimate for {issue_key}: {issue.fields.summary}"
            )
            print(f"Current original estimate: {current_estimate}")

            new_estimate_str = input(
                "Enter new original estimate (e.g., '2h 30m', '90m', '1.5h') or 'none' to clear: "
            )

            if new_estimate_str.lower() == "cancel":
                print("❌ Operation cancelled.")
                return

            new_estimate_seconds = self._parse_time_input(new_estimate_str)

            # Try different approaches to update original estimate
            try:
                # Method 1: Try updating via edit meta to see available fields
                edit_meta = self.jira.editmeta(issue_key)
                available_fields = list(edit_meta["fields"].keys())
                print(f"🔍 Available fields for editing: {available_fields[:10]}...")

                # Method 2: Try using the time tracking specific update
                if new_estimate_seconds:
                    # Convert seconds to Jira time format (e.g., "2h 30m")
                    hours = new_estimate_seconds // 3600
                    minutes = (new_estimate_seconds % 3600) // 60
                    if hours > 0 and minutes > 0:
                        jira_time_format = f"{hours}h {minutes}m"
                    elif hours > 0:
                        jira_time_format = f"{hours}h"
                    else:
                        jira_time_format = f"{minutes}m"
                else:
                    jira_time_format = None

                # Try updating with time tracking
                if "timetracking" in available_fields:
                    timetracking_data = {}
                    if jira_time_format:
                        timetracking_data["originalEstimate"] = jira_time_format
                    else:
                        timetracking_data["originalEstimate"] = None

                    issue.update(fields={"timetracking": timetracking_data})
                    print(
                        f"✅ Successfully updated original estimate to: {jira_time_format or 'None'}"
                    )

                elif "timeoriginalestimate" in available_fields:
                    issue.update(fields={"timeoriginalestimate": new_estimate_seconds})
                    new_display = self._format_time_estimate(new_estimate_seconds)
                    print(
                        f"✅ Successfully updated original estimate to: {new_display}"
                    )
                else:
                    print("❌ Original estimate field is not editable on this issue")
                    print("💡 This might be due to:")
                    print("   • Field not available on the current screen")
                    print("   • Insufficient permissions")
                    print("   • Field is calculated/read-only")

            except Exception as update_error:
                print(f"❌ Could not update original estimate: {str(update_error)}")
                print("💡 Try logging work instead, which might update time tracking")

        except Exception as e:
            print(f"❌ Error updating original estimate: {str(e)}")

    def log_work(self, issue_key: str):
        """Log work on a ticket"""
        if not self.jira:
            print("❌ Not connected to Jira. Please connect first.")
            return

        try:
            issue = self.jira.issue(issue_key)

            print(f"\n⏱️ Logging work for {issue_key}: {issue.fields.summary}")

            time_spent_str = input("Enter time spent (e.g., '2h 30m', '90m', '1.5h'): ")
            comment = input("Enter work description (optional): ")

            if time_spent_str.lower() == "cancel":
                print("❌ Operation cancelled.")
                return

            time_spent_seconds = self._parse_time_input(time_spent_str)

            if not time_spent_seconds:
                print("❌ Invalid time format. Operation cancelled.")
                return

            # Log work
            self.jira.add_worklog(
                issue=issue_key,
                timeSpent=time_spent_str,
                comment=comment if comment else None,
            )

            time_display = self._format_time_estimate(time_spent_seconds)
            print(f"✅ Successfully logged {time_display} of work")
            if comment:
                print(f"   Comment: {comment}")

        except Exception as e:
            print(f"❌ Error logging work: {str(e)}")

    def get_ticket_details(self, issue_key: str):
        """Get detailed information about a ticket"""
        if not self.jira:
            print("❌ Not connected to Jira. Please connect first.")
            return

        try:
            issue = self.jira.issue(issue_key, expand="changelog")

            print(f"\n📋 Ticket Details: {issue_key}")
            print("=" * 60)
            print(f"Summary: {issue.fields.summary}")
            print(f"Status: {issue.fields.status.name}")
            print(
                f"Priority: {issue.fields.priority.name if issue.fields.priority else 'Not set'}"
            )
            print(
                f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}"
            )
            print(
                f"Reporter: {issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown'}"
            )
            print(
                f"Original Estimate: {self._format_time_estimate(issue.fields.timeoriginalestimate)}"
            )
            print(f"Time Spent: {self._format_time_estimate(issue.fields.timespent)}")
            print(
                f"Remaining Estimate: {self._format_time_estimate(issue.fields.timeestimate)}"
            )
            print(f"Created: {issue.fields.created}")
            print(f"Updated: {issue.fields.updated}")

            if issue.fields.fixVersions:
                versions = ", ".join([v.name for v in issue.fields.fixVersions])
                print(f"Fix Version(s): {versions}")

            if issue.fields.description:
                desc = (
                    issue.fields.description[:200] + "..."
                    if len(issue.fields.description) > 200
                    else issue.fields.description
                )
                print(f"Description: {desc}")

            print("=" * 60)

        except Exception as e:
            print(f"❌ Error getting ticket details: {str(e)}")

    def inspect_ticket_fields(self, issue_key: str):
        """Inspect what fields are available for editing on a ticket"""
        if not self.jira:
            print("❌ Not connected to Jira. Please connect first.")
            return

        try:
            print(f"\n🔍 Inspecting editable fields for {issue_key}...")

            # Get edit metadata
            edit_meta = self.jira.editmeta(issue_key)
            fields = edit_meta.get("fields", {})

            print(f"📝 Found {len(fields)} editable fields:")

            # Look for time-related fields specifically
            time_fields = []
            for field_id, field_info in fields.items():
                field_name = field_info.get("name", field_id)
                if "time" in field_id.lower() or "time" in field_name.lower():
                    time_fields.append((field_id, field_name))
                    print(f"   ⏱️  {field_id}: {field_name}")

            if not time_fields:
                print("   ❌ No time-related fields found for editing")

            # Show all fields (limited to first 20)
            print(f"\n📋 All editable fields (showing first 20):")
            for i, (field_id, field_info) in enumerate(fields.items()):
                if i >= 20:
                    print(f"   ... and {len(fields) - 20} more fields")
                    break
                field_name = field_info.get("name", field_id)
                print(f"   • {field_id}: {field_name}")

        except Exception as e:
            print(f"❌ Error inspecting fields: {str(e)}")


def main():
    """Main function with interactive menu"""
    jira_manager = JiraManager()

    print("🎯 Jira Manager - Private Instance Connector")
    print("=" * 50)

    # Connect to Jira
    if not jira_manager.connect():
        print("Failed to connect to Jira. Exiting.")
        return

    current_issues = []

    while True:
        print("\n📋 Main Menu:")
        print("1. Filter tickets")
        print("2. Display current tickets")
        print("3. Get ticket details")
        print("4. Inspect ticket fields")
        print("5. Edit original estimate")
        print("6. Log work")
        print("7. Reconnect to Jira")
        print("0. Exit")

        choice = input("\nEnter your choice (0-7): ").strip()

        if choice == "1":
            print("\n🔍 Filter Tickets")
            project_name = (
                input("Enter project name (or press Enter to skip): ").strip() or None
            )
            release = (
                input("Enter release/fix version (or press Enter to skip): ").strip()
                or None
            )
            assignee = (
                input(
                    "Enter assignee username ('me' for yourself, or press Enter to skip): "
                ).strip()
                or None
            )
            max_results = input("Max results (default 50): ").strip()
            max_results = int(max_results) if max_results.isdigit() else 50

            current_issues = jira_manager.filter_tickets(
                project_name, release, assignee, max_results
            )
            jira_manager.display_tickets(current_issues)

        elif choice == "2":
            if current_issues:
                jira_manager.display_tickets(current_issues)
            else:
                print("No tickets loaded. Please filter tickets first (option 1).")

        elif choice == "3":
            issue_key = input("Enter issue key (e.g., ARTS-3183): ").strip()
            if issue_key:
                jira_manager.get_ticket_details(issue_key)

        elif choice == "4":
            issue_key = input("Enter issue key to inspect fields: ").strip()
            if issue_key:
                jira_manager.inspect_ticket_fields(issue_key)

        elif choice == "5":
            issue_key = input("Enter issue key to edit original estimate: ").strip()
            if issue_key:
                jira_manager.edit_original_estimate(issue_key)

        elif choice == "6":
            issue_key = input("Enter issue key to log work: ").strip()
            if issue_key:
                jira_manager.log_work(issue_key)

        elif choice == "7":
            if jira_manager.connect():
                current_issues = []
                print("✅ Reconnected successfully.")

        elif choice == "0":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
