from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem, QVBoxLayout, 
                              QHeaderView, QMenu, QLineEdit, QDialog, QDialogButtonBox,
                              QLabel, QComboBox, QFormLayout)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from visualization_base import ChartWidget
from backend.data_manager import DataManager
import mplcursors

class TableViewWidget(ChartWidget):
    """Table view chart widget"""
    
    def __init__(self, manager: DataManager, tab_id: str = None):
        super().__init__("Table", manager, tab_id)
        
        # Create table widget
        self.table = QTableWidget()
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self._show_column_menu)
        self.chart_layout.addWidget(self.table)
        
        
        # Column filters (column_name -> filter_value)
        self.column_filters = {}
        
        # Set initial column
        columns = manager.get_columns()
        if columns:
            self.x_column = columns[0]
        
        self.update_chart()
    
    def _show_column_menu(self, position):
        """Show context menu for column header"""
        col_idx = self.table.horizontalHeader().logicalIndexAt(position)
        if col_idx < 0:
            return
        
        column_name = self.table.horizontalHeaderItem(col_idx).text()
        
        menu = QMenu()
        filter_action = menu.addAction("Filter Column...")
        clear_filter_action = menu.addAction("Clear Filter")
        sort_asc_action = menu.addAction("Sort Ascending")
        sort_desc_action = menu.addAction("Sort Descending")
        
        action = menu.exec_(self.table.horizontalHeader().mapToGlobal(position))
        
        if action == filter_action:
            self._filter_column(column_name, col_idx)
        elif action == clear_filter_action:
            self._clear_column_filter(column_name)
        elif action == sort_asc_action:
            self.table.sortItems(col_idx, Qt.AscendingOrder)
        elif action == sort_desc_action:
            self.table.sortItems(col_idx, Qt.DescendingOrder)
    
    def _filter_column(self, column_name: str, col_idx: int):
        """Show filter dialog for column"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Filter: {column_name}")
        layout = QFormLayout(dialog)
        
        # Check if column is numeric
        data = self.get_data()
        is_numeric = False
        if column_name in data.columns:
            import pandas as pd
            is_numeric = pd.api.types.is_numeric_dtype(data[column_name])
        
        if is_numeric:
            # Numeric range filter
            from PyQt5.QtWidgets import QDoubleSpinBox
            
            # Get min/max values from data
            col_data = pd.to_numeric(data[column_name], errors='coerce').dropna()
            if not col_data.empty:
                min_val = float(col_data.min())
                max_val = float(col_data.max())
            else:
                min_val, max_val = 0.0, 100.0
            
            lower_range = QDoubleSpinBox()
            lower_range.setDecimals(2)
            lower_range.setMinimum(-999999999)
            lower_range.setMaximum(999999999)
            lower_range.setValue(min_val)
            
            upper_range = QDoubleSpinBox()
            upper_range.setDecimals(2)
            upper_range.setMinimum(-999999999)
            upper_range.setMaximum(999999999)
            upper_range.setValue(max_val)
            
            # Load existing filter if present
            if column_name in self.column_filters:
                existing = self.column_filters[column_name]
                if isinstance(existing, dict):
                    lower_range.setValue(existing.get('min', min_val))
                    upper_range.setValue(existing.get('max', max_val))
            
            layout.addRow("Lower Range:", lower_range)
            layout.addRow("Upper Range:", upper_range)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                lower = lower_range.value()
                upper = upper_range.value()
                if lower != min_val or upper != max_val:
                    self.column_filters[column_name] = {'min': lower, 'max': upper, 'type': 'numeric'}
                else:
                    self.column_filters.pop(column_name, None)
                self._apply_column_filters()
        else:
            # Text contains filter
            filter_input = QLineEdit()
            if column_name in self.column_filters:
                if isinstance(self.column_filters[column_name], str):
                    filter_input.setText(self.column_filters[column_name])
            
            layout.addRow("Contains:", filter_input)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                filter_value = filter_input.text().strip()
                if filter_value:
                    self.column_filters[column_name] = filter_value
                else:
                    self.column_filters.pop(column_name, None)
                self._apply_column_filters()
    
    def _clear_column_filter(self, column_name: str):
        """Clear filter for column"""
        self.column_filters.pop(column_name, None)
        self._apply_column_filters()
    
    def _apply_column_filters(self):
        """Apply all column filters to table rows"""
        data = self.get_data()
        
        for row_idx in range(self.table.rowCount()):
            show_row = True
            for col_name, filter_value in self.column_filters.items():
                if col_name not in data.columns:
                    continue
                col_idx = list(data.columns).index(col_name)
                item = self.table.item(row_idx, col_idx)
                if item:
                    # Check if it's a numeric range filter
                    if isinstance(filter_value, dict) and filter_value.get('type') == 'numeric':
                        try:
                            cell_num = float(item.text())
                            if not (filter_value['min'] <= cell_num <= filter_value['max']):
                                show_row = False
                                break
                        except (ValueError, TypeError):
                            show_row = False
                            break
                    else:
                        # Text contains filter
                        cell_value = item.text().lower()
                        if str(filter_value).lower() not in cell_value:
                            show_row = False
                            break
            
            self.table.setRowHidden(row_idx, not show_row)
    
    def update_chart(self):
        """Update the table view"""
        data = self.get_data()

        #clear existing data
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.column_filters.clear()

        # Check if data is empty
        if data.empty:
            return


        # Set up table
        self.table.setColumnCount(len(data.columns))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(data.columns)
        
        # Populate table
        for row_idx in range(len(data)):
            for col_idx in range(len(data.columns)):
                value = data.iloc[row_idx, col_idx]  # Use iloc with integer position
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.setUpdatesEnabled(True)
        self.table.setSortingEnabled(True)

        
        self.table.resizeColumnsToContents()

class ScatterPlotWidget(ChartWidget):
    """Scatter plot chart widget"""
    
    def __init__(self, manager: DataManager, tab_id: str = None):
        super().__init__("Scatter", manager, tab_id)
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
            x_clean = x[mask]
            y_clean = y[mask]
            names = data.loc[mask, 'Name'].values if 'Name' in data.columns else None
            
            scatter = ax.scatter(x_clean, y_clean, alpha=0.6)
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Scatter: {self.x_column} vs {self.y_column}")
            
            # Add hover tooltips
            if names is not None:
                cursor = mplcursors.cursor(scatter, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    idx = sel.index
                    if idx < len(names):
                        sel.annotation.set_text(names[idx])
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            pass  # Silently handle chart update errors

class BarChartWidget(ChartWidget):
    """Bar chart widget"""
    
    def __init__(self, manager: DataManager, tab_id: str = None):
        super().__init__("Bar Chart", manager, tab_id)
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
            
            # Group by X and sum Y, also collect names
            grouped = data.groupby(self.x_column, dropna=True)[self.y_column].sum()
            
            # Get names for each group if available
            if 'Name' in data.columns:
                names_per_group = data.groupby(self.x_column, dropna=True)['Name'].apply(
                    lambda x: ', '.join(x.astype(str).unique()[:5])  # Limit to 5 names
                )
            else:
                names_per_group = None
            
            bars = ax.bar(range(len(grouped)), grouped.values)
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels([str(x) for x in grouped.index], rotation=45, ha='right')
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Bar Chart: {self.y_column} by {self.x_column}")
            
            # Add hover tooltips
            if names_per_group is not None:
                cursor = mplcursors.cursor(bars, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    idx = sel.index
                    if idx < len(names_per_group):
                        sel.annotation.set_text(names_per_group.iloc[idx])
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            pass  # Silently handle chart update errors

class LineChartWidget(ChartWidget):
    """Line chart widget"""
    
    def __init__(self, manager: DataManager, tab_id: str = None):
        super().__init__("Line Chart", manager, tab_id)
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
            names = data['Name'].values if 'Name' in data.columns else None
            
            line, = ax.plot(x, y, marker='o', linestyle='-', linewidth=2)
            ax.set_xlabel(self.x_column)
            ax.set_ylabel(self.y_column)
            ax.set_title(f"Line Chart: {self.y_column} over {self.x_column}")
            
            # Add hover tooltips
            if names is not None:
                cursor = mplcursors.cursor(line, hover=True)
                @cursor.connect("add")
                def on_add(sel):
                    idx = sel.index
                    if idx < len(names):
                        sel.annotation.set_text(names[idx])
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            pass  # Silently handle chart update errors

class HistogramWidget(ChartWidget):
    """Histogram widget"""
    
    def __init__(self, manager: DataManager, tab_id: str = None):
        super().__init__("Histogram", manager, tab_id)
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
        except Exception:
            pass  # Silently handle chart update errors
