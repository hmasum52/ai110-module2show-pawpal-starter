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
    def __init__(self, scheduled_tasks: list, skipped_tasks: list):
        self.scheduled_tasks = scheduled_tasks
        self.skipped_tasks = skipped_tasks
        self.total_duration = sum(t.duration for t in scheduled_tasks)

    def display(self) -> str:
        pass

    def get_reasoning(self) -> str:
        pass


class Scheduler:
    def __init__(self, time_budget: int):
        self.tasks: list[Task] = []
        self.time_budget = time_budget

    def add_task(self, task: Task):
        pass

    def remove_task(self, title: str):
        pass

    def generate_plan(self) -> DailyPlan:
        pass

    def explain_plan(self) -> str:
        pass
