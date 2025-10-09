#!/usr/bin/env python3
"""
Batch Time Tracking Demo
Demonstrates the new batch processing features for time tracking
"""

from jira_manager import JiraManager


def demo_batch_processing():
    """Demo the batch time tracking functionality"""

    print("🎯 Batch Time Tracking Demo")
    print("=" * 50)

    # Initialize and connect
    jira_manager = JiraManager()
    if not jira_manager.connect():
        print("❌ Failed to connect to Jira")
        return

    print("\n🔍 Demo: Finding incomplete tickets...")

    # Example: Find incomplete tickets in ARTS project assigned to current user
    incomplete_tickets = jira_manager.find_incomplete_tickets(
        project_name="ARTS", assignee="me", max_results=10
    )

    if not incomplete_tickets:
        print("✅ No incomplete tickets found!")
        return

    print(f"\n📋 Found {len(incomplete_tickets)} incomplete tickets:")
    jira_manager.display_incomplete_tickets(incomplete_tickets)

    # Ask if user wants to proceed with batch update
    proceed = (
        input(
            f"\n🚀 Start batch update for these {len(incomplete_tickets)} tickets? (y/N): "
        )
        .strip()
        .lower()
    )

    if proceed == "y":
        print("\n🔄 Starting batch update process...")
        jira_manager.batch_update_time_tracking(incomplete_tickets)
    else:
        print("👋 Demo completed without updates")


def quick_batch_example():
    """Show a quick example of the workflow"""
    print("\n📋 Quick Batch Processing Workflow:")
    print("=" * 40)
    print("1. 🔍 Find tickets without original estimates")
    print("2. 📊 Display tickets in organized table")
    print("3. 🔄 Iterate through each ticket:")
    print("   • Show current time tracking status")
    print("   • Prompt for original estimate")
    print("   • Prompt for work log with start date/time")
    print("   • Update ticket and move to next")
    print("4. 📈 Show summary of updates")
    print()
    print("💡 Features:")
    print("   ✅ Automatic filtering for incomplete tickets")
    print("   ✅ Batch processing with user control")
    print("   ✅ Custom start date/time for work logs")
    print("   ✅ Skip or stop options during processing")
    print("   ✅ Update summary and error handling")


if __name__ == "__main__":
    print("🎯 Jira Batch Time Tracking")
    print("=" * 30)
    print("1. Run interactive demo")
    print("2. Show workflow overview")
    print("0. Exit")

    choice = input("\nChoose option (0-2): ").strip()

    if choice == "1":
        demo_batch_processing()
    elif choice == "2":
        quick_batch_example()
    else:
        print("👋 Goodbye!")
