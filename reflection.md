# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet** — The owner enters basic info about their pet (name, species, age) so the system knows who needs care.
2. **Add or edit a care task** — The owner creates a task (e.g., "morning walk, 30 min, high priority") with a duration and priority level attached to a specific pet.
3. **Generate today's plan** — The owner requests a daily schedule, and the system orders tasks by priority and available time, displaying the plan and explaining its reasoning.

**Four-Class Architecture:**

- **Task** (Dataclass) — Represents a single care activity with attributes (*name, duration_minutes, priority, recurring, recurrence_pattern, status*) and methods (*is_due_today(), mark_complete(), get_priority_label()*). Status tracking enables completion logging and future plan refinement.

- **Pet** (Dataclass) — Holds a specific pet's info (*name, species, age*) and manages its task list. Methods include *add_task(), remove_task(), get_daily_tasks()* to filter tasks due today.

- **Owner** (Dataclass) — Represents the pet owner with attributes (*name, available_minutes, pets*). Aggregates all pets and provides methods like *add_pet(), remove_pet(), get_all_tasks(), get_total_required_minutes()* to compute total care time needed.

- **Scheduler** (Regular class) — The "decision engine" that takes an Owner and orchestrates the daily plan. Core methods: *generate_plan()* (sorts tasks by priority within time budget), *detect_conflicts()* (flags time overages), *is_feasible()* (checks if all tasks fit), *sort_by_priority()* (ranks tasks), and *explain_plan()* (justifies ordering).

**Design principles:**
- **Separation of concerns**: Data holders (Task, Pet, Owner) are dataclasses; orchestration logic lives in Scheduler
- **Composability**: Scheduler receives a complete Owner object (which has all pets and tasks), enabling single-pass plan generation
- **Transparency**: Status field on Task + explain_plan() method support reasoning and debugging

**b. Design changes**

**Enhancements made during skeleton creation:**

1. **Added status tracking to Task** — Original design lacked task state management. Added `status: str` field ("pending", "completed", "skipped") to enable completion logging and future plan refinement based on user activity patterns.

2. **Expanded Owner methods** — Added `remove_pet()` and `get_total_required_minutes()` to support pet management and feasibility checking before scheduling.

3. **Expanded Pet methods** — Added `remove_task()` and `get_daily_tasks()` to enable task management and prepare for recurring task filtering.

4. **Added Scheduler utility methods** — Separated concerns into `is_feasible()` (boolean check), `sort_by_priority()` (reusable sorting), and `detect_conflicts()` to make the logic more testable and composable than a monolithic `generate_plan()`.

5. **Added Task helper methods** — `is_due_today()` (recurrence filtering), `mark_complete()` (status update), and `get_priority_label()` (UI-friendly display) make Task more self-contained and reduce Scheduler's complexity.

**No relationship changes** — The 1-to-many relationships (Owner→Pets, Pet→Tasks) remained as designed. The Scheduler composition pattern was confirmed as optimal for single Owner scheduling.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers the following constraints:

1. **Time Budget** (Primary) — All tasks must fit within the owner's available_minutes. This is the hard constraint that prevents over-scheduling.

2. **Task Priority** (Primary) — Tasks are ranked 1-5, where 5 is "Critical" (e.g., feeding) and 1 is "Low" (e.g., optional play). Higher priority tasks are always scheduled first.

3. **Task Duration** (Secondary) — Among equal-priority tasks, shorter tasks are scheduled first to maximize task count. This follows the "Shortest Job First" (SJF) algorithm principle.

4. **Recurring Pattern** (Secondary) — Tasks marked as recurring automatically generate new occurrences when completed, enabling multi-day scheduling support.

5. **Scheduled Time** (Tertiary, Phase 4) — Tasks with a specific scheduled_time (HH:MM format, e.g., "08:00") are preferred in order and checked for conflicts.

**Design rationale:**
- Time and priority are non-negotiable: a scheduler must respect the owner's availability and pet needs.
- Duration matters after priority: scheduling 5 easy tasks is better than scheduling 1 hard task if both take the same total time and have equal priority.
- Recurring patterns reduce manual re-entry: marking a task "recurring=True" with "daily" pattern automates tomorrow's plan.
- Scheduled times add realism: some tasks (dog walks, feeding times) should happen at specific times, not randomly.

**b. Tradeoffs**

**Tradeoff 1: Time-Slot Conflict Detection (Exact Match Only)**
- **What**: The scheduler detects conflicts when two tasks have identical scheduled_time values (e.g., both at "08:00"). It does NOT detect overlapping durations (e.g., "08:00-08:30" overlapping with "08:15-08:45" both scheduled for 8:00).
- **Why reasonable**: Owners may want to run tasks in parallel (e.g., "start morning walk at 8:00, also feed at 8:00 — it takes 5 minutes so finish at 8:05"). Exact-time matching identifies clear conflicts without over-constraining. Full duration overlap detection would be complex and may not match real pet-care workflows.
- **Trade**: Simplicity vs. precision. We chose simplicity to keep the code maintainable and the UX clear.

**Tradeoff 2: Greedy Priority-Based Scheduling (vs. Optimal Bin Packing)**
- **What**: `generate_plan()` uses a greedy "sort by priority, then by duration" approach and stuffs tasks into the time budget from highest to lowest priority. This does NOT guarantee the globally optimal assignment (e.g., it may reject a low-priority 60-minute task even though swapping two medium-priority tasks could fit more total time).
- **Why reasonable**: Pet care is inherently ordered: critical needs (feeding) > high needs (walks) > nice-to-haves (play). A greedy approach respects this human priority order and produces a defensible, understandable plan. The owner can see exactly why each task was chosen.
- **Trade**: Optimality vs. transparency. We chose transparency because pet owners need to trust and understand the schedule, not just see the "mathematically optimal" solution.

**Tradeoff 3: Shallow Task Filtering (vs. Complex Query Language)**
- **What**: The scheduler offers simple filter methods (`filter_tasks_by_status()`, `filter_tasks_by_pet()`, `filter_tasks_by_priority()`) that are Boolean AND operations on single fields. It does NOT support complex queries like "all critical tasks for Max that are not completed" in a single call.
- **Why reasonable**: Pet care use cases are simple (list Max's tasks, show pending tasks, etc.). Adding a query language (e.g., SQL-like filtering) would over-engineer for the current scope. Users can compose filters in Python if needed.
- **Trade**: Expressiveness vs. simplicity. We chose simplicity to keep the API discoverable and the code maintainable.

**Tradeoff 4: Recurring Task Cloning (Deep Copy vs. Factory Pattern)**
- **What**: `create_next_occurrence()` uses `deepcopy()` to clone a recurring task, preserving all attributes and resetting status. It does NOT use a factory pattern or template method.
- **Why reasonable**: Recurring tasks should inherit all properties (duration, priority, recurring flag, scheduled_time) from the completed task. A deep copy preserves this naturally. A factory pattern would require more boilerplate and would be overkill for simple duplication.
- **Trade**: Simplicity vs. extensibility. We chose simplicity because recurring tasks are simple at this stage.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
