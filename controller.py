import random

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction

from action import Action, Deck, Card, Sensor
from board import BoardZone
from ui import RadialMenuItem
from pieces import Player
from constants import board_repr, opposite_board_zones, PLAYABLE_ZONES, get_zones_in_range


class BoardController(QObject):

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.board_view = window.board
        self.board_scene = self.board_view.scene()
        self.board_scene.set_controller(self)
        self.gui = self.window.gui
        self.gui.card_selected.connect(self.initialize_action)

        self.deck = Deck()

        self.player = None
        self.students_turn = True # False means Anomaly's turn, could use ptype instead

        self.anomaly = Player(Player.ANOMALY)
        self.students = [
            Player(Player.STUDENT),
        ]

        self.current_action = None

        self.reminder_color = None
        actions = []
        for color in ["red", "blue", "green", "black"]:
            act: QAction = QAction(color)
            act.triggered.connect(self.prompt_for_reminder_selection)
            actions.append(act)

        self.menu = RadialMenuItem(actions)
        self.radiated_zones = [16]

    def initiate_game(self, ptype):
        self.player = self.anomaly if ptype == Player.ANOMALY else self.students[0]

        self.deal_cards()

        self.place_fuel_sources()
        self.board_scene.board_zone_selected.connect(self.place_player_on_board)
        self.prompt_for_selection(self.player, [3])


    def place_fuel_sources(self):
        for n in [0, 4, 8]:
            board_zone: BoardZone = self.get_zone_by_id(random.choice(range(n, n + 4)))
            opp_board_zone = self.get_zone_by_id(opposite_board_zones[board_zone.zid])

            for z in [board_zone, opp_board_zone]:
                z.container.set_fuel_source(True)

    def prompt_for_selection(self, player: Player, zrange, sensor=False):
        self.gui.disable_all()
        current_zid = player.zid() if player.zid() >= 0 else 0
        zids_in_range = get_zones_in_range(current_zid, zrange)
        if sensor:
            zids_in_range = filter(lambda z: not self.board_scene.zones[z].is_sensor(), zids_in_range)
        self.board_scene.highlight_zones_for_selection(zids_in_range)

    def prompt_for_color_selection(self):
        self.gui.disable_all()
        self.window.disable_shortcuts()
        self.board_scene.grey_out(True)

        self.menu.setPos(self.board_view.mapToScene(self.board_view.mapFromGlobal(QCursor.pos())))
        self.board_scene.addItem(self.menu)

    def prompt_for_reminder_selection(self):
        self.reminder_color = self.menu.get_selected_color()
        self.board_scene.grey_out(False)
        self.board_scene.highlight_zones_for_selection(PLAYABLE_ZONES)

    def reset_normal_mode(self):
        self.gui.enable_all()
        # self.window.activate_shortcuts()
        self.board_scene.clear_highlights()
        self.current_action = None

    def get_zone_by_id(self, zone_id):
        assert 0 <= zone_id <= 16
        return self.board_scene.zones[zone_id]
    # ------------- Action Handling -------------- #

    def initialize_action(self, card: Card):
        """
        Initialize the action for the player. Prompts the player for selection depending on which action was selected.
        If no selection is necessary, bypasses directly to process_player_action(...).
        :return:
        """
        self.reset_normal_mode()

        if isinstance(card, Card):
            action = card.get_special_action(self.player)
            self.current_action = action

            if action.requires_selection:
                self.prompt_for_selection(self.player, action.zrange, sensor=isinstance(action, Sensor))
            else:
                self.process_player_action(self.player.zone, None)
        else:
            # maybe need to reset the action -> Action shouldn't change. It should always remain the same.
            self.reset_normal_mode()

    def process_player_action(self, target_zone, scene_pos, player=None):
        """
        Method to process the player action on the given player.
        :param action:
        :param player: Player to apply the action on. Defaults to this client's player.
        :return:
        """
        action = self.current_action

        if player is None:
            player = self.player

        action.execute(self.board_scene, target_zone, scene_pos, player)

        action.step()

        if action.completed():
            self.gui.consume_action_card()
            self.current_action = None
            self.reset_normal_mode()

    def deal_cards(self):
        # calculate number of cards to draw based on number of players, etc.
        for student in self.students:
            student.add_cards(self.deck.draw(4))

        self.gui.update_cards(self.player.cards)

    def place_player_on_board(self, target_zone, scene_pos, player=None):
        if player is None:
            player = self.player
        player.move(scene_pos, target_zone)
        self.board_scene.addItem(player)
        self.board_scene.board_zone_selected.disconnect()
        self.board_scene.board_zone_selected.connect(self.process_player_action)

        self.reset_normal_mode()

    def place_radiation(self):
        valid_zones_for_radiation = []

        for z in self.radiated_zones:
            valid_zones_for_radiation.extend(
                [adj_zone for adj_zone in board_repr[z] if not self.is_radiated(adj_zone)])

        if len(valid_zones_for_radiation) != 0:
            zid = random.choice(valid_zones_for_radiation)
            self.radiated_zones.append(zid)
            self.board_scene.zones[zid].set_radiation(True)
        else:
            self.gui.radiation_button.setDisabled(True)

    def is_radiated(self, zone_id):
        return zone_id in self.radiated_zones

    # TODO: Make tracking symbols selectable when moving on a new zone
