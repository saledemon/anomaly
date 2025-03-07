from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtWidgets import QGraphicsPixmapItem

# types of moveable pieces: player, reminders,

class DraggablePiece(QGraphicsPixmapItem):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.position = -1
        self.setPixmap(QPixmap(image_path).scaled(50, 50, Qt.KeepAspectRatio))
        self.setPos(x, y)  # Initial position
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True) # Allow moving

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # Start drag-and-drop when the piece is clicked
            drag = QDrag(event.widget())
            mime_data = QMimeData()

            # Attach the item's position to the drag event
            mime_data.setImageData(self.pixmap())
            drag.setMimeData(mime_data)

            # Draw the pixmap as feedback while dragging
            drag_pixmap = self.pixmap()
            drag.setPixmap(drag_pixmap)
            drag.setHotSpot(event.pos().toPoint())

            scene = self.scene()
            scene.initiate_drag(self)

            drag.exec_(Qt.MoveAction)

    def move(self, zone):
        self.setPos(zone.hot_point)
        self.position = zone.zone_id


class Player:
    def __init__(self):
        self.cards = []
        self.reminders = []
        self.position = -1

    def is_move_valid(self, move_to):
        # need logic for movement
        return type(move_to) is int and 0 <= move_to <= 15

    def move(self, move_to):
        pass  # change the position

    def play_special_action(self, card):
        pass

    def place_reminder(self):
        pass # place a reminder on the map for a specific player