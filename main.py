import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGridLayout, QWidget
from random import randint
from PyQt5.QtCore import Qt
from string import ascii_uppercase


class ShipPlacementWindow(QWidget):
    def __init__(self, player, game_setup_window):
        super().__init__()

        self.player = player
        self.game_setup_window = game_setup_window

        self.setWindowTitle(f"Расстановка кораблей - Игрок {self.player}")
        self.setGeometry(200, 200, 400, 400)

        self.random_button = QPushButton("Расставить случайно")
        self.random_button.clicked.connect(self.random_placement)

        self.confirm_button = QPushButton("Готово")
        self.confirm_button.clicked.connect(self.confirm_placement)

        self.grid_layout = QGridLayout()
        self.create_grid()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Игрок {self.player}"))
        layout.addLayout(self.grid_layout)
        layout.addWidget(self.random_button)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

        self.player_ships = [[0] * 10 for _ in range(10)]


    def create_grid(self):
        for row in range(11):
            for col in range(11):
                if row == 0 and col == 0:
                    continue

                if row == 0:
                    label = QLabel(ascii_uppercase[col - 1])
                    label.setAlignment(Qt.AlignCenter)
                    self.grid_layout.addWidget(label, row, col)
                elif col == 0:
                    label = QLabel(str(row))
                    label.setAlignment(Qt.AlignCenter)
                    self.grid_layout.addWidget(label, row, col)
                else:
                    button = QPushButton()
                    button.setFixedSize(30, 30)
                    button.clicked.connect(lambda _, r=row-1, c=col-1: self.grid_button_clicked(r, c))
                    self.grid_layout.addWidget(button, row, col)

    def grid_button_clicked(self, row, col):
        button = self.grid_layout.itemAtPosition(row+1, col+1).widget()
        button.setStyleSheet("background-color: blue")

    def random_placement(self):
        for row in range(10):
            for col in range(10):
                item = self.grid_layout.itemAtPosition(row+1, col+1)
                if item is not None:
                    button = item.widget()
                    button.setStyleSheet("background-color: white")

        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            self.grid_layout.removeItem(item)

        self.create_grid()

        self.place_ship(4)

        for _ in range(2):
            self.place_ship(3)

        for _ in range(3):
            self.place_ship(2)

        for _ in range(4):
            self.place_ship(1)

    def place_ship(self, size):
        while True:
            orientation = randint(0, 1)
            if orientation == 0:
                start_row = randint(0, 9)
                start_col = randint(0, 10 - size)
                end_row = start_row
                end_col = start_col + size - 1
            else:
                start_row = randint(0, 10 - size)
                start_col = randint(0, 9)
                end_row = start_row + size - 1
                end_col = start_col

            intersect = False
            for row in range(start_row - 1, end_row + 2):
                for col in range(start_col - 1, end_col + 2):
                    if 0 <= row < 10 and 0 <= col < 10:
                        button = self.grid_layout.itemAtPosition(row+1, col+1).widget()
                        if button.styleSheet() == "background-color: blue":
                            intersect = True
                            break

            if not intersect:
                break

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                button = self.grid_layout.itemAtPosition(row+1, col+1).widget()
                button.setStyleSheet("background-color: blue")

    def confirm_placement(self):
        ship_placement = self.get_ship_placement()
        self.game_setup_window.save_ship_placement(self.player, ship_placement)
        self.close()

    def get_ship_placement(self):
        ship_placement = []
        for row in range(10):
            for col in range(10):
                button = self.grid_layout.itemAtPosition(row+1, col+1).widget()
                if button.styleSheet() == "background-color: blue":
                    ship_placement.append((row, col))
        return ship_placement


class GameSetupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Настройка игры")
        self.setGeometry(200, 200, 400, 200)

        self.player1_button = QPushButton("Игрок 1")
        self.player1_button.clicked.connect(self.open_player1_window)

        self.player2_button = QPushButton("Игрок 2")
        self.player2_button.clicked.connect(self.open_player2_window)

        layout = QVBoxLayout()
        layout.addWidget(self.player1_button)
        layout.addWidget(self.player2_button)

        self.setLayout(layout)

        self.player1_ship_placement_window = None
        self.player2_ship_placement_window = None

        self.ship_placements = {}

        self.start_game_button = QPushButton("Начать игру")
        self.start_game_button.clicked.connect(self.start_game)
        self.start_game_button.setEnabled(False)

        layout.addWidget(self.start_game_button)

    def open_player1_window(self):
        if not self.player1_ship_placement_window:
            self.player1_ship_placement_window = ShipPlacementWindow(player=1, game_setup_window=self)
        self.player1_ship_placement_window.show()

    def open_player2_window(self):
        if not self.player2_ship_placement_window:
            self.player2_ship_placement_window = ShipPlacementWindow(player=2, game_setup_window=self)
        self.player2_ship_placement_window.show()

    def save_ship_placement(self, player, ship_placement):
        self.ship_placements[player] = ship_placement

        if len(self.ship_placements) == 2:
            self.start_game_button.setEnabled(True)

    def start_game(self):
        if len(self.ship_placements) == 2:
            self.game_window = GameWindow(ship_placements=self.ship_placements)
            self.game_window.show()
            self.close()


class GameWindow(QWidget):
    def __init__(self, ship_placements):
        super().__init__()

        self.setWindowTitle("Морской бой - Игровое поле")
        self.setGeometry(200, 200, 800, 400)

        self.ship_placements = ship_placements
        self.current_player = 2  # Изменено здесь

        self.layout = QHBoxLayout()
        self.player_fields = [self.create_player_field(player) for player in range(1, 3)]
        self.layout.addWidget(self.player_fields[0])  # Изменено здесь
        self.layout.addWidget(self.player_fields[1])

        self.setLayout(self.layout)

    def create_player_field(self, player):
        field_widget = QWidget()
        field_layout = QGridLayout()
        field_widget.setLayout(field_layout)

        for row in range(11):
            for col in range(11):
                if row == 0 and col == 0:
                    continue

                if row == 0:
                    label = QLabel(ascii_uppercase[col - 1])
                    label.setAlignment(Qt.AlignCenter)
                    field_layout.addWidget(label, row, col)
                elif col == 0:
                    label = QLabel(str(row))
                    label.setAlignment(Qt.AlignCenter)
                    field_layout.addWidget(label, row, col)
                else:
                    button = QPushButton()
                    button.setFixedSize(30, 30)
                    button.clicked.connect(lambda _, r=row - 1, c=col - 1: self.field_button_clicked(player, r, c))
                    field_layout.addWidget(button, row, col)

        # Добавляем QLabel в макет field_layout
        label = QLabel()
        field_layout.addWidget(label, 0, 0)

        return field_widget

    def field_button_clicked(self, player, row, col):
        button = self.player_fields[player - 1].layout().itemAtPosition(row + 1, col + 1).widget()

        if player == self.current_player:
            if (row, col) in self.ship_placements[player]:
                button.setStyleSheet("background-color: red")
            else:
                button.setStyleSheet("background-color: gray")

            if button.styleSheet() == "background-color: red":

                return

            self.update_current_player_label()
            self.current_player = 2 if self.current_player == 1 else 1


        if all(self.check_all_ships_destroyed(player) for player in range(1, 3)):
            self.show_game_over_message()

    def check_all_ships_destroyed(self, player):
        for ship in self.ship_placements[player]:
            field = self.player_fields[player-1].layout().itemAtPosition(ship[0]+1, ship[1]+1).widget()
            if field.styleSheet() != "background-color: red":
                return False
        return True

    def update_current_player_label(self):
        for player in range(1, 3):
            field = self.player_fields[player-1].layout().itemAtPosition(0, 0).widget()
            if player == self.current_player:
                field.setText("Ваш ход")  # Изменено здесь
            else:
                field.setText("")  # Изменено здесь

    def show_game_over_message(self):
        winner = "Игрок 1" if self.current_player == 2 else "Игрок 2"
        message_box = QDialog(self)
        message_layout = QVBoxLayout()
        message_layout.addWidget(QLabel(f"Игра окончена! {winner} победил."))
        message_box.setLayout(message_layout)
        message_box.setWindowTitle("Конец игры")
        message_box.setModal(True)
        message_box.exec_()
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_setup_window = GameSetupWindow()
    game_setup_window.show()
    sys.exit(app.exec())

