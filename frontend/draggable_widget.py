from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizeGrip, QFrame
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QFont


class DraggableWidget(QFrame):
    """
    A draggable, resizable widget container.
    Drag by clicking and holding the title bar.
    Resize using the size grip in the bottom-right corner.
    """

    closed = pyqtSignal()

    TITLE_HEIGHT = 28

    def __init__(self, title: str = "Widget", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self._drag_start_pos = None
        self._is_dragging = False

        self.setMinimumSize(200, 150)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 4)
        outer.setSpacing(0)

        # ── Title bar ────────────────────────────────────────────────────
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(self.TITLE_HEIGHT)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet(
            "#titleBar { background: #4a86c8; }"
        )
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(6, 0, 4, 0)
        title_layout.setSpacing(4)

        self.title_label = QLabel(title)
        font = QFont()
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: white;")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; color: white; border: none; font-size: 12px; }"
            "QPushButton:hover { background: #cc3333; border-radius: 3px; }"
        )
        close_btn.clicked.connect(self._on_close)
        title_layout.addWidget(close_btn)

        outer.addWidget(self.title_bar)

        # ── Content area (subclasses add their widgets here) ─────────────
        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 0)
        outer.addWidget(self.content_widget, 1)

        # ── Resize grip ──────────────────────────────────────────────────
        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip = QSizeGrip(self)
        grip.setFixedSize(14, 14)
        grip_row.addWidget(grip)
        outer.addLayout(grip_row)

        self.setStyleSheet(
            "DraggableWidget { background: white; border: 1px solid #aaa; }"
        )

    # ── Drag handling (title-bar only) ────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and event.y() <= self.TITLE_HEIGHT:
            self._drag_start_pos = event.globalPos() - self.pos()
            self._is_dragging = True
            self.raise_()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging and self._drag_start_pos is not None:
            new_pos = event.globalPos() - self._drag_start_pos
            if self.parent():
                pr = self.parent().rect()
                new_x = max(0, min(new_pos.x(), pr.width() - self.width()))
                new_y = max(0, min(new_pos.y(), pr.height() - self.height()))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            self._drag_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _on_close(self):
        self.closed.emit()
        self.deleteLater()

    def set_title(self, title: str):
        self.title_label.setText(title)

    def get_position_data(self) -> dict:
        return {
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
        }

    def set_position_data(self, data: dict):
        self.setGeometry(
            data.get("x", 0),
            data.get("y", 0),
            data.get("width", 400),
            data.get("height", 300),
        )
