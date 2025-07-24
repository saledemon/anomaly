from PyQt5.QtCore import Qt, QMimeData, QPoint, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QDrag, QColor, QPainter, QFont, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem, QLabel, QGraphicsGridLayout, QWidget, QHBoxLayout, QGraphicsWidget, \
    QGraphicsItemGroup, QVBoxLayout

from constants import board_sym, sym_map


class Player(QGraphicsPixmapItem):

    STUDENT_COLOR = ["red", "blue", "green"]
    ANY = 2
    ANOMALY = 1
    STUDENT = 0

    cards_drawn: pyqtSignal = pyqtSignal(list)

    def __init__(self, ptype):
        super().__init__()
        self.zone = None
        self.ptype = ptype
        image_path = "anomaly.png" if ptype == self.ANOMALY else "balloon.jpeg"
        self.color = "black" if ptype == self.ANOMALY else self.STUDENT_COLOR.pop()
        self.setPixmap(QPixmap(image_path).scaled(50, 50, Qt.KeepAspectRatio))

        self.cards = []

    def move(self, scene_pos, target_zone):
        self.setPos(scene_pos)
        self.zone = target_zone

    def execute(self, action):
        action.activate()

    def add_cards(self, new_cards: list):
        self.cards.extend(new_cards)

    def is_anomaly(self):
        return self.ptype == self.ANOMALY

    def zid(self):
        """

        :return: -1 if the player is not on a BoardZone yet.
        """
        if self.zone is None:
            return -1
        return self.zone.zid

class CountablePiece(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap):
        super().__init__(pixmap)
        self.count = 1

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        painter.setFont(QFont("Arial", 20))
        painter.setPen(QColor(0, 0, 0))  # Set text color (black)

        painter.drawText(self.pixmap().rect(), Qt.AlignCenter, str(self.count))

class ZoneContainer(QGraphicsItemGroup):
    def __init__(self, zid):
        super().__init__()
        self.zid = zid
        self.track_sym = self.create_track_symbols()
        self.fuel_source = None
        # self.trap_counter = CountablePiece("res/trap.png")
        self.trap_counter = None
        self.e_counter = None

    def boundingRect(self):
        return QRectF(0, 0, 140, 90)

    def create_track_symbols(self):
        track_sym = []
        for i, s in enumerate(board_sym[self.zid]):
            pixmap = QPixmap(sym_map[s]).scaled(40, 40, Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(i * 50, ((i+1)%2)*10) # create circle arch effect
            self.addToGroup(item)
            track_sym.append(item)
        return track_sym

    def set_fuel_source(self, value):
        if value and self.fuel_source is None:
            item = QGraphicsPixmapItem(QPixmap("res/fuel.jpeg").scaled(40, 40, Qt.KeepAspectRatio))
            item.setPos(self.mapToScene(50, 50))
            item.setRotation(self.rotation())
            self.addToGroup(item)
            self.fuel_source = item
        elif not value and self.fuel_source:
            self.removeFromGroup(self.fuel_source)
            self.scene().removeItem(self.fuel_source)
            self.fuel_source = None
        self.update()

    def place_trap(self):
        if self.trap_counter is None:
            self.trap_counter = CountablePiece(QPixmap("res/trap.png").scaled(15, 30))
            self.trap_counter.setPos(self.mapToScene(100, 60))
            self.trap_counter.setRotation(self.rotation())
            self.addToGroup(self.trap_counter)
        else:
            self.trap_counter.count += 1
            self.update()

    def place_electricity(self):
        if self.e_counter is None:
            self.e_counter = CountablePiece(QPixmap("res/electricity.png").scaled(15, 30))
            self.e_counter.setPos(self.mapToScene(125, 60))
            self.e_counter.setRotation(self.rotation())
            self.addToGroup(self.e_counter)
        else:
            self.e_counter.count += 1
            self.update()

    def place_reminder(self, color):
        pass

class Reminder(QLabel):

    NONE_RADIUS = 5
    PRESENT_RADIUS = 15

    def __init__(self):
        super().__init__()
        self.show()
        self.update_reminder(None)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_reminder(self, color):

        radius = self.PRESENT_RADIUS
        if color is None:
            color = QColor(100, 100, 100, 255)
            radius = self.NONE_RADIUS

        pixmap = QPixmap(15, 15)
        painter = QPainter(pixmap)
        painter.setBrush(color) # Set text color (black)

        # Draw text on the pixmap
        painter.drawEllipse(0, 0, radius, radius)

        # End the painter's session
        painter.end()

        # Set the pixmap to the QLabel
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)

