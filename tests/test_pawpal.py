from datetime import datetime
from pawpal_system import Task, Pet


def make_task(task_id: int = 1) -> Task:
    return Task(
        task_id=task_id,
        title="Morning Feeding",
        category="feeding",
        due_datetime=datetime(2026, 3, 30, 8, 0),
        duration=10,
        priority=3,
    )


def make_pet() -> Pet:
    return Pet(pet_id=1, name="Kitty", species="Cat", breed="Tabby", age=3, weight=4.5)


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
    pet = make_pet()

    assert len(pet.tasks) == 0

    pet.add_task(make_task(task_id=1))
    pet.add_task(make_task(task_id=2))

    assert len(pet.tasks) == 2
