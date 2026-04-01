VALID_PRIORITIES = {"low", "medium", "high"}

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self._pets: list = []

    def set_availability(self, minutes: int):
        self.available_minutes = minutes

    def add_pet(self, pet: "Pet"):
        self._pets.append(pet)

    def get_all_tasks(self) -> list:
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
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "notes": self.notes,
            "task_count": len(self.tasks),
        }

    def add_task(self, task: "Task"):
        self.tasks.append(task)

    def remove_task(self, title: str):
        self.tasks = [t for t in self.tasks if t.title != title]


class Task:
    def __init__(self, title: str, duration: int, priority: str, category: str, is_required: bool = False):
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{priority}'")
        self.title = title
        self.duration = duration
        self.priority = priority
        self.category = category
        self.is_required = is_required
        self.completed = False

    def priority_score(self) -> int:
        return PRIORITY_SCORES[self.priority]

    def mark_complete(self):
        self.completed = True

    def __repr__(self) -> str:
        required_tag = " [required]" if self.is_required else ""
        status = " ✓" if self.completed else ""
        return f"Task('{self.title}', {self.duration}min, {self.priority}{required_tag}{status})"


class DailyPlan:
    def __init__(self, scheduled_tasks: list, skipped_tasks: list, reasoning: list[str] = None):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = sum(t.duration for t in scheduled_tasks)
        self.reasoning: list[str] = reasoning or []

    def display(self) -> str:
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
        return self.owner.available_minutes

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, title: str):
        self.tasks = [t for t in self.tasks if t.title != title]

    def generate_plan(self) -> DailyPlan:
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
                    f"Required task '{task.title}' ({task.duration}min) exceeds remaining time ({time_remaining}min) — scheduled anyway."
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
                    f"Skipped '{task.title}' ({task.duration}min) — only {time_remaining}min left."
                )

        return DailyPlan(scheduled, skipped, reasoning)
