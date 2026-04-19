# Glorious Dashboard

A web-based management interface for the Glorious Discord bot, featuring neon green theming (#39FF14) and Discord OAuth2 authentication.

## Features

- **Discord OAuth2 Authentication** - Secure login with Discord accounts
- **Server Management** - View and manage all servers where you have permissions
- **Stock Management** - Add, view, and delete account stock
- **User Management** - Monitor user activity and manage blacklist status
- **Settings** - Configure guild-specific settings (channels, roles)
- **Neon Green Theme** - Sleek, dark interface with toxic neon green accents

## Project Structure

```
dashboard/
├── app.py                 # Flask application entry point
├── config.py             # Configuration loader
├── .env                  # Discord OAuth2 credentials (not in git)
├── .gitignore           # Git ignore rules
├── routes/
│   ├── auth.py          # Discord OAuth2 authentication
│   ├── dashboard.py     # Dashboard pages (servers, overview, stock, users, settings)
│   └── api.py           # JSON API endpoints
├── templates/
│   ├── base.html        # Base template with layout
│   ├── login.html       # Login page
│   ├── servers.html     # Server list
│   ├── dashboard.html   # Guild overview
│   ├── stock.html       # Stock management
│   ├── users.html       # User management
│   └── settings.html    # Guild settings
├── static/
│   ├── css/
│   │   └── style.css    # Neon green theme styling
│   └── js/
│       └── main.js      # API interactions and form handling
└── flask_session/       # Session storage (auto-created)
```

## Setup Instructions

### Prerequisites

- Python 3.7+
- Discord Bot with OAuth2 credentials
- sqlite3 (usually included with Python)

### Installation

1. **Navigate to dashboard directory:**
   ```bash
   cd dashboard
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Create and configure .env file:**
   ```bash
   cp .env.example .env  # If available, or create manually
   ```
   
   Edit `.env` and add your Discord OAuth2 credentials:
   ```
   DISCORD_CLIENT_ID=your_client_id
   DISCORD_CLIENT_SECRET=your_client_secret
   DISCORD_REDIRECT_URI=http://localhost:5000/callback
   ```

4. **Ensure database and config files exist:**
   - The parent directory should have `database.db` (SQLite) and `guilds.json`
   - Both files are shared with the main bot

### Running the Dashboard

```bash
python app.py
```

The dashboard will start at `http://localhost:5000`

## Configuration

### Environment Variables (.env)

- **DISCORD_CLIENT_ID** - OAuth2 Client ID from Discord Developer Portal
- **DISCORD_CLIENT_SECRET** - OAuth2 Client Secret (keep secret!)
- **DISCORD_REDIRECT_URI** - Callback URL (default: http://localhost:5000/callback)

### Parent Directory Files

The dashboard reads from:
- `../config.json` - Bot configuration (colors, settings)
- `../database.db` - SQLite database with user/account data
- `../guilds.json` - Per-guild configuration

## Pages & Features

### Login Page
- Discord OAuth2 authentication
- Automatic user and guild data fetch

### Servers Page
- View all managed servers (where you have Manage Server or Admin permission)
- Server icons and names
- "Manage" button to access guild dashboard
- "Invite Bot" button if bot not in server

### Dashboard (Guild Overview)
- **Total Stock** - Count of all accounts
- **Total Users** - Count of users
- **Total Services** - Count of unique services
- **Recent Users** - Table of top 5 users by gen count

### Stock Page
- Table of all services with stock counts
- Delete buttons to remove all accounts for a service
- Real-time updates via API

### Users Page
- Table of all users with gen counts
- Blacklist status badges
- Toggle blacklist status buttons

### Settings Page
- Configure gen channels (free & premium)
- Set admin roles
- Set suggestions and review channels
- Save settings to guild config

## API Endpoints

All API endpoints require authentication (Discord OAuth2 session).

### Stock Management
- `POST /api/guild/<guild_id>/stock/delete` - Delete all stock for a service
  ```json
  {"service_name": "Netflix"}
  ```

### User Management
- `POST /api/guild/<guild_id>/users/blacklist` - Toggle user blacklist status
  ```json
  {"user_id": "123456789", "blacklisted": true}
  ```

### Settings Management
- `POST /api/guild/<guild_id>/settings` - Update guild settings
  ```json
  {
    "gen-channels": ["channel_id_1", "channel_id_2"],
    "premium-gen-channels": ["channel_id_3"],
    "admin-roles": ["role_id_1"],
    "suggestions-channel-id": "channel_id",
    "review-channel-id": "channel_id"
  }
  ```

## Design Theme

**Colors:**
- Primary: `#39FF14` (Toxic Neon Green)
- Background: `#0d0d0d` (Pure Black)
- Card Background: `#111111` (Dark Gray)
- Text Primary: `#FFFFFF` (White)
- Text Secondary: `#B0B0B0` (Light Gray)

**Effects:**
- Neon glow: `box-shadow: 0 0 20px rgba(57, 255, 20, 0.3)`
- Hover animations with lift effect
- Smooth color transitions

**Font:** Segoe UI, Inter, or system UI font

## Security Notes

- **Never commit .env file** - Contains Discord credentials
- Uses Discord OAuth2 with secure token exchange
- Permission checks: Only users with Manage Server or Admin role can access guild settings
- All form inputs validated server-side
- CSRF protection via Flask sessions

## Troubleshooting

### "Redirect URI Mismatch" Error
- Ensure DISCORD_REDIRECT_URI in .env matches Discord Developer Portal settings
- Local development: `http://localhost:5000/callback`
- Production: Use your domain, e.g., `https://example.com/callback`

### "Cannot find database" Error
- Ensure `database.db` exists in parent directory
- Check that bot has created the database before running dashboard

### Guilds Not Showing
- User must have Manage Server or Administrator permission
- Check permission integers: 0x20 (Manage Server), 0x8 (Administrator)

### Session Expires
- Flask session stored in `flask_session/` directory
- Sessions persist until browser closes or manual logout

## Development

To run with auto-reload:
```bash
FLASK_ENV=development python app.py
```

To run in production (not recommended for local testing):
```bash
python -m gunicorn app:app
```

## Future Enhancements

- [ ] User invitations/referrals tracking
- [ ] Advanced analytics and charts
- [ ] Audit logs for admin actions
- [ ] CSV export for stock/user data
- [ ] Webhook logs for bot events
- [ ] Mobile app support

## Support

For issues or questions, contact the development team or check the main Glorious bot documentation.
