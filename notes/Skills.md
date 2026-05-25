# Skills

**Links:** [[GradeMaster]]

Claude Code skills available in this project. Trigger with `/skill-name` in the Claude Code chat.

---

## /session-notes
Summarizes the current chat session into structured markdown and appends it to `sessions/session-YYYY-MM-DD.md`. Creates the file if it's a new day and auto-adds the link to [[GradeMaster]].

**Sections written:** Goal · What Was Done · Key Decisions · Problems & Fixes · Files Changed · Next Steps

---

## /standup
Generates a Yesterday / Today / Blockers standup by reading session notes + git log + git status. Prints to chat. Optionally saves to `standups/YYYY-MM-DD.md` and auto-adds the link to [[GradeMaster]].

---

## /review
Reviews a pull request — reads the diff and surfaces issues, risks, and suggestions.

---

## /security-review
Full security review of pending changes on the current branch.

---

## /simplify
Reviews recently changed code for quality and efficiency, then fixes issues found.

---

## /verify
Runs the app and observes behavior to confirm a change actually works.

---

## /run
Launches the project app (backend + frontend) and confirms it starts correctly.
