# standup

## description: Generate a standup update (yesterday / today / blockers) from session notes and git history.

## Trigger
User types `/standup` or asks to "generate a standup", "write my standup", or "what's my standup".

## What this skill does

Pulls together a ready-to-paste standup update by combining:
1. Recent session notes from the `notes/` folder
2. Recent git commits on the current branch
3. Current git status (dirty files, uncommitted work)

Prints the standup to the chat — does NOT save a file unless the user asks.

## Steps

1. **Get today's date and current branch** — run:
   ```powershell
   Get-Date -Format "yyyy-MM-dd"
   git branch --show-current
   ```

2. **Read session notes** — look for the following files in `notes/` (most recent first):
   - `notes/session-<today>.md`
   - `notes/session-<yesterday>.md`  
   Read whichever exist. If neither exists, continue without them.

3. **Get git history** — run:
   ```powershell
   git log --oneline -10
   ```

4. **Get git status** — run:
   ```powershell
   git status --short
   ```

5. **Synthesize the standup** using the format below. Derive content from notes + git; do not make things up. If a section has nothing, write "Nothing to report."

6. **Print the standup** to the chat in a clean, copy-pasteable block.

7. Ask the user if they want to save it to `notes/standups/YYYY-MM-DD.md`. When saving, prepend a links line at the top of the file: `**Links:** [[GradeMaster]] · [[sessions/session-YYYY-MM-DD]]`. Also append `- [[standups/YYYY-MM-DD]]` to the `## Standups` section in `notes/GradeMaster.md`.

## Output format

```
📋 Standup — YYYY-MM-DD  (branch: <branch-name>)

✅ Yesterday
- <what was done — from session notes and/or commits>

🎯 Today
- <planned work — from ⏭️ Next Steps in session notes, or inferred from current state>

🚧 Blockers
- <any problems mentioned in notes that aren't resolved, or uncommitted/broken work>
```

## Rules
- Keep each bullet to one line — standups are for skimming
- Yesterday = last session's "What Was Done" + any commits since the previous day
- Today = "Next Steps" from the most recent session notes entry; if none, infer from dirty files or recent context
- Blockers = unresolved "Problems & Fixes" entries, or uncommitted changes that look stuck
- If there are no blockers, write "None" (don't omit the section)
- Use plain language — no jargon, no markdown inside bullets
