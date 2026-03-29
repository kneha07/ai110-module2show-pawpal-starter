"""
PawPal+ Logic Layer — Pet Care Task Scheduling System.

This module implements the core classes for managing pet care tasks and generating
optimized daily schedules. It follows a clear separation of concerns:

- Task: Represents a single care activity with priority and recurrence info.
- Pet: Manages a pet's details and its associated tasks.
- Owner: Aggregates multiple pets and provides unified task access.
- Scheduler: Orchestrates task scheduling based on priority and time constraints.

The Scheduler uses a priority-based algorithm to fit high-priority pet care tasks
within an owner's available time budget, ensuring critical needs are met first.
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
        # If task is completed or skipped, it's not due again until recurrence resets
        if self.status in ["completed", "skipped"]:
            return self.recurring
        # If task is pending, it's due today
        if self.status == "pending":
            return True
        return False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def get_priority_label(self) -> str:
        """Return human-readable priority label (Low, Medium, High, etc.)."""
        priority_map = {
            1: "Low",
            2: "Medium-Low",
            3: "Medium",
            4: "High",
            5: "Critical"
        }
        return priority_map.get(self.priority, "Unknown")


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_daily_tasks(self) -> list[Task]:
        """Return tasks that are due today."""
        return [task for task in self.tasks if task.is_due_today()]


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_total_required_minutes(self) -> int:
        """Calculate total time needed for all tasks across all pets."""
        all_tasks = self.get_all_tasks()
        return sum(task.duration_minutes for task in all_tasks)


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize scheduler with an owner and their available time budget."""
        self.owner = owner
        self.time_budget = owner.available_minutes

    def generate_plan(self) -> list[Task]:
        """Return tasks sorted by priority, respecting the time budget."""
        all_tasks = self.owner.get_all_tasks()
        sorted_tasks = self.sort_by_priority(all_tasks)
        
        # Fit tasks within time budget
        plan = []
        elapsed_time = 0
        for task in sorted_tasks:
            if elapsed_time + task.duration_minutes <= self.time_budget:
                plan.append(task)
                elapsed_time += task.duration_minutes
        
        return plan

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a list of conflict descriptions (e.g. tasks that exceed time budget)."""
        conflicts = []
        total_time = sum(task.duration_minutes for task in tasks)
        
        if total_time > self.time_budget:
            overrun = total_time - self.time_budget
            conflicts.append(
                f"Total time required ({total_time} min) exceeds available time "
                f"({self.time_budget} min) by {overrun} minutes."
            )
        
        return conflicts

    def is_feasible(self) -> bool:
        """Check if all tasks fit within the available time budget."""
        all_tasks = self.owner.get_all_tasks()
        total_time = sum(task.duration_minutes for task in all_tasks)
        return total_time <= self.time_budget

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (highest first), then by duration (shortest first)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why the plan is ordered as it is."""
        if not plan:
            return "No tasks scheduled. Either no tasks exist or time budget is insufficient."
        
        explanation = f"Daily Plan for {self.owner.name} ({self.time_budget} min available):\n\n"
        total_time = 0
        
        for i, task in enumerate(plan, 1):
            total_time += task.duration_minutes
            explanation += (
                f"{i}. {task.name} ({task.duration_minutes} min) - "
                f"Priority: {task.get_priority_label()}\n"
                f"   Cumulative time: {total_time} min\n"
            )
        
        explanation += (
            f"\nReasoning: Tasks are ordered by priority (highest to lowest). "
            f"High-priority tasks ensure critical pet care needs are met first. "
            f"Among equal-priority tasks, shorter tasks are scheduled first to maximize "
            f"the number of tasks completed within your {self.time_budget}-minute budget."
        )
        
        return explanation
