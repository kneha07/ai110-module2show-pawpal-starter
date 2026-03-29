import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from tabulate import tabulate
import os
from pathlib import Path

# Challenge 3 & 4: Helper function for priority-coded formatting
def get_priority_emoji(priority: int) -> str:
    """Challenge 3: Get emoji indicator for task priority."""
    emoji_map = {
        1: "🟢",  # Low - Green
        2: "🟡",  # Medium-Low - Yellow
        3: "🟠",  # Medium - Orange
        4: "🔴",  # High - Red
        5: "⛔"   # Critical - Blocked
    }
    return emoji_map.get(priority, "⚪")

def format_status_badge(status: str) -> str:
    """Challenge 4: Format status with professional badges."""
    status_map = {
        "pending": "⏳ Pending",
        "completed": "✅ Completed",
        "skipped": "⏭️ Skipped"
    }
    return status_map.get(status, status)

def format_task_table_with_tabulate(tasks: list[Task], show_pet_name: bool = False) -> str:
    """
    Challenge 4: Professional task formatting using tabulate.
    Returns a formatted ASCII table string.
    """
    if not tasks:
        return "No tasks to display"
    
    table_data = []
    for task in tasks:
        priority_emoji = get_priority_emoji(task.priority)
        status_badge = format_status_badge(task.status)
        time_str = task.scheduled_time if task.scheduled_time else "—"
        recurring_str = "🔄 Yes" if task.recurring else "No"
        
        row = [
            f"{priority_emoji} {task.name}",
            f"{task.duration_minutes} min",
            task.get_priority_label(),
            time_str,
            recurring_str,
            status_badge
        ]
        table_data.append(row)
    
    headers = ["Task", "Duration", "Priority", "Time", "Recurring", "Status"]
    return tabulate(table_data, headers=headers, tablefmt="grid")

# Challenge 3 & 4: Helper to create color-coded priority slider display
def create_priority_display(priority: int) -> str:
    """Challenge 3: Create visual priority display with emoji and label."""
    emoji = get_priority_emoji(priority)
    label = {1: "Low", 2: "Med-Low", 3: "Medium", 4: "High", 5: "Critical"}[priority]
    return f"{emoji} {priority}/5 - {label}"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ — Pet Care Schedule Generator")

# Challenge 2: Data persistence file path
DATA_FILE = "pawpal_data.json"

# Initialize Streamlit session state for persistent data across reruns
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = {}  # Dictionary: pet_name -> Pet object
if "owner_name" not in st.session_state:
    st.session_state.owner_name = ""
if "available_minutes" not in st.session_state:
    st.session_state.available_minutes = 120

# Challenge 2: Try to load saved data on startup
@st.cache_resource
def load_initial_data():
    """Load saved data if it exists - Challenge 2: Data Persistence."""
    if os.path.exists(DATA_FILE):
        owner = Owner.load_from_json(DATA_FILE)
        if owner:
            return owner, {pet.name: pet for pet in owner.pets}
    return None, {}

# Only load once at startup
if st.session_state.owner is None and os.path.exists(DATA_FILE):
    st.session_state.owner, st.session_state.pets = load_initial_data()


st.markdown(
    """
**PawPal+** helps you plan daily pet care tasks based on priority and time availability.
Build your pet care schedule with the system designed in Phase 2!
"""
)

# Challenge 2: Data Persistence - Save/Load Controls
st.divider()
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.markdown("### 💾 Data Management (Challenge 2)")
with col2:
    if st.button("💾 Save Data", key="save_data_btn", help="Save current schedule to JSON"):
        if st.session_state.owner:
            if st.session_state.owner.save_to_json(DATA_FILE):
                st.success(f"✅ Data saved to {DATA_FILE}")
            else:
                st.error("❌ Error saving data")
        else:
            st.warning("No data to save yet. Create an owner first!")
with col3:
    if st.button("📂 Load Data", key="load_data_btn", help="Load schedule from JSON"):
        if os.path.exists(DATA_FILE):
            owner = Owner.load_from_json(DATA_FILE)
            if owner:
                st.session_state.owner = owner
                st.session_state.pets = {pet.name: pet for pet in owner.pets}
                st.success("✅ Data loaded from file!")
                st.rerun()
            else:
                st.error("❌ Error loading data")
        else:
            st.warning("No saved data file found")

st.divider()

# ============================================================================
# SECTION 1: Owner Setup
# ============================================================================
st.subheader("1️⃣ Owner Setup")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Jordan", key="owner_name_input")
with col2:
    available_minutes = st.number_input(
        "Available time for pet care (min/day)",
        min_value=10,
        max_value=1440,
        value=120,
        key="available_mins_input"
    )

if st.button("✅ Create/Update Owner", key="create_owner_btn"):
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.owner_name = owner_name
    st.session_state.available_minutes = available_minutes
    st.success(f"✅ Owner '{owner_name}' created with {available_minutes} min/day available!")

if st.session_state.owner:
    st.info(f"📌 **Current Owner:** {st.session_state.owner.name} | **Available Time:** {st.session_state.owner.available_minutes} min")
else:
    st.warning("👆 Create an owner first to get started!")

st.divider()

# ============================================================================
# SECTION 2: Pet Management
# ============================================================================
st.subheader("2️⃣ Pet Management")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="species_select")
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=50, value=3, key="age_input")
    
    if st.button("🐾 Add Pet", key="add_pet_btn"):
        if pet_name in st.session_state.pets:
            st.warning(f"⚠️ Pet '{pet_name}' already exists!")
        else:
            # Create a Pet object using the logic from Phase 2
            new_pet = Pet(name=pet_name, species=species, age=age)
            st.session_state.pets[pet_name] = new_pet
            st.session_state.owner.add_pet(new_pet)  # Add to owner
            st.success(f"✅ Pet '{pet_name}' ({species}) added!")
    
    # Display current pets
    if st.session_state.pets:
        st.markdown("### Your Pets:")
        pet_info = []
        for pname, pet in st.session_state.pets.items():
            pet_info.append({
                "Name": pet.name,
                "Species": pet.species,
                "Age": pet.age,
                "Tasks": len(pet.tasks)
            })
        st.table(pet_info)
    else:
        st.info("No pets yet. Add one above!")

st.divider()

# ============================================================================
# SECTION 3: Task Management (with Phase 4 scheduled_time support)
# ============================================================================
st.subheader("3️⃣ Task Management")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
elif not st.session_state.pets:
    st.warning("Add at least one pet first!")
else:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        selected_pet = st.selectbox(
            "Select pet",
            list(st.session_state.pets.keys()),
            key="pet_select"
        )
    with col2:
        task_name = st.text_input("Task name", value="Morning walk", key="task_name_input")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="duration_input")
    with col4:
        priority = st.selectbox("Priority", [1, 2, 3, 4, 5], format_func=lambda x: {
            1: "🟢 Low (1)",
            2: "🟡 Med-Low (2)",
            3: "🟠 Medium (3)",
            4: "🔴 High (4)",
            5: "🔴 Critical (5)"
        }[x], key="priority_select")
    with col5:
        scheduled_time = st.text_input("Scheduled time (HH:MM, optional)", value="", placeholder="e.g., 08:00", key="scheduled_time_input")
    with col6:
        recurring = st.checkbox("Recurring?", key="recurring_check")
    
    if st.button("➕ Add Task", key="add_task_btn"):
        if task_name.strip():
            # Create Task object using Phase 2 logic + Phase 4 scheduled_time
            scheduled_time_val = scheduled_time.strip() if scheduled_time.strip() else None
            new_task = Task(
                name=task_name,
                duration_minutes=duration,
                priority=priority,
                recurring=recurring,
                recurrence_pattern="daily" if recurring else None,
                scheduled_time=scheduled_time_val
            )
            # Add to the selected pet
            st.session_state.pets[selected_pet].add_task(new_task)
            time_info = f" @ {scheduled_time_val}" if scheduled_time_val else ""
            st.success(f"✅ Task '{task_name}' added to {selected_pet}{time_info}!")
        else:
            st.error("Task name cannot be empty!")
    
    # Display tasks by pet
    st.markdown("### Tasks by Pet:")
    for pet_name, pet in st.session_state.pets.items():
        if pet.tasks:
            st.markdown(f"**🐾 {pet_name}** ({len(pet.tasks)} tasks)")
            # Challenge 4: Use tabulate for professional table formatting
            task_table_str = format_task_table_with_tabulate(pet.tasks)
            st.code(task_table_str, language="text")
        else:
            st.caption(f"🐾 {pet_name} — No tasks yet")

st.divider()

# ============================================================================
# SECTION 4A: Phase 4 Algorithmic Features (Sorting & Filtering)
# ============================================================================
st.subheader("4️⃣ Phase 4: Smart Analytics & Filtering")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
elif not st.session_state.pets:
    st.warning("Add at least one pet first!")
else:
    all_tasks = st.session_state.owner.get_all_tasks()
    
    if not all_tasks:
        st.info("Add tasks to see smart analytics.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📅 By Time", "🔍 By Status", "🐾 By Pet", "⏰ By Priority"])
        
        # Tab 1: Tasks sorted by time
        with tab1:
            st.markdown("### Tasks Sorted by Scheduled Time")
            scheduled_tasks = [t for t in all_tasks if t.scheduled_time]
            if scheduled_tasks:
                sorted_by_time = scheduler.sort_by_time(scheduled_tasks)
                # Challenge 4: Use tabulate for professional formatting
                task_table_str = format_task_table_with_tabulate(sorted_by_time)
                st.code(task_table_str, language="text")
            else:
                st.info("No scheduled tasks yet. Add tasks with times using HH:MM format above.")
        
        # Tab 2: Tasks filtered by status
        with tab2:
            st.markdown("### Tasks Filtered by Status")
            status_filter = st.radio("Status", ["pending", "completed", "skipped"], horizontal=True)
            filtered_tasks = scheduler.filter_tasks_by_status(all_tasks, status_filter)
            if filtered_tasks:
                # Challenge 4: Use tabulate for professional formatting
                task_table_str = format_task_table_with_tabulate(filtered_tasks)
                st.code(task_table_str, language="text")
                st.caption(f"Found {len(filtered_tasks)} task(s) with status '{format_status_badge(status_filter)}'")
            else:
                st.info(f"No tasks found with status '{status_filter}'")
        
        # Tab 3: Tasks filtered by pet
        with tab3:
            st.markdown("### Tasks Filtered by Pet")
            pet_filter = st.selectbox("Filter by pet", list(st.session_state.pets.keys()), key="filter_pet")
            filtered_tasks = scheduler.filter_tasks_by_pet(all_tasks, pet_filter)
            if filtered_tasks:
                # Challenge 4: Use tabulate for professional formatting
                task_table_str = format_task_table_with_tabulate(filtered_tasks)
                st.code(task_table_str, language="text")
                st.caption(f"Found {len(filtered_tasks)} task(s) for {pet_filter}")
            else:
                st.info(f"No tasks found for {pet_filter}")
        
        # Tab 4: Priority distribution
        with tab4:
            st.markdown("### Priority Distribution")
            priority_counts = {}
            for task in all_tasks:
                label = task.get_priority_label()
                priority_counts[label] = priority_counts.get(label, 0) + 1
            
            if priority_counts:
                priority_data = [
                    {"Priority": priority, "Count": count}
                    for priority, count in sorted(priority_counts.items())
                ]
                st.table(priority_data)
                st.bar_chart({p["Priority"]: p["Count"] for p in priority_data})

st.divider()

# ============================================================================
# SECTION 4B: Schedule Generation (Enhanced with Phase 4)
# ============================================================================
st.subheader("4️⃣ Generate Today's Schedule")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
elif not st.session_state.pets:
    st.warning("Add at least one pet first!")
else:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("Click the button below to generate an optimized daily schedule based on priorities and time constraints.")
    
    with col2:
        if st.button("🎯 Generate Schedule", key="generate_schedule_btn"):
            # Use Phase 2 Scheduler logic
            scheduler = Scheduler(st.session_state.owner)
            
            # Check feasibility
            is_feasible = scheduler.is_feasible()
            all_tasks = st.session_state.owner.get_all_tasks()
            total_time = st.session_state.owner.get_total_required_minutes()
            
            # Display summary
            st.markdown("### 📊 Schedule Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tasks", len(all_tasks))
            with col2:
                st.metric("Time Needed", f"{total_time} min")
            with col3:
                st.metric("Time Available", f"{st.session_state.owner.available_minutes} min")
            with col4:
                status = "✅ Feasible" if is_feasible else "⚠️ Tight!"
                st.metric("Feasibility", status)
            
            # Display conflicts if any
            conflicts = scheduler.detect_conflicts(all_tasks)
            if conflicts:
                st.warning("⚠️ **Scheduling Conflicts Detected:** Review these before executing your plan.")
                for i, conflict in enumerate(conflicts, 1):
                    st.write(f"**{i}.** {conflict}")
            else:
                st.success("✅ No conflicts detected! Schedule is clean.")
            
            st.markdown("---")
            st.markdown("### ✨ Optimized Daily Plan")
            plan = scheduler.generate_plan()
            
            if plan:
                # Challenge 4: Use tabulate for professional formatting
                schedule_table_data = []
                cumulative_time = 0
                for i, task in enumerate(plan, 1):
                    cumulative_time += task.duration_minutes
                    priority_emoji = get_priority_emoji(task.priority)
                    schedule_table_data.append([
                        i,
                        f"{priority_emoji} {task.name}",
                        f"{task.duration_minutes} min",
                        task.get_priority_label(),
                        f"{cumulative_time} min"
                    ])
                
                schedule_table_str = tabulate(
                    schedule_table_data,
                    headers=["#", "Task", "Duration", "Priority", "Cumulative"],
                    tablefmt="grid"
                )
                st.code(schedule_table_str, language="text")
                
                # Display cumulative stats
                remaining_time = st.session_state.owner.available_minutes - cumulative_time
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ **Total Scheduled:** {cumulative_time} minutes")
                with col2:
                    st.info(f"⏱️ **Free Time Remaining:** {remaining_time} minutes")
            else:
                st.warning("⚠️ No tasks could fit in the available time budget.")
            
            # Display explanation
            st.markdown("### 💭 Scheduler's Reasoning")
            explanation = scheduler.explain_plan(plan)
            st.info(explanation)
            
            # Challenge 1: Advanced Algorithmic Capability - Next Available Slot Finder
            st.markdown("---")
            st.markdown("### 🎯 Challenge 1: Find Next Available Slot")
            st.markdown("*Advanced algorithmic capability using weighted prioritization*")
            
            new_task_duration = st.number_input(
                "What duration task would you like to fit in? (minutes)",
                min_value=5,
                max_value=240,
                value=30,
                key="next_slot_duration"
            )
            
            if st.button("🔍 Find Next Available Slot", key="find_slot_btn"):
                slot_analysis = scheduler.find_next_available_slot(new_task_duration)
                
                if slot_analysis['feasible']:
                    st.success(f"✅ {slot_analysis['recommendation']}")
                    if slot_analysis['earliest_slot']:
                        start, end = slot_analysis['earliest_slot']
                        st.metric("Suggested Time Window", f"{start} - {end} minutes")
                else:
                    st.warning(f"⚠️ {slot_analysis['recommendation']}")
                
                if slot_analysis['alternative_slots']:
                    st.markdown("**Alternative Options:**")
                    for alt in slot_analysis['alternative_slots']:
                        st.info(f"• {alt['description']} (frees up {alt['time_needed']} min)")
                
                st.metric("Scheduling Feasibility Score", f"{slot_analysis['priority_score']}/100")

st.divider()

# ============================================================================
# SECTION 5: Mark Tasks Complete + Recurring Automation
# ============================================================================
st.subheader("5️⃣ Complete Tasks & Recurrence")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
elif not st.session_state.pets:
    st.warning("Add at least one pet first!")
else:
    all_tasks = st.session_state.owner.get_all_tasks()
    pending_tasks = [t for t in all_tasks if t.status == "pending"]

    if not pending_tasks:
        st.info("No pending tasks to mark complete.")
    else:
        task_options = {f"{t.name} ({t.get_priority_label()})": t for t in pending_tasks}
        selected_label = st.selectbox("Select a task to mark complete", list(task_options.keys()), key="complete_task_select")

        if st.button("✅ Mark as Complete", key="mark_complete_btn"):
            task_to_complete = task_options[selected_label]
            next_occurrence = task_to_complete.mark_complete()

            st.success(f"✅ **'{task_to_complete.name}'** marked as complete!")

            if next_occurrence:
                # Find the pet that owns this task and add the next occurrence
                for pet in st.session_state.owner.pets:
                    if task_to_complete in pet.tasks:
                        pet.add_task(next_occurrence)
                        break
                st.info(
                    f"🔄 **Recurring task auto-scheduled!** "
                    f"Next occurrence of **'{next_occurrence.name}'** has been added to tomorrow's queue."
                )
            else:
                st.caption("One-time task — no recurrence created.")

    # Show task completion summary
    scheduler = Scheduler(st.session_state.owner)
    all_tasks_now = st.session_state.owner.get_all_tasks()
    if all_tasks_now:
        completed = scheduler.filter_tasks_by_status(all_tasks_now, "completed")
        pending = scheduler.filter_tasks_by_status(all_tasks_now, "pending")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pending", len(pending), help="Tasks not yet started")
        with col2:
            st.metric("Completed", len(completed), help="Tasks finished today")
        with col3:
            pct = int(len(completed) / len(all_tasks_now) * 100) if all_tasks_now else 0
            st.metric("Progress", f"{pct}%")

st.divider()

# Footer
st.caption("🐾 PawPal+ — Smart Pet Care Scheduler | Built with Streamlit & Python")
