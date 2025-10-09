# 🔄 Batch Time Tracking Guide

## 🎯 **New Features Added**

Your Jira Manager now includes powerful batch processing capabilities to efficiently handle tickets with missing original estimates and incomplete work logs.

## 🚀 **Key Features**

### 1. **🔍 Smart Ticket Detection**
- Automatically finds tickets without original estimates
- Identifies tickets with remaining work (not 100% complete)
- Filters by assignee, project, and release
- Uses advanced JQL queries for precise results

### 2. **📊 Enhanced Display**
- Shows incomplete tickets in organized table format
- Displays current time tracking status for each ticket
- Includes original estimate, time spent, and remaining time
- Numbers tickets for easy reference

### 3. **🔄 Batch Processing**
- Iterates through tickets one by one
- Interactive prompts for each ticket
- Options to set estimates, log work, or both
- Skip individual tickets or stop processing anytime

### 4. **⏰ Advanced Work Logging**
- Custom start date and time for work logs
- Timezone handling (Asia/Tokyo default)
- Flexible time formats (2h 30m, 90m, 1.5h)
- Optional work descriptions

## 📋 **How to Use**

### **Step 1: Find Incomplete Tickets**
```
Menu Option 7: 🔄 Find incomplete tickets
```
1. Enter project name (e.g., "ARTS")
2. Enter release version (optional)
3. Enter assignee ("me" for yourself)
4. Set max results (default 50)

**Example Filters:**
- Project: `ARTS`, Assignee: `me` → Your ARTS tickets
- Project: `ARTS`, Release: `v2.1.0` → Specific release tickets
- Assignee: `john.doe` → Specific person's tickets

### **Step 2: Review Results**
The system will display a table showing:
```
#   Key           Summary                    Status    Original Est  Time Spent  Remaining
1   ARTS-3183     Database optimization      In Prog   Not set      2h 0m       Not set
2   ARTS-3184     UI bug fixes               To Do     4h 0m        0h 0m       4h 0m
```

### **Step 3: Batch Update**
```
Menu Option 8: 🚀 Batch update time tracking
```

For each ticket, you'll see:
```
📋 Ticket 1/5: ARTS-3183
📝 Summary: Database optimization task
📊 Current Status:
   • Original Estimate: Not set
   • Time Spent: 2h 0m
   • Remaining: Not set

🤔 Actions for ARTS-3183:
1. Set original estimate
2. Log work
3. Set original estimate AND log work
4. Skip this ticket
0. Stop batch processing
```

### **Step 4: Enter Time Data**

**For Original Estimates:**
```
Enter original estimate (e.g., '4h', '2h 30m', '90m'): 6h
```

**For Work Logging:**
```
Enter time spent (e.g., '2h', '90m'): 2h 30m
Enter start date (YYYY-MM-DD) or press Enter for today: 2025-10-08
Enter start time (HH:MM) or press Enter for now: 14:30
Enter work description: Fixed database performance issues
```

## 🎯 **Typical Workflow**

### **Scenario 1: Weekly Time Entry**
1. Find your tickets: Project=`ARTS`, Assignee=`me`
2. Review incomplete tickets
3. Batch update with actual work done
4. Set estimates for new tickets

### **Scenario 2: Release Cleanup**
1. Find release tickets: Project=`ARTS`, Release=`v2.1.0`
2. Identify tickets missing estimates
3. Batch update all time tracking data
4. Ensure accurate project metrics

### **Scenario 3: Team Review**
1. Find team member's tickets: Assignee=`teammate`
2. Review time tracking completeness
3. Guide through batch updates
4. Ensure consistent time reporting

## 💡 **Pro Tips**

### **Time Format Flexibility**
- `2h 30m` → 2 hours 30 minutes
- `90m` → 90 minutes (1.5 hours)
- `1.5h` → 1.5 hours
- `4h` → 4 hours exactly

### **Date/Time Handling**
- Leave blank for current date/time
- Use `YYYY-MM-DD` format for dates
- Use `HH:MM` format for times (24-hour)
- System handles timezone conversion automatically

### **Batch Processing Controls**
- **Skip (4)**: Skip current ticket, move to next
- **Stop (0)**: Stop processing, save progress
- **Ctrl+C**: Emergency stop (progress saved)

### **Efficient Workflows**
1. **Daily Updates**: Use `assignee=me` to find your tickets
2. **Sprint Planning**: Use release filters to estimate sprints
3. **Time Audits**: Find tickets with missing data
4. **Project Reports**: Ensure all tickets have complete time data

## 📊 **Results Summary**

After batch processing, you'll see:
```
📊 Batch Update Summary:
✅ Updated: 8 tickets
⏭️ Skipped: 2 tickets  
📋 Total: 10 tickets
```

## 🚨 **Error Handling**

The system handles:
- **Permission Errors**: Some fields may not be editable
- **Network Issues**: Retries and graceful failures
- **Invalid Input**: Format validation and correction prompts
- **Interrupted Processing**: Save progress before stopping

## 🎯 **Ready to Use!**

Your enhanced Jira Manager now provides enterprise-level batch processing capabilities for efficient time tracking management!

```bash
cd /home/arun/Dev/jora
./run.sh
# Choose option 7 to find incomplete tickets
# Choose option 8 to batch update them
```