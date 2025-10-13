# 📝 AI Notes

An AI-powered note-taking and task management application that automatically extracts action items from your notes, assigns priorities, tracks progress, and sends notifications.

![ActionNote](https://img.shields.io/badge/status-MVP-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Quick Start

```bash
cd actionnote
./run.sh          # Linux/macOS
# OR
run.bat           # Windows
```

Then open: **http://localhost:5000**

## 📚 Documentation

- **[Quick Start Guide](actionnote/QUICK_START.md)** - Get started in 5 minutes
- **[Project Summary](actionnote/PROJECT_SUMMARY.md)** - Complete technical overview
- **[Change Log](CHANGE_LOG.md)** - Version history and features

## 📂 Project Location

All application files are in the **`actionnote/`** directory.

---

## 🎯 Features

### User Authentication & Profile Management
- **🔐 User Registration**: Create secure accounts with email and password
- **🔑 User Login**: Secure authentication with session management
- **👤 User Profiles**: Personal profile page with account information
- **🔒 Password Management**: Change password securely from profile
- **📁 Separate User Data**: Each user has their own isolated notes and tasks

### Core Functionality
- **📝 Smart Note Taking**: Write notes in natural language
- **📋 Notes Management**: Dedicated notes page with table view, sorted by most recent
- **✏️ Edit & Delete**: Inline editing and deletion of notes with keyboard shortcuts
- **🤖 AI Task Extraction**: Automatically extract actionable tasks using OpenAI GPT
- **🎯 Priority Management**: AI-suggested priority levels (High, Medium, Low)
- **📊 Task Dashboard**: Visual dashboard with task statistics and color-coded priorities
- **✅ Progress Tracking**: Track task status (Pending, In Progress, Done)

### Notifications & Reminders
- **🔔 Desktop Notifications**: Get notified about approaching deadlines and stale tasks
- **📧 Email Reminders**: Automatic email reminders for tasks with no progress after 72 hours
- **⏰ Smart Scheduling**: Background scheduler checks tasks every 30 minutes

### Automation
- **🗄️ Auto-Archive**: Completed tasks older than 7 days are automatically archived
- **⚡ Task Expiration**: Automatic cleanup of expired tasks
- **🔄 Progress Monitoring**: Detect stale tasks and send reminders

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (optional, has fallback)
- Gmail account for email reminders (optional)

### Installation

1. **Clone or download the repository**
```bash
cd actionnote
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
# GMAIL_ADDRESS=your_email@gmail.com
# GMAIL_PASSWORD=your_app_password
# NOTIFICATION_EMAIL=your_email@gmail.com
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser and register**
```
http://localhost:5000
```
- On first visit, you'll be redirected to the login page
- Click "Sign up" to create a new account
- Enter your details (full name, username, email, password)
- After registration, log in with your credentials
- Each user has their own private notes and tasks

## 📁 Project Structure

```
actionnote/
├── app.py                 # Flask main application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
│
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── profile.html     # User profile page
│   ├── dashboard.html   # Task dashboard
│   ├── add_note.html    # Add note page
│   ├── notes.html       # Notes management page
│   └── settings.html    # Settings page
│
├── static/              # Static files
│   ├── style.css       # CSS styling
│   └── script.js       # JavaScript
│
├── data/               # JSON storage
│   ├── users.json     # User accounts (hashed passwords)
│   └── users/         # User-specific data directories
│       └── user_XXX/  # Each user's notes and archive
│
└── modules/            # Python modules
    ├── __init__.py
    ├── user_manager.py      # User authentication & profiles
    ├── note_handler.py      # Note/task management
    ├── task_extractor.py    # AI task extraction
    ├── notifier.py          # Desktop notifications
    ├── emailer.py           # Email reminders
    └── scheduler.py         # Background jobs
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI task extraction | No (has fallback) |
| `GMAIL_ADDRESS` | Gmail address for sending emails | No |
| `GMAIL_PASSWORD` | Gmail App Password | No |
| `NOTIFICATION_EMAIL` | Email to receive reminders | No |
| `SCHEDULER_ENABLED` | Enable background scheduler (true/false) | No (default: true) |

### Getting API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Add to `.env` file: `OPENAI_API_KEY=sk-...`

#### Gmail App Password
1. Enable 2-Factor Authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Create a new app password
4. Add to `.env` file: `GMAIL_PASSWORD=your_app_password`

## 💡 Usage

### First Time Setup

1. **Register an Account**
   - Visit http://localhost:5000
   - Click "Sign up"
   - Fill in your full name, username, email, and password (min 6 characters)
   - Submit the registration form

2. **Log In**
   - Enter your username and password
   - You'll be redirected to your personal dashboard

3. **Profile Management**
   - Click on your username in the navigation to access your profile
   - Update your profile information
   - Change your password securely
   - View your account creation date and last login

### Adding Notes

1. Click **"Add Note"** in the navigation
2. Write your note in natural language
3. Click **"Extract Tasks & Save"**
4. AI will automatically extract actionable tasks with priorities

**Example Note:**
```
Follow up with Raj by Monday about the project proposal. 
Need to send him the updated timeline and budget estimates.
Also schedule a team meeting for next week to discuss Q4 goals.
```

**Extracted Tasks:**
- ✅ Follow up with Raj (High Priority, Deadline: Monday)
- ✅ Send updated timeline and budget (Medium Priority)
- ✅ Schedule team meeting (Medium Priority, Deadline: Next week)

### Managing Tasks

- **View Dashboard**: See all tasks with color-coded priorities
- **Update Status**: Change task status directly from the dashboard
- **Track Progress**: Monitor deadlines and completion rates
- **Get Notifications**: Receive desktop and email alerts

## 🎨 Features Deep Dive

### AI Task Extraction

The app uses OpenAI GPT-3.5 to analyze your notes and extract:
- **Task Title**: Clear, actionable task description
- **Priority Level**: High, Medium, or Low based on urgency
- **Deadline**: Estimated deadline from context
- **Color Coding**: Red (High), Orange (Medium), Green (Low)

If OpenAI API is not configured, it falls back to rule-based extraction using action keywords.

### Notification System

#### Desktop Notifications
- Approaching deadlines (24 hours before)
- Overdue tasks
- Stale tasks (no update for 48 hours)

#### Email Reminders
- Sent for tasks with no progress after 72 hours
- Includes task details and original note context
- Beautiful HTML email templates

### Background Scheduler

Runs every 30 minutes to:
- Check task deadlines
- Send notifications
- Auto-archive completed tasks (>7 days old)
- Monitor task progress

## 🔧 Troubleshooting

### App won't start
- Check Python version: `python --version` (need 3.8+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check for port conflicts: Change port in `app.py` if 5000 is in use

### AI not extracting tasks
- Verify `OPENAI_API_KEY` is set correctly
- Check OpenAI API credits/usage limits
- App will use fallback extraction if API fails

### Notifications not working
- Desktop: Check `plyer` is installed: `pip install plyer`
- Email: Verify Gmail credentials and App Password
- Check system notification settings

### Tasks not saving
- Ensure `data/` directory exists
- Check file permissions
- View console for error messages

## 🔐 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Session Management**: Secure Flask-Login session handling
- **User Isolation**: Each user's data is stored in separate directories
- **Protected Routes**: All application routes require authentication
- **Secure Password Changes**: Old password verification required

## 🛣️ Roadmap

### Recently Added ✅
- [x] User authentication system
- [x] User registration and login
- [x] Personal user profiles
- [x] Separate data storage per user
- [x] Password management

### Planned Features
- [ ] Password reset via email
- [ ] Remember me option
- [ ] Social login (Google, GitHub)
- [ ] Dark mode theme
- [ ] Mobile responsive design improvements
- [ ] Calendar integration
- [ ] Task categories/tags
- [ ] Recurring tasks
- [ ] Team collaboration features
- [ ] Export to PDF/CSV
- [ ] Task templates
- [ ] Voice note input
- [ ] Advanced analytics

## 🤝 Contributing

Contributions are welcome! This is an MVP, so there's plenty of room for improvement.

### How to Contribute
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the GPT API
- **Flask** for the web framework
- **Plyer** for cross-platform notifications
- All contributors and testers

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/pandiyarajk/mindtrack/issues)
- **Email**: pandiyarajk@live.com
- **Documentation**: [Wiki](https://github.com/pandiyarajk/mindtrack/wiki)
For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section


## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Python Best Practices](https://docs.python.org/3/)

---

**Built with ❤️ using Python + Flask + OpenAI**

*ActionNote MVP - Transform your notes into actionable tasks with AI*
