from datetime import datetime
from pawpal_system import Task, Pet, User, Schedule

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
owner = User(12345, "Kevin", "kevin@gmail.com", "123456789")

# ---------------------------------------------------------------------------
# Pets  (unique pet_ids)
# ---------------------------------------------------------------------------
cat = Pet(11111, "Kitty", "Cat", "Orange Tabby", 6, 10, owner.user_id)
dog = Pet(22222, "Doggo", "Dog", "Husky", 4, 35, owner.user_id)

# ---------------------------------------------------------------------------
# Tasks added intentionally OUT OF ORDER to demonstrate sort_by_time()
# ---------------------------------------------------------------------------
today = datetime.now().date()

# Kitty — added latest-to-earliest
cat.add_task(Task(
    task_id=3,
    title="Evening Playtime",
    category="enrichment",
    due_datetime=datetime(today.year, today.month, today.day, 18, 0),
    duration=20,
    priority=2,
    frequency="daily",
    description="Feather wand or laser pointer session",
))

cat.add_task(Task(
    task_id=2,
    title="Flea Medication",
    category="medication",
    due_datetime=datetime(today.year, today.month, today.day, 12, 0),
    duration=5,
    priority=5,
    frequency="monthly",
    description="Apply topical flea treatment between shoulder blades",
))

cat.add_task(Task(
    task_id=1,
    title="Morning Feeding",
    category="feeding",
    due_datetime=datetime(today.year, today.month, today.day, 7, 30),
    duration=10,
    priority=4,
    frequency="daily",
    description="Half cup dry food + fresh water",
))

# Doggo — added latest-to-earliest
dog.add_task(Task(
    task_id=6,
    title="Evening Grooming",
    category="grooming",
    due_datetime=datetime(today.year, today.month, today.day, 19, 0),
    duration=25,
    priority=3,
    frequency="weekly",
    description="Brush coat and check ears",
))

dog.add_task(Task(
    task_id=5,
    title="Vet Appointment",
    category="appointment",
    due_datetime=datetime(today.year, today.month, today.day, 14, 0),
    duration=60,
    priority=5,
    frequency="once",
    description="Annual check-up and booster shots",
))

dog.add_task(Task(
    task_id=4,
    title="Morning Walk",
    category="walking",
    due_datetime=datetime(today.year, today.month, today.day, 8, 0),
    duration=30,
    priority=4,
    frequency="daily",
    description="30-minute neighbourhood walk",
))

# ---------------------------------------------------------------------------
# Deliberate conflicts
#   Conflict 1 (same pet):      Kitty's Flea Medication starts at 12:00 (5 min)
#                                Kitty's Midday Brush    starts at 12:03 (10 min) → overlaps
#   Conflict 2 (cross-pet):     Doggo's Morning Walk starts at 08:00 (30 min)
#                                Kitty's Breakfast Check starts at 08:15 (15 min) → overlaps
# ---------------------------------------------------------------------------
cat.add_task(Task(
    task_id=7,
    title="Midday Brush",
    category="grooming",
    due_datetime=datetime(today.year, today.month, today.day, 12, 3),
    duration=10,
    priority=2,
    frequency="daily",
    description="Quick brush — starts 3 min into Flea Medication window",
))

cat.add_task(Task(
    task_id=8,
    title="Breakfast Check",
    category="feeding",
    due_datetime=datetime(today.year, today.month, today.day, 8, 15),
    duration=15,
    priority=3,
    frequency="daily",
    description="Check food bowl — overlaps with Doggo's Morning Walk",
))

# Mark one task complete so filter_tasks(completed=...) has something to show
cat.get_task(1).complete()   # Morning Feeding is done

# ---------------------------------------------------------------------------
# Register pets with owner
# ---------------------------------------------------------------------------
owner.add_pet(cat)
owner.add_pet(dog)

# ---------------------------------------------------------------------------
# Build schedule
# ---------------------------------------------------------------------------
schedule = Schedule(owner)

PRIORITY_LABEL   = {1: "Low", 2: "Low+", 3: "Medium", 4: "High", 5: "Critical"}
CATEGORY_ICON    = {
    "feeding":     "[FEED]",
    "walking":     "[WALK]",
    "medication":  "[MED] ",
    "appointment": "[APPT]",
    "grooming":    "[GRMG]",
    "enrichment":  "[PLAY]",
    "training":    "[TRN] ",
    "other":       "[TASK]",
}

DIVIDER = "=" * 56
SUBDIV  = "-" * 56


def print_task_list(tasks, label):
    print(f"\n{DIVIDER}")
    print(f"  {label}  ({len(tasks)} task(s))")
    print(SUBDIV)
    if not tasks:
        print("  (none)")
    for task in tasks:
        icon   = CATEGORY_ICON.get(task.category, "[TASK]")
        pri    = PRIORITY_LABEL[task.priority]
        status = "done" if task.is_completed else "pending"
        print(f"  {icon}  {task.due_datetime.strftime('%I:%M %p')}  |  "
              f"{task.title}  [{pri}]  ({status})")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# 1. All tasks sorted by time — shows tasks interleaved across both pets
# ---------------------------------------------------------------------------
sorted_tasks = schedule.sort_by_time(include_completed=True)
print_task_list(sorted_tasks, "ALL TASKS — sorted by time (out-of-order input)")

# ---------------------------------------------------------------------------
# 2. filter_tasks: only pending tasks (completed=False)
# ---------------------------------------------------------------------------
pending = schedule.filter_tasks(completed=False)
print_task_list(pending, "FILTER — pending tasks only")

# ---------------------------------------------------------------------------
# 3. filter_tasks: only completed tasks (completed=True)
# ---------------------------------------------------------------------------
done = schedule.filter_tasks(completed=True)
print_task_list(done, "FILTER — completed tasks only")

# ---------------------------------------------------------------------------
# 4. filter_tasks: all tasks for Kitty (no completion filter)
# ---------------------------------------------------------------------------
kitty_tasks = schedule.filter_tasks(pet_name="Kitty")
print_task_list(kitty_tasks, "FILTER — Kitty's tasks (any status)")

# ---------------------------------------------------------------------------
# 5. filter_tasks: pending tasks for Doggo only
# ---------------------------------------------------------------------------
doggo_pending = schedule.filter_tasks(completed=False, pet_name="Doggo")
print_task_list(doggo_pending, "FILTER — Doggo's pending tasks")

# ---------------------------------------------------------------------------
# 6. Conflict detection
# ---------------------------------------------------------------------------
conflicts = schedule.detect_conflicts()
print(f"\n{DIVIDER}")
print(f"  CONFLICT DETECTION  ({len(conflicts)} conflict(s) found)")
print(SUBDIV)
if not conflicts:
    print("  No scheduling conflicts detected.")
else:
    for warning in conflicts:
        print(f"  !! {warning}")
print(DIVIDER)
