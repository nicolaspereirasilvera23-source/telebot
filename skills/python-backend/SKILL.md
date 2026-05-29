
## `skills/telegram-bot/SKILL.md`

```md
# Telegram Bot Skill

Use this skill when implementing or modifying Telegram bot behavior.

## Purpose

The Telegram bot receives lead messages, sends them through the qualification workflow and replies with the result.

## Recommended Library

Use `python-telegram-bot`.

For this challenge, use polling unless webhook deployment is explicitly required.

## Main Responsibilities

`main.py` should:

- Load environment variables.
- Start the Telegram bot.
- Register handlers.
- Receive text messages.
- Call service functions.
- Reply to the user.
- Handle errors gracefully.

## Main Flow

```txt
/start command
↓
Bot explains what it does

Text message
↓
Bot receives raw lead
↓
LLM extracts structured data
↓
Qualifier applies rules
↓
Sheets logs result
↓
Bot replies with decision