"""
PawPal+ logic layer — class skeletons derived from UML.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 (low) to 5 (high)
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # e.g. "daily", "weekly"
    status: str = "pending"  # "pending", "completed", "skipped"

    def is_due_today(self) -> bool:
        """Check if this task is due today based on recurrence pattern."""
        pass

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def get_priority_label(self) -> str:
        """Return human-readable priority label (Low, Medium, High, etc.)."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass

    def get_daily_tasks(self) -> list[Task]:
        """Return tasks that are due today."""
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        pass

    def get_total_required_minutes(self) -> int:
        """Calculate total time needed for all tasks across all pets."""
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.time_budget = owner.available_minutes

    def generate_plan(self) -> list[Task]:
        """Return tasks sorted by priority, respecting the time budget."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a list of conflict descriptions (e.g. tasks that exceed time budget)."""
        pass

    def is_feasible(self) -> bool:
        """Check if all tasks fit within the available time budget."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (highest first), then by duration."""
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why the plan is ordered as it is."""
        pass
