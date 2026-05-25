# Skills Index

**Links:** [[Skills]] · [[GradeMaster]]

Custom Claude Code skills for this project. Each skill lives in `.claude/skills/<name>/SKILL.md`.
Trigger any skill by typing `/<name>` in the Claude Code chat.

## Project skills

| Skill | Trigger | Description |
|---|---|---|
| session-notes | `/session-notes` | Summarize the current chat session and append to `notes/sessions/session-YYYY-MM-DD.md`. Creates the file if new day; auto-adds link to `notes/GradeMaster.md`. |
| standup | `/standup` | Generate a Yesterday / Today / Blockers standup from session notes + git log + git status. Optionally saves to `notes/standups/YYYY-MM-DD.md` and auto-adds link to `notes/GradeMaster.md`. |

## Built-in skills (always available)

| Skill | Trigger | Description |
|---|---|---|
| review | `/review` | Review a pull request |
| security-review | `/security-review` | Security review of pending branch changes |
| simplify | `/simplify` | Review changed code for quality/efficiency and fix issues |
| verify | `/verify` | Run the app and confirm a change works end-to-end |
| run | `/run` | Launch the project (backend + frontend) |

## Adding a new skill

1. Create `.claude/skills/<name>/SKILL.md`
2. Add a row to the table above
3. Add an entry to `notes/Skills.md` in the Obsidian vault
