from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QTransform, QPen, QImage
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, \
    QGraphicsGridLayout, QGraphicsWidget, QLabel, QGraphicsItemGroup, QMenu, QAction, QWidgetAction, QGraphicsRectItem

from action import Action
from pieces import Player, Reminder, ZoneContainer
from constants import board_repr, hot_points, board_sym, board_placement, sym_map, get_zones_in_range

class BoardZone(QGraphicsPixmapItem):
    class Overlay(QPixmap):
        def __init__(self, color, item_to_overlay, image=None):
            """Create a semi-transparent overlay and clip it to the shape."""
            super().__init__()
            self.pixmap = QPixmap(item_to_overlay.pixmap().size())  # Same size as the zone
            self.pixmap.fill(Qt.transparent)  # Start with a fully transparent pixmap

            painter = QPainter(self.pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Define the highlight color (adjust opacity)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)  # No border, just the highlight fill

            # Clip to the given shape
            painter.setClipPath(item_to_overlay.shape())
            if image:
                painter.setOpacity(0.5)
                painter.drawImage(QRectF(self.pixmap.rect()), image)
            else:
                painter.drawRect(QRectF(self.pixmap.rect()))  # Fill the whole pixmap but only within the clip

            painter.end()

            self.on = False # whether the overlay is activated or not

        def activated(self, value):
            self.on = value

    def __init__(self, x, y, zid):
        assert 0 <= zid <= 16
        self.rotation = 0
        pixmap = self.retrieve_pixmap(zid)
        super().__init__(pixmap)

        self.zid = zid
        self.setPos(x, y)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setAcceptDrops(zid < 12)
        self.setAcceptHoverEvents(zid < 12)
        self.reminders = []
        hp = hot_points[zid]
        if hp:
            self.hot_point = QPointF(hp[0], hp[1])

        if zid < 12:
            self.tracking_symbols = board_sym[zid]

        self.overlays = { # in paint order
            "radiation": self.Overlay(QColor(255, 125, 125, 255), self),
            "sensor": self.Overlay(QColor(0, 0, 0, 100), self, image=QImage("res/sensor.png")),
            "valid": self.Overlay(QColor(255, 255, 0, 100), self),
            "hover": self.Overlay(QColor(9, 255, 200, 100), self)
        }

        self.container = None
        self.player_slots = None

    def set_container(self, container: QGraphicsItemGroup):
        self.container = container

        center_offset = container.mapToScene(container.boundingRect().center())
        container.setPos(self.hot_point - center_offset)

        container.setTransformOriginPoint(container.boundingRect().center())
        if not (4 <= self.zid < 8):  # do not rotate containers for middle ring
            container.setRotation(-45)

        self.container.setRotation(self.container.rotation() + self.rotation)

    def place_reminder(self, color):
        pass

    def set_radiation(self, value):
        self.overlays["radiation"].activated(True)
        self.update()

    def place_sensor(self):
        self.overlays["sensor"].activated(True)

    def is_sensor(self):
        return self.overlays["sensor"].on

    def retrieve_pixmap(self, zone_id):
        if 0 <= zone_id < 4:
            self.rotation = zone_id * 90
            img_path = "res/outer_ring.png"
        elif 4 <= zone_id < 8:
            self.rotation = (zone_id - 4) * 90
            img_path = "res/middle_ring.png"
        elif 8 <= zone_id < 12:
            self.rotation = (zone_id - 8) * 90
            img_path = "res/inner_ring.png"
        elif 12 <= zone_id < 16:
            self.rotation = (zone_id - 12) * 90
            img_path = "res/shuttle_bay.png"
        elif zone_id == 16:
            img_path = "res/reactor.png"
        else:
            return

        return QPixmap(img_path).transformed(QTransform().rotate(self.rotation))

    def paint(self, painter, option, widget=None):
        """Custom paint method to draw the pixmap and a border if highlighted."""
        super().paint(painter, option, widget)  # Draw the pixmap

        for overlay in self.overlays.values():
            if overlay.on:
                painter.drawPixmap(0, 0, overlay.pixmap)

    def highlight_for_valid_move(self):
        self.overlays["valid"].activated(True)
        self.update()

    def is_valid_move(self):
        return self.overlays["valid"].on

    def clear_highlights(self):
        self.overlays["valid"].activated(False)
        self.overlays["hover"].activated(False)
        self.update()

    def hoverEnterEvent(self, event):
        self.overlays["hover"].activated(True)
        self.update()

    def hoverLeaveEvent(self, event):
        self.overlays["hover"].activated(False)
        self.update()

class BoardScene(QGraphicsScene):
    board_zone_selected: pyqtSignal = pyqtSignal(BoardZone, QPointF)

    def __init__(self):
        super().__init__()
        self.dragged_item = None
        self.controller = None

        self.zones = []
        self.init_board()

        self.place_hot_points()

        self.overlay = QGraphicsRectItem(self.itemsBoundingRect())  # Set the size of the overlay to match the scene
        self.overlay.setBrush(QColor(128, 128, 128, 100))  # Semi-transparent grey
        self.overlay.setZValue(9)

# ----------- Initialization --------------- #
    def init_board(self):
        self.zones = [BoardZone(pos[0], pos[1], i) for i, pos in enumerate(board_placement)]
        for z in self.zones:
            self.addItem(z)

            if z.zid < 12:
                container = ZoneContainer(z.zid)
                z.set_container(container)
                self.addItem(container)

    def place_hot_points(self):
        for p in hot_points.values():
            if p:
                circle = QGraphicsEllipseItem(QRectF(p[0], p[1], 20, 20))
                circle.setBrush(QColor(255, 0, 0))  # Set the fill color to red
                circle.setPen(QColor(0, 0, 0))  # Set the outline color to black
                self.addItem(circle)

    def set_controller(self, controller):
        self.controller = controller

# ---------- Utilities ---------- #
    def highlight_zones_for_selection(self, valid_zids: list):
        for zid in valid_zids:
            self.zones[zid].highlight_for_valid_move()

    def clear_highlights(self):
        for z in self.items():
            if isinstance(z, BoardZone):
                z.clear_highlights()

    def get_board_zone_at(self, pos):
        items_at_pos = self.items(pos)
        if items_at_pos:
            bottom_most_item = items_at_pos[-1]  # Get the last (bottom-most) item
            if isinstance(bottom_most_item, BoardZone):
                return bottom_most_item

# ----------- Event ------------- #
    def mousePressEvent(self, event):
        board_zone = self.get_board_zone_at(event.scenePos())
        if board_zone and board_zone.is_valid_move():
            self.board_zone_selected.emit(board_zone, event.scenePos())
        super().mousePressEvent(event)

    def grey_out(self, value: bool):
        if value and not self.overlay.isActive():
            self.addItem(self.overlay)
        elif not value and self.overlay.isActive():
            self.removeItem(self.overlay)

class Board(QGraphicsView):
    def __init__(self, scene):
        super().__init__()
        self.setScene(scene)
        self.setMouseTracking(True)
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
        self.scale(1.55, 1.55)

