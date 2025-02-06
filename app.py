import sys

from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag, QPen, QPainterPath, QPainterPathStroker, QColor, QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QApplication, \
    QGraphicsPixmapItem, QPushButton, QVBoxLayout, QWidget

from player import GameState, Player
from trying_stuff import board_repr

OUTER_RING = [0, 1, 2, 3]
MIDDLE_RING = [4, 5, 6, 7]
INNER_RING = [8, 9, 10, 11]
SHUTTLE_BAY = [12, 13, 14, 15]
REACTOR = 16

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.board = Board(self.game_state)


        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        button = QPushButton("Move")
        button.clicked.connect(self.board.highlight_valid_moves)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.board)
        widget.setLayout(layout)

        self.setCentralWidget(widget)


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

            scene: Board.BoardScene = self.scene()
            scene.initiate_drag(self)

            drag.exec_(Qt.MoveAction)

    def move(self, zone_id):
        self.position = zone_id

class DraggablePlayer(DraggablePiece):
    def __init__(self, player):
        super().__init__("burger.jpeg", 100, 100)
        self.player = player

    def move(self, zone_id):
        # if self.player.is_move_valid(zone_id):
        #     self.player.position = zone_id
        # else:
        #     pass # fuck off
        pass

class BoardZone(QGraphicsPixmapItem):
    def __init__(self, x, y, pixmap, zone_id):
        super().__init__(pixmap)
        self.zone_id = zone_id
        self.setPos(x, y)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # Allow manual dragging
        self.setAcceptDrops(True)
        self.highlight = False

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
            scene.moveDraggedItemTo(self.mapToScene(event.pos()), self)
            event.acceptProposedAction()
        self.highlight = False
        self.update()

    def dragEnterEvent(self, event):
        self.highlight = True
        self.update()

    def dragLeaveEvent(self, event):
        self.highlight = False
        self.update()

    def highlightForValidMove(self, event):
        self.highlight = True
        self.update()

    def clearHighlights(self, event):
        self.highlight = False
        self.update()

class Board(QGraphicsView):
    class BoardScene(QGraphicsScene):
        def __init__(self):
            super().__init__()
            self.dragged_item = None

        def initiate_drag(self, item):
            self.views()[0].clear_highlights()
            if item in self.items():
                self.dragged_item = item

        def isDragging(self):
            return self.dragged_item is not None

        def moveDraggedItemTo(self, pos, zone):
            x, y = (pos.x() - self.dragged_item.boundingRect().width()/2,
                    pos.y() - self.dragged_item.boundingRect().height()/2)
            self.dragged_item.setPos(x, y)
            self.dragged_item.move(zone.zone_id)
            self.finishDrag()

        def finishDrag(self):
            self.dragged_item = None


    def __init__(self, game_state):
        super().__init__()

        self.game_state = game_state
        self.scene = self.BoardScene()
        self.setScene(self.scene)
        self.player = None

        shuttle = QPixmap("res/shuttle_bay.png")  # Load your image
        outer = QPixmap("res/outer_ring.png")  # Load your image
        inner = QPixmap("res/inner_ring.png")  # Load your image
        middle = QPixmap("res/middle_ring.png")  # Load your image
        rot90 = QTransform().rotate(90)  # Rotate 45 degrees
        rot180 = QTransform().rotate(180)
        rot270 = QTransform().rotate(270)

        res = 2.77777777777777777

        self.scene.addItem(BoardZone(0, 0, outer, OUTER_RING[0]))
        self.scene.addItem(BoardZone(55.2672*res, 55.2552*res, shuttle, SHUTTLE_BAY[0]))
        self.scene.addItem(BoardZone(107.9844*res, 35.9809*res, middle, MIDDLE_RING[0]))
        self.scene.addItem(BoardZone(90.0108*res, 90.0328*res, inner, INNER_RING[0]))

        self.scene.addItem(BoardZone(179.9877 * res, 0, outer.transformed(rot90), OUTER_RING[1]))
        self.scene.addItem(BoardZone(224.9998 * res, 55.2552 * res, shuttle.transformed(rot90), SHUTTLE_BAY[1]))
        self.scene.addItem(BoardZone(257.9467 * res, 107.9702 * res, middle.transformed(rot90), MIDDLE_RING[1]))
        self.scene.addItem(BoardZone(179.9776 * res, 90.0328 * res, inner.transformed(rot90), INNER_RING[1]))

        self.scene.addItem(BoardZone(179.9891 * res, 179.9595 * res, outer.transformed(rot180), OUTER_RING[2]))
        self.scene.addItem(BoardZone(224.9998 * res, 224.9859 * res, shuttle.transformed(rot180), SHUTTLE_BAY[2]))
        self.scene.addItem(BoardZone(107.9843 * res, 257.9323 * res, middle.transformed(rot180), MIDDLE_RING[2]))
        self.scene.addItem(BoardZone(179.9769 * res, 179.9274 * res, inner.transformed(rot180), INNER_RING[2]))

        self.scene.addItem(BoardZone(0, 179.9595 * res, outer.transformed(rot270), OUTER_RING[3]))
        self.scene.addItem(BoardZone(55.2693 * res, 224.9859 * res, shuttle.transformed(rot270), SHUTTLE_BAY[3]))
        self.scene.addItem(BoardZone(35.995  * res, 107.9703 * res, middle.transformed(rot270), MIDDLE_RING[3]))
        self.scene.addItem(BoardZone(90.0108 * res, 179.9274 * res, inner.transformed(rot270), INNER_RING[3]))

        self.scene.addItem(BoardZone(131.8823 * res, 131.8682 * res, QPixmap("res/reactor.png"), REACTOR))

        self.add_player("burger.jpeg", 50, 50)

    def add_player(self, image_path, x, y):
        self.player = DraggablePiece(image_path, x, y)
        self.scene.addItem(self.player)

    def highlight_valid_moves(self):
        # highlight for burger player
        if self.player.position == -1:
            print("player is not in the spaceship yet. put him in the spaceship.")
        elif 0 > self.player.position > 15:
            print("we don't know where the player is. His position is totally impossible!!!")
        else:
            for z in filter(lambda i: type(i) == BoardZone, self.items()):
                if z.zone_id in board_repr[self.player.position]:
                    z.highlightForValidMove(None)

    def clear_highlights(self):
        for z in self.items():
            if type(z) == BoardZone:
                z.clearHighlights(None)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())