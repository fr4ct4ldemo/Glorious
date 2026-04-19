# Glorious Dashboard - Quick Setup Guide

## Complete Dashboard Build ✅

All dashboard components have been successfully created with:
- Flask backend with OAuth2 authentication
- 5 management pages (Servers, Overview, Stock, Users, Settings)
- JSON API endpoints for CRUD operations
- Neon green theme (#39FF14 toxic green + #0d0d0d black)
- Responsive mobile-friendly design
- Permission-based access control

## Files Created

### Backend (Python/Flask)
- ✅ `app.py` - Flask application with blueprint registration
- ✅ `config.py` - Configuration loader and Discord API setup
- ✅ `.env` - Environment variables template
- ✅ `routes/auth.py` - Discord OAuth2 authentication (85 lines)
- ✅ `routes/dashboard.py` - 5 page route handlers (110+ lines)
- ✅ `routes/api.py` - 3 JSON API endpoints (75+ lines)

### Frontend (HTML/CSS/JavaScript)
- ✅ `templates/base.html` - Base layout with sidebar navigation
- ✅ `templates/login.html` - Discord OAuth2 login page
- ✅ `templates/servers.html` - Grid of managed servers with Manage/Invite buttons
- ✅ `templates/dashboard.html` - Guild overview with 3 stat cards + recent users
- ✅ `templates/stock.html` - Service table with delete buttons
- ✅ `templates/users.html` - User table with blacklist toggle
- ✅ `templates/settings.html` - Forms for guild configuration
- ✅ `static/css/style.css` - Complete neon green theme (600+ lines)
- ✅ `static/js/main.js` - API interactions and form handling (200+ lines)

### Configuration & Documentation
- ✅ `.gitignore` - Prevents .env credentials from git commits
- ✅ `README.md` - Complete setup and feature documentation

## Quick Start (5 Minutes)

### 1. Add Discord OAuth2 Credentials
Edit `dashboard/.env`:
```
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:5000/callback
```

Get these from: https://discord.com/developers/applications

### 2. Install Dependencies
```bash
cd dashboard
pip install -r ../requirements.txt
```

The following packages will be installed:
- flask 3.0.0
- flask-session 0.6.0
- requests 2.31.0
- python-dotenv 1.0.0
- All existing bot dependencies

### 3. Run Dashboard
```bash
python app.py
```

Open http://localhost:5000 in your browser
Click "Login with Discord" button

### 4. Access Features
After login, you'll see:
- All servers where you have Manage Server or Admin permission
- Click "Manage" to access guild dashboard
- 5 tabs: Overview, Stock, Users, Settings

## Database & Configuration

The dashboard shares these files with the bot:
- `../database.db` - SQLite database
  - Tables: users (user_id, is_blacklisted, subscription_time_left)
  - Tables: accounts (guild_id, service_name, account_data)
- `../guilds.json` - Per-guild configuration (channels, roles)
- `../config.json` - Bot settings (colors, token, etc.)

## Design Features

### Color Scheme
- **Primary**: #39FF14 (Toxic neon green with glow)
- **Background**: #0d0d0d (Pure black)
- **Card Background**: #111111 (Dark gray)
- **Text**: #FFFFFF (White) / #B0B0B0 (Light gray)
- **Glow Effect**: `box-shadow: 0 0 20px rgba(57, 255, 20, 0.3)`

### Responsive
- Desktop: 3-column layout with sidebar
- Tablet (768px): Single column navigation
- Mobile (480px): Stacked layout, full-width buttons

### Interactive Features
- Real-time form validation
- API success/error notifications
- Confirmation dialogs for destructive actions
- Loading states on buttons during API calls
- Animated transitions and hover effects

## Security & Permissions

- **Authentication**: Discord OAuth2 with secure token exchange
- **Authorization**: Only users with:
  - Manage Server permission (0x20), OR
  - Administrator permission (0x8)
- **Session**: Filesystem-based, cleared on logout
- **Database**: Direct SQLite3 access, parameterized queries

## API Endpoints

All require Discord OAuth2 session authentication:

### Stock Management
```
DELETE /api/guild/<guild_id>/stock/delete
Body: {"service_name": "Netflix"}
Response: {"success": true}
```

### User Management
```
POST /api/guild/<guild_id>/users/blacklist
Body: {"user_id": "123456789", "blacklisted": true}
Response: {"success": true}
```

### Settings
```
POST /api/guild/<guild_id>/settings
Body: {
  "gen-channels": ["id1", "id2"],
  "premium-gen-channels": ["id3"],
  "admin-roles": ["id4"],
  "suggestions-channel-id": "id5",
  "review-channel-id": "id6"
}
Response: {"success": true}
```

## JavaScript Features

- Automatic active nav link highlighting
- Form submission without page reload
- Loading states during API calls
- Success/error notifications with auto-dismiss
- Smooth animations for additions/removals
- Confirmation dialogs for data deletion

## Testing Checklist

- [ ] Dashboard starts on localhost:5000
- [ ] Login redirects to Discord OAuth2 consent screen
- [ ] After login, redirects to servers list
- [ ] Servers page shows guilds with icons and names
- [ ] Manage buttons navigate to guild dashboard
- [ ] Overview page shows stats and recent users
- [ ] Stock page lists services with delete buttons
- [ ] Delete stock shows confirmation and removes row
- [ ] Users page shows blacklist status badges
- [ ] Blacklist toggle updates badge and text
- [ ] Settings form submits and saves config
- [ ] Logout clears session and redirects to login
- [ ] Mobile view is responsive and functional

## Troubleshooting

**Port 5000 already in use:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Missing database error:**
- Ensure `database.db` exists in parent directory
- Run bot once to initialize database

**OAuth2 error:**
- Check .env file has correct CLIENT_ID and SECRET
- Verify redirect URI in Discord Dev Portal matches DISCORD_REDIRECT_URI

**CSS/JS not loading:**
- Verify `static/css/style.css` and `static/js/main.js` exist
- Clear browser cache (Ctrl+Shift+Delete)

## Next Steps

1. ✅ **Add Discord OAuth2 credentials to .env**
2. ✅ **Test dashboard locally**
3. ⏹️ **Deploy to production** (if ready):
   - Use gunicorn/waitress instead of Flask dev server
   - Update DISCORD_REDIRECT_URI to production domain
   - Use environment-based configuration

## Integration with Bot

Dashboard runs independently on port 5000 while bot runs on Discord.
Both share the same database and config files.

**No changes needed to bot** - already compatible with:
- SQLite3 database
- guild-specific JSON config
- Shared folder structure

Run both simultaneously:
```bash
# Terminal 1 - Bot
python glorious.py

# Terminal 2 - Dashboard
cd dashboard && python app.py
```

---

**Status**: ✅ Complete and ready to deploy!
For full documentation, see `README.md`
