from pawpal_system import Owner, Pet, Task, Scheduler, detect_cross_pet_conflicts

# --- Owner ---
owner = Owner(name="Alex", available_minutes=90)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", age=3, notes="Loves fetch")
whiskers = Pet(name="Whiskers", species="Cat", age=5, notes="Indoor cat, shy")
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Tasks for Buddy (Dog) — added OUT OF ORDER intentionally ---
# frequency="daily" / "weekly" tasks will auto-schedule their next occurrence
# when marked complete via Scheduler.mark_task_complete()
buddy_walk     = Task("Morning Walk",   duration=20, priority="high",   category="exercise",  is_required=True,  time="07:00", frequency="daily")
buddy_feed     = Task("Feeding",        duration=10, priority="high",   category="nutrition", is_required=True,  time="08:30", frequency="daily")
buddy_playtime = Task("Playtime",       duration=30, priority="medium", category="exercise",                     time="14:00", frequency="weekly")
buddy_groom    = Task("Brushing",       duration=10, priority="low",    category="hygiene",                      time="09:15")

# Add in scrambled time order to prove sorting works
for task in [buddy_playtime, buddy_groom, buddy_walk, buddy_feed]:
    buddy.add_task(task)
    buddy_scheduler_ref = None  # placeholder — scheduler built below

# --- Tasks for Whiskers (Cat) — also added out of order ---
whiskers_feed     = Task("Feeding",       duration=5,  priority="high",   category="nutrition", is_required=True,  time="08:00")
whiskers_groom    = Task("Grooming",      duration=15, priority="medium", category="hygiene",                      time="10:30")
whiskers_playtime = Task("Laser Pointer", duration=10, priority="low",    category="exercise",                     time="09:00")

for task in [whiskers_groom, whiskers_playtime, whiskers_feed]:
    whiskers.add_task(task)

# --- Schedulers (one per pet) ---
buddy_scheduler    = Scheduler(owner=owner, pet=buddy)
whiskers_scheduler = Scheduler(owner=owner, pet=whiskers)

for task in buddy.tasks:
    buddy_scheduler.add_task(task)

for task in whiskers.tasks:
    whiskers_scheduler.add_task(task)

# ======================================================================
# TODAY'S SCHEDULE  (original plan)
# ======================================================================
print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)
print(f"Owner : {owner.name}  |  Time budget: {owner.available_minutes} min")
print()

for pet, scheduler in [(buddy, buddy_scheduler), (whiskers, whiskers_scheduler)]:
    plan = scheduler.generate_plan()
    print(f"--- {pet.name} ({pet.species}) ---")
    print(plan.display())
    print()
    print("Reasoning:")
    print(plan.get_reasoning())
    print()

print("=" * 40)
print(f"Total tasks across all pets: {len(owner.get_all_tasks())}")

# ======================================================================
# DEMO — sort_by_time()
# ======================================================================
print()
print("=" * 40)
print("  SORTED BY TIME")
print("=" * 40)

for pet, scheduler in [(buddy, buddy_scheduler), (whiskers, whiskers_scheduler)]:
    print(f"\n--- {pet.name}'s tasks (time order) ---")
    for task in scheduler.sort_by_time():
        time_label = task.time if task.time else "unscheduled"
        print(f"  {time_label}  {task.title} ({task.duration}min, {task.priority})")

# ======================================================================
# DEMO — filter_tasks()
# ======================================================================
print()
print("=" * 40)
print("  FILTER: pending tasks for Buddy")
print("=" * 40)
pending = buddy_scheduler.filter_tasks(status="pending", pet_name="Buddy")
if pending:
    for task in pending:
        print(f"  [ ] {task.title} ({task.duration}min, {task.priority})")
else:
    print("  No pending tasks.")

# Mark directly on the task object (no recurrence side-effect) just to show the filter
buddy_walk.mark_complete()

print()
print("=" * 40)
print("  FILTER: completed tasks for Buddy")
print("=" * 40)
completed = buddy_scheduler.filter_tasks(status="completed", pet_name="Buddy")
if completed:
    for task in completed:
        print(f"  [x] {task.title} ({task.duration}min, {task.priority})")
else:
    print("  No completed tasks.")

print()
print("=" * 40)
print("  FILTER: wrong pet name (should be empty)")
print("=" * 40)
wrong_pet = buddy_scheduler.filter_tasks(pet_name="Whiskers")
print(f"  Tasks returned: {len(wrong_pet)}  (expected 0)")

# ======================================================================
# DEMO — Recurring tasks via mark_task_complete()
# ======================================================================
print()
print("=" * 40)
print("  RECURRING TASKS")
print("=" * 40)

# Show Buddy's tasks BEFORE completing any recurring ones
print("\nBefore completing recurring tasks:")
for task in buddy_scheduler.tasks:
    freq = f"  [{task.frequency}]" if task.frequency else ""
    due  = f"  due:{task.due_date}" if task.due_date else ""
    done = "  [done]" if task.completed else ""
    print(f"  {task.title}{freq}{due}{done}")

# Complete "Morning Walk" (daily) — should spawn next occurrence at today + 1 day
next_walk = buddy_scheduler.mark_task_complete("Morning Walk")
print(f"\n  Completed 'Morning Walk'  ->  next occurrence: {next_walk}")

# Complete "Playtime" (weekly) — should spawn next occurrence at today + 7 days
next_play = buddy_scheduler.mark_task_complete("Playtime")
print(f"  Completed 'Playtime'      ->  next occurrence: {next_play}")

# Complete "Brushing" (no frequency) — no new task created
result = buddy_scheduler.mark_task_complete("Brushing")
print(f"  Completed 'Brushing'      ->  next occurrence: {result}  (one-off, no recurrence)")

# Show Buddy's tasks AFTER — originals marked done, new occurrences appended
print("\nAfter completing recurring tasks:")
for task in buddy_scheduler.tasks:
    freq = f"  [{task.frequency}]" if task.frequency else ""
    due  = f"  due:{task.due_date}" if task.due_date else ""
    done = "  [done]" if task.completed else ""
    print(f"  {task.title}{freq}{due}{done}")

# ======================================================================
# DEMO — detect_conflicts()  (same-pet and cross-pet)
# ======================================================================
print()
print("=" * 40)
print("  CONFLICT DETECTION")
print("=" * 40)

# -- Same-pet conflict: add a second task for Buddy at 07:00 (identical to Morning Walk) --
buddy_bath = Task("Bath Time", duration=15, priority="medium", category="hygiene", time="07:00")
buddy_scheduler.add_task(buddy_bath)

print("\n[Same-pet] Buddy's scheduler - pending tasks with a time set:")
for t in [t for t in buddy_scheduler.tasks if t.time and not t.completed]:
    print(f"  {t.time}  {t.title} ({t.duration}min)")

print("\n[Same-pet] Running detect_conflicts() on Buddy's scheduler:")
same_pet_warnings = buddy_scheduler.detect_conflicts()
if same_pet_warnings:
    for w in same_pet_warnings:
        print(f"  WARNING: {w}")
else:
    print("  No conflicts found.")

# -- Cross-pet conflict: add a task for Whiskers also at 07:00 --
whiskers_bath = Task("Bath Time", duration=10, priority="low", category="hygiene", time="07:00")
whiskers_scheduler.add_task(whiskers_bath)

print("\n[Cross-pet] Running detect_cross_pet_conflicts() across all schedulers:")
cross_warnings = detect_cross_pet_conflicts([buddy_scheduler, whiskers_scheduler])
if cross_warnings:
    for w in cross_warnings:
        print(f"  WARNING: {w}")
else:
    print("  No cross-pet conflicts found.")

print()
print("(No crashes - conflict detection returns warnings only)")
