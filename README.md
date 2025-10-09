# Jira Manager

A Python script to connect to your private Jira instance (https://your-jira-instance.example.com) and manage tickets efficiently.

## Features

- 🔐 **Secure Authentication**: Connect to private Jira instance with credentials
- 🔍 **Advanced Filtering**: Filter tickets by project name, release/fix version, and assignee
- 📝 **Time Management**: Edit original estimates and log work time
- 📋 **Ticket Details**: View comprehensive ticket information
- 🎯 **Interactive Menu**: Easy-to-use command-line interface

## Setup

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Get Jira API Token**:
   - Since Wetrack uses SSO, you need an API token
   - Follow the guide in `API_TOKEN_GUIDE.md` to create one
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens

3. **Configure Environment**:
   ```bash
   # Quick setup (recommended)
   uv run setup.py
   
   # OR manual setup
   cp .env.template .env
   # Edit .env with your email and API token
   ```

4. **Run the Script**:
   ```bash
   ./run.sh
   # OR
   uv run jira_manager.py
   ```

## Usage Examples

### Filtering Tickets
- Filter by project: `ARTS`
- Filter by release: `v2.1.0`
- Filter by assignee: `me` or specific username
- Combine filters for precise results

### Time Management
- **Original Estimate**: Set initial time estimates (e.g., `2h 30m`, `90m`, `1.5h`)
- **Work Logging**: Log time spent with descriptions
- **Flexible Formats**: Supports various time formats

### Supported Time Formats
- `2h 30m` - 2 hours 30 minutes
- `90m` - 90 minutes
- `1.5h` - 1.5 hours
- `none` - Clear/remove estimate

## Security Notes

- API tokens are stored in `.env` file (not version controlled)
- SSL certificate verification enabled by default
- Token input is masked using getpass
- Works with SSO-enabled Jira instances

## Example Workflow

1. **Connect** to Jira instance
2. **Filter** tickets by project `ARTS`, release `v2.1.0`, assignee `me`
3. **View** ticket list with key details
4. **Select** a ticket to view full details
5. **Edit** original estimate or log work time
6. **Repeat** as needed

## Troubleshooting

- **SSL Issues**: Set `verify=False` in JIRA connection if needed
- **Authentication**: Ensure correct username/password in `.env`
- **Permissions**: Verify you have access to edit tickets and log work

## Requirements

- Python 3.9+
- Access to https://your-jira-instance.example.com
- Valid Jira credentials with appropriate permissions
