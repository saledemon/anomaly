import requests

# URL du serveur Flask
server_url = "https://zacroc1.dreamhosters.com/content/server"

def get_test():
    response = requests.get(f"{server_url}")
    data = response.json()
    print(data["message"])

def get_burger_pos():
    response = requests.get(f"{server_url}/burger_pos.php")
    data = response.json()
    print(data)
    if "pos" in data.keys():
        return data["pos"], data["zone"]
    else:
        return None, None

def post_burger_pos(pos, zone):
    """
    Send the position in the Scene to update the burger's position on the server
    :param zone: int The Board Zone associated with the position
    :param pos: Scene Pos
    :return:
    """
    response = requests.post(f"{server_url}/move_burger.php", json={"pos":(pos.x(), pos.y()), "zone":zone.zone_id})
    print(response)
    return response

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

#print(update_game_state())
