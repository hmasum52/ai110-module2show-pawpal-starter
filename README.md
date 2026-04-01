# PawPal+

**PawPal+** is a Streamlit app that helps a pet owner plan and schedule daily care tasks for their pet — handling priorities, time constraints, recurring routines, and conflict detection automatically.

---

## Features

### Owner & Pet Profiles
Set your name, daily time budget (in minutes), and pet details (name, species, age, notes). The scheduler reads the budget directly from the owner profile, so updating your availability is instantly reflected in the next generated plan.

### Priority-Based Scheduling
Tasks are ranked by a three-tier priority system (`low / medium / high`). Required tasks (e.g., medication) are always scheduled first regardless of budget. Optional tasks then fill remaining time in descending priority order — the plan always maximizes care value within the available time.

### Chronological Sorting
The `sort_by_time()` algorithm separates tasks into timed (those with an `HH:MM` start time) and untimed groups, sorts the timed group lexicographically (zero-padded `HH:MM` strings sort correctly as plain strings), then appends untimed tasks at the end. The task table always displays in chronological order.

### Conflict Detection
`detect_conflicts()` checks every pair of pending timed tasks using an interval overlap formula — `A.start < B.end AND B.start < A.end` — and surfaces a warning for each overlap. Completed tasks are excluded so already-done work never triggers false positives. Cross-pet conflicts (two pets owned by the same owner with overlapping tasks) are caught by a separate `detect_cross_pet_conflicts()` function.

### Daily & Weekly Recurrence
Tasks can be marked `daily` or `weekly`. Completing a recurring task via `mark_task_complete()` automatically appends a fresh copy with `due_date` advanced by the correct `timedelta` (1 day or 7 days). The completed original is preserved in history; the new occurrence appears immediately in the pending task list.

### Pending / Completed Filtering
`filter_tasks(status, pet_name)` returns only the tasks matching the requested status and pet. The UI uses this to populate the "Mark Complete" dropdown with only pending tasks, keeping the interface clean as the day progresses.

### Daily Plan with Reasoning
`generate_plan()` returns a `DailyPlan` containing scheduled tasks, skipped tasks, total duration, and a human-readable reasoning list that explains every scheduling decision — why each task was included or skipped.

---

## 📸 Demo

<a href="/course_images/ai110/ui.png" target="_blank"><img src='/course_images/ai110/ui.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
