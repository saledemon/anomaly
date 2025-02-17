from PyQt5.QtCore import pyqtSignal, QObject

from board import BoardZone


class BoardController(QObject):
    selection_made: pyqtSignal = pyqtSignal(BoardZone)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BoardController, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        super().__init__()
        if not self.initialized:
            self.board_view = None
            self.board_scene = None
            self.player = None
            self.gui = None

            self.selection_made.connect(self.place_player_on_board)
            self.initialized = True

    def setBoard(self, board):
        self.board_view = board
        self.board_scene = board.scene
        self.player = board.scene.player

    def setGui(self, gui):
        self.gui = gui

    def initiate_game(self):
        self.wait_for_selection()

    def wait_for_selection(self):
        self.gui.disable_all()
        self.board_scene.highlight_all()

    def place_player_on_board(self, selected_zone):
        self.player.move(selected_zone)

        if not self.player in self.board_scene.items():
            self.board_scene.addItem(self.player)

        # -> choose tracking cards

        self.gui.enable_all()
        self.board_scene.clear_highlights()