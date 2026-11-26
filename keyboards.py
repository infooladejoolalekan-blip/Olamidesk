"""
keyboards.py
All inline keyboard builders. No logic — just layouts.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """The welcome menu shown under /start and /menu."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏢 Our Services", callback_data="menu_services"),
                InlineKeyboardButton("📢 Telegram Ads", callback_data="menu_ads"),
            ],
            [
                InlineKeyboardButton("🤖 Bot Development", callback_data="menu_bots"),
                InlineKeyboardButton("💰 Pricing & Enquiries", callback_data="menu_pricing"),
            ],
            [
                InlineKeyboardButton("💬 Talk to Support", callback_data="menu_support"),
                InlineKeyboardButton("ℹ️ About Olamidesk", callback_data="menu_about"),
            ],
        ]
    )


def support_menu_keyboard() -> InlineKeyboardMarkup:
    """Shown when the user is inside the support flow."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📝 Submit Enquiry", callback_data="support_submit")],
            [InlineKeyboardButton("↩️ Back to Menu", callback_data="back_to_menu")],
        ]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """A single back button."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("↩️ Back to Menu", callback_data="back_to_menu")]]
    )


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """The admin panel menu. Only accessible after password authentication."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 Pending Enquiries", callback_data="admin_pending")],
            [InlineKeyboardButton("📊 View Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("↩️ Close Admin Panel", callback_data="admin_close")],
        ]
    )


def confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Confirmation buttons for a broadcast message."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Send Now", callback_data="broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")],
        ]
    )