from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from visualization_base import ChartWidget
from data_manager import DataManager

class TableViewWidget(ChartWidget):
    """Table view chart widget"""
    
    def __init__(self, manager: DataManager):
        super().__init__("Table", manager)
        
        # Create table widget
        self.table = QTableWidget()
        self.chart_layout.addWidget(self.table)
        
        # Set initial column
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        
        self.update_chart()
    
    def update_chart(self):
        """Update the table view"""
        data = self.get_data()
        
        if data.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        
        # Set up table
        self.table.setColumnCount(len(data.columns))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(data.columns)
        
        # Populate table
        for row_idx, row in data.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.resizeColumnsToContents()

class ScatterPlotWidget(ChartWidget):
    """Scatter plot chart widget"""
    
    def __init__(self, manager: DataManager):
        super().__init__("Scatter", manager)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)
        
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        if len(columns) > 1:
            self.y_column = columns[1]
        
        self.update_chart()
    
    def update_chart(self):
        """Update the scatter plot"""
        data = self.get_data()
        
        if data.empty or not self.x_column or not self.y_column:
            return
        
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            x = pd.to_numeric(data[self.x_column], errors='coerce')
            y = pd.to_numeric(data[self.y_column], errors='coerce')
            
            # Remove NaN values
            mask = ~(x.isna() | y.isna())
            x = x[mask]
            y = y[mask]
            
            ax.scatter(x, y, alpha=0.6)
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Scatter: {self.x_column} vs {self.y_column}")
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating scatter plot: {e}")

class BarChartWidget(ChartWidget):
    """Bar chart widget"""
    
    def __init__(self, manager: DataManager):
        super().__init__("Bar Chart", manager)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)
        
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        if len(columns) > 1:
            self.y_column = columns[1]
        
        self.update_chart()
    
    def update_chart(self):
        """Update the bar chart"""
        data = self.get_data()
        
        if data.empty or not self.x_column or not self.y_column:
            return
        
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Group by X and sum Y
            grouped = data.groupby(self.x_column, dropna=True)[self.y_column].sum()
            
            ax.bar(range(len(grouped)), grouped.values)
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels([str(x) for x in grouped.index], rotation=45, ha='right')
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Bar Chart: {self.y_column} by {self.x_column}")
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating bar chart: {e}")

class LineChartWidget(ChartWidget):
    """Line chart widget"""
    
    def __init__(self, manager: DataManager):
        super().__init__("Line Chart", manager)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)
        
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        if len(columns) > 1:
            self.y_column = columns[1]
        
        self.update_chart()
    
    def update_chart(self):
        """Update the line chart"""
        data = self.get_data()
        
        if data.empty or not self.x_column or not self.y_column:
            return
        
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            x = data[self.x_column]
            y = pd.to_numeric(data[self.y_column], errors='coerce')
            
            ax.plot(x, y, marker='o', linestyle='-', linewidth=2)
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Line Chart: {self.y_column} over {self.x_column}")
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating line chart: {e}")

class HistogramWidget(ChartWidget):
    """Histogram widget"""
    
    def __init__(self, manager: DataManager):
        super().__init__("Histogram", manager)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)
        
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        
        self.update_chart()
    
    def on_columns_changed(self):
        """Override to not require Y column"""
        self.x_column = self.x_combo.currentText()
        self.update_chart()
    
    def update_chart(self):
        """Update the histogram"""
        data = self.get_data()
        
        if data.empty or not self.x_column:
            return
        
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            values = pd.to_numeric(data[self.x_column], errors='coerce').dropna()
            
            ax.hist(values, bins=30, edgecolor='black', alpha=0.7)
            ax.set_xlabel(self.x_column)
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram: {self.x_column}")
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating histogram: {e}")