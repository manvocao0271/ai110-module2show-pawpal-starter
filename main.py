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
# Tasks for Kitty
# ---------------------------------------------------------------------------
today = datetime.now().date()

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
    task_id=3,
    title="Evening Playtime",
    category="enrichment",
    due_datetime=datetime(today.year, today.month, today.day, 18, 0),
    duration=20,
    priority=2,
    frequency="daily",
    description="Feather wand or laser pointer session",
))

# ---------------------------------------------------------------------------
# Tasks for Doggo
# ---------------------------------------------------------------------------
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
    task_id=6,
    title="Evening Grooming",
    category="grooming",
    due_datetime=datetime(today.year, today.month, today.day, 19, 0),
    duration=25,
    priority=3,
    frequency="weekly",
    description="Brush coat and check ears",
))

# ---------------------------------------------------------------------------
# Register pets with owner
# ---------------------------------------------------------------------------
owner.add_pet(cat)
owner.add_pet(dog)

# ---------------------------------------------------------------------------
# Build schedule and print Today's Schedule
# ---------------------------------------------------------------------------
schedule = Schedule(owner)
AVAILABLE_MINUTES = 180
summary = schedule.daily_summary(available_minutes=AVAILABLE_MINUTES)
plan = summary["daily_plan"]

CATEGORY_ICON = {
    "feeding":     "[FEED]",
    "walking":     "[WALK]",
    "medication":  "[MED] ",
    "appointment": "[APPT]",
    "grooming":    "[GRMG]",
    "enrichment":  "[PLAY]",
    "training":    "[TRN] ",
    "other":       "[TASK]",
}
PRIORITY_LABEL = {1: "Low", 2: "Low+", 3: "Medium", 4: "High", 5: "Critical"}

# -- find which pet owns each task ------------------------------------------
task_to_pet: dict[int, str] = {}
for pet in owner.pets:
    for t in pet.tasks:
        task_to_pet[t.task_id] = pet.name

# ---------------------------------------------------------------------------
# Print
# ---------------------------------------------------------------------------
DIVIDER  = "=" * 56
SUBDIV   = "-" * 56

print(DIVIDER)
print(f"  PAWPAL+  |  TODAY'S SCHEDULE")
print(f"  {summary['date']}")
print(f"  Owner : {summary['owner']}")
print(f"  Pets  : {', '.join(summary['pets'])}")
print(DIVIDER)
print(f"  Time budget : {summary['available_minutes']} min available  |  "
      f"{summary['planned_minutes']} min planned")
print(f"  Tasks       : {summary['task_counts']['total']} total  |  "
      f"{summary['task_counts']['pending']} pending  |  "
      f"{summary['task_counts']['overdue']} overdue")
print(SUBDIV)

if not plan:
    print("  No tasks scheduled for today.")
else:
    for i, task in enumerate(plan, start=1):
        icon     = CATEGORY_ICON.get(task.category, "📋")
        priority = PRIORITY_LABEL[task.priority]
        pet_name = task_to_pet.get(task.task_id, "?")
        overdue_flag = "  *** OVERDUE ***" if task.is_overdue() else ""
        print(f"  {i}. {icon}  {task.due_datetime.strftime('%I:%M %p')}  |  "
              f"{task.title} ({pet_name}){overdue_flag}")
        print(f"       Priority: {priority}  |  Duration: {task.duration} min  |  "
              f"Category: {task.category}")
        if task.description:
            print(f"       {task.description}")
        if i < len(plan):
            print()

print(SUBDIV)
print(f"  Total planned time : {summary['planned_minutes']} / "
      f"{summary['available_minutes']} min")
print(DIVIDER)
