import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class VisualizationManager:
    """Manages saving and loading of visualization configurations"""
    
    def __init__(self):
        self.current_viz_path: Optional[str] = None
        self.recent_visualizations = []
        self._load_recent()
    
    def save_visualization(self, config: Dict[str, Any], path: str = None) -> bool:
        """Save visualization configuration to JSON file"""
        if path is None:
            path = self.current_viz_path
        
        if path is None:
            return False
        
        try:
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.current_viz_path = path
            self._add_to_recent(path)
            return True
        except Exception as e:
            return False
    
    def load_visualization(self, path: str) -> Optional[Dict[str, Any]]:
        """Load visualization configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            
            self.current_viz_path = path
            self._add_to_recent(path)
            return config
        except Exception as e:
            return None
    
    def auto_save(self, config: Dict[str, Any]) -> bool:
        """Auto-save current visualization"""
        if self.current_viz_path:
            return self.save_visualization(config, self.current_viz_path)
        return False
    
    def _load_recent(self):
        """Load recent visualizations list"""
        recent_file = Path.home() / '.moneyball_recent.json'
        if recent_file.exists():
            try:
                with open(recent_file, 'r') as f:
                    self.recent_visualizations = json.load(f)
            except Exception:
                self.recent_visualizations = []
    
    def _save_recent(self):
        """Save recent visualizations list"""
        recent_file = Path.home() / '.moneyball_recent.json'
        try:
            with open(recent_file, 'w') as f:
                json.dump(self.recent_visualizations, f)
        except Exception:
            pass
    
    def _add_to_recent(self, path: str):
        """Add a path to recent visualizations"""
        if path in self.recent_visualizations:
            self.recent_visualizations.remove(path)
        self.recent_visualizations.insert(0, path)
        self.recent_visualizations = self.recent_visualizations[:10]  # Keep only 10 recent
        self._save_recent()
    
    def get_recent_visualizations(self):
        """Get list of recent visualization paths"""
        # Filter out non-existent files
        self.recent_visualizations = [p for p in self.recent_visualizations if os.path.exists(p)]
        self._save_recent()
        return self.recent_visualizations
    
    def create_config(self, data_source: str, active_tab: str, tabs: list) -> Dict[str, Any]:
        """Create a configuration dictionary from current state"""
        return {
            'version': '1.0',
            'data_source': data_source,
            'active_tab': active_tab,
            'tabs': tabs
        }