import sys
import os
import pytest
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan, detect_cross_pet_conflicts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(title="Feed dog", duration=10, priority="medium", category="feeding",
              is_required=False, time=None, frequency=None, due_date=None):
    return Task(title=title, duration=duration, priority=priority, category=category,
                is_required=is_required, time=time, frequency=frequency, due_date=due_date)


def make_scheduler(available_minutes=60, pet_name="Buddy"):
    owner = Owner(name="Alex", available_minutes=available_minutes)
    pet = Pet(name=pet_name, species="dog", age=3)
    return Scheduler(owner=owner, pet=pet)


# ===========================================================================
# EXISTING TESTS (unchanged)
# ===========================================================================

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


# ===========================================================================
# TASK — creation & validation
# ===========================================================================

def test_task_invalid_priority_raises():
    with pytest.raises(ValueError):
        make_task(priority="urgent")


def test_task_invalid_frequency_raises():
    with pytest.raises(ValueError):
        make_task(frequency="monthly")


def test_recurring_task_auto_sets_due_date_to_today():
    task = make_task(frequency="daily")
    assert task.due_date == date.today()


def test_non_recurring_task_due_date_stays_none():
    task = make_task()
    assert task.due_date is None


# ===========================================================================
# TASK — next_occurrence (recurring tasks)
# ===========================================================================

def test_next_occurrence_daily_advances_one_day():
    today = date.today()
    task = make_task(frequency="daily", due_date=today)
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(days=1)


def test_next_occurrence_weekly_advances_seven_days():
    today = date.today()
    task = make_task(frequency="weekly", due_date=today)
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(weeks=1)


def test_next_occurrence_returns_fresh_uncompleted_task():
    task = make_task(frequency="daily")
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task.completed is False


def test_next_occurrence_on_non_recurring_raises():
    task = make_task(frequency=None)
    with pytest.raises(ValueError):
        task.next_occurrence()


def test_next_occurrence_preserves_all_fields():
    today = date.today()
    task = make_task(title="Walk", duration=30, priority="high", category="exercise",
                     is_required=True, time="08:00", frequency="weekly", due_date=today)
    nxt = task.next_occurrence()
    assert nxt.title == task.title
    assert nxt.duration == task.duration
    assert nxt.priority == task.priority
    assert nxt.is_required == task.is_required
    assert nxt.time == task.time
    assert nxt.frequency == task.frequency


# ===========================================================================
# SCHEDULER — sort_by_time
# ===========================================================================

def test_sort_by_time_orders_timed_tasks_ascending():
    sched = make_scheduler()
    sched.add_task(make_task(title="C", time="14:00"))
    sched.add_task(make_task(title="A", time="07:00"))
    sched.add_task(make_task(title="B", time="08:30"))
    result = sched.sort_by_time()
    assert [t.title for t in result] == ["A", "B", "C"]


def test_sort_by_time_untimed_tasks_go_to_end():
    sched = make_scheduler()
    sched.add_task(make_task(title="Untimed"))
    sched.add_task(make_task(title="Morning", time="07:00"))
    result = sched.sort_by_time()
    assert result[0].title == "Morning"
    assert result[-1].title == "Untimed"


def test_sort_by_time_all_untimed_returns_all():
    sched = make_scheduler()
    sched.add_task(make_task(title="A"))
    sched.add_task(make_task(title="B"))
    result = sched.sort_by_time()
    assert len(result) == 2


def test_sort_by_time_two_tasks_same_time_both_included():
    sched = make_scheduler()
    sched.add_task(make_task(title="A", time="08:00"))
    sched.add_task(make_task(title="B", time="08:00"))
    result = sched.sort_by_time()
    assert len(result) == 2


def test_sort_by_time_empty_scheduler_returns_empty():
    sched = make_scheduler()
    assert sched.sort_by_time() == []


# ===========================================================================
# SCHEDULER — detect_conflicts (same pet)
# ===========================================================================

def test_detect_conflicts_overlapping_tasks():
    sched = make_scheduler()
    sched.add_task(make_task(title="Walk",  time="08:00", duration=60))
    sched.add_task(make_task(title="Groom", time="08:30", duration=30))
    conflicts = sched.detect_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Groom" in conflicts[0]


def test_detect_conflicts_adjacent_tasks_no_conflict():
    # A ends at 08:30, B starts at 08:30 — touching but not overlapping
    sched = make_scheduler()
    sched.add_task(make_task(title="Walk",  time="08:00", duration=30))
    sched.add_task(make_task(title="Groom", time="08:30", duration=30))
    assert sched.detect_conflicts() == []


def test_detect_conflicts_no_timed_tasks_returns_empty():
    sched = make_scheduler()
    sched.add_task(make_task(title="Walk"))
    assert sched.detect_conflicts() == []


def test_detect_conflicts_completed_task_ignored():
    sched = make_scheduler()
    task_a = make_task(title="Walk",  time="08:00", duration=60)
    task_b = make_task(title="Groom", time="08:30", duration=30)
    task_a.mark_complete()
    sched.add_task(task_a)
    sched.add_task(task_b)
    assert sched.detect_conflicts() == []


def test_detect_conflicts_exact_same_start_time_is_conflict():
    sched = make_scheduler()
    sched.add_task(make_task(title="A", time="09:00", duration=30))
    sched.add_task(make_task(title="B", time="09:00", duration=30))
    assert len(sched.detect_conflicts()) == 1


# ===========================================================================
# SCHEDULER — mark_task_complete
# ===========================================================================

def test_mark_task_complete_marks_done():
    sched = make_scheduler()
    sched.add_task(make_task(title="Feed"))
    sched.mark_task_complete("Feed")
    assert sched.tasks[0].completed is True


def test_mark_task_complete_recurring_adds_next_occurrence():
    today = date.today()
    sched = make_scheduler()
    sched.add_task(make_task(title="Walk", frequency="daily", due_date=today))
    sched.mark_task_complete("Walk")
    assert len(sched.tasks) == 2
    next_task = sched.tasks[1]
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)  # must be the following day


def test_mark_task_complete_non_recurring_returns_none():
    sched = make_scheduler()
    sched.add_task(make_task(title="Bath"))
    result = sched.mark_task_complete("Bath")
    assert result is None


def test_mark_task_complete_unknown_title_raises():
    sched = make_scheduler()
    with pytest.raises(ValueError):
        sched.mark_task_complete("Nonexistent")


# ===========================================================================
# SCHEDULER — generate_plan (happy paths & edge cases)
# ===========================================================================

def test_generate_plan_no_tasks_returns_empty_plan():
    sched = make_scheduler(available_minutes=60)
    plan = sched.generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_duration == 0


def test_generate_plan_schedules_high_priority_before_low():
    sched = make_scheduler(available_minutes=30)
    sched.add_task(make_task(title="Low",  duration=20, priority="low"))
    sched.add_task(make_task(title="High", duration=20, priority="high"))
    plan = sched.generate_plan()
    assert plan.scheduled_tasks[0].title == "High"
    assert any(t.title == "Low" for t in plan.skipped_tasks)


def test_generate_plan_required_task_always_scheduled():
    sched = make_scheduler(available_minutes=5)
    sched.add_task(make_task(title="Medicine", duration=30, is_required=True))
    plan = sched.generate_plan()
    assert any(t.title == "Medicine" for t in plan.scheduled_tasks)


def test_generate_plan_optional_task_skipped_when_no_time():
    sched = make_scheduler(available_minutes=0)
    sched.add_task(make_task(title="Walk", duration=20, priority="high"))
    plan = sched.generate_plan()
    assert any(t.title == "Walk" for t in plan.skipped_tasks)


def test_generate_plan_task_exactly_fills_budget():
    sched = make_scheduler(available_minutes=30)
    sched.add_task(make_task(title="Walk", duration=30, priority="medium"))
    plan = sched.generate_plan()
    assert len(plan.scheduled_tasks) == 1
    assert plan.skipped_tasks == []
    assert plan.total_duration == 30


# ===========================================================================
# SCHEDULER — filter_tasks
# ===========================================================================

def test_filter_tasks_status_completed():
    sched = make_scheduler()
    t1 = make_task(title="Done")
    t2 = make_task(title="Pending")
    t1.mark_complete()
    sched.add_task(t1)
    sched.add_task(t2)
    result = sched.filter_tasks(status="completed")
    assert all(t.completed for t in result)
    assert len(result) == 1


def test_filter_tasks_status_pending():
    sched = make_scheduler()
    t1 = make_task(title="Done")
    t1.mark_complete()
    sched.add_task(t1)
    sched.add_task(make_task(title="Pending"))
    result = sched.filter_tasks(status="pending")
    assert all(not t.completed for t in result)


def test_filter_tasks_wrong_pet_name_returns_empty():
    sched = make_scheduler(pet_name="Buddy")
    sched.add_task(make_task(title="Walk"))
    assert sched.filter_tasks(pet_name="Max") == []


def test_filter_tasks_no_filters_returns_all():
    sched = make_scheduler()
    sched.add_task(make_task(title="A"))
    sched.add_task(make_task(title="B"))
    assert len(sched.filter_tasks()) == 2


# ===========================================================================
# detect_cross_pet_conflicts
# ===========================================================================

def test_cross_pet_conflicts_detected():
    sched1 = make_scheduler(pet_name="Buddy")
    sched2 = make_scheduler(pet_name="Max")
    sched1.add_task(make_task(title="Walk",  time="09:00", duration=60))
    sched2.add_task(make_task(title="Groom", time="09:30", duration=30))
    conflicts = detect_cross_pet_conflicts([sched1, sched2])
    assert len(conflicts) == 1
    assert "cross-pet" in conflicts[0]


def test_cross_pet_no_conflict_when_non_overlapping():
    sched1 = make_scheduler(pet_name="Buddy")
    sched2 = make_scheduler(pet_name="Max")
    sched1.add_task(make_task(title="Walk",  time="08:00", duration=30))
    sched2.add_task(make_task(title="Groom", time="09:00", duration=30))
    assert detect_cross_pet_conflicts([sched1, sched2]) == []


def test_cross_pet_same_pet_name_not_flagged():
    # Two schedulers with the same pet name — should not produce cross-pet conflicts
    sched1 = make_scheduler(pet_name="Buddy")
    sched2 = make_scheduler(pet_name="Buddy")
    sched1.add_task(make_task(title="Walk",  time="09:00", duration=60))
    sched2.add_task(make_task(title="Groom", time="09:30", duration=30))
    assert detect_cross_pet_conflicts([sched1, sched2]) == []


def test_cross_pet_empty_list_returns_empty():
    assert detect_cross_pet_conflicts([]) == []


def test_cross_pet_one_scheduler_no_timed_tasks():
    sched1 = make_scheduler(pet_name="Buddy")
    sched2 = make_scheduler(pet_name="Max")
    sched1.add_task(make_task(title="Walk"))  # no time
    sched2.add_task(make_task(title="Groom", time="09:00", duration=30))
    assert detect_cross_pet_conflicts([sched1, sched2]) == []
