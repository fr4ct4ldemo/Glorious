import discord
from discord import app_commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime, timedelta
import json

from .database import (
    create_review,
    update_review_message_id,
    add_like_to_review,
    user_already_liked,
    get_user_today_review,
    get_review_by_message_id,
    remove_like_from_review,
    get_review,
)
from .guild_config import load_guild_config

config = json.load(open("config.json"))

REVIEW_COLOR = 0x39FF14


class ReviewModal(Modal):
    def __init__(self, callback):
        super().__init__(title="Submit A Review")
        self.callback = callback

        self.review = TextInput(
            label="Review",
            placeholder="Write your review here...",
            max_length=200,
            required=True,
        )

        self.rating = TextInput(
            label="Rating",
            placeholder="Enter a number from 1 to 5",
            max_length=1,
            required=True,
        )

        self.add_item(self.review)
        self.add_item(self.rating)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction, self.review.value, self.rating.value)


class ReviewView(View):
    def __init__(self, review_id: int, bot, submit_callback=None):
        super().__init__(timeout=None)
        self.review_id = review_id
        self.bot = bot
        self.submit_callback = submit_callback

    @discord.ui.button(label="❤️ 0", style=discord.ButtonStyle.secondary, custom_id="review_like_btn")
    async def like_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        review = await get_review(self.review_id)
        if not review:
            await interaction.response.defer()
            return

        user_id = str(interaction.user.id)
        already_liked = await user_already_liked(self.review_id, user_id)
        
        if already_liked:
            await remove_like_from_review(self.review_id, user_id)
            new_likes = max(0, review.likes - 1)
        else:
            await add_like_to_review(self.review_id, user_id)
            new_likes = review.likes + 1
        
        button.label = f"❤️ {new_likes}"
        await interaction.response.defer()

    @discord.ui.button(label="📝 Submit A Review", style=discord.ButtonStyle.primary, custom_id="review_submit_btn")
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.submit_callback:
            modal = ReviewModal(self.submit_callback)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.defer()


def get_star_rating(rating: int) -> str:
    rating = int(rating)
    if rating < 1 or rating > 5:
        return "⭐"
    return "⭐" * rating


def format_timestamp(timestamp_str: str) -> str:
    try:
        review_time = datetime.fromisoformat(timestamp_str)
        now = datetime.utcnow()
        diff = now - review_time
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                return "just now"
            elif hours == 1:
                return "1 hour ago"
            else:
                return f"{hours} hours ago"
        elif diff.days == 1:
            return "1 day ago"
        else:
            return f"{diff.days} days ago"
    except:
        return "just now"


async def create_review_embed(review, bot, invite_code: str, submit_callback) -> tuple:
    stars = get_star_rating(review.rating)
    timestamp_text = format_timestamp(review.timestamp)
    
    embed = discord.Embed(
        title="",
        color=REVIEW_COLOR
    )
    
    embed.set_author(
        name=review.username,
        icon_url=review.avatar_url
    )
    
    embed.add_field(
        name="",
        value="A new review has been posted",
        inline=False
    )
    
    embed.add_field(
        name="",
        value=review.review_text,
        inline=False
    )
    
    embed.add_field(
        name="Rating",
        value=f"{stars} ({review.rating}/5)",
        inline=True
    )
    
    embed.add_field(
        name="Reviewed",
        value=timestamp_text,
        inline=True
    )
    
    embed.set_thumbnail(url=review.avatar_url)
    
    bot_name = bot.user.name if bot.user else "Bot"
    footer_text = f"{bot_name} | {invite_code}"
    embed.set_footer(text=footer_text)
    
    view = ReviewView(review.id, bot, submit_callback)
    
    return embed, view
