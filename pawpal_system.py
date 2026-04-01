VALID_PRIORITIES = {"low", "medium", "high"}


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: dict = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}

    def set_availability(self, minutes: int):
        pass


class Pet:
    def __init__(self, name: str, species: str, age: int, notes: str = ""):
        self.name = name
        self.species = species
        self.age = age
        self.notes = notes

    def get_profile(self) -> dict:
        pass


class Task:
    def __init__(self, title: str, duration: int, priority: str, category: str, is_required: bool = False):
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}, got '{priority}'")
        self.title = title
        self.duration = duration
        self.priority = priority
        self.category = category
        self.is_required = is_required

    def priority_score(self) -> int:
        pass

    def __repr__(self) -> str:
        pass


class DailyPlan:
    def __init__(self, scheduled_tasks: list, skipped_tasks: list, reasoning: list[str] = None):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = sum(t.duration for t in scheduled_tasks)
        self.reasoning: list[str] = reasoning or []

    def display(self) -> str:
        pass

    def get_reasoning(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    @property
    def time_budget(self) -> int:
        return self.owner.available_minutes

    def add_task(self, task: Task):
        pass

    def remove_task(self, title: str):
        pass

    def generate_plan(self) -> DailyPlan:
        pass
