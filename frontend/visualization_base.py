from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal
import pandas as pd
from abc import abstractmethod
from data_manager import DataManager
from draggable_widget import DraggableWidget


class ChartWidget(DraggableWidget):
    """Base class for all chart types — draggable, resizable panel."""

    data_updated = pyqtSignal()

    # Subclasses set this
    CHART_TYPE: str = "Chart"

    def __init__(self, chart_type: str, manager: DataManager, tab_id: str = None):
        super().__init__(title=chart_type)
        self.chart_type = chart_type
        self.manager = manager
        self.tab_id = tab_id  # Which tab this chart belongs to
        self.x_column: str | None = None
        self.y_column: str | None = None

        # ── Column selector row ──────────────────────────────────────────
        ctrl_row = QHBoxLayout()
        columns = manager.get_columns()

        ctrl_row.addWidget(QLabel("X:"))
        self.x_combo = QComboBox()
        self.x_combo.addItems(columns)
        self.x_combo.currentTextChanged.connect(self._on_columns_changed)
        ctrl_row.addWidget(self.x_combo)

        if chart_type not in ("Table", "Histogram"):
            ctrl_row.addWidget(QLabel("Y:"))
            self.y_combo = QComboBox()
            self.y_combo.addItems(columns)
            if len(columns) > 1:
                self.y_combo.setCurrentIndex(1)
            self.y_combo.currentTextChanged.connect(self._on_columns_changed)
            ctrl_row.addWidget(self.y_combo)
        else:
            self.y_combo = None

        ctrl_row.addStretch()
        self.content_layout.addLayout(ctrl_row)

        # ── Chart placeholder area ───────────────────────────────────────
        self.chart_layout = self.content_layout  # subclasses append to this

        # initialise column references
        if columns:
            self.x_column = columns[0]
        if self.y_combo and len(columns) > 1:
            self.y_column = columns[1]

    # ── Column change ──────────────────────────────────────────────────

    def _on_columns_changed(self):
        self.x_column = self.x_combo.currentText()
        if self.y_combo:
            self.y_column = self.y_combo.currentText()
        self.update_chart()

    # ── Abstract interface ─────────────────────────────────────────────

    @abstractmethod
    def update_chart(self):
        """Refresh the chart with current data / column selection."""

    # ── Helpers ────────────────────────────────────────────────────────

    def get_data(self) -> pd.DataFrame:
        return self.manager.get_filtered_data(self.tab_id)

    def get_state(self) -> dict:
        return {
            "type": self.chart_type,
            "x_column": self.x_column,
            "y_column": self.y_column,
            "position": self.get_position_data(),
        }
