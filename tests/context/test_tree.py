"""Tests for Context Tree."""

import pytest
from frctl.context import ContextTree, ContextNode


class TestContextNode:
    """Test ContextNode class."""
    
    def test_create_node(self):
        """Test basic node creation."""
        node = ContextNode(
            goal_id="test-goal",
            parent_goal_id="parent-goal",
            token_limit=4096,
        )
        
        assert node.goal_id == "test-goal"
        assert node.parent_goal_id == "parent-goal"
        assert node.tokens_used == 0
        assert node.token_limit == 4096
        assert node.digest is None
    
    def test_token_tracking(self):
        """Test token usage tracking."""
        node = ContextNode(goal_id="test", token_limit=1000)
        
        assert node.remaining_tokens() == 1000
        assert not node.is_over_limit()
        
        node.add_tokens(300)
        assert node.tokens_used == 300
        assert node.remaining_tokens() == 700
        
        node.add_tokens(800)
        assert node.tokens_used == 1100
        assert node.is_over_limit()
        assert node.remaining_tokens() == 0
    
    def test_context_content(self):
        """Test context content storage."""
        node = ContextNode(
            goal_id="test",
            global_context={"project": "frctl", "version": "0.1"},
            parent_intent="Build a feature",
            local_context={"task": "implement", "priority": "high"},
        )
        
        assert node.global_context["project"] == "frctl"
        assert node.parent_intent == "Build a feature"
        assert node.local_context["task"] == "implement"


class TestContextTree:
    """Test ContextTree class."""
    
    def test_create_tree(self):
        """Test basic tree creation."""
        tree = ContextTree(
            default_token_limit=4096,
            global_context={"project": "frctl"},
        )
        
        assert tree.default_token_limit == 4096
        assert tree.global_context["project"] == "frctl"
        assert tree.get_total_tokens() == 0
    
    def test_create_root_context(self):
        """Test creating root context."""
        tree = ContextTree(global_context={"project": "frctl"})
        
        root = tree.create_root_context("root-goal")
        
        assert root.goal_id == "root-goal"
        assert root.parent_goal_id is None
        assert root.global_context["project"] == "frctl"
        assert root.tokens_used == 0
        
        # Verify it's stored in the tree
        assert tree.get_context("root-goal") == root
    
    def test_create_child_context(self):
        """Test creating child context with hydration."""
        tree = ContextTree(global_context={"project": "frctl"})
        
        # Create root
        root = tree.create_root_context("root")
        
        # Create child
        child = tree.create_child_context(
            goal_id="child",
            parent_goal_id="root",
            parent_intent="Build feature X",
        )
        
        assert child.goal_id == "child"
        assert child.parent_goal_id == "root"
        assert child.parent_intent == "Build feature X"
        assert child.global_context["project"] == "frctl"
    
    def test_create_child_without_parent_fails(self):
        """Test that creating child without parent fails."""
        tree = ContextTree()
        
        with pytest.raises(ValueError, match="Parent context not found"):
            tree.create_child_context(
                goal_id="child",
                parent_goal_id="nonexistent",
            )
    
    def test_hydrate_context(self):
        """Test context hydration."""
        tree = ContextTree(global_context={"project": "frctl", "version": "0.1"})
        
        # Create root and child
        root = tree.create_root_context("root")
        tree.set_local_context("root", "phase", "planning")
        
        child = tree.create_child_context(
            goal_id="child",
            parent_goal_id="root",
            parent_intent="Implement feature",
        )
        tree.set_local_context("child", "task", "coding")
        
        # Hydrate child context
        hydrated = tree.hydrate_context("child")
        
        assert hydrated["global"]["project"] == "frctl"
        assert hydrated["global"]["version"] == "0.1"
        assert hydrated["parent_intent"] == "Implement feature"
        assert hydrated["local"]["task"] == "coding"
    
    def test_hydrate_root_context(self):
        """Test hydrating root context (no parent intent)."""
        tree = ContextTree(global_context={"project": "frctl"})
        
        root = tree.create_root_context("root")
        tree.set_local_context("root", "stage", "initial")
        
        hydrated = tree.hydrate_context("root")
        
        assert hydrated["global"]["project"] == "frctl"
        assert hydrated["local"]["stage"] == "initial"
        assert "parent_intent" not in hydrated
    
    def test_dehydrate_context(self):
        """Test context dehydration with digest."""
        tree = ContextTree()
        root = tree.create_root_context("root")
        
        # Dehydrate with digest
        digest = "Completed feature X with 3 subtasks: A, B, C"
        tree.dehydrate_context("root", digest=digest, digest_tokens=12)
        
        node = tree.get_context("root")
        assert node.digest == digest
        assert node.digest_tokens == 12
    
    def test_update_token_usage(self):
        """Test updating token usage."""
        tree = ContextTree(default_token_limit=1000)
        root = tree.create_root_context("root")
        
        tree.update_token_usage("root", 300)
        assert tree.get_context("root").tokens_used == 300
        
        tree.update_token_usage("root", 200)
        assert tree.get_context("root").tokens_used == 500
        
        assert tree.get_total_tokens() == 500
    
    def test_set_global_context(self):
        """Test setting global context propagates to all nodes."""
        tree = ContextTree()
        root = tree.create_root_context("root")
        child = tree.create_child_context("child", "root")
        
        # Set global context
        tree.set_global_context("constraint", "use Python 3.11+")
        
        # Should propagate to all nodes
        assert tree.get_context("root").global_context["constraint"] == "use Python 3.11+"
        assert tree.get_context("child").global_context["constraint"] == "use Python 3.11+"
    
    def test_set_local_context(self):
        """Test setting local context."""
        tree = ContextTree()
        root = tree.create_root_context("root")
        child = tree.create_child_context("child", "root")
        
        tree.set_local_context("root", "key", "value1")
        tree.set_local_context("child", "key", "value2")
        
        # Local context should not propagate
        assert tree.get_context("root").local_context["key"] == "value1"
        assert tree.get_context("child").local_context["key"] == "value2"
    
    def test_get_total_tokens(self):
        """Test calculating total tokens across tree."""
        tree = ContextTree()
        
        root = tree.create_root_context("root")
        child1 = tree.create_child_context("child1", "root")
        child2 = tree.create_child_context("child2", "root")
        
        tree.update_token_usage("root", 100)
        tree.update_token_usage("child1", 200)
        tree.update_token_usage("child2", 300)
        
        assert tree.get_total_tokens() == 600
    
    def test_get_tree_stats(self):
        """Test getting tree statistics."""
        tree = ContextTree(default_token_limit=1000)
        
        # Empty tree
        stats = tree.get_tree_stats()
        assert stats["total_nodes"] == 0
        assert stats["total_tokens"] == 0
        
        # Tree with nodes
        root = tree.create_root_context("root")
        child1 = tree.create_child_context("child1", "root")
        child2 = tree.create_child_context("child2", "root")
        
        tree.update_token_usage("root", 500)
        tree.update_token_usage("child1", 800)
        tree.update_token_usage("child2", 1200)  # Over limit
        
        stats = tree.get_tree_stats()
        assert stats["total_nodes"] == 3
        assert stats["total_tokens"] == 2500
        assert stats["avg_tokens_per_node"] == pytest.approx(833.33, rel=0.01)
        assert stats["max_tokens"] == 1200
        assert stats["nodes_over_limit"] == 1
    
    def test_context_isolation(self):
        """Test that sibling contexts are isolated."""
        tree = ContextTree(global_context={"project": "frctl"})
        
        root = tree.create_root_context("root")
        child1 = tree.create_child_context("child1", "root", "Task A")
        child2 = tree.create_child_context("child2", "root", "Task B")
        
        # Set different local contexts
        tree.set_local_context("child1", "approach", "method1")
        tree.set_local_context("child2", "approach", "method2")
        
        # Siblings should not see each other's local context
        ctx1 = tree.hydrate_context("child1")
        ctx2 = tree.hydrate_context("child2")
        
        assert ctx1["local"]["approach"] == "method1"
        assert ctx2["local"]["approach"] == "method2"
        assert ctx1["parent_intent"] == "Task A"
        assert ctx2["parent_intent"] == "Task B"
        
        # But both should see global context
        assert ctx1["global"]["project"] == "frctl"
        assert ctx2["global"]["project"] == "frctl"
    
    def test_serialize_deserialize(self):
        """Test serialization and deserialization."""
        tree = ContextTree(
            default_token_limit=4096,
            global_context={"project": "frctl", "version": "0.1"},
        )
        
        root = tree.create_root_context("root")
        tree.set_local_context("root", "stage", "planning")
        tree.update_token_usage("root", 500)
        
        child = tree.create_child_context("child", "root", "Build feature")
        tree.set_local_context("child", "task", "implement")
        tree.update_token_usage("child", 300)
        tree.dehydrate_context("child", "Completed task", 10)
        
        # Serialize
        data = tree.serialize()
        
        # Deserialize
        restored = ContextTree.deserialize(data)
        
        # Verify structure
        assert restored.default_token_limit == 4096
        assert restored.global_context["project"] == "frctl"
        assert restored.get_total_tokens() == 800
        
        # Verify root
        root_node = restored.get_context("root")
        assert root_node.goal_id == "root"
        assert root_node.tokens_used == 500
        assert root_node.local_context["stage"] == "planning"
        
        # Verify child
        child_node = restored.get_context("child")
        assert child_node.goal_id == "child"
        assert child_node.parent_goal_id == "root"
        assert child_node.parent_intent == "Build feature"
        assert child_node.tokens_used == 300
        assert child_node.digest == "Completed task"
        assert child_node.digest_tokens == 10
    
    def test_deep_hierarchy(self):
        """Test deep context hierarchy."""
        tree = ContextTree(global_context={"project": "frctl"})
        
        # Create 5-level hierarchy
        root = tree.create_root_context("root")
        level1 = tree.create_child_context("l1", "root", "Level 1")
        level2 = tree.create_child_context("l2", "l1", "Level 2")
        level3 = tree.create_child_context("l3", "l2", "Level 3")
        level4 = tree.create_child_context("l4", "l3", "Level 4")
        
        # Each level should have parent intent
        assert tree.get_context("l1").parent_intent == "Level 1"
        assert tree.get_context("l2").parent_intent == "Level 2"
        assert tree.get_context("l3").parent_intent == "Level 3"
        assert tree.get_context("l4").parent_intent == "Level 4"
        
        # All should inherit global context
        for node_id in ["root", "l1", "l2", "l3", "l4"]:
            assert tree.get_context(node_id).global_context["project"] == "frctl"
