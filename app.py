import sys

from PyQt5.QtCore import Qt, QMimeData, QRectF
from PyQt5.QtGui import QPixmap, QDrag, QPen, QPainterPath, QPainterPathStroker, QColor, QTransform, QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow, QApplication, \
    QGraphicsPixmapItem, QPushButton, QVBoxLayout, QWidget

from board import Board, BoardScene
from player import GameState, Player

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.board_scene = BoardScene()
        self.board = Board(self.game_state, self.board_scene)

        self.setWindowTitle("Game Board with GUI")
        self.setGeometry(100, 100, 800, 600)

        button: QPushButton = QPushButton("Move")
        button.clicked.connect(self.board_scene.initiateMove)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.board)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec_())