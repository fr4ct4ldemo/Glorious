import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
import asyncio
import os
from typing import Optional

from .database import (
    Ticket,
    create_ticket,
    get_ticket_by_channel,
    update_ticket_claim,
    close_ticket,
)
from .guild_config import load_guild_config

# global config used only for colors/messages
import json
config = json.load(open("config.json"))


class TicketModal(Modal):
    def __init__(self):
        super().__init__(title="Open a Ticket")

        self.subject = TextInput(
            label="Subject",
            placeholder="Brief title of your concern",
            max_length=100,
            required=True,
        )

        self.description = TextInput(
            label="Description",
            placeholder="Please describe your issue in detail",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True,
        )

        self.add_item(self.subject)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild_cfg = load_guild_config(str(interaction.guild.id))

        if not guild_cfg.get("ticket-category"):
            embed = discord.Embed(
                title="Error",
                description="Ticket category not configured. Please run `/setup ticketcategory` first.",
                color=config["colors"]["error"],
            )
            embed.set_footer(text=config["messages"]["footer-msg"])
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        category = discord.utils.get(
            interaction.guild.categories, id=guild_cfg["ticket-category"]
        )
        if not category:
            embed = discord.Embed(
                title="Error",
                description="Ticket category not found. Please reconfigure it.",
                color=config["colors"]["error"],
            )
            embed.set_footer(text=config["messages"]["footer-msg"])
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        channel_name = f"ticket-{interaction.user.name.lower()}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }

        if guild_cfg.get("ticket-staff-role"):
            staff_role = interaction.guild.get_role(guild_cfg["ticket-staff-role"])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True,
                )

        channel = await interaction.guild.create_text_channel(
            name=channel_name, category=category, overwrites=overwrites
        )

        ticket_data = {
            "channel_id": str(channel.id),
            "user_id": str(interaction.user.id),
            "subject": self.subject.value,
            "description": self.description.value,
            "is_open": True,
            "opened_at": datetime.utcnow().isoformat(),
        }

        ticket = await create_ticket(ticket_data)

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket.id}",
            description=f"**Subject:** {self.subject.value}\n**Description:** {self.description.value}",
            color=config["colors"]["success"],
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name="Opened by", value=f"{interaction.user.mention} ({interaction.user})"
        )
        embed.add_field(name="Status", value="Open")
        embed.set_footer(text=config["messages"]["footer-msg"])

        view = TicketView(ticket.id)
        await channel.send(embed=embed, view=view)

        embed = discord.Embed(
            title="Ticket Created",
            description=f"Your ticket has been created: {channel.mention}",
            color=config["colors"]["success"],
        )
        embed.set_footer(text=config["messages"]["footer-msg"])
        await interaction.followup.send(embed=embed, ephemeral=True)


class CloseTicketModal(Modal):
    def __init__(self, ticket_id: int):
        super().__init__(title="Close Ticket")
        self.ticket_id = ticket_id
        
        self.reason = TextInput(
            label="Close Reason",
            placeholder="Reason for closing",
            max_length=100,
            required=True
        )
        
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild_cfg = load_guild_config(str(interaction.guild.id))
        
        # Get ticket
        ticket = await get_ticket_by_channel(str(interaction.channel.id))
        if not ticket:
            embed = discord.Embed(
                title="Error",
                description="Ticket not found.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Generate transcript
        messages = []
        async for message in interaction.channel.history(limit=None, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(f"[{timestamp}] {message.author}: {message.content}")
        
        transcript_text = "\n".join(messages)
        
        # Save transcript file
        transcript_file = f"transcript_{ticket.id}.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"Ticket #{ticket.id}\n")
            f.write(f"User: {interaction.guild.get_member(int(ticket.user_id))}\n")
            f.write(f"Subject: {ticket.subject}\n")
            f.write(f"Opened: {ticket.opened_at}\n")
            f.write(f"Closed: {datetime.utcnow().isoformat()}\n")
            f.write(f"Reason: {self.reason.value}\n")
            f.write("\n" + "="*50 + "\n\n")
            f.write(transcript_text)
        
        # Send to transcript channel if configured
        if guild_cfg.get('ticket-transcript-channel'):
            transcript_channel = interaction.guild.get_channel(guild_cfg['ticket-transcript-channel'])
            if transcript_channel:
                try:
                    with open(transcript_file, 'rb') as f:
                        file = discord.File(f, filename=transcript_file)
                        await transcript_channel.send(f"Transcript for ticket #{ticket.id}", file=file)
                except Exception as e:
                    print(f"Error sending transcript to channel: {e}")
        
        # Try to DM user
        user = interaction.guild.get_member(int(ticket.user_id))
        if user:
            try:
                with open(transcript_file, 'rb') as f:
                    file = discord.File(f, filename=transcript_file)
                    await user.send(f"Transcript for your ticket #{ticket.id}", file=file)
            except discord.Forbidden:
                # User has DMs closed, silently ignore
                pass
            except Exception as e:
                print(f"Error sending transcript to user: {e}")
        
        # Close ticket in database
        await close_ticket(ticket.id, self.reason.value)
        
        # Update embed
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket.id} - CLOSED",
            description=f"**Subject:** {ticket.subject}\n**Description:** {ticket.description}",
            color=config['colors']['error'],
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Opened by", value=f"{user.mention if user else 'Unknown'}")
        embed.add_field(name="Closed by", value=f"{interaction.user.mention}")
        embed.add_field(name="Status", value="Closed")
        embed.add_field(name="Reason", value=self.reason.value)
        embed.set_footer(text=config['messages']['footer-msg'])
        
        # Disable buttons
        view = TicketView(ticket.id, closed=True)
        await interaction.channel.send(embed=embed, view=view)
        
        # Delete file
        if os.path.exists(transcript_file):
            os.remove(transcript_file)
        
        # Delete channel after 5 seconds
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except discord.NotFound:
            pass  # Channel already deleted


class TicketView(View):
    def __init__(self, ticket_id: int, closed: bool = False):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.closed = closed
        
        if not closed:
            self.close_button = Button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id=f"close_ticket_{ticket_id}")
            self.claim_button = Button(label="👤 Claim", style=discord.ButtonStyle.primary, custom_id=f"claim_ticket_{ticket_id}")
            self.unclaim_button = Button(label="🔘 Unclaim", style=discord.ButtonStyle.secondary, custom_id=f"unclaim_ticket_{ticket_id}", row=1)
            
            self.close_button.callback = self.close_ticket
            self.claim_button.callback = self.claim_ticket
            self.unclaim_button.callback = self.unclaim_ticket
            
            self.add_item(self.close_button)
            self.add_item(self.claim_button)
            self.add_item(self.unclaim_button)
    
    async def close_ticket(self, interaction: discord.Interaction):
        guild_cfg = load_guild_config(str(interaction.guild.id))
        if not guild_cfg.get('ticket-staff-role'):
            embed = discord.Embed(
                title="Error",
                description="Staff role not configured.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        staff_role = interaction.guild.get_role(guild_cfg['ticket-staff-role'])
        if not staff_role or staff_role not in interaction.user.roles:
            embed = discord.Embed(
                title="Error",
                description="You don't have permission to close tickets.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        modal = CloseTicketModal(self.ticket_id)
        await interaction.response.send_modal(modal)
    
    async def claim_ticket(self, interaction: discord.Interaction):
        guild_cfg = load_guild_config(str(interaction.guild.id))
        if not guild_cfg.get('ticket-staff-role'):
            embed = discord.Embed(
                title="Error",
                description="Staff role not configured.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        staff_role = interaction.guild.get_role(guild_cfg['ticket-staff-role'])
        if not staff_role or staff_role not in interaction.user.roles:
            embed = discord.Embed(
                title="Error",
                description="You don't have permission to claim tickets.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update ticket
        await update_ticket_claim(self.ticket_id, str(interaction.user.id))
        
        # Update embed
        ticket = await get_ticket_by_channel(str(interaction.channel.id))
        if ticket:
            user = interaction.guild.get_member(int(ticket.user_id))
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket.id}",
                description=f"**Subject:** {ticket.subject}\n**Description:** {ticket.description}",
                color=config['colors']['success'],
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Opened by", value=f"{user.mention if user else 'Unknown'} ({user})" if user else "Unknown")
            embed.add_field(name="Status", value=f"Claimed by {interaction.user.mention}")
            embed.set_footer(text=config['messages']['footer-msg'])
            
            # Update view to show unclaim button
            view = TicketView(self.ticket_id)
            view.claim_button.label = "🔘 Unclaim"
            view.claim_button.style = discord.ButtonStyle.secondary
            view.claim_button.callback = self.unclaim_ticket
            view.remove_item(view.unclaim_button)  # Remove the unclaim button since we're replacing claim with unclaim
            
            await interaction.response.edit_message(embed=embed, view=view)
    
    async def unclaim_ticket(self, interaction: discord.Interaction):
        guild_cfg = load_guild_config(str(interaction.guild.id))
        if not guild_cfg.get('ticket-staff-role'):
            embed = discord.Embed(
                title="Error",
                description="Staff role not configured.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        staff_role = interaction.guild.get_role(guild_cfg['ticket-staff-role'])
        if not staff_role or staff_role not in interaction.user.roles:
            embed = discord.Embed(
                title="Error",
                description="You don't have permission to unclaim tickets.",
                color=config['colors']['error']
            )
            embed.set_footer(text=config['messages']['footer-msg'])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update ticket
        await update_ticket_claim(self.ticket_id, None)
        
        # Update embed
        ticket = await get_ticket_by_channel(str(interaction.channel.id))
        if ticket:
            user = interaction.guild.get_member(int(ticket.user_id))
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket.id}",
                description=f"**Subject:** {ticket.subject}\n**Description:** {ticket.description}",
                color=config['colors']['success'],
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Opened by", value=f"{user.mention if user else 'Unknown'} ({user})" if user else "Unknown")
            embed.add_field(name="Status", value="Open")
            embed.set_footer(text=config['messages']['footer-msg'])
            
            # Update view to show claim button
            view = TicketView(self.ticket_id)
            view.claim_button.label = "👤 Claim"
            view.claim_button.style = discord.ButtonStyle.primary
            view.claim_button.callback = self.claim_ticket
            
            await interaction.response.edit_message(embed=embed, view=view)


class TicketSystem:
    def __init__(self, bot):
        self.bot = bot
    
    async def setup(self):
        # Register the ticket panel button callback
        self.bot.add_view(TicketView(0))  # Dummy view for persistent components