import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session-state bootstrap ──────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Step 1 – Owner setup ─────────────────────────────────────────────────────
st.subheader("Step 1: Owner")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input(
        "Available time today (minutes)", min_value=1, max_value=1440, value=60
    )

if st.button("Set owner"):
    st.session_state.owner = Owner(owner_name, int(available_minutes))
    st.session_state.pet = None
    st.session_state.scheduler = None
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min available.")

if st.session_state.owner:
    o = st.session_state.owner
    st.caption(f"Current owner: **{o.name}** — {o.available_minutes} min available")

st.divider()

# ── Step 2 – Pet setup ───────────────────────────────────────────────────────
st.subheader("Step 2: Add a Pet")

if st.session_state.owner is None:
    st.info("Set an owner first.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    pet_notes = st.text_input("Notes (optional)", value="")

    if st.button("Add pet"):
        pet = Pet(pet_name, species, int(pet_age), pet_notes)
        st.session_state.owner.add_pet(pet)
        st.session_state.pet = pet
        st.session_state.scheduler = Scheduler(st.session_state.owner, pet)
        st.success(f"Pet '{pet_name}' added and scheduler initialised.")

    if st.session_state.pet:
        p = st.session_state.pet
        profile = p.get_profile()
        st.caption(
            f"Current pet: **{profile['name']}** ({profile['species']}, age {profile['age']}) "
            f"— {profile['task_count']} task(s)"
        )

st.divider()

# ── Step 3 – Tasks ───────────────────────────────────────────────────────────
st.subheader("Step 3: Add Tasks")

if st.session_state.scheduler is None:
    st.info("Add a pet first.")
else:
    # Task input form
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.text_input("Category", value="exercise")

    col5, col6, col7 = st.columns(3)
    with col5:
        task_time = st.text_input("Start time (HH:MM, optional)", value="")
    with col6:
        frequency = st.selectbox("Frequency", ["none", "daily", "weekly"])
    with col7:
        is_required = st.checkbox("Required task")

    if st.button("Add task"):
        time_val = task_time.strip() if task_time.strip() else None
        freq_val = None if frequency == "none" else frequency
        task = Task(
            title=task_title,
            duration=int(duration),
            priority=priority,
            category=category,
            is_required=is_required,
            time=time_val,
            frequency=freq_val,
        )
        st.session_state.pet.add_task(task)
        st.session_state.scheduler.add_task(task)
        st.success(f"Task '{task_title}' added.")

    # ── Task display: sorted by time via Scheduler.sort_by_time() ────────────
    sched: Scheduler = st.session_state.scheduler
    sorted_tasks = sched.sort_by_time()

    if sorted_tasks:
        st.markdown("#### Tasks (sorted by start time)")
        st.table(
            [
                {
                    "Title": t.title,
                    "Start": t.time if t.time else "—",
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Frequency": t.frequency if t.frequency else "once",
                    "Required": "Yes" if t.is_required else "No",
                    "Status": "Done" if t.completed else "Pending",
                }
                for t in sorted_tasks
            ]
        )

        # ── Conflict warnings via Scheduler.detect_conflicts() ────────────────
        conflicts = sched.detect_conflicts()
        if conflicts:
            st.markdown("#### Scheduling Conflicts")
            for msg in conflicts:
                st.warning(msg)
        else:
            st.success("No time conflicts detected.")
    else:
        st.info("No tasks yet. Add one above.")

    st.divider()

    # ── Mark task complete ───────────────────────────────────────────────────
    st.markdown("#### Mark a Task Complete")

    pending = sched.filter_tasks(status="pending")
    if pending:
        pending_titles = [t.title for t in pending]
        selected_title = st.selectbox("Select task to complete", pending_titles)

        if st.button("Mark complete"):
            next_task = sched.mark_task_complete(selected_title)
            if next_task:
                st.success(
                    f"'{selected_title}' marked done. "
                    f"Next occurrence scheduled for {next_task.due_date}."
                )
            else:
                st.success(f"'{selected_title}' marked done.")
    else:
        st.info("No pending tasks.")

st.divider()

# ── Step 4 – Generate schedule ───────────────────────────────────────────────
st.subheader("Step 4: Build Schedule")

if st.session_state.scheduler is None:
    st.info("Add an owner, pet, and tasks first.")
elif not st.session_state.scheduler.tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        plan = st.session_state.scheduler.generate_plan()

        st.success(f"Schedule generated! Total time: {plan.total_duration} min")

        st.markdown("#### Scheduled tasks")
        if plan.scheduled_tasks:
            st.table(
                [
                    {
                        "Title": t.title,
                        "Start": t.time if t.time else "—",
                        "Duration (min)": t.duration,
                        "Priority": t.priority,
                        "Required": "Yes" if t.is_required else "No",
                    }
                    for t in plan.scheduled_tasks
                ]
            )
        else:
            st.warning("No tasks could be scheduled.")

        if plan.skipped_tasks:
            st.markdown("#### Skipped tasks")
            st.table(
                [
                    {
                        "Title": t.title,
                        "Duration (min)": t.duration,
                        "Priority": t.priority,
                    }
                    for t in plan.skipped_tasks
                ]
            )

        st.markdown("#### Reasoning")
        st.markdown(plan.get_reasoning())
