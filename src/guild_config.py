import json
import os

GUILDS_FILE = "guilds.json"

def _read_all() -> dict:
    if not os.path.exists(GUILDS_FILE):
        with open(GUILDS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(GUILDS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _write_all(data: dict):
    with open(GUILDS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_guild_config(guild_id: str) -> dict:
    data = _read_all()
    if guild_id not in data:
        data[guild_id] = {
            "gen-channels": [],
            "premium-gen-channels": [],
            "admin-roles": [],
            "suggestions-channel-id": None,
            "ticket-category": None,
            "ticket-staff-role": None,
            "ticket-transcript-channel": None,
            "roles": [],
            "review-channel": None,
            "invite-code": None,
            "review-channel-id": None
        }
        _write_all(data)
    return data[guild_id]

def save_guild_config(guild_id: str, cfg: dict):
    data = _read_all()
    data[guild_id] = cfg
    _write_all(data)

def get_guild_field(guild_id: str, field: str, default=None):
    cfg = load_guild_config(guild_id)
    return cfg.get(field, default)
