from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent

class DraggableWidget(QWidget):
    """Base class for draggable widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_pos = None
        self.is_dragging = False
        self.original_geometry = None
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press - start drag"""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos()
            self.original_geometry = self.geometry()
            self.is_dragging = True
            self.raise_()  # Bring to front
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move - drag widget"""
        if self.is_dragging and self.drag_start_pos:
            delta = event.globalPos() - self.drag_start_pos
            new_pos = self.pos() + delta
            
            # Constrain to parent bounds
            if self.parent():
                parent_rect = self.parent().rect()
                new_x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
                new_y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
            
            self.drag_start_pos = event.globalPos()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release - end drag"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def get_position_data(self) -> dict:
        """Get position data for saving"""
        return {
            'x': self.pos().x(),
            'y': self.pos().y(),
            'width': self.width(),
            'height': self.height()
        }
    
    def set_position_data(self, data: dict):
        """Restore position from data"""
        self.setGeometry(data.get('x', 0), data.get('y', 0), 
                        data.get('width', 400), data.get('height', 300))