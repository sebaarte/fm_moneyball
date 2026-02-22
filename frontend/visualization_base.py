from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
import pandas as pd
from abc import abstractmethod
from data_manager import DataManager
from draggable_widget import DraggableWidget

class ChartWidget(DraggableWidget):
    """Base class for all chart types"""
    
    closed = pyqtSignal()
    
    def __init__(self, chart_type: str, manager: DataManager):
        super().__init__()
        self.chart_type = chart_type
        self.manager = manager
        self.x_column = None
        self.y_column = None
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Control bar
        control_layout = QHBoxLayout()
        
        columns = self.manager.get_columns()
        
        # X axis selection
        control_layout.addWidget(QLabel("X Axis:"))
        self.x_combo = QComboBox()
        self.x_combo.addItems(columns)
        self.x_combo.currentTextChanged.connect(self.on_columns_changed)
        control_layout.addWidget(self.x_combo)
        
        # Y axis selection (not for table view)
        if chart_type != "Table":
            control_layout.addWidget(QLabel("Y Axis:"))
            self.y_combo = QComboBox()
            self.y_combo.addItems(columns)
            if len(columns) > 1:
                self.y_combo.setCurrentIndex(1)
            self.y_combo.currentTextChanged.connect(self.on_columns_changed)
            control_layout.addWidget(self.y_combo)
        
        control_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_chart)
        control_layout.addWidget(close_btn)
        
        main_layout.addLayout(control_layout)
        
        # Chart area
        self.chart_layout = QVBoxLayout()
        main_layout.addLayout(self.chart_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
        """)
    
    def on_columns_changed(self):
        """Called when column selection changes"""
        self.x_column = self.x_combo.currentText()
        if self.chart_type != "Table":
            self.y_column = self.y_combo.currentText()
        self.update_chart()
    
    @abstractmethod
    def update_chart(self):
        """Update the chart with current data and columns"""
        pass
    
    def get_data(self) -> pd.DataFrame:
        """Get filtered data from manager"""
        return self.manager.get_filtered_data()
    
    def close_chart(self):
        """Close this chart"""
        self.closed.emit()
        self.deleteLater()