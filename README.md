# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## System Design

```mermaid
classDiagram
    class Owner {
        +str name
        +int available_minutes
        +list[Pet] pets
        +add_pet(pet: Pet)
        +get_all_tasks() list[Task]
    }

    class Pet {
        +str name
        +str species
        +int age
        +list[Task] tasks
        +add_task(task: Task)
    }

    class Task {
        +str name
        +int duration_minutes
        +int priority
        +bool recurring
        +str recurrence_pattern
    }

    class Scheduler {
        +Owner owner
        +int time_budget
        +generate_plan() list[Task]
        +detect_conflicts(tasks: list[Task]) list[str]
        +explain_plan(plan: list[Task]) str
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : schedules for
```

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## Phase 4: Smarter Scheduling (Algorithmic Intelligence)

Building on the core system, Phase 4 adds algorithmic features for more intelligent and flexible scheduling.

### Features Added

#### 🔷 **Smart Sorting by Time**
- `Scheduler.sort_by_time(tasks)` — Sorts tasks by their scheduled_time (HH:MM format)
- Scheduled tasks appear first (in chronological order), followed by unscheduled tasks
- **Example**: Sort morning walks (08:00), feeds (12:00), evening walks (18:00)

#### 🔷 **Flexible Filtering**
- Per-pet filtering: `Pet.filter_tasks_by_status(status)`, `Pet.filter_tasks_by_priority(priority)`
- System-wide filtering: `Scheduler.filter_tasks_by_status(tasks, status)`, `Scheduler.filter_tasks_by_pet(tasks, pet_name)`
- **Example**: Show only pending high-priority tasks for Max, or all completed tasks across all pets

#### 🔷 **Recurring Task Automation**
- `Task.create_next_occurrence()` — Creates a deep copy of a recurring task with status reset to "pending"
- `Task.mark_complete()` — Now returns the next occurrence for recurring tasks (or None for one-time tasks)
- `Scheduler.process_recurring_tasks()` — Auto-creates next occurrences for all completed recurring tasks
- **Example**: Complete "Morning walk" at 8:05 → system automatically creates tomorrow's "Morning walk"

#### 🔷 **Advanced Conflict Detection**
- Enhanced `Scheduler.detect_conflicts()` now checks:
  - **Time-slot conflicts**: Two tasks scheduled at the exact same time (e.g., both at "08:00")
  - **Budget overages**: Total task time exceeds available minutes
  - **Clear messaging**: Each conflict includes the reason and affected tasks
- **Example**: Detect that "Morning walk @ 08:00" conflicts with "Feed Tweety @ 08:00"

### Usage Examples

```python
from pawpal_system import Task, Pet, Owner, Scheduler

# Create a pet with scheduled tasks
max_dog = Pet("Max", "Dog", 5)
max_dog.add_task(Task("Morning walk", 30, 5, scheduled_time="08:00", recurring=True, recurrence_pattern="daily"))
max_dog.add_task(Task("Feed Max", 15, 4, scheduled_time="12:00"))
max_dog.add_task(Task("Play", 20, 3))

owner = Owner("Sarah", 180)
owner.add_pet(max_dog)

scheduler = Scheduler(owner)

# Sort by time
all_tasks = owner.get_all_tasks()
sorted_by_time = scheduler.sort_by_time(all_tasks)
# → [Morning walk @ 08:00, Feed Max @ 12:00, Play (no time)]

# Filter by pet and priority
max_tasks = scheduler.filter_tasks_by_pet(all_tasks, "Max")
high_pri = max_dog.filter_tasks_by_priority(5)
# → [Morning walk, Feed Max]

# Detect conflicts
conflicts = scheduler.detect_conflicts(all_tasks)
# → ["Time conflict: 'Morning walk' and 'Feed Tweety' both scheduled at 08:00"]

# Process recurring tasks
recurring_updates = scheduler.process_recurring_tasks()
# → After completing "Morning walk", next occurrence is auto-created
```

### Test Coverage

Phase 4 includes **14 comprehensive tests** for algorithmic features:
- 2 tests for time-based sorting
- 5 tests for filtering (by status, priority, pet)
- 4 tests for recurring task automation
- 3 tests for conflict detection

**Run tests**: `python3 -m pytest tests/test_pawpal.py::TestPhase4Algorithms -v`

### Design Tradeoffs

See [reflection.md](reflection.md) Section 2b for detailed tradeoff documentation:
- **Time-slot conflicts** (exact match only, not duration overlap) — prioritizes simplicity
- **Greedy scheduling** (not optimal bin packing) — prioritizes transparency
- **Deep copy for recurring tasks** — prioritizes simplicity over extensibility


