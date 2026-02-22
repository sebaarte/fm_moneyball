from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                     QComboBox, QLineEdit, QLabel, QSpinBox, 
                                     QDoubleSpinBox, QScrollArea, QFrame)
from PyQt5.QtCore import pyqtSignal
from data_manager import DataManager

class FilterWidget(QFrame):
    """Individual filter widget in the filter panel"""
    removed = pyqtSignal(int)
    changed = pyqtSignal(int)
    
    def __init__(self, manager: DataManager, filter_index: int):
        super().__init__()
        self.manager = manager
        self.filter_index = filter_index
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        
        layout = QHBoxLayout(self)
        
        # Column selection
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.manager.get_columns())
        self.column_combo.currentTextChanged.connect(self.on_change)
        layout.addWidget(QLabel("Column:"))
        layout.addWidget(self.column_combo)
        
        # Operator selection
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["==", "!=", ">", "<", ">=", "<=", "contains", "not contains"])
        self.operator_combo.currentTextChanged.connect(self.on_change)
        layout.addWidget(QLabel("Operator:"))
        layout.addWidget(self.operator_combo)
        
        # Value input
        self.value_input = QLineEdit()
        self.value_input.textChanged.connect(self.on_change)
        layout.addWidget(QLabel("Value:"))
        layout.addWidget(self.value_input)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.removed.emit(self.filter_index))
        layout.addWidget(remove_btn)
        
        # Set initial values if filter exists
        if self.filter_index < len(self.manager.get_filters()):
            f = self.manager.get_filters()[self.filter_index]
            self.column_combo.setCurrentText(f.column)
            self.operator_combo.setCurrentText(f.operator)
            self.value_input.setText(str(f.value))
    
    def on_change(self):
        """Called when any input changes"""
        self.changed.emit(self.filter_index)
    
    def get_values(self):
        """Get current filter values"""
        return (self.column_combo.currentText(), 
                self.operator_combo.currentText(), 
                self.value_input.text())

class FilterPanel(QWidget):
    """Panel for managing data filters"""
    filters_changed = pyqtSignal()
    
    def __init__(self, manager: DataManager):
        super().__init__()
        self.manager = manager
        self.filter_widgets = []
        
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Data Filters")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        main_layout.addWidget(title)
        
        # Scrollable area for filters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.filters_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Add filter button
        add_btn = QPushButton("Add Filter")
        add_btn.clicked.connect(self.add_filter)
        main_layout.addWidget(add_btn)
    
    def add_filter(self):
        """Add a new filter widget"""
        filter_index = len(self.filter_widgets)
        widget = FilterWidget(self.manager, filter_index)
        widget.removed.connect(self.remove_filter)
        widget.changed.connect(self.on_filter_changed)
        
        self.filter_widgets.append(widget)
        self.filters_layout.insertWidget(len(self.filter_widgets) - 1, widget)
    
    def remove_filter(self, index: int):
        """Remove a filter by index"""
        if 0 <= index < len(self.filter_widgets):
            widget = self.filter_widgets.pop(index)
            widget.deleteLater()
            
            # Update indices
            for i in range(index, len(self.filter_widgets)):
                self.filter_widgets[i].filter_index = i
            
            # Apply removal in data manager
            self.manager.remove_filter(index)
            self.filters_changed.emit()
    
    def on_filter_changed(self, index: int):
        """Called when a filter widget changes"""
        if index < len(self.filter_widgets):
            column, operator, value = self.filter_widgets[index].get_values()
            self.manager.update_filter(index, column, operator, value)
            self.filters_changed.emit()
    
    def clear_filters(self):
        """Remove all filters"""
        for widget in self.filter_widgets:
            widget.deleteLater()
        self.filter_widgets.clear()
        self.manager.filters.clear()