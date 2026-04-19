## ##
##
##    (!) YOU DON'T HAVE TO CHANGE ANYTHING IN THIS FILE.
##    (!) DON'T CHANGE THIS FILE IF YOU DON'T KNOW WHAT YOU'RE DOING.
##    (!) EVERYTHING YOU NEED TO CHANGE IS IN THE CONFIG.JSON FILE.
## 
##    THE TUTORIAL ON HOW TO SETUP THIS IS IN THE GITHUB.
##    https://github.com/Atluzka/account-gen-bot
##
## ##

import discord, json, asyncio, os, time
from datetime import datetime
from discord import app_commands
from discord.ui import View, Button

from io import StringIO
from typing import List

from src import database
from src import utils
from src.guild_config import load_guild_config, save_guild_config
from src import stock_files

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
config = json.load(open("config.json"))

EMOJIS = {
    "success": "<:glorious_success:1477834465748324362>",
    "error": "<:glorious_error:1477834514829938839>",
    "warning": "<:glorious_warning:1477834567166726174>",
    "wrench": "<:glorious_wrench:1477834637345554452>",
    "settings": "<:glorious_settings:1477834694472241203>",
    "key": "<:glorious_key:1477834743390273578>",
    "cooldown": "<:glorious_cooldown:1477834799023521913>",
    "delete": "<:glorious_delete:1477834859673288875>",
    "crown": "<:glorious_crown:1477834918363922492>",
    "premium": "<:glorious_premium:1477834960999288932>",
    "gen": "<:glorious_gen:1477835006524264472>",
    "addstock": "<:glorious_addstock:1477835088463925359>",
    "stock": "<:glorious_stock:1477835242931753073>",
    "user": "<:glorious_user:1477835301987684455>",
    "blacklist": "<:glorious_blacklist:1477835342613713039>",
    "setnote": "<:glorious_setnote:1477835386901237966>",
    "suggestions": "<:glorious_suggestions:1477835424222285924>",
    "review": "<:glorious_review:1477835468799348746>",
    "massadd": "<:glorious_massadd:1477958569944023153>",
    "view": "<:glorious_view:1477835544846270535>",
    "vouch": "<:glorious_vouch:1494586436131754085>",
    "shop": "<:glorious_shop:1494586033206067310>",
    "home": "<:glorious_home:1494585722881966196>",
}

NEON_GREEN = 0x39FF14
DARK_THEME = 0x2b2d31

# ============================================
# HELP COMMAND CONFIGURATION
# ============================================
# Replace these URLs to customize your help embed
HELP_BANNER_URL = "https://cdn.discordapp.com/attachments/1436697540853633188/1494433260527288320/X2rc9.jpg?ex=69e296ee&is=69e1456e&hm=d7e4f9a479a63b8d414b8a08ac36c26606842b91be97ada181861378c3ef6408"  # Banner image at top of home embed
HELP_ICON_URL = "https://example.com/icon.png"      # Thumbnail icon on right side
# ============================================

# Help command categories data
HELP_CATEGORIES = {
    "home": {
        "emoji": "🏠",
        "title": "Help Menu",
    },
    "stock": {
        "emoji": "🛒",
        "title": "Stock & Accounts",
        "commands": [
            ("/gen <type>", "Generate an account from stock"),
            ("/stock", "View available stock and quantities"),
            ("/addstock <type> <accounts>", "Add accounts to stock (admin)"),
            ("/removestock <type>", "Remove a stock category (admin)"),
            ("/clearstock <type>", "Clear all accounts in a category (admin)"),
        ]
    },
    "setup": {
        "emoji": "⚙️",
        "title": "Setup & Config",
        "commands": [
            ("/setup", "Configure the bot for your server"),
            ("/setgenchannel", "Set the allowed gen channel"),
            ("/setlogchannel", "Set the log channel"),
            ("/setrole", "Set the required role to use /gen"),
        ]
    },
    "vouches": {
        "emoji": "🎟️",
        "title": "Vouches",
        "commands": [
            ("/vouch <user>", "Vouch for a user"),
            ("/vouches <user>", "View a user's vouch count"),
        ]
    },
    "general": {
        "emoji": "🔧",
        "title": "General",
        "commands": [
            ("/help", "Show this help menu"),
            ("/ping", "Check bot latency"),
            ("/botinfo", "View info about the bot"),
        ]
    },
}


class HelpSelect(discord.ui.Select):
    def __init__(self, selected_category: str = "Home"):
        options = [
            discord.SelectOption(
                label="Home",
                description="Back to the main help overview",
                emoji="<:glorious_home:1494585722881966196>",
                value="home",
            ),
            discord.SelectOption(
                label="Stock & Accounts",
                description="Generate and manage account stock",
                emoji="<:glorious_shop:1494586033206067310>",
                value="stock",
            ),
            discord.SelectOption(
                label="Setup & Config",
                description="Configure the bot for your server",
                emoji="<:glorious_settings:1477834694472241203>",
                value="setup",
            ),
            discord.SelectOption(
                label="Vouches",
                description="Vouch system commands",
                emoji="<:glorious_vouch:1494586436131754085>",
                value="vouches",
            ),
            discord.SelectOption(
                label="General",
                description="General bot commands",
                emoji="<:glorious_wrench:1477834637345554452>",
                value="general",
            ),
        ]
        super().__init__(
            placeholder=selected_category,
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_select",
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        category_data = HELP_CATEGORIES.get(category, HELP_CATEGORIES["home"])

        # Update placeholder to show selected category
        self.placeholder = category_data["title"]

        # Get the user who triggered the interaction for thumbnail
        user = interaction.user

        if category == "home":
            # Home embed with banner
            embed = discord.Embed(
                title="Help Menu",
                description=(
                    "> Use `/` commands to get started\n"
                    "> Join the support server for help\n\n"
                    "Select a category from the menu below to browse all available commands."
                ),
                color=NEON_GREEN,
            )
            embed.set_image(url=HELP_BANNER_URL)
            # Use user's avatar as thumbnail
            if user.display_avatar:
                embed.set_thumbnail(url=user.display_avatar.url)
            else:
                embed.set_thumbnail(url=HELP_ICON_URL)
            embed.set_footer(text="Made By Fr4ct4l — Glorious Bot")
        else:
            # Category embed without banner
            embed = discord.Embed(
                title=f"{category_data['emoji']} {category_data['title']}",
                color=NEON_GREEN,
            )
            for cmd, desc in category_data["commands"]:
                embed.add_field(name=cmd, value=desc, inline=False)
            embed.set_footer(text="Made By Fr4ct4l — Glorious Bot")

        # Update the view with new placeholder
        view = HelpView(selected_category=self.placeholder)
        await interaction.response.edit_message(embed=embed, view=view)


class HelpView(discord.ui.View):
    def __init__(self, selected_category: str = "Home"):
        super().__init__(timeout=None)
        self.add_item(HelpSelect(selected_category=selected_category))


def get_home_embed(user: discord.User = None) -> discord.Embed:
    """Create the initial home embed for the help command."""
    embed = discord.Embed(
        title="Help Menu",
        description=(
            "> Use `/` commands to get started\n"
            "> Join the support server for help\n\n"
            "Select a category from the menu below to browse all available commands."
        ),
        color=NEON_GREEN,
    )
    embed.set_image(url=HELP_BANNER_URL)
    # Use the user's avatar as thumbnail, fallback to icon URL
    if user and user.display_avatar:
        embed.set_thumbnail(url=user.display_avatar.url)
    else:
        embed.set_thumbnail(url=HELP_ICON_URL)
    embed.set_footer(text="Made By Fr4ct4l — Glorious Bot")
    return embed


serviceList = {}
serviceList_2 = {}
is_everything_ready = False

# Track active live stock messages: {message_id: {"channel_id": ..., "guild_id": ..., "task": ...}}
live_stock_messages = {}

def load_guilds():
    try:
        with open('guilds.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_guilds(guilds):
    with open('guilds.json', 'w') as f:
        json.dump(guilds, f, indent=4)

def get_guild_config(guild_id: str):
    guilds = load_guilds()
    if guild_id not in guilds:
        guilds[guild_id] = {
            "gen-channels": [],
            "premium-gen-channels": [],
            "admin-roles": [],
            "suggestions-channel-id": None,
            "ticket-category": None,
            "ticket-staff-role": None,
            "ticket-transcript-channel": None,
            "roles": [],
            "review-channel-id": None
        }
        save_guilds(guilds)
    return guilds[guild_id]

def update_guild_config(guild_id: str, key: str, value):
    guilds = load_guilds()
    if guild_id not in guilds:
        get_guild_config(guild_id)
        guilds = load_guilds()
    guilds[guild_id][key] = value
    save_guilds(guilds)

async def getServiceName(service_name, is_premium=False, get_real_name=False):
    if get_real_name:
        return service_name.split("_")[0]

    if is_premium:
        return f"{service_name}_premium"
    else:
        return f"{service_name}_free"


async def updateServices(guild_id: str, service_to_add=None):
    global serviceList, serviceList_2
    if service_to_add:
        serviceList_temp = await database.getServices(guild_id)
        serviceList[guild_id] = [str(s) for s in serviceList_temp]
        
        if service_to_add not in serviceList[guild_id]:
            serviceList[guild_id].append(service_to_add)

        serviceList_2[guild_id] = []
        for service in serviceList[guild_id]:
            real_name = await getServiceName(service, get_real_name=True)
            if real_name not in serviceList_2[guild_id]:
                serviceList_2[guild_id].append(real_name)

        return serviceList[guild_id]
    else:
        services = await database.getServices(guild_id)
        serviceList[guild_id] = [str(s) for s in services]
        serviceList_2[guild_id] = []
        for service in serviceList[guild_id]:
            real_name = await getServiceName(service, get_real_name=True)
            if real_name not in serviceList_2[guild_id]:
                serviceList_2[guild_id].append(real_name)

async def stage_autcom(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    types = config["subscription-stages"]
    return [
        app_commands.Choice(name=service, value=service)
        for service in types
        if current.lower() in service.lower()
    ]


async def service_autcom(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    guild_id = str(interaction.guild_id)
    types = serviceList_2.get(guild_id, [])
    return [
        app_commands.Choice(name=service, value=service)
        for service in types
        if current.lower() in service.lower()
    ]






















# ----- ping command -----
@tree.command(name="ping", description="Check the bot's latency")
async def ping_command(interaction: discord.Interaction):
    """Show the bot's real roundtrip and websocket latency."""
    start = time.perf_counter()
    await interaction.response.defer(ephemeral=False)
    end = time.perf_counter()
    roundtrip = round((end - start) * 1000)
    ws_latency = round(bot.latency * 1000)

    if roundtrip < 100:
        emoji = EMOJIS["success"]
    elif roundtrip <= 200:
        emoji = EMOJIS["warning"]
    else:
        emoji = EMOJIS["error"]

    embed = discord.Embed(
        title=f"{emoji} Pong!",
        color=NEON_GREEN,
    )
    embed.add_field(name="🏓 Roundtrip", value=f"`{roundtrip}ms`", inline=True)
    embed.add_field(name="🌐 Websocket", value=f"`{ws_latency}ms`", inline=True)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=config["messages"]["footer-msg"])

    await interaction.followup.send(embed=embed)


subscription = app_commands.Group(name="subscription", description="Manage subscriptions")
cooldown = app_commands.Group(name="cooldown", description="Manage cooldowns")
setup = app_commands.Group(name="setup", description="Server configuration commands")


@bot.event
async def on_ready():
    global is_everything_ready

    tree.add_command(subscription)
    tree.add_command(cooldown)
    tree.add_command(setup)

    await tree.sync()
    await database.init_db()
    await updateServices('')

    is_everything_ready = True
    print(f"[+] Logged in as {bot.user}")
    print(f"[+] Serving {len(bot.guilds)} servers")
    print(f"[+] Commands synced globally")


@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"DEBUG: on_guild_join fired for {guild.name} ({guild.id})")

    # Auto create guild config
    get_guild_config(str(guild.id))
    await updateServices(str(guild.id))
    os.makedirs(
        os.path.join(config["stock-storage-path"], str(guild.id)), exist_ok=True
    )

    await asyncio.sleep(2)

    # Find target channel
    target_channel = None

    # Priority 1 - system channel
    if guild.system_channel:
        perms = guild.system_channel.permissions_for(guild.me)
        if perms.send_messages and perms.embed_links:
            target_channel = guild.system_channel
            print(f"DEBUG: Using system channel #{guild.system_channel.name}")

    # Priority 2 - common channel names
    if not target_channel:
        priority_names = [
            'general', 'welcome', 'bot', 
            'commands', 'chat', 'lobby', 
            'main', 'talk', 'lounge'
        ]
        for name in priority_names:
            for channel in guild.text_channels:
                if name in channel.name.lower():
                    perms = channel.permissions_for(guild.me)
                    if perms.send_messages and perms.embed_links:
                        target_channel = channel
                        print(f"DEBUG: Found channel by name #{channel.name}")
                        break
            if target_channel:
                break

    # Priority 3 - first available channel
    if not target_channel:
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.send_messages and perms.embed_links:
                target_channel = channel
                print(f"DEBUG: Using first available channel #{channel.name}")
                break

    if not target_channel:
        print(f"DEBUG: No valid channel found in {guild.name}")
        print(f"DEBUG: Total text channels: {len(guild.text_channels)}")
        for ch in guild.text_channels:
            perms = ch.permissions_for(guild.me)
            print(f"DEBUG: #{ch.name} - send:{perms.send_messages} embed:{perms.embed_links}")
        return

    # Build welcome embed
    welcome_embed = discord.Embed(
        title=f"{EMOJIS['crown']} Glorious has arrived!",
        description=(
            f"Hey **{guild.name}**! Thanks for adding me {EMOJIS['success']}\n\n"
            f"I'm **Glorious** — an account generator bot built to distribute\n"
            f"digital accounts to your members easily and securely.\n\n"
            f"{EMOJIS['key']} **To get started, run the `/help` command.**\n"
            f"It will walk you through everything I can do."
        ),
        color=NEON_GREEN
    )

    welcome_embed.add_field(
        name=f"{EMOJIS['wrench']} Quick Setup",
        value="Before generating, make sure an admin runs `/setup` first\n"
              "to configure roles and channels for this server.",
        inline=False
    )
    welcome_embed.add_field(
        name=f"{EMOJIS['warning']} Note",
        value="Slash commands may take up to **1 hour** to appear after\n"
              "first adding the bot. If they're missing, restart Discord.",
        inline=False
    )

    welcome_embed.set_footer(text=config['messages']['footer-msg'])

    try:
        welcome_embed.set_thumbnail(url=bot.user.display_avatar.url)
    except Exception:
        pass

    try:
        await target_channel.send(embed=welcome_embed)
        print(f"[+] Welcome message sent in {guild.name} -> #{target_channel.name}")
    except discord.Forbidden:
        print(f"[-] Forbidden: No permission in {guild.name} -> #{target_channel.name}")
    except discord.HTTPException as e:
        print(f"[-] HTTPException in {guild.name}: {e}")
    except Exception as e:
        print(f"[-] Unexpected error in {guild.name}: {e}")


async def checkPermission(interaction: discord.Interaction, admin_check: bool = False):
    if not is_everything_ready:
        await interaction.response.send_message("Bot is starting.", ephemeral=True)
        return False

    if admin_check:
        guild_cfg = load_guild_config(str(interaction.guild_id))
        role_ids = [role.id for role in interaction.user.roles]
        has_admin_role = any(role_id in guild_cfg.get("admin-roles", []) for role_id in role_ids)
        is_server_admin = interaction.user.guild_permissions.administrator
        
        if not has_admin_role and not is_server_admin:
            embed_error = discord.Embed(
                title=f"Error: Access Forbidden",
                description=f"You don't have permission to use this command.",
                color=NEON_GREEN,
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
            return False
    return True


def get_user_pfp(user: discord.User):
    try:
        display_url = user.display_avatar
        return display_url
    except:
        return None


async def removeExpiredRoles(
    interaction: discord.Interaction, user: discord.User = None
):
    user = interaction.user if not user else user
    user_roles = [role.id for role in user.roles]
    guild_cfg = load_guild_config(str(interaction.guild_id))
    config_roles = guild_cfg.get("roles", [])

    for _role in config_roles:
        role_id = _role["id"]
        _remove = _role.get("remove-if-expired", False)

        if role_id in user_roles and _remove:
            role: discord.Role = interaction.guild.get_role(int(role_id))
            if isinstance(role, discord.Role):
                await user.remove_roles(role, reason="Subscription has expired.")
    return


# ----- commands -----
@tree.command(
    name="gen", description="Generate an account of your choice | by Fr4ct4l"
)
@app_commands.autocomplete(service=service_autcom)
async def gen(
    interaction: discord.Interaction, service: str, is_premium: bool = False
):
    val = await checkPermission(interaction)
    if not val:
        return

    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)

    if not guild_cfg.get("gen-channels") and not guild_cfg.get("roles"):
        embed = discord.Embed(
            title=f"{EMOJIS['warning']} Server Not Configured",
            description="This server hasn't been set up yet. A server admin must run /setup first.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    _user = await database.addUser(str(interaction.user.id))
    if _user.is_blacklisted:
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Access Forbidden",
            description="You're blacklisted from using this service!",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    role_ids = [role.id for role in interaction.user.roles]
    is_admin = any(
        role_id in guild_cfg.get("admin-roles", []) for role_id in role_ids
    )

    if not is_admin:
        if str(_user.subscription_stage) != str(config["subscription-stages"][0]):
            resp = await database.has_subscription_left(str(interaction.user.id))
            if not resp and is_premium:
                await removeExpiredRoles(interaction)
                embed_error = discord.Embed(
                    title=f"{EMOJIS['error']} Error: No Subscription",
                    description="Your subscription has ran out, if this is a mistake contact an administrator.",
                    color=NEON_GREEN,
                )
                return await interaction.response.send_message(
                    embed=embed_error, ephemeral=True
                )
        else:
            if is_premium:
                await removeExpiredRoles(interaction)
                embed_error = discord.Embed(
                    title=f"{EMOJIS['error']} Error: Access Forbidden",
                    description=f"You don't have permission to use this service, verify your subscription status and try again.",
                    color=NEON_GREEN,
                )
                return await interaction.response.send_message(
                    embed=embed_error, ephemeral=True
                )

    if service not in serviceList_2.get(guild_id, []):
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Invalid service",
            description=f"This service (`{service}`) does not exist, make sure you typed it right.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    if (
        not is_admin
        and interaction.channel_id not in guild_cfg.get("gen-channels", [])
        and interaction.channel_id not in guild_cfg.get("premium-gen-channels", [])
    ):
        channel_list = [f"<#${channel}>" for channel in guild_cfg.get("gen-channels", [])]
        p_channel_list = [
            f"<#${channel}>" for channel in guild_cfg.get("premium-gen-channels", [])
        ]
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Wrong channel",
            description=(
                "You don't have permission to use this command in this channel\n\n"
                f":smile: **Free channels**: {', '.join(channel_list)}.\n"
                f":gem: **Premium channels**: {', '.join(p_channel_list)}."
            ),
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    utl_res = await utils.does_user_meet_requirements(
        interaction.user.roles, guild_cfg.get("roles", []), service
    )
    if not is_admin and not utl_res:
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Access Forbidden",
            description=f"You don't have permission to use this command.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    rndm_stage = "Premium" if is_premium else "Free"

    _user_cldw = None
    has_cldw = await database.does_user_have_cooldown(
        interaction.user.id, rndm_stage
    )
    if not is_admin and not has_cldw:
        _user_cldw = await database.get_role_user_cooldown(
            interaction,
            role_ids,
            is_premium,
            guild_cfg.get("roles", []),
            config["default_cooldown"],
        )
        if _user_cldw is not None:
            await database.set_user_cooldown(
                interaction.user.id, rndm_stage, int(_user_cldw)
            )
    elif has_cldw:
        _data = await database.getCooldownData(
            interaction.user.id, rndm_stage
        )
        if _data["stillHasCooldown"]:
            embd = discord.Embed(
                title=f"{EMOJIS['cooldown']} Cooldown",
                description=f':no_entry_sign: {_data["formatedCooldownMsg"]}',
                color=NEON_GREEN,
            )
            return await interaction.response.send_message(embed=embd, ephemeral=False)
        elif _data["secondsTillEnd"] == 0:
            _user_cldw = await database.get_role_user_cooldown(
                interaction,
                role_ids,
                is_premium,
                guild_cfg.get("roles", []),
                config["default_cooldown"],
            )
            if _user_cldw is not None:
                await database.set_user_cooldown(
                    interaction.user.id, rndm_stage, int(_user_cldw)
                )

    await interaction.response.defer()

    real_service_name = await getServiceName(service, is_premium)

    # try file stock
    account_from_file = False
    account = stock_files.pop_from_stock_file(guild_id, real_service_name)
    if account:
        account_from_file = True
        success = True
    else:
        success, account = await database.getAccount(real_service_name, guild_id)


    if not success:
        if _user_cldw:
            await database.reset_user_cooldown(
                str(interaction.user.id), rndm_stage
            )
        return await interaction.followup.send("There is no stock left.", ephemeral=False)
    else:
        try:
            await _user.update_gen_count(is_premium=is_premium)

            # Server channel embed - NO credentials
            embd = discord.Embed(
                title="<:glorious_success:1477834465748324362> Account Generated",
                description=f"Check your DMS {interaction.user.mention} for your **{real_service_name}** account details!",
                color=NEON_GREEN,
            )
            embd.add_field(
                name="⚠️ NOTICE",
                value="This account is personally owned and provided by the server. Please do not change the password or account details.",
                inline=False
            )
            embd.set_footer(
                text=config["messages"]["footer-msg"],
                icon_url=get_user_pfp(interaction.user),
            )
            embd.set_image(url=config["generate-settings"]["gif-img-url"])
            await interaction.followup.send(embed=embd, ephemeral=False)
        except discord.errors.NotFound:
            return await interaction.followup.send(
                content=f"{interaction.user.mention}, there was an error with your command execution!",
                ephemeral=True,
            )

    # Send account credentials via DM
    try:
        channel = await interaction.user.create_dm()
        
        # DM embed with account credentials AND review button
        dm_embed = discord.Embed(
            title=f"{EMOJIS['key']} Your Account",
            description=f"Here is your generated account for **{real_service_name}**",
            color=NEON_GREEN,
        )
        dm_embed.add_field(
            name="Account Credentials",
            value=f"```\n{account}\n```",
            inline=False
        )
        dm_embed.add_field(
            name="⚠️ Important",
            value="Please do not change the password or account details. This account is personally owned by the server.",
            inline=False
        )
        dm_embed.set_footer(text=config["messages"]["footer-msg"])
        
        # Add review button directly to the account embed
        view = ReviewPromptView(interaction.guild_id)
        await channel.send(embed=dm_embed, view=view)
        
    except discord.errors.Forbidden:
        # DM failed - restore account and send ephemeral message
        if account_from_file:
            stock_files.append_to_stock_file(guild_id, real_service_name, [account])
        else:
            await database.addStock(real_service_name, [account], config["remove-capture-from-stock"], guild_id)
        await database.reset_user_cooldown(str(interaction.user.id), rndm_stage)
        return await interaction.followup.send(
            content=f"{interaction.user.mention}, couldn't send you a DM! Please open your DMs and try again.",
            ephemeral=True,
        )

@tree.command(
    name="addstock", description="(admin only) Add stock to the database | by Fr4ct4l"
)
@app_commands.autocomplete(service=service_autcom)
async def addaccounts(
    interaction: discord.Interaction,
    service: str,
    file: discord.Attachment,
    is_premium: bool = False,
    is_silent: bool = True,
):
    global serviceList

    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    # Confirmation warning before adding stock
    warning_embed = discord.Embed(
        title="⚠️ Read First!",
        description="⚠️ Warning: make sure the accounts you are adding are legitimate and comply with discord's terms of service. adding invalid or unauthorized accounts may result in issues.",
        color=discord.Color.orange(),
    )
    warning_embed.set_footer(text="Click Confirm to proceed or Cancel to abort.")

    confirm_btn = discord.ButtonStyle.success
    cancel_btn = discord.ButtonStyle.danger

    class StockConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.button(label="Confirm", style=confirm_btn)
        async def confirm_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != interaction.user.id:
                return await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
            await button_interaction.response.defer()
            await self.process_stock(button_interaction)

        @discord.ui.button(label="Cancel", style=cancel_btn)
        async def cancel_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user.id != interaction.user.id:
                return await button_interaction.response.send_message("You cannot interact with this button.", ephemeral=True)
            cancel_embed = discord.Embed(
                title="❌ Operation Cancelled",
                description="Stock addition has been cancelled.",
                color=discord.Color.red()
            )
            await button_interaction.response.send_message(embed=cancel_embed, ephemeral=True)
            self.stop()

        async def process_stock(self, button_interaction: discord.Interaction):
            guild_id = str(button_interaction.guild_id)
            guild_cfg = load_guild_config(guild_id)

            real_name = await getServiceName(service, is_premium)
            if real_name not in serviceList.get(guild_id, []):
                await updateServices(guild_id, real_name)

            try:
                if not str(file.filename).endswith(".txt"):
                    return await button_interaction.followup.send(
                        f"You can only upload files with .txt extension", ephemeral=True
                    )
            except Exception:
                return await button_interaction.followup.send(
                    f"Error when checking file.", ephemeral=True
                )

            if file.size > config["maximum-file-size"]:
                return await button_interaction.followup.send(
                    f"Maximum file size: `{config['maximum-file-size']} bytes`",
                    ephemeral=True,
                )
            content = await file.read()

            filtered_stock = []
            dec_cont = content.decode("utf-8")
            content_lines = str(dec_cont).split("\n")
            for item in content_lines:
                if len(item) > 2:
                    filtered_stock.append(item)
            add_cnt, dupe_cnt = await database.addStock(real_name, filtered_stock, config["remove-capture-from-stock"], guild_id)

            os.makedirs(os.path.join(config["stock-storage-path"], guild_id), exist_ok=True)
            stock_files.append_to_stock_file(
                guild_id, real_name, filtered_stock
            )

            added_acc_embed = discord.Embed(
                title=f"{EMOJIS['addstock']} Stock Added",
                description=(
                    f"{EMOJIS['success']} `{add_cnt}` accounts added "
                    f"(skipped `{dupe_cnt}` duplicates) "
                    f"for `{service}` service."
                ),
                color=NEON_GREEN,
            )
            added_acc_embed.set_footer(
                text=config["messages"]["footer-msg"],
                icon_url=get_user_pfp(button_interaction.user),
            )
            await button_interaction.followup.send(
                embed=added_acc_embed, ephemeral=is_silent
            )
            self.stop()

    await interaction.response.send_message(embed=warning_embed, view=StockConfirmView(), ephemeral=is_silent)
    return


@tree.command(
    name="bulkgen", description="(admin only) Generate multiple accounts | by Fr4ct4l"
)
@app_commands.autocomplete(service=service_autcom)
async def bulkgen(
    interaction: discord.Interaction,
    service: str,
    amount: int,
    is_premium: bool,
    is_silent: bool = True,
):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    guild_id = str(interaction.guild_id)

    if service not in serviceList_2.get(guild_id, []):
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Invalid service",
            description=f"This service (`{service}`) does not exist, make sure you typed it right.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    service_name_rl = await getServiceName(service, is_premium)

    # try file first
    accounts = stock_files.pop_multiple_from_stock_file(
        guild_id, service_name_rl, amount
    )
    if len(accounts) < amount:
        # get remainder from DB
        needed = amount - len(accounts)
        success_db, db_accounts = await database.getMultipleAccounts(
            str(service_name_rl), needed, guild_id
        )
        if not success_db:
            # put back whatever we popped
            if accounts:
                stock_files.append_to_stock_file(
                    guild_id, service_name_rl, accounts
                )
            embed_error = discord.Embed(
                title=f"{EMOJIS['error']} Error: Out of stock",
                description=f"This service doesn't seem to have enough accounts to generate.",
                color=NEON_GREEN,
            )
            return await interaction.response.send_message(
                embed=embed_error, ephemeral=True
            )
        else:
            accounts += db_accounts

    accounts_in_file = discord.File(
        fp=StringIO("\n".join([str(account) for account in accounts])),
        filename=f"{service}-{amount}.txt",
    )
    return await interaction.response.send_message(
        content=f"Successfully generated `{amount}` accounts for `{service}`",
        file=accounts_in_file,
        ephemeral=True,
    )


@tree.command(
    name="user", description="(admin only) View user info | by Fr4ct4l"
)
async def usercmd(interaction: discord.Interaction, user: discord.User):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    _user = await database.addUser(str(user.id))
    if _user:
        embd = discord.Embed(
            title=f"{EMOJIS['user']} Found {user.name}",
            description=(
                f"**ID**: `{str(_user.user_id)}`\n"
                f"**Last Gen**: `{str(_user.last_time_genned)}`\n"
                f"**Total Genned**: `{str(_user.amount_genned)}`\n"
                f"**Is Blacklisted**: `{str(_user.is_blacklisted)}`\n"
                f"**Cooldown end**: `{str(_user.user_cooldown)}`\n"
                f"**Sub Time Left**: `{str(_user.subscription_time_left)}`\n"
                f"**Sub Stage**: `{str(_user.subscription_stage)}`\n"
                f"**Notes**: `{str(_user.notes)}`\n"
            ),
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


@tree.command(
    name="clearservice", description="(admin only) Delete a service | by Fr4ct4l"
)
@app_commands.autocomplete(service=service_autcom)
async def clearservice(
    interaction: discord.Interaction, service: str, is_premium: bool = False
):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    guild_id = str(interaction.guild_id)
    service_name_rl = await getServiceName(service, is_premium=is_premium)
    db_res1 = await database.deleteService(service_name_rl, guild_id)
    if db_res1:
        await updateServices(guild_id)
        stock_files.delete_stock_file(guild_id, service_name_rl)

    embd = discord.Embed(
        title=f"{EMOJIS['delete']} Delete Service",
        description=f'{"Successfully deleted service" if db_res1 else "Error. Service doesnt exist."}',
        color=NEON_GREEN if db_res1 else NEON_GREEN,
    )
    embd.set_footer(
        text=config["messages"]["footer-msg"],
        icon_url=get_user_pfp(interaction.user),
    )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


@tree.command(
    name="blacklist", description="(admin only) Blacklist a user | by Fr4ct4l"
)
async def blacklistuser(
    interaction: discord.Interaction, user: discord.User, status: bool = None
):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    the_user = await database.getUser(str(user.id))
    if the_user:
        bl_status = await database.blacklist_user(str(user.id), status)
        embd = discord.Embed(
            title=f"{EMOJIS['blacklist']} Blacklist User",
            description=f"{user.mention}'s blacklist status changed to `{bl_status}`",
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


@tree.command(
    name="setnote", description="(admin only) Set a note on a user | by Fr4ct4l"
)
async def setnote(interaction: discord.Interaction, user: discord.User, note: str):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    the_user = await database.getUser(str(user.id))
    if the_user:
        await database.set_user_note(str(user.id), note)
        embd = discord.Embed(
            title=f"{EMOJIS['setnote']} Set Note",
            description=f"{user.mention}'s note has been updated.",
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


async def build_stock_embed(
    guild_id: str, requester: discord.User = None
) -> discord.Embed:
    if guild_id is None:
        guild_id = "0"
    stock = await database.getStock(serviceList.get(guild_id, []), guild_id)
    now = datetime.utcnow().strftime("%H:%M:%S UTC")

    grouped_stock = {}
    for stk in stock:
        service, count = [s.strip() for s in stk.split(":")]
        db_count = int(count)
        file_count = stock_files.count_stock_file(guild_id, service)
        total = db_count + file_count
        base_name, _, tier = service.rpartition("_")
        if base_name not in grouped_stock:
            grouped_stock[base_name] = {"free": 0, "premium": 0}
        if tier in grouped_stock[base_name]:
            grouped_stock[base_name][tier] += total

    if not grouped_stock:
        embd = discord.Embed(
            title=f"Stock - 0 services",
            description="There are no services to display",
        )
        embd.set_footer(
            text=f"{config['messages']['footer-msg']} • Live • Updates every 30s • Last updated: {now}"
        )
        return embd

    filtered_stock = []
    for base_name, counts in grouped_stock.items():
        free_count = counts.get("free", 0)
        premium_count = counts.get("premium", 0)
        service_name = await getServiceName(base_name, get_real_name=True)
        filtered_stock.append(
            f"**{service_name}**: Free: `{free_count}`; Premium: `{premium_count}`"
        )

    embd = discord.Embed(
        title=f"{EMOJIS['stock']} Live Stock — {len(filtered_stock)} services",
        description="\n".join(filtered_stock),
        color=NEON_GREEN,
    )
    embd.set_footer(
        text=f"{config['messages']['footer-msg']} • Live • Updates every 30s • Last updated: {now}"
    )
    return embd

async def live_stock_updater(message: discord.Message, guild_id: str, requester: discord.User):
    global live_stock_messages

    try:
        while True:
            await asyncio.sleep(30)

            if message.id not in live_stock_messages:
                break

            try:
                new_embed = await build_stock_embed(guild_id, requester)
                await message.edit(embed=new_embed)
            except discord.errors.NotFound:
                live_stock_messages.pop(message.id, None)
                break
            except discord.errors.Forbidden:
                live_stock_messages.pop(message.id, None)
                break
            except Exception:
                pass
    finally:
        live_stock_messages.pop(message.id, None)


@tree.command(
    name="stock", description="Get the live amount of stock (updates every 30s) | by Fr4ct4l"
)
async def stock(interaction: discord.Interaction):
    val = await checkPermission(interaction)
    if not val:
        return

    await database.addUser(str(interaction.user.id))

    embd = await build_stock_embed(str(interaction.guild_id), interaction.user)
    embd.set_footer(
        text=f"{config['messages']['footer-msg']} • Live • Updates every 30s • Last updated: {datetime.utcnow().strftime('%H:%M:%S UTC')}",
        icon_url=get_user_pfp(interaction.user),
    )

    await interaction.response.send_message(
        embed=embd, ephemeral=config["stock-command-silent"]
    )

    sent_message = await interaction.original_response()

    for msg_id, entry in list(live_stock_messages.items()):
        if entry.get("channel_id") == interaction.channel_id:
            entry["task"].cancel()
            live_stock_messages.pop(msg_id, None)

    task = asyncio.create_task(
        live_stock_updater(sent_message, str(interaction.guild_id), interaction.user)
    )
    live_stock_messages[sent_message.id] = {
        "channel_id": interaction.channel_id,
        "task": task,
    }


@subscription.command(name="add", description="(admin only) Add subscription to a user | by Fr4ct4l")
async def addsubscription(
    interaction: discord.Interaction, user: discord.User, time_sec: int, is_silent: bool = False
):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    _user = await database.getUser(str(user.id))
    if _user:
        await database.add_subscription(_user.user_id, time_sec)
        embd = discord.Embed(
            title=f"{EMOJIS['premium']} Subscription Added",
            description=f"{user.mention}'s subscription extended by `{time_sec}` seconds.",
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=is_silent)


# ... subscription massadd, view, set, remove (unchanged) ...


# cooldown commands (unchanged) ...


@cooldown.command(name="reset", description="(admin only) Reset a user's cooldown | by Fr4ct4l")
async def cooldown_reset(interaction: discord.Interaction, user: discord.User):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    _user = await database.getUser(str(user.id))
    if _user:
        await database.reset_user_cooldown(str(user.id), "Free")
        await database.reset_user_cooldown(str(user.id), "Premium")
        embd = discord.Embed(
            title=f"{EMOJIS['cooldown']} Cooldown Reset",
            description=f"{user.mention}'s cooldown has been reset.",
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


@cooldown.command(name="set", description="(admin only) Set a user's cooldown | by Fr4ct4l")
@app_commands.autocomplete(stage=stage_autcom)
async def cooldown_set(
    interaction: discord.Interaction, user: discord.User, stage: str, seconds: int
):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    if stage not in config["subscription-stages"]:
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Invalid stage",
            description=f"Stage must be one of: {', '.join(config['subscription-stages'])}",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    _user = await database.getUser(str(user.id))
    if _user:
        await database.set_user_cooldown(str(user.id), stage, seconds)
        embd = discord.Embed(
            title=f"{EMOJIS['cooldown']} Cooldown Set",
            description=f"{user.mention}'s `{stage}` cooldown set to `{seconds}` seconds.",
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )
    else:
        embd = discord.Embed(
            title=f"{EMOJIS['error']} Error getting user!",
            description=f'`This user does not exist in the database.`',
            color=NEON_GREEN,
        )
        embd.set_footer(
            text=config["messages"]["footer-msg"],
            icon_url=get_user_pfp(interaction.user),
        )

    return await interaction.response.send_message(embed=embd, ephemeral=True)


# old commands redirections:
@tree.command(name="setsuggestions", description="(admin only) Set the suggestions channel | by Fr4ct4l")
async def setsuggestions(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    embed = discord.Embed(
        title=f"{EMOJIS['warning']} Deprecated command",
        description="Use `/setup suggestions` instead.",
        color=NEON_GREEN,
    )
    return await interaction.response.send_message(embed=embed, ephemeral=True)





# ---------- setup commands ----------
@setup.command(name="genchannel", description="Add a gen channel | by Fr4ct4l")
async def setup_genchannel(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    if channel.id not in guild_cfg["gen-channels"]:
        guild_cfg["gen-channels"].append(channel.id)
        save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['gen']} Gen Channel Set",
        description=f"{channel.mention} has been added as a gen channel.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@setup.command(name="premiumchannel", description="Add a premium gen channel | by Fr4ct4l")
async def setup_premiumchannel(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    if channel.id not in guild_cfg["premium-gen-channels"]:
        guild_cfg["premium-gen-channels"].append(channel.id)
        save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['premium']} Premium Channel Set",
        description=f"{channel.mention} has been set as the premium gen channel.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@setup.command(name="adminrole", description="Add an admin role | by Fr4ct4l")
async def setup_adminrole(interaction: discord.Interaction, role: discord.Role):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    if role.id not in guild_cfg["admin-roles"]:
        guild_cfg["admin-roles"].append(role.id)
        save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['crown']} Admin Role Set",
        description=f"{role.mention} has been added as an admin role.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@setup.command(name="freerole", description="Configure a free role entry | by Fr4ct4l")
async def setup_freerole(
    interaction: discord.Interaction,
    role: discord.Role,
    cooldown: int,
    remove_if_expired: bool,
):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )

    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    found = False
    for entry in guild_cfg["roles"]:
        if entry["id"] == role.id and entry.get("type") == "free":
            entry.update(
                {
                    "free-cooldown": cooldown,
                    "premium-cooldown": cooldown,
                    "remove-if-expired": remove_if_expired,
                }
            )
            found = True
            break
    if not found:
        guild_cfg["roles"].append(
            {
                "id": role.id,
                "type": "free",
                "free-cooldown": cooldown,
                "premium-cooldown": cooldown,
                "gen-access": ["all"],
                "remove-if-expired": remove_if_expired,
            }
        )
    save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['settings']} Free Role Configured",
        description=f"{role.mention} has been added/updated as a free role with cooldown `{cooldown}` seconds.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@setup.command(name="premiumrole", description="Configure a premium role entry | by Fr4ct4l")
async def setup_premiumrole(
    interaction: discord.Interaction,
    role: discord.Role,
    cooldown: int,
    remove_if_expired: bool,
):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )

    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    found = False
    for entry in guild_cfg["roles"]:
        if entry["id"] == role.id and entry.get("type") == "premium":
            entry.update(
                {
                    "free-cooldown": cooldown,
                    "premium-cooldown": cooldown,
                    "remove-if-expired": remove_if_expired,
                }
            )
            found = True
            break
    if not found:
        guild_cfg["roles"].append(
            {
                "id": role.id,
                "type": "premium",
                "free-cooldown": cooldown,
                "premium-cooldown": cooldown,
                "gen-access": ["all"],
                "remove-if-expired": remove_if_expired,
            }
        )
    save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['premium']} Premium Role Configured",
        description=f"{role.mention} has been added/updated as a premium role with cooldown `{cooldown}` seconds.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@setup.command(name="suggestions", description="Set suggestions channel | by Fr4ct4l")
async def setup_suggestions(
    interaction: discord.Interaction, channel: discord.TextChannel
):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )

        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    guild_cfg["suggestions-channel-id"] = channel.id
    save_guild_config(guild_id, guild_cfg)
    embed = discord.Embed(
        title=f"{EMOJIS['suggestions']} Suggestions Channel Set",
        description=f"Suggestions channel set to {channel.mention}",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)



@setup.command(name="view", description="View this server's configuration | by Fr4ct4l")
async def setup_view(interaction: discord.Interaction):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.guild_permissions.administrator
    ):
        embed_error = discord.Embed(
            title="Error: Permission Denied",
            description="You need Manage Guild or Administrator permission.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(
            embed=embed_error, ephemeral=True
        )
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)

    embd = discord.Embed(
        title=f"{EMOJIS['settings']} Server Configuration",
        color=NEON_GREEN,
        timestamp=datetime.utcnow(),
    )
    embd.add_field(
        name="Gen channels",
        value=", ".join(f"<#{c}>" for c in guild_cfg.get("gen-channels", [])) or "`none`",
        inline=False,
    )
    embd.add_field(
        name="Premium channels",
        value=", ".join(f"<#{c}>" for c in guild_cfg.get("premium-gen-channels", [])) or "`none`",
        inline=False,
    )
    embd.add_field(
        name="Admin roles",
        value=", ".join(f"<@&{r}>" for r in guild_cfg.get("admin-roles", [])) or "`none`",
        inline=False,
    )
    free_roles = [r for r in guild_cfg.get("roles", []) if r.get("type") == "free"]
    premium_roles = [r for r in guild_cfg.get("roles", []) if r.get("type") == "premium"]
    embd.add_field(
        name="Free roles",
        value="\n".join(
            f"<@&{r['id']}> cooldowns F:{r['free-cooldown']} P:{r['premium-cooldown']} remove:{r['remove-if-expired']}"
            for r in free_roles
        ) if free_roles else "`none`",
        inline=False,
    )
    embd.add_field(
        name="Premium roles",
        value="\n".join(
            f"<@&{r['id']}> cooldowns F:{r['free-cooldown']} P:{r['premium-cooldown']} remove:{r['remove-if-expired']}"
            for r in premium_roles
        ) if premium_roles else "`none`",
        inline=False,
    )
    embd.add_field(
        name="Suggestions channel",
        value=f"<#{guild_cfg.get('suggestions-channel-id')}>" if guild_cfg.get("suggestions-channel-id") else "`none`",
        inline=False,
    )
    embd.add_field(
        name="Stock folder",
        value=os.path.join(config["stock-storage-path"], guild_id),
        inline=False,
    )
    embd.set_footer(text=config["messages"]["footer-msg"])
    await interaction.response.send_message(embed=embd, ephemeral=True)


@setup.command(name="reviewchannel", description="Set the channel where reviews are posted | by Fr4ct4l")
async def setup_reviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return
    
    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    guild_cfg["review-channel-id"] = str(channel.id)
    save_guild_config(guild_id, guild_cfg)
    
    embed = discord.Embed(
        title=f"{EMOJIS['review']} Review Channel Set",
        description=f"Review channel has been set to {channel.mention}",
        color=NEON_GREEN
    )
    embed.set_footer(text=config["messages"]["footer-msg"])
    await interaction.response.send_message(embed=embed, ephemeral=True)


class ReviewModal(discord.ui.Modal, title="Submit a Review"):
    review_text = discord.ui.TextInput(
        label="Your Review",
        placeholder="Write your review here...",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=True
    )

    rating = discord.ui.TextInput(
        label="Rating (1-5)",
        placeholder="Enter a number from 1 to 5",
        max_length=1,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.rating.value.isdigit() or int(self.rating.value) not in range(1, 6):
            await interaction.response.send_message(
                "Please enter a valid rating between 1 and 5.",
                ephemeral=True
            )
            return

        rating_num = int(self.rating.value)
        stars = "⭐" * rating_num

        guilds = load_guilds()
        review_channel_id = None
        for guild_id, guild_data in guilds.items():
            if guild_data.get('review-channel-id'):
                review_channel_id = guild_data['review-channel-id']
                break

        if not review_channel_id:
            await interaction.response.send_message(
                "Review channel is not configured. Please contact an administrator.",
                ephemeral=True
            )
            return

        review_channel = bot.get_channel(int(review_channel_id))
        if not review_channel:
            await interaction.response.send_message(
                "Review channel not found. Please contact an administrator.",
                ephemeral=True
            )
            return

        review_embed = discord.Embed(
            title=f"{EMOJIS['review']} A new review has been posted",
            description=self.review_text.value,
            color=NEON_GREEN
        )
        review_embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
        )
        review_embed.set_thumbnail(
            url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
        )
        review_embed.add_field(
            name="Rating",
            value=f"{stars} ({rating_num}/5)",
            inline=True
        )
        review_embed.add_field(
            name="Reviewed",
            value="just now",
            inline=True
        )
        review_embed.set_footer(text=config["messages"]["footer-msg"])

        like_view = ReviewLikeView()
        await review_channel.send(embed=review_embed, view=like_view)

        await interaction.response.send_message(
            "✅ Your review has been submitted! Thank you for your feedback.",
            ephemeral=True
        )


class ReviewLikeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.likes = 0
        self.liked_users = set()

    @discord.ui.button(label="❤️ 0", style=discord.ButtonStyle.secondary, custom_id="review_like")
    async def like_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.liked_users:
            await interaction.response.send_message(
                "You already liked this review!",
                ephemeral=True
            )
            return

        self.likes += 1
        self.liked_users.add(interaction.user.id)
        button.label = f"❤️ {self.likes}"
        await interaction.message.edit(view=self)
        await interaction.response.send_message(
            "❤️ Thanks for liking this review!",
            ephemeral=True
        )


class ReviewPromptView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="📝 Submit A Review", style=discord.ButtonStyle.primary, custom_id="submit_review_dm")
    async def submit_review(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ReviewModal())


# ---------- help command ----------
@tree.command(name="vouch", description="Leave a vouch/testimonial for the server | by Fr4ct4l")
async def vouch_command(interaction: discord.Interaction, message: str):
    """Let a user leave a vouch/testimonial for the server."""
    val = await checkPermission(interaction)
    if not val:
        return

    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)
    review_channel_id = guild_cfg.get("review-channel-id")

    if not review_channel_id:
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: No Review Channel",
            description="This server hasn't configured a review channel. Contact an administrator.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    review_channel = bot.get_channel(int(review_channel_id))
    if not review_channel:
        embed_error = discord.Embed(
            title=f"{EMOJIS['error']} Error: Channel Not Found",
            description="The review channel could not be found. Contact an administrator.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    vouch_embed = discord.Embed(
        title=f"{EMOJIS['vouch']} New Vouch",
        description=message,
        color=NEON_GREEN,
    )
    vouch_embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
    )
    vouch_embed.set_thumbnail(
        url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
    )
    vouch_embed.set_footer(text=config["messages"]["footer-msg"])

    await review_channel.send(embed=vouch_embed)

    confirm_embed = discord.Embed(
        title=f"{EMOJIS['success']} Vouch Submitted",
        description="Thank you for your vouch! It has been posted to the review channel.",
        color=NEON_GREEN,
    )
    await interaction.response.send_message(embed=confirm_embed, ephemeral=True)


@tree.command(name="shop", description="View the server's shop and available services | by Fr4ct4l")
async def shop_command(interaction: discord.Interaction):
    """Display the server's shop/available services list."""
    val = await checkPermission(interaction)
    if not val:
        return

    guild_id = str(interaction.guild_id)
    services = serviceList_2.get(guild_id, [])

    if not services:
        embed = discord.Embed(
            title=f"{EMOJIS['shop']} Shop",
            description="No services are currently available in this server.",
            color=NEON_GREEN,
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    service_list = "\n".join([f"• **{service}**" for service in services])
    embed = discord.Embed(
        title=f"{EMOJIS['shop']} Shop - Available Services",
        description=service_list,
        color=NEON_GREEN,
    )
    embed.set_footer(text=config["messages"]["footer-msg"])
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="home", description="Show welcome/info about the bot | by Fr4ct4l")
async def home_command(interaction: discord.Interaction):
    """Show a welcome/info embed about the bot."""
    guild = interaction.guild
    bot_user = bot.user

    embed = discord.Embed(
        title=f"{EMOJIS['home']} Welcome to {guild.name}",
        description=(
            f"Hello **{interaction.user.name}**! {EMOJIS['success']}\n\n"
            f"I'm **{bot_user.name}** — an account generator bot designed to "
            f"distribute digital accounts to server members easily and securely.\n\n"
            f"{EMOJIS['key']} Use `/help` to see all available commands.\n"
            f"{EMOJIS['stock']} Use `/stock` to check available accounts.\n"
            f"{EMOJIS['gen']} Use `/gen <service>` to generate an account."
        ),
        color=NEON_GREEN,
    )
    if bot_user.display_avatar:
        embed.set_thumbnail(url=bot_user.display_avatar.url)
    embed.set_footer(text=config["messages"]["footer-msg"])
    await interaction.response.send_message(embed=embed, ephemeral=False)


@setup.command(name="settings", description="View bot settings for this server | by Fr4ct4l")
async def setup_settings(interaction: discord.Interaction):
    """Show all current guild config values in a readable embed."""
    val = await checkPermission(interaction, admin_check=True)
    if not val:
        return

    guild_id = str(interaction.guild_id)
    guild_cfg = load_guild_config(guild_id)

    embd = discord.Embed(
        title=f"{EMOJIS['settings']} Bot Settings",
        description=f"Current configuration for **{interaction.guild.name}**",
        color=NEON_GREEN,
        timestamp=datetime.utcnow(),
    )

    # Gen channels
    gen_channels = guild_cfg.get("gen-channels", [])
    embd.add_field(
        name=f"{EMOJIS['gen']} Gen Channels",
        value=", ".join(f"<#{c}>" for c in gen_channels) or "`none`",
        inline=False,
    )

    # Premium gen channels
    premium_channels = guild_cfg.get("premium-gen-channels", [])
    embd.add_field(
        name=f"{EMOJIS['premium']} Premium Gen Channels",
        value=", ".join(f"<#{c}>" for c in premium_channels) or "`none`",
        inline=False,
    )

    # Admin roles
    admin_roles = guild_cfg.get("admin-roles", [])
    embd.add_field(
        name=f"{EMOJIS['crown']} Admin Roles",
        value=", ".join(f"<@&{r}>" for r in admin_roles) or "`none`",
        inline=False,
    )

    # Suggestions channel
    suggestions_channel = guild_cfg.get("suggestions-channel-id")
    embd.add_field(
        name=f"{EMOJIS['suggestions']} Suggestions Channel",
        value=f"<#{suggestions_channel}>" if suggestions_channel else "`none`",
        inline=False,
    )

    # Review channel
    review_channel = guild_cfg.get("review-channel-id")
    embd.add_field(
        name=f"{EMOJIS['review']} Review Channel",
        value=f"<#{review_channel}>" if review_channel else "`none`",
        inline=False,
    )

    # Roles configuration
    roles = guild_cfg.get("roles", [])
    if roles:
        roles_text = []
        for r in roles:
            role_type = r.get("type", "unknown").upper()
            role_mention = f"<@&{r['id']}>"
            free_cd = r.get("free-cooldown", "N/A")
            prem_cd = r.get("premium-cooldown", "N/A")
            remove_exp = r.get("remove-if-expired", False)
            roles_text.append(f"{role_mention} ({role_type}) | F:{free_cd}s P:{prem_cd}s | Remove:{remove_exp}")
        embd.add_field(
            name=f"{EMOJIS['settings']} Role Configs",
            value="\n".join(roles_text),
            inline=False,
        )
    else:
        embd.add_field(
            name=f"{EMOJIS['settings']} Role Configs",
            value="`none`",
            inline=False,
        )

    embd.set_footer(text=config["messages"]["footer-msg"])
    await interaction.response.send_message(embed=embd, ephemeral=True)


@tree.command(name="help", description="Show the bot's help menu | by Fr4ct4l")
async def help_command(interaction: discord.Interaction):
    """Display a help menu with selectable categories."""
    embed = get_home_embed(user=interaction.user)
    view = HelpView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


bot.run(config["token"])
