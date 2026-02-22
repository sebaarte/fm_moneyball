from PyQt5.QtWidgets import QWidget, QVBoxLayout, QInputDialog
from PyQt5.QtCore import pyqtSignal
from data_manager import DataManager

class VisualizationTab(QWidget):
    """A single visualization tab that contains draggable plots and filters"""
    
    def __init__(self, name: str, manager: DataManager):
        super().__init__()
        self.name = name
        self.manager = manager
        self.charts = []
        self.filters = []
        
        # Use absolute positioning
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
    
    def add_chart(self, chart):
        """Add a chart widget to this tab"""
        chart.setParent(self)
        chart.setGeometry(50 + len(self.charts) * 20, 50 + len(self.charts) * 20, 400, 300)
        chart.show()
        self.charts.append(chart)
    
    def add_filter(self, filter_widget):
        """Add a filter widget to this tab"""
        filter_widget.setParent(self)
        filter_widget.setGeometry(50, 50 + len(self.charts) * 30 + len(self.filters) * 30, 200, 100)
        filter_widget.show()
        self.filters.append(filter_widget)
    
    def remove_chart(self, chart):
        """Remove a chart from this tab"""
        if chart in self.charts:
            self.charts.remove(chart)
    
    def remove_filter(self, filter_widget):
        """Remove a filter from this tab"""
        if filter_widget in self.filters:
            self.filters.remove(filter_widget)
    
    def get_filtered_data(self):
        """Get data filtered by this tab's filters"""
        data = self.manager.get_filtered_data()
        return data
    
    def get_state(self) -> dict:
        """Get the state for saving"""
        charts_state = []
        for chart in self.charts:
            charts_state.append({
                'type': chart.chart_type,
                'x_column': chart.x_column,
                'y_column': chart.y_column if hasattr(chart, 'y_column') else None,
                'position': chart.get_position_data()
            })
        
        filters_state = []
        for f in self.filters:
            column, operator, value = f.get_values()
            filters_state.append({
                'column': column,
                'operator': operator,
                'value': value,
                'position': f.get_position_data()
            })
        
        return {
            'name': self.name,
            'charts': charts_state,
            'filters': filters_state
        }
    
    def set_state(self, state: dict):
        """Restore state from saved data"""
        self.name = state.get('name', self.name)

class TabManager:
    """Manages multiple visualization tabs"""
    
    def __init__(self, manager: DataManager):
        self.manager = manager
        self.tabs = {}
        self.active_tab = None
        self.create_tab("Tab 1")
    
    def create_tab(self, name: str = None) -> VisualizationTab:
        """Create a new tab"""
        if name is None:
            name = f"Tab {len(self.tabs) + 1}"
        
        tab = VisualizationTab(name, self.manager)
        self.tabs[name] = tab
        
        if self.active_tab is None:
            self.active_tab = name
        
        return tab
    
    def rename_tab(self, old_name: str, new_name: str) -> bool:
        """Rename a tab"""
        if old_name in self.tabs:
            self.tabs[new_name] = self.tabs.pop(old_name)
            if self.active_tab == old_name:
                self.active_tab = new_name
            self.tabs[new_name].name = new_name
            return True
        return False
    
    def delete_tab(self, name: str) -> bool:
        """Delete a tab"""
        if name in self.tabs and len(self.tabs) > 1:
            if self.active_tab == name:
                # Switch to another tab
                self.active_tab = list(self.tabs.keys())[0]
            
            self.tabs[name].deleteLater()
            del self.tabs[name]
            return True
        return False
    
    def get_tab(self, name: str) -> VisualizationTab:
        """Get a tab by name"""
        return self.tabs.get(name)
    
    def get_active_tab(self) -> VisualizationTab:
        """Get the currently active tab"""
        if self.active_tab:
            return self.tabs.get(self.active_tab)
        return None
    
    def set_active_tab(self, name: str) -> bool:
        """Set the active tab"""
        if name in self.tabs:
            self.active_tab = name
            return True
        return False
    
    def get_all_tabs(self) -> list:
        """Get all tab names"""
        return list(self.tabs.keys())
    
    def get_state(self) -> dict:
        """Get state of all tabs for saving"""
        tabs_state = []
        for name, tab in self.tabs.items():
            tabs_state.append(tab.get_state())
        
        return {
            'active_tab': self.active_tab,
            'tabs': tabs_state
        }
    
    def clear_all(self):
        """Clear all tabs except the first one"""
        for name in list(self.tabs.keys()):
            if name != "Tab 1":
                self.delete_tab(name)
        self.tabs["Tab 1"].charts.clear()
        self.tabs["Tab 1"].filters.clear()