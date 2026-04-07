# Jora Prompt Library

Copy-paste prompts for common Jira workflows using Jora with an LLM agent (Claude, etc.).

**How to use:** Paste a prompt into Claude (or any LLM with shell tool access). Replace anything in `{CURLY_BRACES}` with your actual values before sending.

> **Tip:** Start every session by running `jora context` and pasting the output above your prompt. This gives the agent a complete picture of available commands and output schemas without wasting tokens on `--help` calls.

---

## Time tracking

### Fill estimates and log work for all my tickets in a release

Use this at the end of a sprint or release cycle to catch up on time tracking in one pass.

```
I need to fill in original estimates and log work for all my incomplete tickets
in release {RELEASE} of project {PROJECT}.

Use `jora batch find-incomplete --project {PROJECT} --fix-version {RELEASE} --assignee me --json`
to get the list.

For each ticket:
1. Fetch its full details with `jora issue get {KEY} --json` so you understand the scope.
2. Based on the summary and description, suggest a realistic original estimate if one is missing.
3. Ask me to confirm or adjust the estimate for each ticket before setting it.
4. After estimates are confirmed, ask how much time I actually spent and log it with an
   appropriate comment using `jora worklog add`.

Work through tickets one at a time. Show me the current status (estimate, time spent,
remaining) before asking for each input.
```

---

### End-of-day worklog

Log today's work across multiple tickets without hunting for keys.

```
Help me log today's work in Jira. Today is {DATE}.

Search for my in-progress tickets with:
`jora search "assignee = currentUser() AND status = 'In Progress' AND project = {PROJECT}" --json`

Show me the list, then ask me which ones I worked on today and for how long.
For each ticket I worked on, log the time using:
`jora worklog add {KEY} --time {TIME} --started {DATE}T{START_TIME} --comment "{DESCRIPTION}" --json`

Use my local timezone {TIMEZONE}.
```

---

### Estimate all unestimated tickets in a sprint

Useful before a sprint review to ensure accurate metrics.

```
Find all tickets in project {PROJECT} assigned to me that are missing original estimates.

Use: `jora batch find-incomplete --project {PROJECT} --assignee me --json`

For each ticket without an original estimate, read the full description with
`jora issue get {KEY} --json` and suggest an estimate based on:
- Issue type (Bug = typically smaller, Story/Task = varies)
- Summary and description length and complexity
- Any sub-tasks or acceptance criteria mentioned in the description

Present your suggestions as a table (key, summary, suggested estimate, reasoning).
Once I approve, set them all using `jora issue update {KEY} --estimate {ESTIMATE} --json`.
```

---

## Summarisation

### Summarise a ticket's discussion thread

Get a quick read on a long comment thread without opening Jira.

```
Summarise the discussion on ticket {KEY}.

First fetch the ticket: `jora issue get {KEY} --json`
Then fetch all comments: `jora issue comment {KEY} --json`

Write a concise summary covering:
- What the ticket is about (one sentence)
- Key decisions made in the comments
- Any unresolved questions or blockers
- The current agreed next step (if any)

Keep the summary under 200 words.
```

---

### Add an LLM-generated summary comment to a ticket

Useful after a long discussion to leave a "TL;DR" for future readers.

```
Read ticket {KEY} and summarise the discussion, then post the summary as a comment.

Steps:
1. `jora issue get {KEY} --json` — understand the ticket
2. `jora issue comment {KEY} --json` — read all comments
3. Write a "Discussion Summary" in this format:
   **Summary** (2–3 sentences on what was discussed and decided)
   **Decision** (what was agreed, or "No decision reached")
   **Next steps** (bullet list, or "None identified")
   _Summary generated on {TODAY'S DATE}_
4. Post it: `jora issue comment {KEY} --body "..." --json`

Show me the draft summary before posting so I can approve or edit it.
```

---

### Generate a release summary for stakeholders

Turn a list of completed tickets into a readable update.

```
Generate a release summary for {PROJECT} version {RELEASE}.

Fetch all done tickets in this release:
`jora search "project = {PROJECT} AND fixVersion = {RELEASE} AND status = Done" --json`

Group them by issue type (Bug, Story, Task, etc.) and write a concise release summary
in this format:

## {PROJECT} {RELEASE} — Release Summary

**What's new**
(bullet list of Stories and Tasks, one line each)

**Bug fixes**
(bullet list of Bugs resolved)

**Stats**
- X issues completed
- Total estimated: Yh / Total logged: Zh

Keep each bullet to one line. Use plain language, not ticket keys, unless the key adds context.
```

---

## Ticket management

### Create tickets from meeting notes

Turn raw meeting output into structured Jira tickets.

```
I have notes from a meeting. Extract action items and create Jira tickets for each one.

Meeting notes:
---
{PASTE MEETING NOTES HERE}
---

For each distinct action item:
1. Decide the appropriate issue type (Bug, Task, Story, Improvement)
2. Write a clear, specific summary (imperative verb, e.g. "Add rate limiting to login endpoint")
3. Write a one-paragraph description with context from the notes
4. Assign to me if the action item mentions me, leave unassigned otherwise

Show me the proposed tickets as a list before creating any. Once I confirm, create them
one at a time using:
`jora issue create --project {PROJECT} --summary "..." --type {TYPE} --description "..." --json`

Report each created ticket key after creation.
```

---

### Find duplicate or related tickets before creating a new one

Avoid cluttering the board with tickets that already exist.

```
Before I create a new ticket, search for existing ones that might be related.

My intended ticket: "{DESCRIPTION OF WHAT YOU WANT TO CREATE}"
Project: {PROJECT}

Search for related issues using several JQL queries:
1. Keywords from the summary: `jora search "project = {PROJECT} AND text ~ '{KEYWORD1}'" --json --compact`
2. Status is not Done (avoid resolved duplicates): add `AND status != Done` to each search

Review the results and tell me:
- Any tickets that look like exact duplicates (I should not create a new one)
- Any tickets that are closely related (I should link or reference them in my new ticket)
- Whether it's safe to proceed with creating a new ticket

If I should proceed, help me draft and create the ticket.
```

---

### Triage unassigned tickets

Quickly process a backlog of unassigned work.

```
Help me triage unassigned tickets in project {PROJECT}.

Fetch them with:
`jora search "project = {PROJECT} AND assignee is EMPTY AND status = Open" --json --max 20`

For each ticket, fetch full details and present a one-line summary:
`{KEY} | {TYPE} | {PRIORITY} | {SUMMARY} | Recommended action`

Recommended actions to suggest:
- **Assign to me** — if it's in my area of work
- **Needs more info** — if the description is unclear or missing
- **Duplicate** — if it sounds like something already tracked
- **Backlog** — if it's valid but not urgent

After I review the list, execute my decisions: assign tickets to me with
`jora issue update {KEY} --assignee me --json`, or add a clarifying comment where needed.
```

---

### Flag stale in-progress tickets

Surface tickets that have been "in progress" without any activity.

```
Find tickets in project {PROJECT} that have been In Progress for a long time without updates.

Use: `jora search "project = {PROJECT} AND status = 'In Progress' AND updated <= -{DAYS}d" --json`

For each ticket, check:
- Is there any time logged? (time_tracking.time_spent_seconds > 0)
- Is there a remaining estimate still set?

Group results into:
1. **Stale with no time logged** — likely forgotten or blocked
2. **Active but over-estimate** — time spent exceeds original estimate

For group 1, draft a comment asking for a status update, and show it to me before posting.
For group 2, suggest an updated estimate based on time already spent.
```

---

## Code review & PR workflows

### Log review time and summarise a PR discussion

After finishing a code review on a related ticket.

```
I just finished reviewing the PR for ticket {KEY}. It took me about {TIME}.

1. Log my review time: `jora worklog add {KEY} --time {TIME} --comment "Code review" --json`
2. Fetch the current ticket comments: `jora issue comment {KEY} --json`
3. Summarise any review decisions or change requests from the comments in 3–5 bullets.
4. If there are open questions in the comments that haven't been answered, list them.

Show the worklog confirmation and the summary.
```
