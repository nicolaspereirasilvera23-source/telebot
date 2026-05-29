# Project Rules — Orbyn Lead Bot

This project is a Telegram lead qualification bot built for the Orbyn developer pool challenge.

## Main Goal

Build a simple, functional and readable bot that:

- Receives lead information through Telegram.
- Uses an LLM to extract structured information from free text.
- Applies business rules to decide if the lead qualifies.
- Replies in Telegram with the decision and reasoning.
- Logs each lead into Google Sheets.

## Architecture

Keep the project simple and separated by responsibility:

```txt
main.py
services/
  llm_service.py
  qualifier_service.py
  sheets_service.py
models/
  lead.py
utils/
  config.py