import sys

from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPen, QPainterPath, QPainterPathStroker, QColor, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QApplication, \
    QGraphicsPixmapItem

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.game_state = {"player1_pos":0, "player2_pos":11}

        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        self.setCentralWidget(self.board)
        #self.setFixedSize(300, 400)

class DraggablePiece(QGraphicsPixmapItem):
    def __init__(self, image_path, x, y):
        super().__init__()
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

            scene: Board.BoardScene = self.scene()
            scene.setDraggedItem(self)

            drag.exec_(Qt.MoveAction)




class BoardZone(QGraphicsPixmapItem):
    def __init__(self, x, y, pixmap):
        super().__init__(pixmap)
        self.setPos(x, y)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # Allow manual dragging
        self.setAcceptDrops(True)
        self.highlight = False

    # def shape(self):
    #     """Returns a path that only includes the non-transparent parts."""
    #     path = QPainterPath()
    #     image = self.pixmap().toImage()  # Get transparency mask
    #
    #     # Convert the mask to a path
    #     for x in range(image.width()):
    #         for y in range(image.height()):
    #             if image.pixelColor(x, y).alpha() > 0:  # Non-transparent pixels
    #                 path.addRect(x, y, 1, 1)
    #
    #     return path

    def paint(self, painter, option, widget=None):
        """Custom paint method to draw the pixmap and a border if highlighted."""
        super().paint(painter, option, widget)  # Draw the pixmap

        if self.highlight:
            pen = QPen(QColor(200, 200, 200, 150), 5)  # Red border with thickness 3
            painter.setPen(pen)
            painter.drawPath(self.shape())

    def dropEvent(self, event):
        scene: Board.BoardScene = self.scene()
        if scene.isDragging() and type(scene.dragged_item) == DraggablePiece:
            scene.moveDraggedItemTo(self.pos())
            event.acceptProposedAction()
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

        shuttle = QPixmap("res/shuttle_bay.png")  # Load your image
        outer = QPixmap("res/outer_ring.png")  # Load your image
        inner = QPixmap("res/inner_ring.png")  # Load your image
        middle = QPixmap("res/middle_ring.png")  # Load your image
        rot90 = QTransform().rotate(90)  # Rotate 45 degrees
        rot180 = QTransform().rotate(180)
        rot270 = QTransform().rotate(270)

        res = 2.77777777777777777

        self.scene.addItem(BoardZone(0, 0, outer))
        self.scene.addItem(BoardZone(55.2672*res, 55.2552*res, shuttle))
        self.scene.addItem(BoardZone(107.9844*res, 35.9809*res, middle))
        self.scene.addItem(BoardZone(90.0108*res, 90.0328*res, inner))

        self.scene.addItem(BoardZone(179.9877 * res, 0, outer.transformed(rot90)))
        self.scene.addItem(BoardZone(224.9998 * res, 55.2552 * res, shuttle.transformed(rot90)))
        self.scene.addItem(BoardZone(257.9467 * res, 107.9702 * res, middle.transformed(rot90)))
        self.scene.addItem(BoardZone(179.9776 * res, 90.0328 * res, inner.transformed(rot90)))

        self.scene.addItem(BoardZone(179.9891 * res, 179.9595 * res, outer.transformed(rot180)))
        self.scene.addItem(BoardZone(224.9998 * res, 224.9859 * res, shuttle.transformed(rot180)))
        self.scene.addItem(BoardZone(107.9843 * res, 257.9323 * res, middle.transformed(rot180)))
        self.scene.addItem(BoardZone(179.9769 * res, 179.9274 * res, inner.transformed(rot180)))

        self.scene.addItem(BoardZone(0, 179.9595 * res, outer.transformed(rot270)))
        self.scene.addItem(BoardZone(55.2693 * res, 224.9859 * res, shuttle.transformed(rot270)))
        self.scene.addItem(BoardZone(35.995  * res, 107.9703 * res, middle.transformed(rot270)))
        self.scene.addItem(BoardZone(90.0108 * res, 179.9274 * res, inner.transformed(rot270)))

        self.scene.addItem(BoardZone(131.8823 * res, 131.8682 * res, QPixmap("res/reactor.png")))



        # for i in range(3):
        #     for j in range(4):
        #         zone = BoardZone(i*100, j*100, QPixmap("res/shuttle_bay.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        #         self.scene.addItem(zone)

        self.add_piece("burger.jpeg", 50, 50)


    def add_piece(self, image_path, x, y):
        self.piece = DraggablePiece(image_path, x, y)
        self.scene.addItem(self.piece)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())