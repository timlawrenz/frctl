#!/usr/bin/env python3
"""Demo of plan persistence functionality."""

from pathlib import Path
from frctl.planning import Plan, Goal, GoalStatus, PlanStore

def main():
    print("=" * 80)
    print("Plan Persistence Demo")
    print("=" * 80)
    
    # Create a temporary store for demo
    demo_path = Path("/tmp/frctl-demo/.frctl/plans")
    store = PlanStore(base_path=demo_path)
    
    print(f"\n📁 Storage location: {demo_path}")
    print(f"   Plans dir: {store.plans_dir}")
    print(f"   Archive dir: {store.archive_dir}")
    print(f"   Index file: {store.index_file}")
    
    # Create a sample plan
    print("\n1️⃣  Creating a sample plan...")
    plan = Plan(id="demo-plan-001", root_goal_id="root")
    
    root = Goal(
        id="root",
        description="Build a REST API for user management",
        status=GoalStatus.COMPLETE,
        depth=0,
    )
    
    child1 = Goal(
        id="goal-1",
        description="Design database schema",
        status=GoalStatus.ATOMIC,
        parent_id="root",
        depth=1,
    )
    
    child2 = Goal(
        id="goal-2",
        description="Implement authentication",
        status=GoalStatus.ATOMIC,
        parent_id="root",
        depth=1,
    )
    
    child3 = Goal(
        id="goal-3",
        description="Create API endpoints",
        status=GoalStatus.PENDING,
        parent_id="root",
        depth=1,
    )
    
    root.add_child("goal-1")
    root.add_child("goal-2")
    root.add_child("goal-3")
    
    plan.add_goal(root)
    plan.add_goal(child1)
    plan.add_goal(child2)
    plan.add_goal(child3)
    
    print(f"   Created plan: {plan.id}")
    print(f"   Goals: {len(plan.goals)}")
    print(f"   Atomic: {len(plan.get_atomic_goals())}")
    
    # Save the plan
    print("\n2️⃣  Saving plan to disk...")
    plan_path = store.save(plan)
    print(f"   ✅ Saved to: {plan_path}")
    print(f"   File exists: {plan_path.exists()}")
    print(f"   File size: {plan_path.stat().st_size} bytes")
    
    # Check index
    print("\n3️⃣  Checking plan index...")
    index = store._load_index()
    plan_meta = index.get("demo-plan-001")
    if plan_meta:
        print(f"   ✅ Plan in index:")
        print(f"      Description: {plan_meta['description']}")
        print(f"      Status: {plan_meta['status']}")
        print(f"      Goal count: {plan_meta['goal_count']}")
        print(f"      Atomic count: {plan_meta['atomic_count']}")
    
    # Load the plan
    print("\n4️⃣  Loading plan from disk...")
    loaded = store.load("demo-plan-001")
    if loaded:
        print(f"   ✅ Loaded plan: {loaded.id}")
        print(f"   Goals loaded: {len(loaded.goals)}")
        print(f"   Root goal: {loaded.get_root_goal().description}")
        print(f"   Children: {len(loaded.get_root_goal().child_ids)}")
    
    # List plans
    print("\n5️⃣  Listing all plans...")
    plans = store.list_plans()
    print(f"   Total plans: {len(plans)}")
    for p in plans:
        print(f"   - {p['id']}: {p['description'][:50]}... ({p['status']})")
    
    # Create another plan
    print("\n6️⃣  Creating second plan...")
    plan2 = Plan(id="demo-plan-002", root_goal_id="root2")
    plan2.add_goal(Goal(
        id="root2",
        description="Implement CI/CD pipeline",
        status=GoalStatus.PENDING,
        depth=0,
    ))
    plan2.status = "in_progress"
    store.save(plan2)
    print(f"   ✅ Saved: {plan2.id}")
    
    # List by status
    print("\n7️⃣  Filtering plans by status...")
    in_progress = store.list_plans(status="in_progress")
    complete = store.list_plans(status="complete")
    print(f"   In progress: {len(in_progress)}")
    print(f"   Complete: {len(complete)}")
    
    # Export
    print("\n8️⃣  Exporting plan...")
    export_path = Path("/tmp/exported-plan.json")
    success = store.export("demo-plan-001", export_path)
    if success:
        print(f"   ✅ Exported to: {export_path}")
        print(f"   File size: {export_path.stat().st_size} bytes")
    
    # Archive
    print("\n9️⃣  Archiving plan...")
    archive_path = store.archive("demo-plan-001")
    if archive_path:
        print(f"   ✅ Archived to: {archive_path}")
        print(f"   Original removed: {not store.exists('demo-plan-001')}")
    
    # Final listing
    print("\n🔟 Final plan list...")
    final_plans = store.list_plans()
    print(f"   Remaining plans: {len(final_plans)}")
    for p in final_plans:
        print(f"   - {p['id']}: {p['description'][:40]}... ({p['status']})")
    
    print("\n" + "=" * 80)
    print("✅ Demo complete!")
    print(f"📁 Check files at: {demo_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
