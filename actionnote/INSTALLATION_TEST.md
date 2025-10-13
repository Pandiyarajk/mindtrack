# 🧪 ActionNote MVP - Installation & Testing Guide

This guide helps you verify that ActionNote is properly installed and working.

## Pre-Installation Checklist

### System Requirements
- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] 50MB free disk space
- [ ] Internet connection (for OpenAI API, optional)

### Check Python Installation
```bash
python3 --version
# Should show: Python 3.8.x or higher

pip3 --version
# Should show: pip 20.x or higher
```

## Installation Test

### Step 1: Navigate to Project
```bash
cd actionnote
pwd
# Should show: .../actionnote
```

### Step 2: Verify File Structure
```bash
ls -la
# Should see:
# - app.py
# - requirements.txt
# - modules/
# - templates/
# - static/
# - data/
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
ls venv/
# Should see: bin/ lib/ include/ pyvenv.cfg
```

### Step 4: Activate Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
# Prompt should change to show (venv)
```

**On Windows:**
```cmd
venv\Scripts\activate.bat
# Prompt should change to show (venv)
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
# Should install: Flask, openai, plyer, python-dotenv
```

**Verify Installation:**
```bash
pip list | grep -E "Flask|openai|plyer|python-dotenv"
# Should show all 4 packages installed
```

### Step 6: Syntax Check
```bash
python3 -m py_compile app.py
python3 -m py_compile modules/*.py
# No output = success!
```

### Step 7: Test Import
```bash
python3 -c "from modules.note_handler import NoteHandler; print('✓ Imports work!')"
# Should print: ✓ Imports work!
```

## Functional Testing

### Test 1: Start Application (Basic)
```bash
# In one terminal:
python3 app.py
```

**Expected Output:**
```
==================================================
ActionNote MVP - Starting...
==================================================
OpenAI API: ✗ Disabled (using fallback)
Email: ✗ Disabled
Desktop Notifications: ✓ Enabled
Scheduler: ✓ Running
==================================================

Access the app at: http://localhost:5000

Press Ctrl+C to stop
```

### Test 2: Check Web Interface
Open browser: `http://localhost:5000`

**Expected:**
- ✅ Page loads without errors
- ✅ Navigation bar visible
- ✅ "ActionNote" title present
- ✅ Three menu items: Dashboard, Add Note, Settings

### Test 3: Dashboard Page
Navigate to: `http://localhost:5000/dashboard`

**Expected:**
- ✅ Statistics cards showing (Total, Pending, In Progress, Done)
- ✅ All counters showing 0 (if first time)
- ✅ Empty state message: "No tasks yet!"
- ✅ "Add Note" button visible

### Test 4: Add Note Page
Navigate to: `http://localhost:5000/add_note`

**Expected:**
- ✅ Large text area for note input
- ✅ Placeholder text visible
- ✅ "Extract Tasks & Save" button
- ✅ Can type in text area

### Test 5: Create Test Note
1. Go to Add Note page
2. Enter text: `Call John tomorrow about the meeting`
3. Click "Extract Tasks & Save"

**Expected:**
- ✅ Success message appears
- ✅ "1 task(s) extracted and saved!"
- ✅ Can view dashboard link

### Test 6: Verify Task Creation
1. Click "View Dashboard"
2. Check task list

**Expected:**
- ✅ One task card visible
- ✅ Task title: "Call John tomorrow about the meeting"
- ✅ Priority badge visible (color-coded)
- ✅ Status dropdown showing "Pending"
- ✅ Deadline displayed

### Test 7: Update Task Status
1. On dashboard, find task
2. Change status dropdown from "Pending" to "In Progress"

**Expected:**
- ✅ Toast notification: "Task status updated to In Progress"
- ✅ Page reloads
- ✅ Task now shows "In Progress" badge
- ✅ Statistics updated (1 in progress)

### Test 8: Settings Page
Navigate to: `http://localhost:5000/settings`

**Expected:**
- ✅ System status cards visible
- ✅ Configuration guide present
- ✅ Quick action buttons work
- ✅ No console errors

### Test 9: API Endpoints
```bash
# Test GET notes
curl http://localhost:5000/api/notes
# Should return JSON with notes

# Test GET tasks
curl http://localhost:5000/api/tasks
# Should return JSON with tasks

# Test GET config
curl http://localhost:5000/api/config
# Should return configuration status
```

### Test 10: Data Persistence
1. Stop server (Ctrl+C)
2. Check data files:
```bash
cat data/notes.json
# Should show your created note and task
```
3. Restart server
4. Visit dashboard - task should still be there

## Optional: With OpenAI API

### Setup
1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. Create `.env` file:
```bash
cp .env.example .env
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
```
3. Restart server

### Test AI Extraction
1. Add note: `Schedule team meeting next Friday at 2pm. Need to send agenda to everyone by Wednesday.`
2. Click "Extract Tasks & Save"

**Expected:**
- ✅ Multiple tasks extracted (2-3 tasks)
- ✅ Priorities assigned intelligently
- ✅ Deadlines extracted from text
- ✅ Success message shows correct count

## Performance Testing

### Test 1: Response Time
```bash
# Test page load time
time curl -s http://localhost:5000/dashboard > /dev/null
# Should be < 1 second
```

### Test 2: Multiple Tasks
1. Create 10 test notes
2. Check dashboard loads quickly
3. All tasks visible and functional

### Test 3: Large Note
1. Create note with 1000+ characters
2. Should save successfully
3. Dashboard displays truncated version

## Error Handling Testing

### Test 1: Invalid API Endpoint
```bash
curl http://localhost:5000/api/invalid
# Should return 404 error (handled by Flask)
```

### Test 2: Empty Note
1. Try to save empty note
2. Should show error: "Note text is required"

### Test 3: Invalid Task ID
```bash
curl -X PUT http://localhost:5000/api/tasks/invalid123 \
  -H "Content-Type: application/json" \
  -d '{"status":"Done"}'
# Should return: {"error": "Task not found"}
```

## Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (macOS)
- [ ] Edge (Windows)

**All should work identically**

## Mobile Responsive Testing

1. Open in mobile browser or DevTools mobile view
2. Check responsive layout:
   - [ ] Navigation stacks vertically
   - [ ] Cards stack in single column
   - [ ] Buttons full-width
   - [ ] Text readable
   - [ ] No horizontal scroll

## Common Issues & Solutions

### Issue: Port 5000 already in use
**Solution:**
```python
# Edit app.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Module not found errors
**Solution:**
```bash
# Make sure venv is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Can't save notes (Permission denied)
**Solution:**
```bash
chmod -R 755 data/
```

### Issue: OpenAI API not working
**Solution:**
1. Check API key in `.env`
2. Verify API credits at OpenAI dashboard
3. App will use fallback if API fails

## Success Criteria

Your installation is successful if:

- ✅ Server starts without errors
- ✅ All pages load correctly
- ✅ Can create notes
- ✅ Tasks are extracted (with or without AI)
- ✅ Dashboard displays tasks
- ✅ Can update task status
- ✅ Data persists after restart
- ✅ No console errors
- ✅ Responsive on mobile

## Performance Benchmarks

Expected performance (localhost):
- **Server startup**: < 2 seconds
- **Page load**: < 500ms
- **Note creation**: < 1 second (without AI)
- **Note creation**: 2-5 seconds (with AI)
- **Status update**: < 200ms
- **Dashboard render**: < 1 second (100 tasks)

## Security Checklist

- [ ] `.env` file not committed to git
- [ ] API keys not visible in source code
- [ ] HTTPS used in production
- [ ] Input validation working
- [ ] No SQL injection possible (using JSON)
- [ ] Session security configured

## Next Steps After Testing

If all tests pass:
1. ✅ **Production Ready** - Configure for deployment
2. ✅ **Add API Keys** - Enable full features
3. ✅ **Customize** - Adjust settings to your needs
4. ✅ **Use Daily** - Start managing your tasks!

If tests fail:
1. ❌ Review error messages
2. ❌ Check troubleshooting section
3. ❌ Verify system requirements
4. ❌ Open issue if bug found

## Test Log Template

Use this to track your testing:

```
Date: __________
Tester: __________

Installation Tests:
[ ] Python version check
[ ] Virtual environment created
[ ] Dependencies installed
[ ] Syntax check passed
[ ] Imports work

Functional Tests:
[ ] Server starts
[ ] Web interface loads
[ ] Dashboard works
[ ] Add note works
[ ] Task creation works
[ ] Status update works
[ ] Settings page works

API Tests:
[ ] GET /api/notes
[ ] GET /api/tasks
[ ] POST /api/notes
[ ] PUT /api/tasks/<id>

Performance:
[ ] Page loads < 500ms
[ ] No memory leaks
[ ] Handles 100+ tasks

Browser Tests:
[ ] Chrome
[ ] Firefox
[ ] Safari/Edge

Mobile:
[ ] Responsive layout
[ ] Touch interactions

Notes:
_________________________________
_________________________________

Result: PASS / FAIL
```

---

**Happy Testing! 🧪✅**

*If all tests pass, congratulations - ActionNote is ready to use!*
