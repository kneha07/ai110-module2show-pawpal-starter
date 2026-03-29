"""
Test suite for PawPal+ core classes (Task, Pet, Owner, Scheduler).
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


class TestTask:
    """Tests for the Task class."""
    
    def test_task_completion(self):
        """Verify that mark_complete() changes task status to 'completed'."""
        task = Task("Morning walk", 30, 5)
        
        # Initial status should be "pending"
        assert task.status == "pending"
        
        # Mark as complete
        task.mark_complete()
        
        # Status should now be "completed"
        assert task.status == "completed"
    
    def test_task_priority_label(self):
        """Verify that get_priority_label() returns correct labels."""
        task_critical = Task("Urgent task", 10, 5)
        task_high = Task("High task", 10, 4)
        task_medium = Task("Medium task", 10, 3)
        task_low = Task("Low task", 10, 1)
        
        assert task_critical.get_priority_label() == "Critical"
        assert task_high.get_priority_label() == "High"
        assert task_medium.get_priority_label() == "Medium"
        assert task_low.get_priority_label() == "Low"
    
    def test_task_due_today_pending(self):
        """Verify that a pending task is due today."""
        task = Task("Feed pet", 15, 3, recurring=False)
        assert task.is_due_today() is True
    
    def test_task_due_today_completed_non_recurring(self):
        """Verify that a completed non-recurring task is not due today."""
        task = Task("Feed pet", 15, 3, recurring=False)
        task.mark_complete()
        assert task.is_due_today() is False
    
    def test_task_due_today_completed_recurring(self):
        """Verify that a completed recurring task is still due today."""
        task = Task("Feed pet", 15, 3, recurring=True, recurrence_pattern="daily")
        task.mark_complete()
        assert task.is_due_today() is True


class TestPet:
    """Tests for the Pet class."""
    
    def test_add_task_to_pet(self):
        """Verify that adding a task to a Pet increases the task count."""
        pet = Pet("Buddy", "Dog", 3)
        
        # Initially, pet has no tasks
        assert len(pet.tasks) == 0
        
        # Add a task
        task = Task("Walk", 30, 5)
        pet.add_task(task)
        
        # Task count should increase to 1
        assert len(pet.tasks) == 1
        
        # Verify the task is in the list
        assert task in pet.tasks
    
    def test_add_multiple_tasks(self):
        """Verify that multiple tasks can be added to a pet."""
        pet = Pet("Max", "Dog", 5)
        
        task1 = Task("Morning walk", 30, 5)
        task2 = Task("Feed Max", 15, 4)
        task3 = Task("Playtime", 20, 3)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        assert len(pet.tasks) == 3
    
    def test_remove_task_from_pet(self):
        """Verify that removing a task decreases the task count."""
        pet = Pet("Whiskers", "Cat", 2)
        
        task1 = Task("Feed", 10, 4)
        task2 = Task("Play", 15, 3)
        
        pet.add_task(task1)
        pet.add_task(task2)
        assert len(pet.tasks) == 2
        
        # Remove a task
        pet.remove_task(task1)
        assert len(pet.tasks) == 1
        assert task1 not in pet.tasks
        assert task2 in pet.tasks
    
    def test_get_daily_tasks(self):
        """Verify that get_daily_tasks() returns only pending tasks."""
        pet = Pet("Tweety", "Bird", 1)
        
        task1 = Task("Feed", 5, 5)  # pending
        task2 = Task("Water", 5, 4)  # pending
        task3 = Task("Clean cage", 20, 3)  # pending
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        daily_tasks = pet.get_daily_tasks()
        assert len(daily_tasks) == 3
        
        # Complete one task
        task2.mark_complete()
        daily_tasks = pet.get_daily_tasks()
        assert len(daily_tasks) == 2
        assert task2 not in daily_tasks


class TestOwner:
    """Tests for the Owner class."""
    
    def test_add_pet_to_owner(self):
        """Verify that adding a pet to an Owner increases the pet count."""
        owner = Owner("Alice", 120)
        
        # Initially, owner has no pets
        assert len(owner.pets) == 0
        
        # Add a pet
        pet = Pet("Max", "Dog", 5)
        owner.add_pet(pet)
        
        # Pet count should increase to 1
        assert len(owner.pets) == 1
        assert pet in owner.pets
    
    def test_add_multiple_pets(self):
        """Verify that an owner can have multiple pets."""
        owner = Owner("Bob", 180)
        
        pet1 = Pet("Max", "Dog", 5)
        pet2 = Pet("Whiskers", "Cat", 2)
        pet3 = Pet("Tweety", "Bird", 1)
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        owner.add_pet(pet3)
        
        assert len(owner.pets) == 3
    
    def test_get_all_tasks(self):
        """Verify that get_all_tasks() collects tasks from all pets."""
        owner = Owner("Charlie", 120)
        
        # Create pets with tasks
        pet1 = Pet("Max", "Dog", 5)
        pet1.add_task(Task("Walk", 30, 5))
        pet1.add_task(Task("Feed", 15, 4))
        
        pet2 = Pet("Whiskers", "Cat", 2)
        pet2.add_task(Task("Feed", 10, 4))
        pet2.add_task(Task("Clean box", 10, 5))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 4
    
    def test_get_total_required_minutes(self):
        """Verify that get_total_required_minutes() sums all task durations."""
        owner = Owner("Diana", 120)
        
        pet1 = Pet("Max", "Dog", 5)
        pet1.add_task(Task("Walk", 30, 5))
        pet1.add_task(Task("Feed", 15, 4))
        
        pet2 = Pet("Whiskers", "Cat", 2)
        pet2.add_task(Task("Feed", 10, 4))
        pet2.add_task(Task("Clean box", 10, 5))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        total_minutes = owner.get_total_required_minutes()
        assert total_minutes == 30 + 15 + 10 + 10  # 65 minutes


class TestScheduler:
    """Tests for the Scheduler class."""
    
    def test_scheduler_initialization(self):
        """Verify that Scheduler initializes with correct time budget."""
        owner = Owner("Eve", 150)
        scheduler = Scheduler(owner)
        
        assert scheduler.owner == owner
        assert scheduler.time_budget == 150
    
    def test_is_feasible_true(self):
        """Verify that is_feasible() returns True when tasks fit in budget."""
        owner = Owner("Frank", 120)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        pet.add_task(Task("Play", 20, 3))  # Total: 65 min, budget: 120
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        assert scheduler.is_feasible() is True
    
    def test_is_feasible_false(self):
        """Verify that is_feasible() returns False when tasks exceed budget."""
        owner = Owner("Grace", 60)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 40, 5))
        pet.add_task(Task("Feed", 30, 4))  # Total: 70 min, budget: 60
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        assert scheduler.is_feasible() is False
    
    def test_sort_by_priority(self):
        """Verify that tasks are sorted by priority (highest first), then by duration."""
        owner = Owner("Henry", 200)
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Low priority long", 60, 1),
            Task("High priority short", 10, 5),
            Task("Medium priority", 30, 3),
            Task("High priority long", 50, 5),
        ]
        
        sorted_tasks = scheduler.sort_by_priority(tasks)
        
        # Should be sorted: priority 5 (short first), priority 5 (long), priority 3, priority 1
        assert sorted_tasks[0].name == "High priority short"
        assert sorted_tasks[1].name == "High priority long"
        assert sorted_tasks[2].name == "Medium priority"
        assert sorted_tasks[3].name == "Low priority long"
    
    def test_generate_plan_respects_budget(self):
        """Verify that generate_plan() doesn't exceed the time budget."""
        owner = Owner("Ivy", 50)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        pet.add_task(Task("Play", 20, 3))
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        plan = scheduler.generate_plan()
        
        total_time = sum(task.duration_minutes for task in plan)
        assert total_time <= owner.available_minutes
    
    def test_detect_conflicts(self):
        """Verify that detect_conflicts() identifies time budget overages."""
        owner = Owner("Jack", 100)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 60, 5))
        pet.add_task(Task("Feed", 50, 4))  # Total: 110 min, exceeds budget of 100
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        all_tasks = owner.get_all_tasks()
        conflicts = scheduler.detect_conflicts(all_tasks)
        
        assert len(conflicts) > 0
        assert "exceeds available time" in conflicts[0]
    
    def test_explain_plan(self):
        """Verify that explain_plan() returns a non-empty explanation."""
        owner = Owner("Kate", 100)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        plan = scheduler.generate_plan()
        explanation = scheduler.explain_plan(plan)
        
        assert len(explanation) > 0
        assert owner.name in explanation
        assert "Priority" in explanation
