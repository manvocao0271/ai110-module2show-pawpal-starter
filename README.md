# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

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

## Smarter Scheduling

The `Schedule` class in `pawpal_system.py` extends the core daily planner with three features:

### Sort by time
`Schedule.sort_by_time()` returns all pending tasks ordered by their `"HH:MM"` due time using a `sorted()` lambda key. Pass `include_completed=True` to include finished tasks in the result.

```python
schedule.sort_by_time()                      # pending only
schedule.sort_by_time(include_completed=True) # all tasks
```

### Filter tasks
`Schedule.filter_tasks()` narrows the task list by completion status, pet name, or both. Both parameters are optional; omitting them returns every task sorted by due time.

```python
schedule.filter_tasks(completed=False)              # pending only
schedule.filter_tasks(pet_name="Kitty")             # one pet, any status
schedule.filter_tasks(completed=True, pet_name="Doggo")  # completed + pet
```

### Conflict detection
`Schedule.detect_conflicts()` finds every pair of pending tasks whose execution windows overlap — within the same pet or across different pets. It returns plain warning strings and never raises an exception.

```python
warnings = schedule.detect_conflicts()
for w in warnings:
    print(w)
# CONFLICT: 'Flea Medication' (Kitty, 12:00 PM–12:05 PM) overlaps with
#           'Midday Brush' (Kitty, 12:03 PM–12:13 PM)
```

The algorithm sorts tasks by start time first so the inner comparison loop can break as soon as a candidate starts after the current task ends — conflict-free schedules pay only the sort cost.

### Auto-scheduling recurring tasks
`Schedule.complete_task()` marks a task done and, for `"daily"` and `"weekly"` tasks, automatically creates a fresh pending instance for the next occurrence using `timedelta`. The completed task is kept as a historical record.

| Frequency | Next due |
|-----------|----------|
| `daily`   | `due_datetime + 1 day` |
| `weekly`  | `due_datetime + 7 days` |
| `once` / `monthly` | no new instance created |

---

```mermaid
classDiagram
    class User {
        +int user_id
        +str name
        +str email
        +str phone
        +List~Pet~ pets
        +register()
        +login()
        +add_pet(pet: Pet)
        +remove_pet(pet_id: int)
        +view_schedule()
    }

    class Pet {
        +int pet_id
        +str name
        +str species
        +str breed
        +int age
        +float weight
        +str medical_notes
        +List~Schedule~ schedules
        +add_schedule(schedule: Schedule)
        +get_upcoming_tasks()
        +update_profile()
    }

    class Schedule {
        +int schedule_id
        +str title
        +datetime start_date
        +datetime end_date
        +str recurrence
        +List~Task~ tasks
        +Pet pet
        +int pet_id
        +add_task(task: Task)
        +remove_task(task_id: int)
        +get_tasks_by_priority()
    }

    class Task {
        +int task_id
        +str title
        +str category
        +str description
        +datetime due_datetime
        +int priority
        +bool is_completed
        +str notes
        +int schedule_id
        +complete()
        +prioritize()
        +is_overdue()
    }

    User "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Schedule : has
    Schedule "0..*" --> "1" Pet : belongs to
    Schedule "1" --> "1..*" Task : contains

```
