import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ — Pet Care Schedule Generator")

# Initialize Streamlit session state for persistent data across reruns
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = {}  # Dictionary: pet_name -> Pet object
if "owner_name" not in st.session_state:
    st.session_state.owner_name = ""
if "available_minutes" not in st.session_state:
    st.session_state.available_minutes = 120


st.markdown(
    """
**PawPal+** helps you plan daily pet care tasks based on priority and time availability.
Build your pet care schedule with the system designed in Phase 2!
"""
)

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
# SECTION 3: Task Management
# ============================================================================
st.subheader("3️⃣ Task Management")

if st.session_state.owner is None:
    st.warning("Create an owner first!")
elif not st.session_state.pets:
    st.warning("Add at least one pet first!")
else:
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
        recurring = st.checkbox("Recurring?", key="recurring_check")
    
    if st.button("➕ Add Task", key="add_task_btn"):
        if task_name.strip():
            # Create Task object using Phase 2 logic
            new_task = Task(
                name=task_name,
                duration_minutes=duration,
                priority=priority,
                recurring=recurring,
                recurrence_pattern="daily" if recurring else None
            )
            # Add to the selected pet
            st.session_state.pets[selected_pet].add_task(new_task)
            st.success(f"✅ Task '{task_name}' added to {selected_pet}!")
        else:
            st.error("Task name cannot be empty!")
    
    # Display tasks by pet
    st.markdown("### Tasks by Pet:")
    for pet_name, pet in st.session_state.pets.items():
        if pet.tasks:
            st.markdown(f"**🐾 {pet_name}** ({len(pet.tasks)} tasks)")
            task_info = []
            for task in pet.tasks:
                priority_label = task.get_priority_label()  # Use Phase 2 method
                task_info.append({
                    "Task": task.name,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": priority_label,
                    "Recurring": "✓" if task.recurring else "✗",
                    "Status": task.status
                })
            st.table(task_info)
        else:
            st.caption(f"🐾 {pet_name} — No tasks yet")

st.divider()

# ============================================================================
# SECTION 4: Schedule Generation
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
                st.warning("⚠️ **Conflicts Detected:**")
                for conflict in conflicts:
                    st.write(f"• {conflict}")
            
            # Generate and display the optimized plan
            st.markdown("### ✨ Optimized Daily Plan")
            plan = scheduler.generate_plan()
            
            if plan:
                schedule_info = []
                cumulative_time = 0
                for i, task in enumerate(plan, 1):
                    cumulative_time += task.duration_minutes
                    schedule_info.append({
                        "#": i,
                        "Task": task.name,
                        "Duration": f"{task.duration_minutes} min",
                        "Priority": task.get_priority_label(),
                        "Cumulative": f"{cumulative_time} min"
                    })
                st.table(schedule_info)
                
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

st.divider()

# Footer
st.caption("🐾 PawPal+ — Powered by Phase 2 Backend Logic | Built with Streamlit & Python")
