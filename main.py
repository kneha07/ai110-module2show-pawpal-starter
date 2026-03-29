"""
Demo script for PawPal+ — creates a realistic scenario and displays today's schedule.
"""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create Owner
    owner = Owner("Sarah", available_minutes=180)  # 3 hours available
    
    # Create first pet: Max (Dog)
    max_dog = Pet("Max", "Dog", 5)
    max_dog.add_task(Task("Morning walk", 30, 5, recurring=True, recurrence_pattern="daily"))
    max_dog.add_task(Task("Feed Max", 15, 4))
    max_dog.add_task(Task("Playtime in backyard", 25, 3))
    max_dog.add_task(Task("Evening walk", 30, 5, recurring=True, recurrence_pattern="daily"))
    
    # Create second pet: Whiskers (Cat)
    whiskers_cat = Pet("Whiskers", "Cat", 2)
    whiskers_cat.add_task(Task("Feed Whiskers", 10, 4))
    whiskers_cat.add_task(Task("Clean litter box", 10, 5))
    whiskers_cat.add_task(Task("Play with toy mouse", 15, 2))
    
    # Create third pet: Tweety (Bird)
    tweety_bird = Pet("Tweety", "Bird", 1)
    tweety_bird.add_task(Task("Feed Tweety", 5, 5))
    tweety_bird.add_task(Task("Change water", 5, 4))
    tweety_bird.add_task(Task("Clean cage", 20, 3))
    
    # Add pets to owner
    owner.add_pet(max_dog)
    owner.add_pet(whiskers_cat)
    owner.add_pet(tweety_bird)
    
    # Create scheduler
    scheduler = Scheduler(owner)
    
    # Print system overview
    print("\n" + "=" * 70)
    print("🐾 PAWPAL+ DAILY SCHEDULE GENERATOR 🐾")
    print("=" * 70)
    
    print(f"\n📌 Owner: {owner.name}")
    print(f"📌 Available Time: {owner.available_minutes} minutes")
    print(f"📌 Pets: {', '.join([p.name for p in owner.pets])}")
    
    # Collect all tasks
    all_tasks = owner.get_all_tasks()
    total_time_needed = owner.get_total_required_minutes()
    
    print(f"\n📊 Task Summary:")
    print(f"   Total tasks: {len(all_tasks)}")
    print(f"   Total time needed: {total_time_needed} minutes")
    print(f"   Time available: {owner.available_minutes} minutes")
    print(f"   Feasible? {'✅ Yes' if scheduler.is_feasible() else '❌ No'}")
    
    # Display all tasks grouped by pet
    print(f"\n📋 All Tasks by Pet:")
    for pet in owner.pets:
        print(f"\n   🐕 {pet.name} ({pet.species}, age {pet.age}):")
        for task in pet.tasks:
            print(f"      • {task.name}: {task.duration_minutes}min | Priority: {task.get_priority_label()}")
    
    # Generate and display optimized plan
    plan = scheduler.generate_plan()
    
    print(f"\n✨ TODAY'S OPTIMIZED SCHEDULE ✨")
    print(f"{'─' * 70}")
    
    if not plan:
        print("   ⚠️  No tasks could fit in the available time budget.")
    else:
        cumulative_time = 0
        for i, task in enumerate(plan, 1):
            cumulative_time += task.duration_minutes
            status_icon = "✓"
            print(f"\n   {i}. {status_icon} {task.name}")
            print(f"      Duration: {task.duration_minutes} min | Priority: {task.get_priority_label()}")
            print(f"      Time elapsed: {cumulative_time} min / {owner.available_minutes} min")
    
    print(f"\n{'─' * 70}")
    print(f"   Total scheduled: {sum(t.duration_minutes for t in plan)} minutes")
    print(f"   Remaining free time: {owner.available_minutes - sum(t.duration_minutes for t in plan)} minutes")
    
    # Check for conflicts
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        print(f"\n⚠️  Conflicts Detected:")
        for conflict in conflicts:
            print(f"   • {conflict}")
    
    # Display explanation
    print(f"\n💭 Scheduler's Reasoning:")
    print(f"{'─' * 70}")
    explanation = scheduler.explain_plan(plan)
    for line in explanation.split('\n'):
        print(f"   {line}")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
