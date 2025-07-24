import json
import sys
from typing import Callable

from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QShortcut

from board import Board, BoardScene
from controller import BoardController
from constants import board_sym, sym_map
from ui import Gui, GameSetupPopup


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.board_scene = BoardScene()
        self.board = Board(self.board_scene)
        self.gui = Gui()

        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        widget = QWidget()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.board)
        self.layout.addWidget(self.gui)
        widget.setLayout(self.layout)

        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    bcontroller = BoardController(window)
    popup = GameSetupPopup()
    if popup.exec_():
        bcontroller.initiate_game(popup.get_value())

    window.showMaximized()
    sys.exit(app.exec_())