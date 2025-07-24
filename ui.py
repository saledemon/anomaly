import math

from PyQt5.QtCore import QRectF, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QVBoxLayout, QPushButton, QLabel, QDialog, QWidget

from action import Card
from constants import board_sym, sym_map
from pieces import Player


class RadialMenuItem(QGraphicsItem):
    def __init__(self, actions):
        super().__init__()
        self.actions = actions
        self.radius = 50
        self.setZValue(10)  # Ensure it's above other elements
        self.selected_color = ""

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, option, widget=None):
        num_actions = len(self.actions)
        angle_step = 360 / num_actions

        for i, action in enumerate(self.actions):
            start_angle = i * angle_step
            color = QColor(action.text())
            painter.setBrush(QBrush(color))
            painter.drawPie(self.boundingRect(), int(start_angle * 16), int(angle_step * 16))

    def mousePressEvent(self, event):
        angle = math.degrees(math.atan2(-event.pos().y(), event.pos().x())) % 360
        index = int(angle // (360 / len(self.actions)))
        if 0 <= index < len(self.actions):
            self.selected_color = self.actions[index].text()
            self.actions[index].trigger()
        self.scene().removeItem(self)  # Remove the menu after selection

    def get_selected_color(self):
        return self.selected_color

class Gui(QWidget):

    card_selected: pyqtSignal = pyqtSignal(Card)

    def __init__(self):
        super().__init__()
        self.card_layout = QVBoxLayout()
        self.cards = []
        self.selected_card = None

        self.setLayout(self.card_layout)

    def update_cards(self, cards):
        for c in cards:
            if not c in self.cards:
                self.cards.append(c)
                self.card_layout.addWidget(c)

    def mousePressEvent(self, e):
        card = self.childAt(e.pos())
        if isinstance(card, Card):
            self.select_card(card)

    def select_card(self, card):
        if card is self.selected_card:
            card.setStyleSheet("")
            self.card_selected.emit(None)
            self.selected_card = None
        else:
            if self.selected_card:
                self.selected_card.setStyleSheet("")
            card.setStyleSheet("background-color: yellow; border: 2px solid red;")
            self.selected_card = card
            self.card_selected.emit(card)

    def consume_action_card(self):
        """
        Called by the controller after an action has been completed. The card should either
        be discarded or given to the Anomaly player depending on if the player played a basic
        or special action (and whether the player is Anomaly or Student)
        """
        self.discard(self.selected_card)
        self.selected_card.student_action.reset_count()
        self.selected_card.anomaly_action.reset_count()
        self.selected_card = None

    def discard(self, card):
        self.card_layout.removeWidget(card)
        card.setParent(None)

    def disable_all(self):
        pass

    def enable_all(self):
        pass

    def choose_tracking_cards(self, zone_id):
        for i, s in enumerate(board_sym[zone_id]):
            self.choice_labels[i].setPixmap(QPixmap(sym_map[s]))
            self.choice_labels[i].repaint()

class GameSetupPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Setup")
        self.current_choice = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Play as..."))
        self.student_btn: QPushButton = QPushButton("Student")
        self.anomaly_btn: QPushButton = QPushButton("Anomaly")
        self.student_btn.clicked.connect(self.toggle_choice)
        self.anomaly_btn.clicked.connect(self.toggle_choice)

        self.start_btn: QPushButton = QPushButton("Start Game")
        self.start_btn.setDisabled(True)
        self.start_btn.clicked.connect(self.accept)
        self.start_btn.setDefault(True)

        layout.addWidget(self.student_btn)
        layout.addWidget(self.anomaly_btn)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)
        self.setModal(True)  # This blocks Main Window until closed

    def toggle_choice(self):
        button = self.sender()
        if self.current_choice and self.current_choice != button:
            self.current_choice.setStyleSheet("")

        self.current_choice = button
        button.setStyleSheet("""QPushButton{background-color: blue;}""")
        self.start_btn.setDisabled(False)

    def get_value(self):
        return Player.ANOMALY if self.current_choice is self.anomaly_btn else Player.STUDENT

# TODO:
#  give to anomaly player (or not) after student play or discard,
#  ✅toggle action card selection (radio button-like behavior),
#  card design,
#  consume for basic or special action,
#  pass button for anomaly,
#  rotate cards according to player type

# TODO: in action ->
#  create more action
#  ✅ make sure steps() functions the right way, re-initialize card action steps before reusing
#  ✅ place sensor only on tiles that do not already have a sensor (affects the selection, filter the selection...)
