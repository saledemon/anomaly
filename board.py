from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsView, QGraphicsScene

import client
from player import DraggablePiece
from trying_stuff import board_repr

OUTER_RING = [0, 1, 2, 3]
MIDDLE_RING = [4, 5, 6, 7]
INNER_RING = [8, 9, 10, 11]
SHUTTLE_BAY = [12, 13, 14, 15]
REACTOR = 16

class BoardScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.dragged_item = None
        self.is_moving = False
        self.hover_board_zone = None
        self.player = None

    def highlight_valid_moves(self):
        # highlight for burger player
        if self.player.position == -1:
            print("player is not in the spaceship yet. put him in the spaceship.")
        elif 0 > self.player.position > 15:
            print("we don't know where the player is. His position is totally impossible!!!")
        else:
            for z in filter(lambda i: type(i) == BoardZone, self.items()):
                if z.zone_id in board_repr[self.player.position]:
                    z.highlightForValidMove()

    def clear_highlights(self):
        for z in self.items():
            if isinstance(z, BoardZone):
                z.clearHighlights()

    def initiate_drag(self, item):
        self.clear_highlights()
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

    def initiateMove(self):
        self.highlight_valid_moves()
        self.is_moving = True

    def get_board_zone_at(self, pos):
        items_at_pos = self.items(pos)
        if items_at_pos:
            bottom_most_item = items_at_pos[-1]  # Get the last (bottom-most) item
            if isinstance(bottom_most_item, BoardZone):
                return bottom_most_item

    def mousePressEvent(self, event):
        board_zone = self.get_board_zone_at(event.scenePos())
        if board_zone:
            if board_zone.highlight:
                self.moveTo(event.scenePos(), board_zone)
                self.clear_highlights()
                client.post_burger_pos(event.scenePos(), board_zone)
            else:
                self.clear_highlights()
            self.is_moving = False
            self.hover_board_zone = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_moving:
            board_zone = self.get_board_zone_at(event.scenePos())

            if board_zone is self.hover_board_zone:
                return

            if board_zone is None:
                self.hover_board_zone.highlightForValidMove()
                self.hover_board_zone = None
                return

            if self.hover_board_zone:
                assert isinstance(self.hover_board_zone, BoardZone)
                self.hover_board_zone.highlightForValidMove()

            if board_zone.highlight:
                board_zone.highlightForHoverMouse()
                self.hover_board_zone = board_zone

        super().mouseMoveEvent(event)

    def moveTo(self, pos, board_zone):
        x, y = (pos.x() - self.player.boundingRect().width() / 2,
                pos.y() - self.player.boundingRect().height() / 2)
        self.player.setPos(x, y)
        self.player.move(board_zone.zone_id)

    def cancelMove(self):
        self.clear_highlights()

    def update_burger(self):
        pos, zone = client.get_burger_pos()
        if pos and zone:
            self.moveTo(pos, zone)

class BoardZone(QGraphicsPixmapItem):
    def __init__(self, x, y, pixmap, zone_id):
        super().__init__(pixmap)
        self.zone_id = zone_id
        self.setPos(x, y)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # Allow manual dragging
        self.setAcceptDrops(zone_id < 12)
        self.highlight = None
        self.reminders = []

        self.valid_move_highlight = self.create_highlight_overlay(QColor(255, 255, 0, 100))
        self.hover_highlight = self.create_highlight_overlay(QColor(9, 255, 200, 100))

    def s(self) ->  BoardScene:
        s = self.scene()
        assert isinstance(s, BoardScene)
        return s

    def create_highlight_overlay(self, color):
        """Create a semi-transparent overlay and clip it to the shape."""
        pixmap = QPixmap(self.pixmap().size())  # Same size as the zone
        pixmap.fill(Qt.transparent)  # Start with a fully transparent pixmap

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the highlight color (adjust opacity)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)  # No border, just the highlight fill

        # Clip to the given shape
        painter.setClipPath(self.shape())
        painter.drawRect(QRectF(pixmap.rect()))  # Fill the whole pixmap but only within the clip

        painter.end()
        return pixmap

    def paint(self, painter, option, widget=None):
        """Custom paint method to draw the pixmap and a border if highlighted."""
        super().paint(painter, option, widget)  # Draw the pixmap

        if self.highlight:
            painter.drawPixmap(0, 0, self.highlight)

    def dropEvent(self, event):
        if self.s().isDragging() and type(self.s().dragged_item) == DraggablePiece:
            self.s().moveDraggedItemTo(self.mapToScene(event.pos()), self)
            event.acceptProposedAction()
        self.highlight = None
        self.update()

    def dragEnterEvent(self, event):
        self.highlight = self.hover_highlight
        self.update()

    def dragLeaveEvent(self, event):
        self.highlight = None
        self.update()

    def highlightForHoverMouse(self):
        self.highlight = self.hover_highlight
        self.update()

    def highlightForValidMove(self):
        self.highlight = self.valid_move_highlight
        self.update()

    def clearHighlights(self):
        self.highlight = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            r = QGraphicsPixmapItem(QPixmap("balloon.jpeg").scaled(50, 50, Qt.KeepAspectRatio))
            r.setPos(event.scenePos())
            self.reminders.append(r)
            self.s().addItem(r)

class Board(QGraphicsView):
    def __init__(self, game_state, scene):
        super().__init__()

        self.game_state = game_state
        self.scene = scene
        self.setScene(self.scene)
        self.setMouseTracking(True)

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

        self.scene.player = DraggablePiece("anomaly.png", 50, 50)
        self.scene.addItem(self.scene.player)

        # self.scene.anomaly = DraggablePiece("anomaly.png", 100, 100)
        # self.scene.addItem(self.scene.anomaly)

