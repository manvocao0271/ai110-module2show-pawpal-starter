import streamlit as st
from datetime import datetime, time
from pawpal_system import Task, Pet, User, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialisation — runs once per browser session
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None          # created after owner form submit

if "schedule" not in st.session_state:
    st.session_state.schedule = None      # created after user exists

if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.caption("Smart pet care management — plan your pet's day in minutes.")
st.divider()

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.subheader("1. Owner Info")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name  = st.text_input("Name",  placeholder="e.g. Kevin")
        owner_email = st.text_input("Email", placeholder="e.g. kevin@email.com")
    with col2:
        owner_phone = st.text_input("Phone", placeholder="e.g. 555-1234")
    submitted_owner = st.form_submit_button("Save Owner")

if submitted_owner:
    if not owner_name.strip():
        st.error("Owner name is required.")
    else:
        user_id = 1
        st.session_state.user = User(user_id, owner_name.strip(), owner_email.strip(), owner_phone.strip())
        st.session_state.schedule = Schedule(st.session_state.user)
        st.success(f"Owner '{owner_name}' saved!")

if st.session_state.user:
    st.info(f"Current owner: **{st.session_state.user.name}** | {len(st.session_state.user.pets)} pet(s) registered")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------
st.subheader("2. Add a Pet")

if st.session_state.user is None:
    st.warning("Save an owner first before adding pets.")
else:
    with st.form("pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_name    = st.text_input("Pet name",    placeholder="e.g. Kitty")
            species     = st.selectbox("Species",      ["cat", "dog", "rabbit", "bird", "other"])
            breed       = st.text_input("Breed",       placeholder="e.g. Orange Tabby")
        with col2:
            age         = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
            weight      = st.number_input("Weight (kg)", min_value=0.1, max_value=200.0, value=4.0, step=0.1)
            medical_notes = st.text_area("Medical notes", placeholder="Allergies, conditions, etc.", height=80)
        submitted_pet = st.form_submit_button("Add Pet")

    if submitted_pet:
        if not pet_name.strip():
            st.error("Pet name is required.")
        else:
            new_pet = Pet(
                pet_id=st.session_state.next_pet_id,
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age),
                weight=float(weight),
                medical_notes=medical_notes.strip(),
            )
            st.session_state.user.add_pet(new_pet)       # <-- User.add_pet()
            st.session_state.next_pet_id += 1
            st.success(f"'{new_pet.name}' added to {st.session_state.user.name}'s profile!")

    # -- pet roster display --------------------------------------------------
    pets = st.session_state.user.pets
    if pets:
        st.markdown("**Registered Pets**")
        for pet in pets:
            with st.expander(f"{pet.name}  —  {pet.species} / {pet.breed}  |  {len(pet.tasks)} task(s)"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Age",    f"{pet.age} yr")
                col2.metric("Weight", f"{pet.weight} kg")
                col3.metric("Tasks",  len(pet.tasks))
                if pet.medical_notes:
                    st.caption(f"Medical: {pet.medical_notes}")
    else:
        st.info("No pets yet. Fill out the form above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Schedule a task
# ---------------------------------------------------------------------------
st.subheader("3. Schedule a Task")

PRIORITY_MAP  = {"Low (1)": 1, "Low+ (2)": 2, "Medium (3)": 3, "High (4)": 4, "Critical (5)": 5}
CATEGORY_OPTS = ["feeding", "walking", "medication", "appointment", "grooming", "training", "enrichment", "other"]
FREQ_OPTS     = ["once", "daily", "weekly", "monthly"]

user = st.session_state.user
if user is None or not user.pets:
    st.warning("Add an owner and at least one pet before scheduling tasks.")
else:
    pet_names   = [p.name for p in user.pets]
    pet_lookup  = {p.name: p for p in user.pets}

    with st.form("task_form"):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)

        col1, col2 = st.columns(2)
        with col1:
            task_title    = st.text_input("Task title",       placeholder="e.g. Morning walk")
            category      = st.selectbox("Category",          CATEGORY_OPTS)
            priority_label = st.selectbox("Priority",         list(PRIORITY_MAP.keys()), index=2)
        with col2:
            due_date      = st.date_input("Due date",         value=datetime.today())
            due_time      = st.time_input("Due time",         value=time(8, 0))
            duration      = st.number_input("Duration (min)", min_value=1, max_value=480, value=20)

        frequency    = st.selectbox("Frequency", FREQ_OPTS)
        description  = st.text_input("Description", placeholder="Optional details")
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        if not task_title.strip():
            st.error("Task title is required.")
        else:
            due_dt   = datetime.combine(due_date, due_time)
            priority = PRIORITY_MAP[priority_label]
            target_pet = pet_lookup[selected_pet_name]

            new_task = Task(
                task_id=st.session_state.next_task_id,
                title=task_title.strip(),
                category=category,
                due_datetime=due_dt,
                duration=int(duration),
                priority=priority,
                frequency=frequency,
                description=description.strip(),
            )
            target_pet.add_task(new_task)                # <-- Pet.add_task()
            st.session_state.next_task_id += 1
            st.success(f"Task '{new_task.title}' added to {target_pet.name}'s schedule!")

    # -- task list per pet ---------------------------------------------------
    for pet in user.pets:
        pending = pet.get_pending_tasks()                # <-- Pet.get_pending_tasks()
        if pending:
            st.markdown(f"**{pet.name}'s pending tasks**")
            rows = []
            for t in pending:
                rows.append({
                    "Title":    t.title,
                    "Category": t.category,
                    "Due":      t.due_datetime.strftime("%b %d  %I:%M %p"),
                    "Duration": f"{t.duration} min",
                    "Priority": t.priority,
                    "Overdue":  "Yes" if t.is_overdue() else "No",
                })
            st.table(rows)

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate today's schedule
# ---------------------------------------------------------------------------
st.subheader("4. Generate Today's Schedule")

if user is None or not user.pets:
    st.warning("Add an owner, pets, and tasks first.")
else:
    available_minutes = st.slider("Available time today (minutes)", 30, 480, 120, step=15)

    if st.button("Generate Schedule"):
        if st.session_state.schedule is None:
            st.session_state.schedule = Schedule(user)
        sched: Schedule = st.session_state.schedule
        summary = sched.daily_summary(available_minutes=available_minutes)  # <-- Schedule.daily_summary()
        plan    = summary["daily_plan"]

        st.markdown(f"### Today's Plan — {summary['date']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Planned",   f"{summary['planned_minutes']} min")
        col2.metric("Budget",    f"{summary['available_minutes']} min")
        col3.metric("Overdue",   summary["overdue_count"])
        col4.metric("Upcoming",  summary["upcoming_count"])

        if not plan:
            st.info("No tasks due today.")
        else:
            for i, task in enumerate(plan, 1):
                overdue_badge = " 🔴 OVERDUE" if task.is_overdue() else ""
                with st.expander(
                    f"{i}. [{task.priority}] {task.due_datetime.strftime('%I:%M %p')}  |  "
                    f"{task.title}{overdue_badge}"
                ):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Duration", f"{task.duration} min")
                    col2.metric("Category", task.category)
                    col3.metric("Priority", task.priority)
                    if task.description:
                        st.caption(task.description)
