import requests

# URL du serveur Flask
server_url = "http://127.0.0.1:5000"

# Récupérer les données du jeu
response = requests.get(f"{server_url}/get_game_data")
game_data = response.json()
print("Données du jeu récupérées :", game_data)

# Envoyer une mise à jour
new_data = {"player1": {"score": 10}, "turn": "player2"}
response = requests.post(f"{server_url}/update_game_data", json=new_data)
print("Réponse du serveur :", response.json())
