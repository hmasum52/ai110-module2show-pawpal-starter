from datetime import date, timedelta

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_FREQUENCIES = {None, "daily", "weekly"}

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCY_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _time_to_minutes(time_str: str) -> int:
    """
    Convert a zero-padded "HH:MM" string to total minutes from midnight.

    Examples:
        "07:00" -> 420
        "08:30" -> 510
        "14:00" -> 840

    Used internally so interval overlap math can work on plain integers
    rather than string comparisons.
    """
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self._pets: list = []

    def set_availability(self, minutes: int):
        """Update the owner's daily available time in minutes."""
        self.available_minutes = minutes

    def add_pet(self, pet: "Pet"):
        """Register a pet under this owner."""
        self._pets.append(pet)

    def get_all_tasks(self) -> list:
        """Return a flat list of all tasks across every owned pet."""
        tasks = []
        for pet in self._pets:
            tasks.extend(pet.tasks)
        return tasks


class Pet:
    def __init__(self, name: str, species: str, age: int, notes: str = ""):
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes
        self.tasks: list["Task"] = []

    def get_profile(self) -> dict:
        """Return a dictionary summarising the pet's profile and task count."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "notes": self.notes,
            "task_count": len(self.tasks),
        }

    def add_task(self, task: "Task"):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove all tasks matching the given title from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.title != title]


class Task:
    def __init__(
        self,
        title: str,
        duration: int,
        priority: str,
        category: str,
        is_required: bool = False,
        time: str = None,
        frequency: str = None,
        due_date: date = None,
    ):
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{priority}'")
        if frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}, got '{frequency}'")
        self.title = title
        self.duration = duration
        self.priority = priority
        self.category = category
        self.is_required = is_required
        self.completed = False
        self.time = time            # Optional start time as "HH:MM" string, e.g. "08:30"
        self.frequency = frequency  # None | "daily" | "weekly"
        self.due_date = due_date    # date object; defaults to today when frequency is set

        # Auto-set due_date to today if the task recurs but no date was given
        if self.frequency and self.due_date is None:
            self.due_date = date.today()

    def priority_score(self) -> int:
        """Return the numeric score for this task's priority level."""
        return PRIORITY_SCORES[self.priority]

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """
        Return a new Task for the next occurrence of this recurring task.

        Uses FREQUENCY_DELTA to advance the due_date:
          - "daily"  → due_date + 1 day   (timedelta(days=1))
          - "weekly" → due_date + 7 days  (timedelta(weeks=1))

        Raises ValueError if called on a non-recurring task (frequency=None).
        The returned task is a fresh copy: completed=False, same all other fields.
        """
        if self.frequency is None:
            raise ValueError(f"Task '{self.title}' has no frequency — cannot create next occurrence.")

        next_due = self.due_date + FREQUENCY_DELTA[self.frequency]

        return Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            is_required=self.is_required,
            time=self.time,
            frequency=self.frequency,
            due_date=next_due,
        )

    def __repr__(self) -> str:
        """Return a human-readable string representation of the task."""
        required_tag = " [required]" if self.is_required else ""
        status = " [done]" if self.completed else ""
        freq_tag = f" [{self.frequency}]" if self.frequency else ""
        due_tag = f" due:{self.due_date}" if self.due_date else ""
        return f"Task('{self.title}', {self.duration}min, {self.priority}{required_tag}{status}{freq_tag}{due_tag})"


class DailyPlan:
    def __init__(self, scheduled_tasks: list, skipped_tasks: list, reasoning: list[str] = None):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = sum(t.duration for t in scheduled_tasks)
        self.reasoning: list[str] = reasoning or []

    def display(self) -> str:
        """Format and return the daily plan as a human-readable string."""
        lines = ["=== Daily Plan ==="]
        lines.append(f"Total time: {self.total_duration} min\n")
        lines.append("Scheduled:")
        for task in self.scheduled_tasks:
            lines.append(f"  - {task.title} ({task.duration}min, {task.priority})")
        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.title} ({task.duration}min, {task.priority})")
        return "\n".join(lines)

    def get_reasoning(self) -> str:
        """Return the scheduling reasoning as a bulleted string."""
        if not self.reasoning:
            return "No reasoning provided."
        return "\n".join(f"- {r}" for r in self.reasoning)


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    @property
    def time_budget(self) -> int:
        """Return the owner's total available minutes as the scheduling budget."""
        return self.owner.available_minutes

    def add_task(self, task: Task):
        """Add a task to the scheduler's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str):
        """Remove all tasks with the given title from the scheduler."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def sort_by_time(self) -> list:
        """
        Return tasks sorted by their 'time' attribute in ascending order.

        Tasks with a time set (HH:MM strings) come first, sorted using a
        lambda that compares the strings directly — lexicographic order works
        correctly for zero-padded HH:MM values.
        Tasks with time=None are placed at the end, preserving their original order.
        """
        timed = sorted(
            [t for t in self.tasks if t.time is not None],
            key=lambda t: t.time,
        )
        untimed = [t for t in self.tasks if t.time is None]
        return timed + untimed

    def filter_tasks(self, status: str = None, pet_name: str = None) -> list:
        """
        Return a filtered list of tasks from this scheduler.

        Args:
            status:   'completed' returns only finished tasks;
                      'pending'   returns only unfinished tasks;
                      None        returns all tasks regardless of status.
            pet_name: When provided, only tasks belonging to the matching pet
                      are included (case-insensitive match against self.pet.name).

        Returns:
            List of Task objects that match all supplied filters.
        """
        tasks = list(self.tasks)

        if pet_name and self.pet.name.lower() != pet_name.lower():
            return []  # This scheduler's pet doesn't match — nothing to return

        if status == "completed":
            tasks = [t for t in tasks if t.completed]
        elif status == "pending":
            tasks = [t for t in tasks if not t.completed]

        return tasks

    def mark_task_complete(self, title: str) -> "Task | None":
        """
        Mark the first matching task complete and, if it recurs, schedule the
        next occurrence automatically.

        Workflow:
          1. Find the task by title (first match, case-sensitive).
          2. Call task.mark_complete() to set completed=True.
          3. If frequency is "daily" or "weekly", call task.next_occurrence()
             which uses timedelta to compute the new due_date, then appends
             the fresh Task copy to this scheduler's task list.

        Args:
            title: The exact title of the task to complete.

        Returns:
            The newly created next-occurrence Task if the task recurs, else None.
        """
        task = next((t for t in self.tasks if t.title == title), None)
        if task is None:
            raise ValueError(f"No task named '{title}' found in scheduler.")

        task.mark_complete()

        if task.frequency is not None:
            next_task = task.next_occurrence()
            self.tasks.append(next_task)
            return next_task

        return None

    def detect_conflicts(self) -> list[str]:
        """
        Check for overlapping time windows among this scheduler's timed tasks.

        Only tasks with a 'time' value set are evaluated — untimed tasks are
        skipped silently.  For each pair (A, B), the windows overlap when:

            A.start < B.end  AND  B.start < A.end

        where start = _time_to_minutes(task.time) and end = start + task.duration.

        Returns a list of human-readable warning strings — one per conflict.
        Returns an empty list when no conflicts exist.  Never raises an exception.
        """
        warnings = []
        # Only check tasks that are still pending — completed tasks are done and
        # should not flag conflicts against their own next-occurrence copies.
        timed = [t for t in self.tasks if t.time is not None and not t.completed]

        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                a_start = _time_to_minutes(a.time)
                b_start = _time_to_minutes(b.time)
                a_end = a_start + a.duration
                b_end = b_start + b.duration

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"CONFLICT [{self.pet.name}]: '{a.title}' ({a.time}, {a.duration}min) "
                        f"overlaps '{b.title}' ({b.time}, {b.duration}min)"
                    )

        return warnings

    def generate_plan(self) -> DailyPlan:
        """Schedule tasks within the time budget and return a DailyPlan."""
        reasoning = []
        scheduled = []
        skipped = []
        time_remaining = self.time_budget

        # Required tasks first, then sort the rest by priority score descending
        required = [t for t in self.tasks if t.is_required]
        optional = sorted(
            [t for t in self.tasks if not t.is_required],
            key=lambda t: t.priority_score(),
            reverse=True,
        )
        ordered = required + optional

        for task in ordered:
            if task.is_required and task.duration > time_remaining:
                reasoning.append(
                    f"Required task '{task.title}' ({task.duration}min) exceeds remaining time ({time_remaining}min) - scheduled anyway."
                )
                scheduled.append(task)
                time_remaining -= task.duration
            elif task.duration <= time_remaining:
                scheduled.append(task)
                time_remaining -= task.duration
                reasoning.append(f"Scheduled '{task.title}' ({task.duration}min, {task.priority}).")
            else:
                skipped.append(task)
                reasoning.append(
                    f"Skipped '{task.title}' ({task.duration}min) - only {time_remaining}min left."
                )

        return DailyPlan(scheduled, skipped, reasoning)


def detect_cross_pet_conflicts(schedulers: list) -> list[str]:
    """
    Check for overlapping time windows across tasks from multiple schedulers
    (i.e. across different pets belonging to the same owner).

    Builds a flat list of (pet_name, task) pairs from every scheduler, then
    compares all cross-scheduler pairs using the same interval overlap formula:

        A.start < B.end  AND  B.start < A.end

    Same-pet pairs are skipped here — use Scheduler.detect_conflicts() for those.

    Args:
        schedulers: List of Scheduler objects to check against each other.

    Returns:
        A list of human-readable warning strings — one per cross-pet conflict.
        Returns an empty list when no conflicts exist.  Never raises an exception.
    """
    warnings = []

    # Flatten to (pet_name, task) keeping only pending timed tasks
    labeled = [
        (sched.pet.name, task)
        for sched in schedulers
        for task in sched.tasks
        if task.time is not None and not task.completed
    ]

    for i in range(len(labeled)):
        for j in range(i + 1, len(labeled)):
            pet_a, a = labeled[i]
            pet_b, b = labeled[j]

            if pet_a == pet_b:
                continue  # same-pet conflicts handled by Scheduler.detect_conflicts()

            a_start = _time_to_minutes(a.time)
            b_start = _time_to_minutes(b.time)
            a_end = a_start + a.duration
            b_end = b_start + b.duration

            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"CONFLICT [cross-pet]: '{a.title}' ({pet_a}, {a.time}, {a.duration}min) "
                    f"overlaps '{b.title}' ({pet_b}, {b.time}, {b.duration}min)"
                )

    return warnings
