import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session-state bootstrap ──────────────────────────────────────────────────
# Streamlit reruns the whole script on every interaction, so we keep our
# objects in st.session_state (the "vault") to avoid resetting them.
if "owner" not in st.session_state:
    st.session_state.owner = None          # Owner instance
if "pet" not in st.session_state:
    st.session_state.pet = None            # Pet instance
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None      # Scheduler instance

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
    # Reset downstream objects when owner changes
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
        st.session_state.owner.add_pet(pet)   # register under owner
        st.session_state.pet = pet            # keep a direct reference
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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        category = st.text_input("Category", value="exercise")

    is_required = st.checkbox("Required task (must be scheduled)")

    if st.button("Add task"):
        task = Task(task_title, int(duration), priority, category, is_required)
        st.session_state.pet.add_task(task)        # attach to pet
        st.session_state.scheduler.add_task(task)  # register with scheduler
        st.success(f"Task '{task_title}' added.")

    # Display current tasks
    all_tasks = st.session_state.scheduler.tasks
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "Title": t.title,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Required": t.is_required,
                }
                for t in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

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
                        "Duration (min)": t.duration,
                        "Priority": t.priority,
                        "Required": t.is_required,
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
