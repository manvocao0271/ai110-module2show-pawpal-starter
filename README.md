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
