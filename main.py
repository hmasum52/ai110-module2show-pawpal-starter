from pawpal_system import Owner, Pet, Task, Scheduler

# --- Owner ---
owner = Owner(name="Alex", available_minutes=90)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", age=3, notes="Loves fetch")
whiskers = Pet(name="Whiskers", species="Cat", age=5, notes="Indoor cat, shy")
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Tasks for Buddy (Dog) ---
buddy_walk     = Task("Morning Walk",   duration=20, priority="high",   category="exercise",  is_required=True)
buddy_feed     = Task("Feeding",        duration=10, priority="high",   category="nutrition", is_required=True)
buddy_playtime = Task("Playtime",       duration=30, priority="medium", category="exercise")

for task in [buddy_walk, buddy_feed, buddy_playtime]:
    buddy.add_task(task)

# --- Tasks for Whiskers (Cat) ---
whiskers_feed    = Task("Feeding",       duration=5,  priority="high",   category="nutrition", is_required=True)
whiskers_groom   = Task("Grooming",      duration=15, priority="medium", category="hygiene")
whiskers_playtime = Task("Laser Pointer", duration=10, priority="low",   category="exercise")

for task in [whiskers_feed, whiskers_groom, whiskers_playtime]:
    whiskers.add_task(task)

# --- Schedulers (one per pet) ---
buddy_scheduler    = Scheduler(owner=owner, pet=buddy)
whiskers_scheduler = Scheduler(owner=owner, pet=whiskers)

for task in buddy.tasks:
    buddy_scheduler.add_task(task)

for task in whiskers.tasks:
    whiskers_scheduler.add_task(task)

# --- Today's Schedule ---
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
