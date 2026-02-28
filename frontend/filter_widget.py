from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
                                     QPushButton, QLineEdit, QListWidget, QCheckBox,
                                     QDoubleSpinBox, QWidget)
from PyQt5.QtCore import pyqtSignal, Qt
from backend.data_manager import DataManager
from backend.utils import parse_numeric
from draggable_widget import DraggableWidget



class FilterWidget(DraggableWidget):
    """Draggable filter widget that can be placed on tabs"""
    
    filter_changed = pyqtSignal()
    
    def __init__(self, manager: DataManager, tab_id: str, filter_index: int = 0):
        super().__init__(title="Filter")
        self.manager = manager
        self.tab_id = tab_id
        self.filter_index = filter_index
        
        # Main layout
        layout = QVBoxLayout()
        self.content_layout.addLayout(layout)
        
        # Column selection
        col_row = QHBoxLayout()
        col_row.addWidget(QLabel("Column:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.manager.get_columns())
        self.column_combo.currentTextChanged.connect(self._on_column_changed)
        col_row.addWidget(self.column_combo)
        layout.addLayout(col_row)
        
        # Operator selection
        op_row = QHBoxLayout()
        op_row.addWidget(QLabel("Operator:"))
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["==", "!=", ">", "<", ">=", "<=", "contains", "not contains"])
        self.operator_combo.currentTextChanged.connect(self._on_operator_changed)
        op_row.addWidget(self.operator_combo)
        layout.addLayout(op_row)
        
        # Value input area (will change based on column type)
        self.value_widget_container = QWidget()
        self.value_widget_layout = QVBoxLayout(self.value_widget_container)
        self.value_widget_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.value_widget_container)
        
        # Current value widget
        self.value_widget = None
        
        # Apply button
        apply_btn = QPushButton("Apply Filter")
        apply_btn.clicked.connect(self._on_apply)
        layout.addWidget(apply_btn)
        
        # Initialize value widget based on first column
        if self.manager.get_columns():
            self._update_value_widget()
        
        self.setMinimumSize(250, 200)
    
    def _on_column_changed(self):
        """Called when column selection changes"""
        self._update_value_widget()
    
    def _on_operator_changed(self):
        """Called when operator changes"""
        # Some operators may affect which value widgets are appropriate
        pass
    
    def _update_value_widget(self):
        """Update the value input widget based on selected column type"""
        column = self.column_combo.currentText()
        if not column:
            return
        
        # Clear existing widget
        if self.value_widget:
            self.value_widget_layout.removeWidget(self.value_widget)
            self.value_widget.deleteLater()
            self.value_widget = None
        
        # Determine column type
        dtype = self.manager.get_column_dtype(column)
        unique_values = self.manager.get_unique_values(column)
        
        # Decide widget type
        is_numeric = 'int' in dtype or 'float' in dtype
        is_categorical = len(unique_values) <= 20 and len(unique_values) > 0
        
        if is_categorical and not is_numeric:
            # Multi-select list for categorical data
            self.value_widget = QListWidget()
            self.value_widget.setSelectionMode(QListWidget.MultiSelection)
            for value in unique_values:
                self.value_widget.addItem(str(value))
            self.value_widget.setMaximumHeight(150)
        elif is_numeric:
            # Numeric spinner
            self.value_widget = QDoubleSpinBox()
            self.value_widget.setDecimals(2)
            self.value_widget.setMinimum(-999999999)
            self.value_widget.setMaximum(999999999)
            if unique_values:
                try:
                    self.value_widget.setValue(float(unique_values[0]))
                except (ValueError, TypeError):
                    self.value_widget.setValue(0)
        else:
            # Text input for everything else
            self.value_widget = QLineEdit()
            if unique_values:
                self.value_widget.setText(str(unique_values[0]))
        
        self.value_widget_layout.addWidget(self.value_widget)
    
    def _get_selected_values(self):
        """Get the current value(s) from the value widget"""
        if isinstance(self.value_widget, QListWidget):
            # Multi-select list
            selected_items = self.value_widget.selectedItems()
            if selected_items:
                return [item.text() for item in selected_items]
            return []
        elif isinstance(self.value_widget, QDoubleSpinBox):
            return self.value_widget.value()
        elif isinstance(self.value_widget, QLineEdit):
            return parse_numeric(self.value_widget.text()) 
        return ""
    
    def _on_apply(self):
        """Apply the current filter configuration"""
        column = self.column_combo.currentText()
        operator = self.operator_combo.currentText()
        values = self._get_selected_values()

        
        if not column or not values:
            return
        
        # Handle multiple values (from multi-select)
        if isinstance(values, list) and len(values) > 0:
            # For multi-select, we'll apply each value as a separate filter
            # or combine them with OR logic
            # For simplicity, let's just use the first value for now
            # TODO: Enhance to support multiple values properly
            value = values[0]
        else:
            value = values
        
        # Update or add filter
        filters = self.manager.get_filters(self.tab_id)
        if self.filter_index < len(filters):
            self.manager.update_filter(self.tab_id, self.filter_index, column, operator, value)
        else:
            self.manager.add_filter(self.tab_id, column, operator, value)
        
        self.filter_changed.emit()
    
    def get_state(self) -> dict:
        """Get the state for saving"""
        return {
            'column': self.column_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'position': self.get_position_data(),
            'filter_index': self.filter_index
        }