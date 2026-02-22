import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QScrollArea, 
                             QSplitter, QToolBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pandas as pd
from backend.parser import parse_html
from backend.transform import fix_positions, fix_wage, fix_value, fix_numerics
from data_manager import DataManager
from filter_panel import FilterPanel
from chart_types import (TableViewWidget, ScatterPlotWidget, BarChartWidget, 
                        LineChartWidget, HistogramWidget)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moneyball Data Visualization")
        self.setGeometry(100, 100, 1600, 900)
        
        # Data manager
        self.data_manager = DataManager()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel: Toolbox for chart types
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File loading section
        file_section = QWidget()
        file_layout = QVBoxLayout(file_section)
        file_layout.addWidget(QLabel("Data File"))
        load_btn = QPushButton("Load HTML File")
        load_btn.clicked.connect(self.load_file)
        file_layout.addWidget(load_btn)
        file_layout.addStretch()
        left_layout.addWidget(file_section)
        
        # Chart type toolbox
        left_layout.addWidget(QLabel("Chart Types"))
        chart_types = {
            "Table": self.add_table_chart,
            "Scatter Plot": self.add_scatter_chart,
            "Bar Chart": self.add_bar_chart,
            "Line Chart": self.add_line_chart,
            "Histogram": self.add_histogram_chart,
        }
        
        for chart_name, callback in chart_types.items():
            btn = QPushButton(chart_name)
            btn.clicked.connect(callback)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        # Filter panel
        self.filter_panel = FilterPanel(self.data_manager)
        self.filter_panel.filters_changed.connect(self.on_filters_changed)
        left_layout.addWidget(self.filter_panel)
        
        left_panel.setMaximumWidth(250)
        
        # Center panel: Canvas for charts
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        
        # Chart canvas area
        self.canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidgetResizable(True)
        canvas_scroll.setWidget(self.canvas_widget)
        
        splitter.addWidget(canvas_scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        self.charts = []
    
    def load_file(self):
        """Load HTML file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open HTML File", "", "HTML Files (*.html);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Parse and transform data
            df = parse_html(file_path).infer_objects()
            df = fix_positions(df)
            df = fix_wage(df)
            df = fix_value(df)
            df = fix_numerics(df)
            
            # Load into manager
            self.data_manager.load_data(df)
            
            # Clear existing charts
            self.clear_charts()
            
            # Clear filters
            self.filter_panel.clear_filters()
            
            QMessageBox.information(self, "Success", f"Loaded {len(df)} rows from {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def add_table_chart(self):
        """Add a table view chart"""
        if self.data_manager.original_df is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        chart = TableViewWidget(self.data_manager)
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
        self.canvas_layout.addWidget(chart)
    
    def add_scatter_chart(self):
        """Add a scatter plot chart"""
        if self.data_manager.original_df is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        chart = ScatterPlotWidget(self.data_manager)
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
        self.canvas_layout.addWidget(chart)
    
    def add_bar_chart(self):
        """Add a bar chart"""
        if self.data_manager.original_df is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        chart = BarChartWidget(self.data_manager)
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
        self.canvas_layout.addWidget(chart)
    
    def add_line_chart(self):
        """Add a line chart"""
        if self.data_manager.original_df is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        chart = LineChartWidget(self.data_manager)
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
        self.canvas_layout.addWidget(chart)
    
    def add_histogram_chart(self):
        """Add a histogram chart"""
        if self.data_manager.original_df is None:
            QMessageBox.warning(self, "No Data", "Please load a data file first.")
            return
        
        chart = HistogramWidget(self.data_manager)
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
        self.canvas_layout.addWidget(chart)
    
    def remove_chart(self, chart):
        """Remove a chart from the canvas"""
        if chart in self.charts:
            self.charts.remove(chart)
    
    def clear_charts(self):
        """Clear all charts"""
        for chart in self.charts:
            chart.deleteLater()
        self.charts.clear()
    
    def on_filters_changed(self):
        """Called when filters change - update all charts"""
        for chart in self.charts:
            chart.update_chart()

def main():
    """Main entry point"""
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()