# session-notes

## description: Summarize the current chat session into structured markdown notes and save them to a file.

## Trigger
User types `/session-notes` or asks to "summarize this session", "save session notes", or "give me notes from this session".

## What this skill does

Look back through the **entire current conversation** and produce a well-structured notes entry. Save it to `notes/session-YYYY-MM-DD.md` in the repo root (create the folder/file if needed).

**One file per day. Append, never overwrite.**
- If `notes/session-YYYY-MM-DD.md` already exists → append a new timestamped entry at the bottom, leaving all previous entries untouched.
- If it does not exist → create it with a day-level header, then write the first entry.

## File structure

A day file looks like this (multiple entries accumulate throughout the day):

```markdown
# Session Notes — YYYY-MM-DD

**Links:** [[GradeMaster]] · [[standups/YYYY-MM-DD]] · [[sessions/session-YYYY-MM-DD]]

---

### 🕐 HH:MM

#### 🎯 Goal / Topic
One-sentence summary of what this session/run was about.

#### ✅ What Was Done
- bullet

#### 💡 Key Decisions
- bullet

#### 🐛 Problems & Fixes
- bullet

#### 📁 Files Changed
- bullet

#### ⏭️ Next Steps
- bullet

#### 📝 Raw Notes / Context
Any other important context, code snippets, or links.

---

### 🕐 HH:MM

#### 🎯 Goal / Topic
...
```

Each new `/session-notes` run adds one new `### 🕐 HH:MM` block at the bottom (preceded by `---`). Only sections with content are included in that block.

## Steps

1. Read through the full conversation history visible in context.
2. Extract the relevant information for each section.
3. **Get the actual current time** by running `Get-Date -Format "HH:mm"` via the PowerShell tool. Use this for the `### 🕐 HH:MM` timestamp — never use `00-00` as a placeholder.
4. Determine today's filename: `notes/sessions/session-YYYY-MM-DD.md` (date from `currentDate` context). Sessions live in `notes/sessions/`.
5. Check if the file exists:
   - **Exists** → Read it, then append a new `---\n\n### 🕐 HH:MM\n...` block at the end using the Write tool (full file content = old content + new block).
   - **Does not exist** → Write a new file with the `# Session Notes — YYYY-MM-DD` header followed by the first entry block. Also append `- [[sessions/session-YYYY-MM-DD]]` to the `## Sessions` section in `notes/GradeMaster.md`.
6. Tell the user where the file was saved and give a short preview (Goal + What Was Done of the new entry).
7. Offer to open the file or copy any section.

## Style rules
- Be concise — notes are for skimming, not reading
- Use past tense for completed actions ("Added login route", not "Add login route")
- Group related bullets together
- For code snippets in the notes, use fenced code blocks with the language tag
- If a section is empty, omit it entirely — don't leave placeholder text
