import random
from abc import abstractmethod

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from constants import TELEPORT_RANGE, INFINITE_RANGE
from pieces import Player

class Action:
    def __init__(self, display_text, zrange, atype, requires_selection=True, steps=1):
        self.zrange = zrange
        self.requires_selection = requires_selection
        self.steps = steps
        self.count = 0
        self.atype = atype
        self.display_text = display_text

    def reset_count(self):
        self.count = 0

    def step(self):
        self.count += 1

    def completed(self):
        return self.count == self.steps

    @abstractmethod
    def execute(self, board_scene, target_zone, scene_pos: QPointF, player: Player):
        pass

class Stims(Action):
    def __init__(self):
        super().__init__("Stims", [1, 2], Player.STUDENT)

    def execute(self, board_scene, target_zone, scene_pos, player):
        player.move(scene_pos, target_zone)

class Trap(Action):
    def __init__(self):
        super().__init__("Trap", [0], Player.STUDENT, requires_selection=False)

    def execute(self, board_scene, target_zone, scene_pos, player):
        target_zone.container.place_trap()

class Sensor(Action):
    def __init__(self):
        super().__init__("Sensor", [0, 1], Player.STUDENT)

    def execute(self, board_scene, target_zone, scene_pos, player):
        target_zone.place_sensor()

class Bait(Action):
    def __init__(self):
        super().__init__("Bait", [0, 1], Player.STUDENT)

    def execute(self, board_scene, target_zone, scene_pos, player):
        pass

class _Hit(Action):
    def __init__(self, text, zrange, steps=1, requires_selection=True, damage=1):
        super().__init__(text, zrange, Player.STUDENT, steps=steps, requires_selection=requires_selection)
        self.damage = damage

    def execute(self, board_scene, target_zone, scene_pos, player):
        if target_zone.container.fuel_source:
                 target_zone.container.set_fuel_source(False)

class Bludgeon(_Hit):
    def __init__(self):
        super().__init__("Bludgeon", [0], requires_selection=False, damage=2)

class StunBaton(_Hit):
    def __init__(self):
        super().__init__("Stun Baton", [0], requires_selection=False, damage=3)

class SingleShot(_Hit):
    def __init__(self):
        super().__init__("Single Shot", [0, 1])

class DoubleShot(_Hit):
    def __init__(self):
        super().__init__("Double Shot", [0, 1], steps=2)

class LongShot(_Hit):
    def __init__(self):
        super().__init__("Long Shot", [0, 1, 2])

# ------------- ANOMALY Actions ------------------ #

class Electricity(Action):
    def __init__(self):
        super().__init__("Electricity", [3], Player.ANOMALY, steps=2)

    def execute(self, board_scene, target_zone, scene_pos, player):
        target_zone.container.place_electricity()

class Teleport(Action):
    def __init__(self):
        super().__init__("Teleport", TELEPORT_RANGE, Player.ANOMALY)

    def execute(self, board_scene, target_zone, scene_pos, player):
        player.move(scene_pos, target_zone)

class Evolve(Action):
    def __init__(self):
        super().__init__("Evolve", [], Player.ANOMALY, requires_selection=False)

    def execute(self, board_scene, target_zone, scene_pos, player):
        pass

class Possess(Action):
    def __init__(self):
        super().__init__("Possess", [0], Player.ANOMALY, requires_selection=False)

    def execute(self, board_scene, target_zone, scene_pos, player):
        pass

class Scent(Action):
    def __init__(self):
        super().__init__("Scent", INFINITE_RANGE, Player.ANOMALY, requires_selection=True)

    def execute(self, board_scene, target_zone, scene_pos, player):
        pass


class Card(QWidget):
    def __init__(self, student_action, anomaly_action):
        super().__init__()

        layout = QVBoxLayout()

        self.student_action = student_action
        self.anomaly_action = anomaly_action

        self.slabel = QLabel(student_action.display_text)
        self.slabel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.alabel = QLabel(anomaly_action.display_text)
        self.alabel.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout.addWidget(self.slabel)
        layout.addWidget(self.alabel)

        self.setLayout(layout)
        self.setFixedSize(90, 150)

        self.selected = False

    def get_special_action(self, player: Player):
        return self.anomaly_action if player.is_anomaly() else self.student_action

class Deck:
    def __init__(self):
        self.cards = [
            Card(Stims(), Electricity()),
            Card(Trap(), Electricity()),
            Card(Bait(), Electricity()),
            *[Card(Bludgeon(), Electricity()) for _ in range(2)],
            *[Card(SingleShot(), Electricity()) for _ in range(4)],

            Card(Trap(), Evolve()),
            *[Card(Sensor(), Evolve()) for _ in range(2)],
            Card(Bait(), Evolve()),
            Card(Stims(), Evolve()),
            Card(SingleShot(), Evolve()),
            Card(LongShot(), Evolve()),
            *[Card(Bludgeon(), Evolve()) for _ in range(2)],

            Card(Sensor(), Possess()),
            Card(Bait(), Possess()),
            Card(DoubleShot(), Possess()),
            Card(Bludgeon(), Possess()),
            *[Card(LongShot(), Possess()) for _ in range(2)],

            *[Card(Trap(), Scent()) for _ in range(4)],
            Card(Stims(), Scent()),
            *[Card(SingleShot(), Scent()) for _ in range(2)],
            Card(LongShot(), Scent()),

            *[Card(DoubleShot(), Teleport()) for _ in range(3)],
            Card(StunBaton(), Teleport())
        ]

        random.shuffle(self.cards)

    def draw(self, nb_of_cards):
        cards_drawn = self.cards[0:nb_of_cards]
        self.cards = self.cards[nb_of_cards:]
        return cards_drawn

    def test_hand(self):
        return self.cards[10:12]