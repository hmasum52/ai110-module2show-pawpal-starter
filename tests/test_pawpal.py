import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Feed dog", duration=5, priority="high", category="feeding")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog", age=3)
    assert len(pet.tasks) == 0
    task = Task(title="Walk", duration=20, priority="medium", category="exercise")
    pet.add_task(task)
    assert len(pet.tasks) == 1
