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

Phase 4 Enhancements:
- Sorting tasks by scheduled time
- Filtering tasks by status or pet
- Automatic recurring task creation
- Advanced conflict detection
"""

from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 (low) to 5 (high)
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # e.g. "daily", "weekly"
    status: str = "pending"  # "pending", "completed", "skipped"
    scheduled_time: Optional[str] = None  # e.g. "09:00" in HH:MM format

    def is_due_today(self) -> bool:
        """Check if this task is due today based on recurrence pattern."""
        # If task is completed or skipped, it's not due again until recurrence resets
        if self.status in ["completed", "skipped"]:
            return self.recurring
        # If task is pending, it's due today
        if self.status == "pending":
            return True
        return False

    def mark_complete(self) -> "Task":
        """Mark this task as completed and return the next occurrence if recurring."""
        self.status = "completed"
        # Auto-create next occurrence for recurring tasks
        if self.recurring:
            return self.create_next_occurrence()
        return None

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create a new instance of this task for the next occurrence (for recurring tasks)."""
        if not self.recurring:
            return None
        # Create a copy with reset status for next occurrence
        next_task = deepcopy(self)
        next_task.status = "pending"
        return next_task

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

    def filter_tasks_by_status(self, status: str) -> list[Task]:
        """Filter this pet's tasks by status (pending, completed, skipped)."""
        return [task for task in self.tasks if task.status == status]

    def filter_tasks_by_priority(self, priority: int) -> list[Task]:
        """Filter this pet's tasks by priority level."""
        return [task for task in self.tasks if task.priority == priority]


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
        self.scheduled_tasks = {}  # Dictionary to track scheduled time slots

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
        """Detect time budget overages and task scheduling conflicts."""
        conflicts = []
        total_time = sum(task.duration_minutes for task in tasks)
        
        # Check time budget
        if total_time > self.time_budget:
            overrun = total_time - self.time_budget
            conflicts.append(
                f"Total time required ({total_time} min) exceeds available time "
                f"({self.time_budget} min) by {overrun} minutes."
            )
        
        # Check for time-based conflicts (identical scheduled times)
        time_slots = {}
        for task in tasks:
            if task.scheduled_time:
                if task.scheduled_time in time_slots:
                    conflicts.append(
                        f"Time conflict: '{time_slots[task.scheduled_time].name}' and "
                        f"'{task.name}' both scheduled at {task.scheduled_time}"
                    )
                else:
                    time_slots[task.scheduled_time] = task
        
        return conflicts

    def is_feasible(self) -> bool:
        """Check if all tasks fit within the available time budget."""
        all_tasks = self.owner.get_all_tasks()
        total_time = sum(task.duration_minutes for task in all_tasks)
        return total_time <= self.time_budget

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (highest first), then by duration (shortest first)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by scheduled time (HH:MM format). Unscheduled tasks go last."""
        scheduled = [t for t in tasks if t.scheduled_time]
        unscheduled = [t for t in tasks if not t.scheduled_time]
        
        # Sort scheduled tasks by time string (lexicographic works for HH:MM)
        scheduled.sort(key=lambda t: t.scheduled_time)
        
        return scheduled + unscheduled

    def filter_tasks_by_status(self, tasks: list[Task], status: str) -> list[Task]:
        """Filter tasks by completion status (pending, completed, skipped)."""
        return [task for task in tasks if task.status == status]

    def filter_tasks_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Filter tasks by pet name."""
        filtered = []
        for pet in self.owner.pets:
            if pet.name == pet_name:
                filtered.extend([t for t in pet.tasks if t in tasks])
        return filtered

    def process_recurring_tasks(self) -> dict:
        """
        Process recurring tasks: mark completed ones and create next occurrences.
        Returns a dict with pet names and newly created tasks.
        """
        new_tasks = {}
        
        for pet in self.owner.pets:
            pet_name = pet.name
            new_tasks[pet_name] = []
            
            # Find completed recurring tasks
            completed_recurring = [
                t for t in pet.tasks
                if t.status == "completed" and t.recurring
            ]
            
            # Create next occurrences
            for task in completed_recurring:
                next_task = task.create_next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                    new_tasks[pet_name].append(next_task)
        
        return new_tasks

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why the plan is ordered as it is."""
        if not plan:
            return "No tasks scheduled. Either no tasks exist or time budget is insufficient."
        
        explanation = f"Daily Plan for {self.owner.name} ({self.time_budget} min available):\n\n"
        total_time = 0
        
        for i, task in enumerate(plan, 1):
            total_time += task.duration_minutes
            time_info = f" @ {task.scheduled_time}" if task.scheduled_time else ""
            explanation += (
                f"{i}. {task.name}{time_info} ({task.duration_minutes} min) - "
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
