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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
