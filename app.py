import sys

from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QColor, QPixmap, QDrag, QPen
from PyQt5.QtWidgets import QWidget, QGraphicsRectItem, QGraphicsView, QGraphicsScene, QMainWindow, QApplication, \
    QGraphicsPixmapItem

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.game_state = {"player1_pos":0, "player2_pos":11}

        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        self.setCentralWidget(self.board)
        self.setFixedSize(300, 400)

class DraggablePiece(QGraphicsPixmapItem):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.setPixmap(QPixmap(image_path).scaled(50, 50, Qt.KeepAspectRatio))
        self.setPos(x, y)  # Initial position
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True) # Allow moving
        self.setAcceptDrops(True)

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
            drag.exec_(Qt.MoveAction)

            scene: Board.BoardScene = self.scene()
            scene.setDraggedItem(self)
            print("mouse moved")

class BoardZone(QGraphicsPixmapItem):
    def __init__(self, x, y, pixmap):
        super().__init__(pixmap)
        self.setPos(x, y)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # Allow manual dragging
        self.setAcceptDrops(True)
        self.highlight = False

    def paint(self, painter, option, widget=None):
        """Custom paint method to draw the pixmap and a border if highlighted."""
        super().paint(painter, option, widget)  # Draw the pixmap

        if self.highlight:
            pen = QPen(Qt.red, 3)  # Red border with thickness 3
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def dropEvent(self, event):
        scene: Board.BoardScene = self.scene()
        if scene.isDragging() and type(scene.dragged_item) == DraggablePiece:
            scene.moveDraggedItemTo(self.pos())
            event.acceptProposedAction()
            print("dropped")
        self.highlight = False
        self.update()

    def dragEnterEvent(self, event):
        self.highlight = True
        self.update()

    def dragLeaveEvent(self, event):
        self.highlight = False
        self.update()

class Board(QGraphicsView):
    class BoardScene(QGraphicsScene):
        def __init__(self):
            super().__init__()
            self.dragged_item = None

        def setDraggedItem(self, item):
            if item in self.items():
                self.dragged_item = item

        def isDragging(self):
            return self.dragged_item is not None

        def moveDraggedItemTo(self, pos):
            self.dragged_item.setPos(pos)
            self.finishDrag()

        def finishDrag(self):
            self.dragged_item = None


    def __init__(self):
        super().__init__()

        self.scene = self.BoardScene()
        self.setScene(self.scene)
        #self.setAcceptDrops(True)
        self.piece = None

        for i in range(3):
            for j in range(4):
                zone = BoardZone(i*100, j*100, QPixmap("burger.jpeg").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.scene.addItem(zone)

        self.add_piece("balloon.jpeg", 50, 50)


    def add_piece(self, image_path, x, y):
        self.piece = DraggablePiece(image_path, x, y)
        self.scene.addItem(self.piece)

    # def dropEvent(self, event):
    #     grid_size = 100  # Adjust based on your grid size
    #     new_x = round(event.pos().x() / grid_size) * grid_size
    #     new_y = round(event.pos().y() / grid_size) * grid_size
    #     self.piece.setPos(new_x, new_y)
    #     event.acceptProposedAction()
    #     print("dropped")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())