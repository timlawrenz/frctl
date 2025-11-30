"""Plan persistence for saving/loading plans to/from disk."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from frctl.planning.goal import Plan


class PlanStore:
    """Manages plan persistence to .frctl/plans/ directory.
    
    Features:
    - Save/load plans as JSON
    - Plan indexing for quick lookup
    - Versioning and archiving
    - Backup mechanism
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize plan store.
        
        Args:
            base_path: Base directory for plans (defaults to .frctl/plans in cwd)
        """
        if base_path is None:
            base_path = Path.cwd() / ".frctl" / "plans"
        
        self.base_path = Path(base_path)
        self.plans_dir = self.base_path
        self.archive_dir = self.base_path / "archive"
        self.index_file = self.base_path / "index.json"
        
        # Create directories if they don't exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize index if it doesn't exist
        if not self.index_file.exists():
            self._save_index({})
    
    def save(self, plan: Plan, create_backup: bool = True) -> Path:
        """Save a plan to disk.
        
        Args:
            plan: Plan to save
            create_backup: Whether to create a backup of existing plan
            
        Returns:
            Path to saved plan file
        """
        plan_path = self.plans_dir / f"{plan.id}.json"
        
        # Create backup if plan already exists
        if create_backup and plan_path.exists():
            self._backup_plan(plan.id)
        
        # Update metadata
        plan.updated_at = datetime.now(datetime.now().astimezone().tzinfo or None)
        
        # Save plan as JSON
        plan_data = plan.model_dump(mode='json')
        with open(plan_path, 'w') as f:
            json.dump(plan_data, f, indent=2, default=str)
        
        # Update index
        self._update_index(plan)
        
        return plan_path
    
    def load(self, plan_id: str) -> Optional[Plan]:
        """Load a plan from disk.
        
        Args:
            plan_id: ID of plan to load
            
        Returns:
            Loaded plan or None if not found
        """
        plan_path = self.plans_dir / f"{plan_id}.json"
        
        if not plan_path.exists():
            return None
        
        with open(plan_path, 'r') as f:
            plan_data = json.load(f)
        
        return Plan.model_validate(plan_data)
    
    def list_plans(self, status: Optional[str] = None) -> List[Dict]:
        """List all plans with metadata.
        
        Args:
            status: Filter by status (in_progress, complete, failed)
            
        Returns:
            List of plan metadata dicts
        """
        index = self._load_index()
        plans = list(index.values())
        
        if status:
            plans = [p for p in plans if p.get('status') == status]
        
        # Sort by updated_at descending
        plans.sort(key=lambda p: p.get('updated_at', ''), reverse=True)
        
        return plans
    
    def exists(self, plan_id: str) -> bool:
        """Check if a plan exists.
        
        Args:
            plan_id: Plan ID to check
            
        Returns:
            True if plan exists
        """
        return (self.plans_dir / f"{plan_id}.json").exists()
    
    def delete(self, plan_id: str, archive: bool = True) -> bool:
        """Delete a plan.
        
        Args:
            plan_id: Plan ID to delete
            archive: Whether to archive before deleting
            
        Returns:
            True if deleted successfully
        """
        plan_path = self.plans_dir / f"{plan_id}.json"
        
        if not plan_path.exists():
            return False
        
        # Archive if requested
        if archive:
            self.archive(plan_id)
        else:
            plan_path.unlink()
        
        # Remove from index
        index = self._load_index()
        if plan_id in index:
            del index[plan_id]
            self._save_index(index)
        
        return True
    
    def archive(self, plan_id: str) -> Optional[Path]:
        """Archive a plan.
        
        Args:
            plan_id: Plan ID to archive
            
        Returns:
            Path to archived plan or None if not found
        """
        plan_path = self.plans_dir / f"{plan_id}.json"
        
        if not plan_path.exists():
            return None
        
        # Create archive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.archive_dir / f"{plan_id}_{timestamp}.json"
        
        # Move to archive
        shutil.move(str(plan_path), str(archive_path))
        
        return archive_path
    
    def export(self, plan_id: str, output_path: Path, format: str = "json") -> bool:
        """Export a plan to another format.
        
        Args:
            plan_id: Plan ID to export
            output_path: Where to save exported file
            format: Export format (currently only 'json' supported)
            
        Returns:
            True if exported successfully
        """
        plan = self.load(plan_id)
        if not plan:
            return False
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            plan_data = plan.model_dump(mode='json')
            with open(output_path, 'w') as f:
                json.dump(plan_data, f, indent=2, default=str)
            return True
        
        return False
    
    def _backup_plan(self, plan_id: str) -> Optional[Path]:
        """Create a backup of a plan.
        
        Args:
            plan_id: Plan ID to backup
            
        Returns:
            Path to backup file
        """
        plan_path = self.plans_dir / f"{plan_id}.json"
        
        if not plan_path.exists():
            return None
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.plans_dir / f".{plan_id}.backup_{timestamp}.json"
        
        # Copy to backup
        shutil.copy2(str(plan_path), str(backup_path))
        
        return backup_path
    
    def _update_index(self, plan: Plan) -> None:
        """Update the plan index.
        
        Args:
            plan: Plan to add/update in index
        """
        index = self._load_index()
        
        # Get root goal description
        root_goal = plan.get_root_goal()
        description = root_goal.description if root_goal else ""
        
        index[plan.id] = {
            'id': plan.id,
            'description': description,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'updated_at': plan.updated_at.isoformat(),
            'goal_count': len(plan.goals),
            'atomic_count': len(plan.get_atomic_goals()),
            'max_depth': plan.max_depth,
            'total_tokens': plan.total_tokens,
        }
        
        self._save_index(index)
    
    def _load_index(self) -> Dict:
        """Load the plan index.
        
        Returns:
            Index dictionary mapping plan_id -> metadata
        """
        if not self.index_file.exists():
            return {}
        
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict) -> None:
        """Save the plan index.
        
        Args:
            index: Index dictionary to save
        """
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2, default=str)
