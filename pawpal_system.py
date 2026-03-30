from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Task — a singular pet care activity
# ---------------------------------------------------------------------------

VALID_CATEGORIES = {"feeding", "walking", "medication", "appointment", "grooming", "training", "enrichment", "other"}
VALID_FREQUENCIES = {"once", "daily", "weekly", "monthly"}

@dataclass
class Task:
    task_id: int
    title: str
    category: str           # one of VALID_CATEGORIES
    due_datetime: datetime
    duration: int           # estimated minutes to complete
    priority: int           # 1 (low) – 5 (critical)
    frequency: str = "once" # one of VALID_FREQUENCIES
    description: str = ""
    notes: str = ""
    is_completed: bool = False

    def __post_init__(self) -> None:
        """Validate category, frequency, priority, and duration on construction."""
        if self.category not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}")
        if not (1 <= self.priority <= 5):
            raise ValueError("priority must be between 1 and 5")
        if self.duration <= 0:
            raise ValueError("duration must be a positive number of minutes")

    # -- state changes -------------------------------------------------------

    def complete(self) -> None:
        """Mark the task as done."""
        self.is_completed = True

    def reset(self) -> None:
        """Un-complete a recurring task and advance its due date by one cycle."""
        if self.frequency == "once":
            raise ValueError("Cannot reset a one-time task")
        self.is_completed = False
        if self.frequency == "daily":
            self.due_datetime += timedelta(days=1)
        elif self.frequency == "weekly":
            self.due_datetime += timedelta(weeks=1)
        elif self.frequency == "monthly":
            # Advance by ~30 days; production code would use dateutil.relativedelta
            self.due_datetime += timedelta(days=30)

    def snooze(self, minutes: int) -> None:
        """Push the due time forward by the given number of minutes."""
        if minutes <= 0:
            raise ValueError("snooze minutes must be positive")
        self.due_datetime += timedelta(minutes=minutes)

    def update_priority(self, new_priority: int) -> None:
        """Change the priority (1–5)."""
        if not (1 <= new_priority <= 5):
            raise ValueError("priority must be between 1 and 5")
        self.priority = new_priority

    # -- queries -------------------------------------------------------------

    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """True if past due and not yet completed. Accepts an explicit 'now' for testability."""
        now = now or datetime.now()
        return not self.is_completed and now > self.due_datetime

    def is_due_today(self, reference: Optional[datetime] = None) -> bool:
        """True if the task falls on the same calendar day as reference (default: today)."""
        reference = reference or datetime.now()
        return self.due_datetime.date() == reference.date()

    def __repr__(self) -> str:
        """Return a compact string showing id, priority, title, category, duration, and status."""
        status = "done" if self.is_completed else ("OVERDUE" if self.is_overdue() else "pending")
        return (
            f"Task({self.task_id} | [{self.priority}] {self.title} "
            f"| {self.category} | {self.duration}min | {status})"
        )


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns a list of tasks directly
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    pet_id: int
    name: str
    species: str            # e.g. "dog", "cat", "rabbit"
    breed: str
    age: int                # years
    weight: float           # kg
    owner_id: Optional[int] = None
    medical_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    # -- task management -----------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Add a task to this pet. Raises if the task_id is already present."""
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError(f"Task {task.task_id} already exists for pet '{self.name}'")
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        """Remove a task by id. Raises if not found."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        if len(self.tasks) == before:
            raise ValueError(f"Task {task_id} not found for pet '{self.name}'")

    def get_task(self, task_id: int) -> Task:
        """Fetch a single task by id."""
        for t in self.tasks:
            if t.task_id == task_id:
                return t
        raise ValueError(f"Task {task_id} not found for pet '{self.name}'")

    # -- filtered views ------------------------------------------------------

    def get_pending_tasks(self) -> List[Task]:
        """All incomplete tasks, sorted by due time."""
        return sorted(
            [t for t in self.tasks if not t.is_completed],
            key=lambda t: t.due_datetime,
        )

    def get_overdue_tasks(self, now: Optional[datetime] = None) -> List[Task]:
        """All tasks that are past due and not completed."""
        return [t for t in self.tasks if t.is_overdue(now)]

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Return all tasks matching a category."""
        return [t for t in self.tasks if t.category == category]

    def get_tasks_due_today(self, reference: Optional[datetime] = None) -> List[Task]:
        """Return incomplete tasks due on the reference date (default: today)."""
        return [t for t in self.tasks if not t.is_completed and t.is_due_today(reference)]

    # -- profile update ------------------------------------------------------

    def update_profile(self, **kwargs) -> None:
        """Update profile fields by keyword. Raises on unknown keys."""
        protected = {"pet_id", "tasks"}
        for key, value in kwargs.items():
            if key in protected:
                raise ValueError(f"'{key}' cannot be updated via update_profile")
            if not hasattr(self, key):
                raise ValueError(f"Unknown field '{key}' on Pet")
            setattr(self, key, value)

    def __repr__(self) -> str:
        """Return a compact string showing id, name, species, and task count."""
        return f"Pet({self.pet_id} | {self.name} | {self.species} | {len(self.tasks)} tasks)"


# ---------------------------------------------------------------------------
# User — manages multiple pets and provides unified access to all their tasks
# ---------------------------------------------------------------------------

class User:
    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        phone: str = "",
    ) -> None:
        """Initialise a user account with contact details and an empty pet roster."""
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.pets: List[Pet] = []

    # -- pet management ------------------------------------------------------

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this user. Stamps the pet with owner_id."""
        if any(p.pet_id == pet.pet_id for p in self.pets):
            raise ValueError(f"Pet {pet.pet_id} is already registered")
        pet.owner_id = self.user_id
        self.pets.append(pet)

    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by id."""
        before = len(self.pets)
        self.pets = [p for p in self.pets if p.pet_id != pet_id]
        if len(self.pets) == before:
            raise ValueError(f"Pet {pet_id} not found")

    def get_pet(self, pet_id: int) -> Pet:
        """Fetch a single pet by id."""
        for p in self.pets:
            if p.pet_id == pet_id:
                return p
        raise ValueError(f"Pet {pet_id} not found")

    # -- cross-pet task access -----------------------------------------------

    def get_all_tasks(self) -> List[Task]:
        """Every task across all pets, sorted by due time."""
        all_tasks = [task for pet in self.pets for task in pet.tasks]
        return sorted(all_tasks, key=lambda t: t.due_datetime)

    def get_all_pending_tasks(self) -> List[Task]:
        """All incomplete tasks across all pets, sorted by due time."""
        return [t for t in self.get_all_tasks() if not t.is_completed]

    def get_all_overdue_tasks(self, now: Optional[datetime] = None) -> List[Task]:
        """All overdue tasks across all pets."""
        return [t for t in self.get_all_tasks() if t.is_overdue(now)]

    # -- convenience ---------------------------------------------------------

    def task_count(self) -> Dict[str, int]:
        """Summary counts: total, pending, overdue, completed."""
        all_tasks = self.get_all_tasks()
        return {
            "total": len(all_tasks),
            "pending": sum(1 for t in all_tasks if not t.is_completed),
            "overdue": sum(1 for t in all_tasks if t.is_overdue()),
            "completed": sum(1 for t in all_tasks if t.is_completed),
        }

    def __repr__(self) -> str:
        """Return a compact string showing id, name, and pet count."""
        return f"User({self.user_id} | {self.name} | {len(self.pets)} pets)"


# ---------------------------------------------------------------------------
# Schedule — the "brain": retrieves, organizes, and plans tasks across pets
# ---------------------------------------------------------------------------

class Schedule:
    """
    Coordinates task planning for a User's entire roster of pets.
    Core algorithm: generate_daily_plan() uses a greedy priority-first
    approach to fit tasks into an available time window.
    """

    def __init__(self, user: User) -> None:
        """Bind the Schedule brain to a User and their full pet roster."""
        self.user = user

    # -- retrieval -----------------------------------------------------------

    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """All tasks across every pet, sorted by due time."""
        tasks = self.user.get_all_tasks()
        if not include_completed:
            tasks = [t for t in tasks if not t.is_completed]
        return tasks

    def get_tasks_by_priority(self, include_completed: bool = False) -> List[Task]:
        """Tasks sorted highest priority first, then soonest due."""
        tasks = self.get_all_tasks(include_completed)
        return sorted(tasks, key=lambda t: (-t.priority, t.due_datetime))

    def sort_by_time(self, include_completed: bool = False) -> List[Task]:
        """All tasks sorted by their due time as 'HH:MM' strings."""
        tasks = self.get_all_tasks(include_completed)
        return sorted(tasks, key=lambda t: t.due_datetime.strftime("%H:%M"))

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return
                       only incomplete tasks. If None, completion is not filtered.
            pet_name:  If given, return only tasks belonging to that pet
                       (case-insensitive). If None, all pets are included.

        Returns:
            Matching tasks sorted by due time.
        """
        results = []
        for pet in self.user.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.is_completed != completed:
                    continue
                results.append(task)
        return sorted(results, key=lambda t: t.due_datetime)

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """All pending tasks matching a specific category."""
        return [t for t in self.get_all_tasks() if t.category == category]

    def get_tasks_for_pet(self, pet_id: int) -> List[Task]:
        """All pending tasks belonging to a specific pet."""
        pet = self.user.get_pet(pet_id)
        return pet.get_pending_tasks()

    def get_overdue_tasks(self, now: Optional[datetime] = None) -> List[Task]:
        """All overdue tasks across every pet."""
        return self.user.get_all_overdue_tasks(now)

    def get_upcoming_tasks(self, hours: int = 24, now: Optional[datetime] = None) -> List[Task]:
        """Pending tasks due within the next N hours."""
        now = now or datetime.now()
        cutoff = now + timedelta(hours=hours)
        return [
            t for t in self.get_all_tasks()
            if now <= t.due_datetime <= cutoff
        ]

    # -- mutation helpers ----------------------------------------------------

    def _next_task_id(self) -> int:
        """Return an id one above the current maximum across all pets."""
        all_ids = [t.task_id for pet in self.user.pets for t in pet.tasks]
        return max(all_ids, default=0) + 1

    def complete_task(self, pet_id: int, task_id: int) -> None:
        """Mark a task done and, for daily/weekly tasks, add a new instance
        for the next occurrence using timedelta.  The completed task is kept
        as a historical record; the new instance starts fresh (pending).

        Frequency behaviour:
          - daily:   next due = original due + 1 day
          - weekly:  next due = original due + 7 days
          - monthly / once: task is marked complete only (no new instance)
        """
        pet = self.user.get_pet(pet_id)
        task = pet.get_task(task_id)
        task.complete()

        if task.frequency == "daily":
            next_due = task.due_datetime + timedelta(days=1)
        elif task.frequency == "weekly":
            next_due = task.due_datetime + timedelta(weeks=1)
        else:
            return  # "once" and "monthly" — no new instance created

        next_task = Task(
            task_id=self._next_task_id(),
            title=task.title,
            category=task.category,
            due_datetime=next_due,
            duration=task.duration,
            priority=task.priority,
            frequency=task.frequency,
            description=task.description,
            notes=task.notes,
        )
        pet.add_task(next_task)

    def add_task_to_pet(self, pet_id: int, task: Task) -> None:
        """Convenience: add a task directly through the Schedule."""
        self.user.get_pet(pet_id).add_task(task)

    # -- conflict detection --------------------------------------------------

    def detect_conflicts(self) -> List[str]:
        """Return a list of human-readable warning strings for every pair of
        pending tasks whose time windows overlap.

        Two tasks conflict when their execution intervals intersect:
            [due_a, due_a + duration_a)  overlaps  [due_b, due_b + duration_b)

        Works across different pets as well as within the same pet.
        Returns an empty list when no conflicts are found.

        Performance: entries are sorted by start time so the inner loop can
        break as soon as task_b starts at or after task_a ends — no later
        task can overlap task_a either.  Conflict-free schedules cost only
        the sort (O(n log n)); the comparison loop exits immediately each time.
        """
        # Pre-compute (task, pet_name, start, end) and sort by start time
        entries: List[tuple] = sorted(
            [
                (task, pet.name,
                 task.due_datetime,
                 task.due_datetime + timedelta(minutes=task.duration))
                for pet in self.user.pets
                for task in pet.tasks
                if not task.is_completed
            ],
            key=lambda e: e[2],  # sort by start datetime
        )

        warnings: List[str] = []

        for i, (task_a, pet_a, start_a, end_a) in enumerate(entries):
            for task_b, pet_b, start_b, end_b in entries[i + 1:]:
                # Early termination: sorted order guarantees no later task overlaps
                if start_b >= end_a:
                    break

                warnings.append(
                    f"CONFLICT: '{task_a.title}' ({pet_a}, "
                    f"{start_a.strftime('%I:%M %p')}–"
                    f"{end_a.strftime('%I:%M %p')}) overlaps with "
                    f"'{task_b.title}' ({pet_b}, "
                    f"{start_b.strftime('%I:%M %p')}–"
                    f"{end_b.strftime('%I:%M %p')})"
                )

        return warnings

    # -- core scheduling algorithm -------------------------------------------

    def generate_daily_plan(
        self,
        available_minutes: int,
        reference: Optional[datetime] = None,
    ) -> List[Task]:
        """Return a priority-first greedy task list that fits within available_minutes; critical tasks always included."""
        reference = reference or datetime.now()

        # Pool: due today + overdue (deduplicated by task_id)
        today_tasks = {
            t.task_id: t
            for t in self.get_all_tasks()
            if t.is_due_today(reference) or t.is_overdue(reference)
        }
        candidates = sorted(
            today_tasks.values(),
            key=lambda t: (-t.priority, t.due_datetime),
        )

        plan: List[Task] = []
        time_used = 0

        # Pass 1 — always include critical tasks (priority 5)
        non_critical: List[Task] = []
        for task in candidates:
            if task.priority == 5:
                plan.append(task)
                time_used += task.duration
            else:
                non_critical.append(task)

        # Pass 2 — greedily fill remaining budget
        for task in non_critical:
            if time_used + task.duration <= available_minutes:
                plan.append(task)
                time_used += task.duration

        # Re-sort final plan: overdue first, then by priority, then by due time
        plan.sort(key=lambda t: (not t.is_overdue(reference), -t.priority, t.due_datetime))
        return plan

    # -- summary -------------------------------------------------------------

    def daily_summary(
        self,
        available_minutes: int = 120,
        reference: Optional[datetime] = None,
    ) -> Dict:
        """Return a structured summary dict containing the daily plan, counts, and metadata for the UI."""
        reference = reference or datetime.now()
        plan = self.generate_daily_plan(available_minutes, reference)
        overdue = self.get_overdue_tasks(reference)
        upcoming = self.get_upcoming_tasks(hours=24, now=reference)
        counts = self.user.task_count()

        return {
            "date": reference.strftime("%A, %B %d %Y"),
            "owner": self.user.name,
            "pets": [p.name for p in self.user.pets],
            "available_minutes": available_minutes,
            "planned_minutes": sum(t.duration for t in plan),
            "daily_plan": plan,
            "overdue_count": len(overdue),
            "upcoming_count": len(upcoming),
            "task_counts": counts,
        }

    def __repr__(self) -> str:
        """Return a compact string showing the owner name and pet count."""
        return f"Schedule(owner={self.user.name} | {len(self.user.pets)} pets)"
