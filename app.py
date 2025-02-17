import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QHBoxLayout

from board import Board, BoardScene
from controller import BoardController

class Gui(QVBoxLayout):
    def __init__(self, scene):
        super().__init__()
        self.board_scene = scene
        self.button: QPushButton = QPushButton("Move")
        self.button.clicked.connect(self.board_scene.initiateMove)

        self.addWidget(self.button)

    def disable_all(self):
        self.button.setDisabled(True)

    def enable_all(self):
        self.button.setDisabled(False)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.board_scene = BoardScene()
        self.board = Board(self.board_scene)

        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        widget = QWidget()
        layout = QHBoxLayout()
        gui = Gui(self.board_scene)
        layout.addLayout(gui)
        layout.addWidget(self.board)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.controller = BoardController()
        self.controller.setBoard(self.board)
        self.controller.setGui(gui)
        self.board_scene.setController(self.controller)
        self.controller.initiate_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.showMaximized()
    sys.exit(app.exec_())