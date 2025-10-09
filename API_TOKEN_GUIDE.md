# 🔑 How to Get Your Jira API Token

Since Wetrack uses SSO (Single Sign-On) authentication, you'll need to create an API token to authenticate with the Jira API. Here's how:

## 📋 Step-by-Step Guide

### 1. **Access Atlassian Account Settings**

1. **Go to Atlassian Account Management**:
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - OR navigate to your Jira instance and click on your profile → Account Settings

2. **Login with SSO**:
   - Use your company SSO credentials to log in

### 2. **Create API Token**

1. **Find API Tokens Section**:
   - Look for "API tokens" in the Security section
   - Click "Create API token"

2. **Configure Token**:
   - **Label**: Give it a descriptive name (e.g., "Jira Manager Script")
   - **Expiration**: Set appropriate expiration (or leave blank for no expiration)
   - Click "Create"

3. **Copy Token**:
   - ⚠️ **IMPORTANT**: Copy the token immediately - you won't be able to see it again!
   - Save it securely (password manager recommended)

### 3. **Alternative: If Direct Access Doesn't Work**

If the above doesn't work due to company restrictions:

#### **Option A: Through Jira Interface**
1. Log into https://your-jira-instance.example.com
2. Click your profile picture (top right)
3. Select "Account settings" or "Manage account"
4. Look for "Security" → "API tokens"

#### **Option B: Contact IT Admin**
If you can't access API token creation:
1. Contact your Jira administrator
2. Request API token creation for automation purposes
3. Provide them with the script requirements

## 🔧 Configuration

### **Method 1: Using Setup Script**
```bash
cd /home/arun/Dev/jora
uv run setup.py
```
Enter when prompted:
- **Username**: Your email address (e.g., `john.doe@example.com`)
- **API Token**: The token you just created

### **Method 2: Manual Configuration**
```bash
cp .env.template .env
nano .env
```

Edit the `.env` file:
```bash
JIRA_SERVER=https://your-jira-instance.example.com
JIRA_USERNAME=your.email@example.com
JIRA_API_TOKEN=ATBBxxxxxxxxxxxxxxxxxxx
DEFAULT_PROJECT=ARTS
DEFAULT_ASSIGNEE=me
```

## 🧪 Testing Your Connection

```bash
cd /home/arun/Dev/jora
uv run jira_manager.py
```

If successful, you should see:
```
✅ Successfully connected to Jira: https://your-jira-instance.example.com
👤 Logged in as: John Doe
```

## 🔒 Security Best Practices

### **Token Storage**
- ✅ Store in `.env` file (git-ignored)
- ✅ Use a password manager for backup
- ❌ Never commit tokens to version control
- ❌ Don't share tokens in chat/email

### **Token Management**
- 🔄 Rotate tokens periodically
- 🗑️ Revoke unused tokens
- 📝 Use descriptive labels
- ⏰ Set appropriate expiration dates

## 🚨 Troubleshooting

### Common Issues:

#### **403 Forbidden**
- Check if your account has permission to access the project
- Verify API token is valid and not expired
- Ensure you're using the correct email address

#### **401 Unauthorized**
- Double-check the API token (no extra spaces/characters)
- Verify the username/email is correct
- Try regenerating the API token

#### **SSL Certificate Issues**
If you get SSL errors, temporarily set `verify=False` in the script:
```python
options={'verify': False}  # Only for testing!
```

#### **Cannot Access Token Creation**
- Try different browsers
- Clear browser cache
- Contact IT administrator
- Check if your account has the necessary permissions

## 📞 Need Help?

1. **Check Jira Permissions**: Ensure you can access ARTS project in the web interface
2. **Verify Token**: Test the token with a simple curl command:
   ```bash
   curl -u your.email@example.com:your_api_token \
        https://your-jira-instance.example.com/rest/api/2/myself
   ```
3. **Contact Support**: If issues persist, contact your Jira administrator

---

**Once configured, you'll have full API access to manage your Jira tickets programmatically!** 🚀