import requests

class PokeServer:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.session = requests.Session()

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        return response.json()
    
    def get_id_from_mon(self, name):
        response = self.get(f"pokemon/{name}")
        if 'id' not in response:
            print("Pokemon not found")
            exit()
        return int(response['id'])
    
    def get_mon_from_id(self, id):
        response = self.get(f"pokemon/{id}")
        if 'name' not in response:
            print("Pokemon not found")
            exit()
        return response['name']