from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ---------------------------------------------------------------------------
# Task — atomic unit of pet care work
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: int
    title: str
    category: str          # e.g. "feeding", "walking", "medication", "appointment"
    due_datetime: datetime
    priority: int          # 1 (low) – 5 (critical)
    description: str = ""
    notes: str = ""
    is_completed: bool = False
    schedule_id: Optional[int] = None

    def complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def prioritize(self, new_priority: int) -> None:
        """Update the priority level (1–5)."""
        self.priority = new_priority

    def is_overdue(self) -> bool:
        """Return True if the task is past its due time and not yet completed."""
        return not self.is_completed and datetime.now() > self.due_datetime


# ---------------------------------------------------------------------------
# Pet — a single animal owned by a User
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: int
    name: str
    species: str           # e.g. "dog", "cat", "rabbit"
    breed: str
    age: int               # years
    weight: float          # kg
    medical_notes: str = ""
    schedules: List[Schedule] = field(default_factory=list)

    def add_schedule(self, schedule: Schedule) -> None:
        """Attach a schedule to this pet."""
        self.schedules.append(schedule)

    def get_upcoming_tasks(self) -> List[Task]:
        """Return all incomplete tasks across every schedule, sorted by due time."""
        tasks = [
            task
            for schedule in self.schedules
            for task in schedule.tasks
            if not task.is_completed
        ]
        return sorted(tasks, key=lambda t: t.due_datetime)

    def update_profile(self, **kwargs) -> None:
        """Update any profile field by keyword (e.g. update_profile(weight=12.5))."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


# ---------------------------------------------------------------------------
# Schedule — a named collection of tasks for one pet
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(
        self,
        schedule_id: int,
        title: str,
        pet_id: int,
        start_date: datetime,
        end_date: datetime,
        recurrence: str = "none",   # "none" | "daily" | "weekly" | "monthly"
    ) -> None:
        self.schedule_id = schedule_id
        self.title = title
        self.pet_id = pet_id
        self.start_date = start_date
        self.end_date = end_date
        self.recurrence = recurrence
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task and stamp it with this schedule's id."""
        task.schedule_id = self.schedule_id
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task by id."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted highest priority first, then soonest due."""
        return sorted(self.tasks, key=lambda t: (-t.priority, t.due_datetime))

    def get_overdue_tasks(self) -> List[Task]:
        """Return all overdue tasks in this schedule."""
        return [t for t in self.tasks if t.is_overdue()]


# ---------------------------------------------------------------------------
# User — the pet owner
# ---------------------------------------------------------------------------

class User:
    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        phone: str = "",
    ) -> None:
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: List[Pet] = []

    def register(self) -> None:
        """Placeholder for account creation logic."""
        pass

    def login(self) -> None:
        """Placeholder for authentication logic."""
        pass

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this user's profile."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by id."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def view_schedule(self) -> List[Task]:
        """Return all upcoming tasks across every owned pet, sorted by due time."""
        tasks = [
            task
            for pet in self.pets
            for task in pet.get_upcoming_tasks()
        ]
        return sorted(tasks, key=lambda t: t.due_datetime)