from flask import Flask, request, jsonify

app = Flask(__name__)

# Une variable pour stocker des données (comme l'état du jeu)
game_data = {"player1": {}, "player2": {}, "turn": "player1"}

# Endpoint pour récupérer les données du jeu
@app.route('/get_game_data', methods=['GET'])
def get_game_data():
    return jsonify(game_data)

# Endpoint pour mettre à jour les données (via POST)
@app.route('/update_game_data', methods=['POST'])
def update_game_data():
    new_data = request.json  # Récupère les données envoyées par un client
    game_data.update(new_data)  # Met à jour les données du jeu
    return jsonify({"message": "Game data updated", "new_data": game_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Le serveur écoute sur le port 5000