import requests

# URL du serveur Flask
server_url = "https://zacroc1.dreamhosters.com"

def get_game_state():
    # Récupérer les données du jeu
    response = requests.get(f"{server_url}/get_game_data")
    print(response)
    game_data = response.json()
    return game_data

def update_game_state():
    # Envoyer une mise à jour
    new_data = {"player1": {"score": 10}, "turn": "player2"}
    response = requests.post(f"{server_url}/update_game_data", json=new_data)
    return response

print(get_game_state())
#print(update_game_state())
