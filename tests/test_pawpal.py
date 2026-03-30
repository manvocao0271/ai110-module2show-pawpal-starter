from datetime import datetime, timedelta
from pawpal_system import Task, Pet, User, Schedule


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(task_id: int = 1, hour: int = 8, minute: int = 0,
              completed: bool = False, priority: int = 3,
              category: str = "feeding", frequency: str = "once") -> Task:
    t = Task(
        task_id=task_id,
        title=f"Task {task_id}",
        category=category,
        due_datetime=datetime(2026, 3, 30, hour, minute),
        duration=10,
        priority=priority,
        frequency=frequency,
    )
    if completed:
        t.complete()
    return t


def make_schedule() -> Schedule:
    """Two pets, tasks added out of order, one completed task."""
    owner = User(1, "Kevin", "kevin@test.com")

    cat = Pet(11, "Kitty", "Cat", "Tabby", 3, 4.5)
    cat.add_task(make_task(task_id=3, hour=18, minute=0,  frequency="daily"))    # Evening  — added first
    cat.add_task(make_task(task_id=2, hour=12, minute=0,  completed=True))       # Noon     — done, once
    cat.add_task(make_task(task_id=1, hour=7,  minute=30, frequency="daily"))    # Morning  — added last

    dog = Pet(22, "Doggo", "Dog", "Husky", 4, 35)
    dog.add_task(make_task(task_id=6, hour=19, minute=0, category="grooming",     frequency="weekly"))
    dog.add_task(make_task(task_id=5, hour=14, minute=0, priority=5, category="appointment"))  # once
    dog.add_task(make_task(task_id=4, hour=8,  minute=0, category="walking",      frequency="daily"))

    owner.add_pet(cat)
    owner.add_pet(dog)
    return Schedule(owner)


# ---------------------------------------------------------------------------
# Test 1 — Task Completion
# ---------------------------------------------------------------------------

def test_task_complete_changes_status():
    task = make_task()

    assert task.is_completed is False

    task.complete()

    assert task.is_completed is True


# ---------------------------------------------------------------------------
# Test 2 — Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = Pet(pet_id=1, name="Kitty", species="Cat", breed="Tabby", age=3, weight=4.5)

    assert len(pet.tasks) == 0

    pet.add_task(make_task(task_id=1))
    pet.add_task(make_task(task_id=2))

    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Test 3 — sort_by_time: ascending HH:MM order
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_ascending_order():
    sched = make_schedule()
    tasks = sched.sort_by_time(include_completed=True)
    times = [t.due_datetime.strftime("%H:%M") for t in tasks]

    assert times == sorted(times), f"Expected ascending time order, got {times}"


def test_sort_by_time_excludes_completed_by_default():
    sched = make_schedule()
    tasks = sched.sort_by_time()   # include_completed defaults to False

    assert all(not t.is_completed for t in tasks)


def test_sort_by_time_includes_completed_when_requested():
    sched = make_schedule()
    tasks_with    = sched.sort_by_time(include_completed=True)
    tasks_without = sched.sort_by_time(include_completed=False)

    assert len(tasks_with) > len(tasks_without)
    assert any(t.is_completed for t in tasks_with)


# ---------------------------------------------------------------------------
# Test 4 — filter_tasks: by completion status
# ---------------------------------------------------------------------------

def test_filter_tasks_pending_only():
    sched = make_schedule()
    pending = sched.filter_tasks(completed=False)

    assert all(not t.is_completed for t in pending)


def test_filter_tasks_completed_only():
    sched = make_schedule()
    done = sched.filter_tasks(completed=True)

    assert len(done) == 1
    assert done[0].is_completed is True


def test_filter_tasks_no_completion_filter_returns_all():
    sched = make_schedule()
    all_tasks = sched.filter_tasks()   # both completed and pending

    assert len(all_tasks) == 6        # 3 cat + 3 dog


# ---------------------------------------------------------------------------
# Test 5 — filter_tasks: by pet name
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_name_returns_only_that_pets_tasks():
    sched = make_schedule()
    kitty_tasks = sched.filter_tasks(pet_name="Kitty")

    assert len(kitty_tasks) == 3
    # All returned tasks belong to Kitty (verify via task_ids 1-3)
    assert {t.task_id for t in kitty_tasks} == {1, 2, 3}


def test_filter_tasks_pet_name_is_case_insensitive():
    sched = make_schedule()

    assert sched.filter_tasks(pet_name="kitty") == sched.filter_tasks(pet_name="Kitty")


def test_filter_tasks_unknown_pet_name_returns_empty():
    sched = make_schedule()
    result = sched.filter_tasks(pet_name="Goldfish")

    assert result == []


# ---------------------------------------------------------------------------
# Test 6 — filter_tasks: combined (completion + pet name)
# ---------------------------------------------------------------------------

def test_filter_tasks_pending_for_specific_pet():
    sched = make_schedule()
    doggo_pending = sched.filter_tasks(completed=False, pet_name="Doggo")

    assert len(doggo_pending) == 3
    assert all(not t.is_completed for t in doggo_pending)


def test_filter_tasks_completed_for_specific_pet():
    sched = make_schedule()
    kitty_done = sched.filter_tasks(completed=True, pet_name="Kitty")

    assert len(kitty_done) == 1
    assert kitty_done[0].task_id == 2


def test_filter_tasks_completed_for_pet_with_none_done():
    sched = make_schedule()
    doggo_done = sched.filter_tasks(completed=True, pet_name="Doggo")

    assert doggo_done == []


# ---------------------------------------------------------------------------
# Test 7 — filter_tasks result is sorted by due time
# ---------------------------------------------------------------------------

def test_filter_tasks_result_is_sorted_by_due_time():
    sched = make_schedule()
    tasks = sched.filter_tasks()
    times = [t.due_datetime for t in tasks]

    assert times == sorted(times)


# ---------------------------------------------------------------------------
# Test 8 — complete_task: daily task spawns a new instance the next day
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_new_instance():
    sched = make_schedule()
    pet = sched.user.get_pet(11)        # Kitty
    original = pet.get_task(1)          # task_id=1, hour=7:30, frequency="daily"
    original_due = original.due_datetime
    original_count = len(pet.tasks)

    sched.complete_task(pet_id=11, task_id=1)

    assert original.is_completed is True
    assert len(pet.tasks) == original_count + 1

    new_task = pet.tasks[-1]
    assert new_task.due_datetime == original_due + timedelta(days=1)
    assert new_task.is_completed is False
    assert new_task.frequency == "daily"
    assert new_task.title == original.title


def test_complete_daily_task_new_instance_has_unique_id():
    sched = make_schedule()
    existing_ids = {t.task_id for pet in sched.user.pets for t in pet.tasks}

    sched.complete_task(pet_id=11, task_id=1)

    pet = sched.user.get_pet(11)
    new_task = pet.tasks[-1]
    assert new_task.task_id not in existing_ids


# ---------------------------------------------------------------------------
# Test 9 — complete_task: weekly task spawns a new instance 7 days later
# ---------------------------------------------------------------------------

def test_complete_weekly_task_creates_new_instance():
    sched = make_schedule()
    pet = sched.user.get_pet(22)        # Doggo
    original = pet.get_task(6)          # task_id=6, hour=19:00, frequency="weekly"
    original_due = original.due_datetime

    sched.complete_task(pet_id=22, task_id=6)

    assert original.is_completed is True

    new_task = pet.tasks[-1]
    assert new_task.due_datetime == original_due + timedelta(weeks=1)
    assert new_task.is_completed is False
    assert new_task.frequency == "weekly"


# ---------------------------------------------------------------------------
# Test 10 — complete_task: "once" task does NOT spawn a new instance
# ---------------------------------------------------------------------------

def test_complete_once_task_does_not_create_new_instance():
    sched = make_schedule()
    pet = sched.user.get_pet(22)        # Doggo
    original = pet.get_task(5)          # task_id=5, frequency="once"
    original_count = len(pet.tasks)

    sched.complete_task(pet_id=22, task_id=5)

    assert original.is_completed is True
    assert len(pet.tasks) == original_count   # no new task added


# ---------------------------------------------------------------------------
# Test 11 — complete_task: new instance copies all task fields
# ---------------------------------------------------------------------------

def test_complete_task_new_instance_inherits_fields():
    sched = make_schedule()
    pet = sched.user.get_pet(11)
    original = pet.get_task(1)

    sched.complete_task(pet_id=11, task_id=1)

    new_task = pet.tasks[-1]
    assert new_task.category    == original.category
    assert new_task.duration    == original.duration
    assert new_task.priority    == original.priority
    assert new_task.description == original.description
    assert new_task.notes       == original.notes


# ---------------------------------------------------------------------------
# Helpers for conflict detection tests
# ---------------------------------------------------------------------------

def make_conflict_schedule() -> Schedule:
    """Schedule with three known conflicts:
       - same-pet exact overlap:   task A and task B both start at 09:00
       - same-pet partial overlap: task C starts at 10:00 (30 min), task D at 10:20 (30 min)
       - cross-pet overlap:        task E (pet 1) starts at 14:00 (60 min),
                                   task F (pet 2) starts at 14:30 (15 min)
    And one non-overlapping pair:
       - task G starts at 16:00, task H starts at 17:00 (no overlap)
    """
    owner = User(99, "Tester", "t@test.com")

    p1 = Pet(1, "Alpha", "Dog", "Lab", 2, 20.0)
    p2 = Pet(2, "Beta",  "Cat", "Tabby", 3, 4.5)

    base = datetime(2026, 3, 30)

    # same-pet exact overlap (both 09:00, 20 min)
    p1.add_task(Task(101, "Task A", "feeding",     base.replace(hour=9,  minute=0),  20, 3))
    p1.add_task(Task(102, "Task B", "walking",     base.replace(hour=9,  minute=0),  20, 3))

    # same-pet partial overlap (10:00–10:30 vs 10:20–10:50)
    p1.add_task(Task(103, "Task C", "grooming",    base.replace(hour=10, minute=0),  30, 2))
    p1.add_task(Task(104, "Task D", "enrichment",  base.replace(hour=10, minute=20), 30, 2))

    # cross-pet overlap (14:00–15:00 vs 14:30–14:45)
    p1.add_task(Task(105, "Task E", "appointment", base.replace(hour=14, minute=0),  60, 5))
    p2.add_task(Task(106, "Task F", "medication",  base.replace(hour=14, minute=30), 15, 4))

    # no overlap (16:00–16:30 vs 17:00–17:30)
    p1.add_task(Task(107, "Task G", "training",    base.replace(hour=16, minute=0),  30, 1))
    p2.add_task(Task(108, "Task H", "other",       base.replace(hour=17, minute=0),  30, 1))

    owner.add_pet(p1)
    owner.add_pet(p2)
    return Schedule(owner)


# ---------------------------------------------------------------------------
# Test 12 — detect_conflicts: returns a list of strings (never raises)
# ---------------------------------------------------------------------------

def test_detect_conflicts_returns_list():
    sched = make_conflict_schedule()
    result = sched.detect_conflicts()

    assert isinstance(result, list)
    assert all(isinstance(w, str) for w in result)


# ---------------------------------------------------------------------------
# Test 13 — detect_conflicts: correct count of conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_correct_count():
    sched = make_conflict_schedule()
    conflicts = sched.detect_conflicts()

    # Expected: A/B exact, C/D partial, E/F cross-pet = 3 conflicts
    assert len(conflicts) == 3


# ---------------------------------------------------------------------------
# Test 14 — detect_conflicts: identifies same-pet exact overlap
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_pet_exact_overlap():
    sched = make_conflict_schedule()
    conflicts = sched.detect_conflicts()

    assert any("Task A" in w and "Task B" in w for w in conflicts)


# ---------------------------------------------------------------------------
# Test 15 — detect_conflicts: identifies same-pet partial overlap
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_pet_partial_overlap():
    sched = make_conflict_schedule()
    conflicts = sched.detect_conflicts()

    assert any("Task C" in w and "Task D" in w for w in conflicts)


# ---------------------------------------------------------------------------
# Test 16 — detect_conflicts: identifies cross-pet overlap
# ---------------------------------------------------------------------------

def test_detect_conflicts_cross_pet_overlap():
    sched = make_conflict_schedule()
    conflicts = sched.detect_conflicts()

    assert any("Task E" in w and "Task F" in w for w in conflicts)


# ---------------------------------------------------------------------------
# Test 17 — detect_conflicts: non-overlapping tasks not reported
# ---------------------------------------------------------------------------

def test_detect_conflicts_no_false_positives():
    sched = make_conflict_schedule()
    conflicts = sched.detect_conflicts()

    assert not any("Task G" in w and "Task H" in w for w in conflicts)


# ---------------------------------------------------------------------------
# Test 18 — detect_conflicts: completed tasks are ignored
# ---------------------------------------------------------------------------

def test_detect_conflicts_ignores_completed_tasks():
    sched = make_conflict_schedule()
    # Complete Task A so the A/B conflict disappears
    sched.user.get_pet(1).get_task(101).complete()
    conflicts = sched.detect_conflicts()

    assert not any("Task A" in w for w in conflicts)


# ---------------------------------------------------------------------------
# Test 19 — detect_conflicts: no conflicts returns empty list
# ---------------------------------------------------------------------------

def test_detect_conflicts_no_conflicts_returns_empty():
    owner = User(1, "Solo", "s@test.com")
    pet   = Pet(1, "Solo Pet", "Dog", "Poodle", 1, 5.0)
    base  = datetime(2026, 3, 30)
    pet.add_task(Task(1, "Morning Walk", "walking",  base.replace(hour=8),  30, 3))
    pet.add_task(Task(2, "Evening Walk", "walking",  base.replace(hour=18), 30, 3))
    owner.add_pet(pet)
    sched = Schedule(owner)

    assert sched.detect_conflicts() == []
