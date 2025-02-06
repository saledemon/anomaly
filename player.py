class Player:
    def __init__(self):
        self.cards = []
        self.reminders = []
        self.position = -1

    def is_move_valid(self, move_to):
        # need logic for movement
        return type(move_to) is int and 0 <= move_to <= 15

    def move(self, move_to):
        pass  # change the position

    def play_special_action(self, card):
        pass

    def place_reminder(self):
        pass # place a reminder on the map for a specific player


class AnomalyPlayer(Player):
    def __init__(self):
        super().__init__()
        self.power_ups = []
        self.action_tokens = 3
        self.actions = ["move", "feed", "free special action"]

    def feed(self):
        pass


class StudentPlayer(Player):
    def __init__(self):
        super().__init__()
        self.actions = ["move", "track", "special action"]
        self.tracking_info = []

    def track(self):
        pass

class GameState:
    def __init__(self):
        self.health_students = 0
        self.health_anomaly = 0
        self.health_zero_marker = 0


        self.fuel_tanks = []
        self.radiation = []
        self.action_cards_deck = []

    def reveal_player_pos(self):
        pass