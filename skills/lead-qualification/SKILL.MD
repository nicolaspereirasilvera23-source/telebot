
## `skills/lead-qualification/SKILL.md`

```md
# Lead Qualification Skill

Use this skill when implementing or modifying lead extraction, lead validation or qualification logic.

## Purpose

The bot receives free text from Telegram and must decide if the lead matches Orbyn's ICP.

The ICP is:

- Services or consulting company.
- At least 5 employees.
- Spain or Latin America.
- Interest in automation or AI.

## Recommended Design

Separate extraction from decision.

```txt
LLM extraction
↓
Python qualification rules