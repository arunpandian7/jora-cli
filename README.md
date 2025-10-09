# 🃏 Jora - Because Jira is a Joke!

*Making ticket management less painful, one batch at a time* 😉

A Python script that actually makes Jira usable (revolutionary concept!). Connect to your private Jira instance and manage tickets efficiently - without pulling your hair out.

## Features (That Actually Work!)

- 🔐 **Secure Authentication**: Connect to private Jira instances (unlike their broken SSO)
- 🔍 **Smart Filtering**: Filter tickets by project, release, assignee (properly, not like the web UI)
- 📝 **Batch Time Management**: Edit original estimates and log work in bulk (efficiency!)
- � **Intelligent Ticket Detection**: Find incomplete tickets automatically
- 📋 **Readable Ticket Details**: View ticket info without the web interface nightmare
- 🎯 **Sane Command Interface**: Because clicking through 50 menus is ridiculous

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

4. **Run Jora (The Better Way)**:
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

## Example Workflow (The Sane Way)

1. **Connect** to Jira instance (once, not every 5 minutes like the web UI)
2. **Batch Find** incomplete tickets by project `ARTS`, assignee `me`
3. **Review** tickets in a readable table (revolutionary!)
4. **Batch Update** original estimates and work logs efficiently
5. **Actually Get Work Done** instead of fighting with Jira's interface
6. **Profit** from increased productivity 💰

## Troubleshooting

- **SSL Issues**: Set `verify=False` in JIRA connection if needed
- **Authentication**: Ensure correct username/password in `.env`
- **Permissions**: Verify you have access to edit tickets and log work

## Requirements

- Python 3.9+
- Access to https://your-jira-instance.example.com
- Valid Jira credentials with appropriate permissions
