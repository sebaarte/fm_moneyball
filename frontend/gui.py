import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QTabWidget, 
                             QSplitter, QMessageBox, QMenuBar, QMenu, QAction,
                             QInputDialog, QStatusBar)
from PyQt5.QtCore import Qt
import pandas as pd
from backend.parser import parse_html
from backend.transform import fix_positions, fix_wage, fix_value, fix_numerics
from backend.data_manager import DataManager
from filter_widget import FilterWidget
from frontend.chart_types import (TableViewWidget, ScatterPlotWidget, BarChartWidget, 
                        LineChartWidget, HistogramWidget)
from visualization_manager import VisualizationManager


class TabCanvas(QWidget):
    """Canvas widget for a single tab - holds draggable charts and filters"""
    
    def __init__(self, tab_id: str, manager: DataManager):
        super().__init__()
        self.tab_id = tab_id
        self.manager = manager
        self.charts = []
        self.filters = []
        
        # No layout - use absolute positioning for draggable widgets
        self.setMinimumSize(800, 600)
    
    def add_chart(self, chart):
        """Add a chart to this canvas"""
        chart.setParent(self)
        chart.tab_id = self.tab_id
        chart.setGeometry(50 + len(self.charts) * 20, 50 + len(self.charts) * 20, 600, 400)
        chart.show()
        chart.closed.connect(lambda: self.remove_chart(chart))
        self.charts.append(chart)
    
    def add_filter(self, filter_widget):
        """Add a filter to this canvas"""
        filter_widget.setParent(self)
        filter_widget.tab_id = self.tab_id
        filter_widget.setGeometry(700, 50 + len(self.filters) * 30, 300, 250)
        filter_widget.show()
        filter_widget.closed.connect(lambda: self.remove_filter(filter_widget))
        filter_widget.filter_changed.connect(self.on_filter_changed)
        self.filters.append(filter_widget)
    
    def remove_chart(self, chart):
        """Remove a chart from this canvas"""
        if chart in self.charts:
            self.charts.remove(chart)
    
    def remove_filter(self, filter_widget):
        """Remove a filter from this canvas"""
        if filter_widget in self.filters:
            self.filters.remove(filter_widget)
            # Remove from data manager
            self.manager.remove_filter(self.tab_id, filter_widget.filter_index)
            self.on_filter_changed()
    
    def on_filter_changed(self):
        """Called when any filter changes - update all charts"""
        for chart in self.charts:
            chart.update_chart()
    
    def clear_all(self):
        """Clear all charts and filters"""
        for chart in self.charts[:]:
            chart.deleteLater()
        for filter_widget in self.filters[:]:
            filter_widget.deleteLater()
        self.charts.clear()
        self.filters.clear()
        self.manager.clear_tab_filters(self.tab_id)
    
    def get_state(self) -> dict:
        """Get state for saving"""
        charts_state = []
        for chart in self.charts:
            charts_state.append(chart.get_state())
        
        filters_state = []
        for f in self.filters:
            filters_state.append(f.get_state())
        
        return {
            'charts': charts_state,
            'filters': filters_state
        }


class MainWindow(QMainWindow):
    """Main application window with tab-based visualization"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moneyball Data Visualization")
        self.setGeometry(100, 100, 1600, 900)
        
        # Data manager
        self.data_manager = DataManager()
        
        # Visualization manager
        self.viz_manager = VisualizationManager()
        
        # Tab canvases: {tab_name: TabCanvas}
        self.tab_canvases = {}
        
        # Create menu bar
        self._create_menu_bar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel: Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File loading section
        file_section = QWidget()
        file_layout = QVBoxLayout(file_section)
        file_layout.addWidget(QLabel("Data Files"))
        
        load_html_btn = QPushButton("Load HTML File")
        load_html_btn.clicked.connect(self.load_html_file)
        file_layout.addWidget(load_html_btn)
        
        load_csv_btn = QPushButton("Load CSV File")
        load_csv_btn.clicked.connect(self.load_csv_file)
        file_layout.addWidget(load_csv_btn)
        
        file_layout.addStretch()
        left_layout.addWidget(file_section)
        
        # Chart type buttons
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
        
        # Filter button
        left_layout.addWidget(QLabel("Filters"))
        add_filter_btn = QPushButton("Add Filter")
        add_filter_btn.clicked.connect(self.add_filter)
        left_layout.addWidget(add_filter_btn)
        
        left_layout.addStretch()
        left_panel.setMaximumWidth(250)
        
        # Right panel: Tab widget
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add new tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setMaximumWidth(30)
        new_tab_btn.clicked.connect(self.create_new_tab)
        self.tab_widget.setCornerWidget(new_tab_btn, Qt.TopRightCorner)
        
        # Create first tab
        self.create_new_tab("Tab 1")
        
        splitter.addWidget(self.tab_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
    
    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # Visualization menu
        viz_menu = menubar.addMenu("Visualization")
        
        new_action = QAction("New Visualization", self)
        new_action.triggered.connect(self.new_visualization)
        viz_menu.addAction(new_action)
        
        save_action = QAction("Save Visualization As...", self)
        save_action.triggered.connect(self.save_visualization_as)
        viz_menu.addAction(save_action)
        
        load_action = QAction("Load Visualization...", self)
        load_action.triggered.connect(self.load_visualization)
        viz_menu.addAction(load_action)
        
        viz_menu.addSeparator()
        
        # Recent visualizations submenu
        self.recent_menu = QMenu("Recent Visualizations", self)
        viz_menu.addMenu(self.recent_menu)
        self._update_recent_menu()
    
    def _update_recent_menu(self):
        """Update the recent visualizations menu"""
        self.recent_menu.clear()
        recent = self.viz_manager.get_recent_visualizations()
        
        if not recent:
            no_recent = QAction("(None)", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            for path in recent:
                action = QAction(os.path.basename(path), self)
                action.triggered.connect(lambda checked, p=path: self._load_visualization_from_path(p))
                self.recent_menu.addAction(action)
    
    def create_new_tab(self, name=None):
        """Create a new tab"""
        if name is None or isinstance(name, bool):
            name, ok = QInputDialog.getText(self, "New Tab", "Enter tab name:")
            if not ok or not name:
                return
        
        # Ensure name is a string
        name = str(name)
        
        # Create canvas
        canvas = TabCanvas(name, self.data_manager)
        self.tab_canvases[name] = canvas
        
        # Add to tab widget
        self.tab_widget.addTab(canvas, name)
        self.tab_widget.setCurrentWidget(canvas)
        
        self._auto_save()
    
    def close_tab(self, index: int):
        """Close a tab"""
        if self.tab_widget.count() <= 1:
            QMessageBox.warning(self, "Cannot Close", "Cannot close the last tab.")
            return
        
        tab_name = self.tab_widget.tabText(index)
        
        reply = QMessageBox.question(
            self, "Close Tab", 
            f"Close tab '{tab_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            canvas = self.tab_canvases.pop(tab_name)
            canvas.clear_all()
            self.tab_widget.removeTab(index)
            self._auto_save()
    
    def get_current_canvas(self) -> TabCanvas:
        """Get the currently active tab canvas"""
        return self.tab_widget.currentWidget()
    
    def load_html_file(self):
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

            
            # Auto-save as CSV
            csv_path = os.path.splitext(file_path)[0] + ".csv"
            df.to_csv(csv_path, index=False)
            
            # Load into manager
            self.data_manager.load_data(df, csv_path)
            
            self.status_bar.showMessage(f"Loaded {len(df)} rows from {file_path} (saved to {csv_path})")
            self._auto_save()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
    
    def load_csv_file(self):
        """Load CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            df = pd.read_csv(file_path)
            self.data_manager.load_data(df, file_path)
            self.status_bar.showMessage(f"Loaded {len(df)} rows from {file_path}")
            self._auto_save()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV: {str(e)}")
    
    def add_table_chart(self):
        """Add a table view chart"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        chart = TableViewWidget(self.data_manager, canvas.tab_id)
        canvas.add_chart(chart)
        self._auto_save()
    
    def add_scatter_chart(self):
        """Add a scatter plot chart"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        chart = ScatterPlotWidget(self.data_manager, canvas.tab_id)
        canvas.add_chart(chart)
        self._auto_save()
    
    def add_bar_chart(self):
        """Add a bar chart"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        chart = BarChartWidget(self.data_manager, canvas.tab_id)
        canvas.add_chart(chart)
        self._auto_save()
    
    def add_line_chart(self):
        """Add a line chart"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        chart = LineChartWidget(self.data_manager, canvas.tab_id)
        canvas.add_chart(chart)
        self._auto_save()
    
    def add_histogram_chart(self):
        """Add a histogram chart"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        chart = HistogramWidget(self.data_manager, canvas.tab_id)
        canvas.add_chart(chart)
        self._auto_save()
    
    def add_filter(self):
        """Add a filter widget"""
        if self.data_manager.original_df is None:
            self.status_bar.showMessage("Please load a data file first")
            return
        
        canvas = self.get_current_canvas()
        filter_index = len(canvas.filters)
        filter_widget = FilterWidget(self.data_manager, canvas.tab_id, filter_index)
        canvas.add_filter(filter_widget)
        self._auto_save()
    
    def new_visualization(self):
        """Create a new visualization"""
        reply = QMessageBox.question(
            self, "New Visualization", 
            "Clear all tabs and start fresh?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all tabs
            while self.tab_widget.count() > 0:
                tab_name = self.tab_widget.tabText(0)
                canvas = self.tab_canvases.pop(tab_name)
                canvas.clear_all()
                self.tab_widget.removeTab(0)
            
            # Create first tab
            self.create_new_tab("Tab 1")
            self.viz_manager.current_viz_path = None
            self.status_bar.showMessage("New visualization created")
    
    def save_visualization_as(self):
        """Save visualization to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Visualization", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        config = self._get_current_config()
        if self.viz_manager.save_visualization(config, file_path):
            self.status_bar.showMessage(f"Saved visualization to {file_path}")
            self._update_recent_menu()
        else:
            QMessageBox.critical(self, "Error", "Failed to save visualization")
    
    def load_visualization(self):
        """Load visualization from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Visualization", "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        self._load_visualization_from_path(file_path)
    
    def _load_visualization_from_path(self, file_path: str):
        """Load visualization from a specific path"""
        config = self.viz_manager.load_visualization(file_path)
        
        if config is None:
            QMessageBox.critical(self, "Error", "Failed to load visualization")
            return
        
        # TODO: Implement full loading logic
        # For now, just show a message
        self.status_bar.showMessage(f"Loaded visualization from {file_path}")
        self._update_recent_menu()
    
    def _get_current_config(self) -> dict:
        """Get current configuration for saving"""
        tabs = []
        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i)
            canvas = self.tab_canvases[tab_name]
            tabs.append({
                'name': tab_name,
                **canvas.get_state()
            })
        
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        data_source = self.data_manager.data_source_path or ""
        
        return self.viz_manager.create_config(data_source, current_tab, tabs)
    
    def _auto_save(self):
        """Auto-save current visualization"""
        config = self._get_current_config()
        self.viz_manager.auto_save(config)


def main():
    """Main entry point"""
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()