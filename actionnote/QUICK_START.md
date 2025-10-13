# 🚀 ActionNote - Quick Start Guide

Get ActionNote up and running in 5 minutes!

## Option 1: Automated Setup (Recommended)

### On macOS/Linux:
```bash
cd actionnote
./run.sh
```

### On Windows:
```batch
cd actionnote
run.bat
```

The script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` file from template
- ✅ Start the Flask server

## Option 2: Manual Setup

### Step 1: Install Dependencies
```bash
cd actionnote
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

**Add your API keys** (all optional):
```
OPENAI_API_KEY=sk-your-key-here
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=your-email@gmail.com
```

### Step 3: Run
```bash
python app.py
```

### Step 4: Open Browser
```
http://localhost:5000
```

## 🎯 First Steps

1. **Add Your First Note**
   - Click "Add Note" in the navigation
   - Write something like: "Call John tomorrow about the project proposal"
   - Click "Extract Tasks & Save"
   - Watch AI extract the task automatically!

2. **View Dashboard**
   - See all your tasks organized by priority
   - Update task status with dropdown
   - View statistics at a glance

3. **Configure Settings**
   - Go to Settings page
   - Check system status
   - Configure notifications

## ⚙️ Configuration Tips

### Minimal Setup (No API Keys)
The app works without any API keys! It will:
- Use rule-based task extraction (looks for action words)
- Skip email notifications
- Show console notifications instead of desktop alerts

Perfect for testing and light usage!

### Full Setup (With API Keys)
For the complete experience:

1. **Get OpenAI API Key** (for smart AI extraction)
   - Visit: https://platform.openai.com/api-keys
   - Create new key
   - Add to `.env`: `OPENAI_API_KEY=sk-...`

2. **Setup Gmail** (for email reminders)
   - Enable 2FA on your Google account
   - Visit: https://myaccount.google.com/apppasswords
   - Create app password
   - Add to `.env`:
     ```
     GMAIL_ADDRESS=you@gmail.com
     GMAIL_PASSWORD=your-16-char-password
     NOTIFICATION_EMAIL=you@gmail.com
     ```

## 🔧 Troubleshooting

### Port 5000 Already in Use?
Edit `app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Import Errors?
Make sure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Can't Save Notes?
Check that `data/` directory has write permissions:
```bash
chmod -R 755 data/
```

## 📱 Usage Examples

### Example 1: Meeting Notes
**Input:**
```
Team meeting tomorrow at 2 PM. Need to prepare Q4 report and 
send budget proposal to Sarah by Friday. Also follow up with 
marketing about the new campaign.
```

**AI Extracts:**
- ✅ Prepare Q4 report (High Priority)
- ✅ Send budget proposal to Sarah (High Priority, Friday deadline)
- ✅ Follow up with marketing about campaign (Medium Priority)

### Example 2: Personal Tasks
**Input:**
```
Buy groceries this weekend. Call dentist to schedule appointment.
Finish reading the new book when I have time.
```

**AI Extracts:**
- ✅ Buy groceries (Medium Priority, Weekend)
- ✅ Call dentist (Medium Priority)
- ✅ Finish reading book (Low Priority)

## 🎨 Keyboard Shortcuts

- `Ctrl/Cmd + N` - Add new note
- `Ctrl/Cmd + D` - Go to dashboard

## 💡 Pro Tips

1. **Be Specific**: Include deadlines and names for better task extraction
2. **Use Action Verbs**: "Call", "Send", "Prepare", "Schedule", etc.
3. **Check Dashboard Regularly**: Update task status to avoid stale task alerts
4. **Archive Completed**: Completed tasks auto-archive after 7 days
5. **Export Data**: Use Settings → Export Data to backup your notes

## 🆘 Need Help?

- Check the main [README.md](README.md) for full documentation
- Review [CHANGE_LOG.md](CHANGE_LOG.md) for features and updates
- Open an issue if something's broken

## 🎉 You're Ready!

That's it! Start taking notes and let AI handle your task management.

Happy note-taking! 📝✨
