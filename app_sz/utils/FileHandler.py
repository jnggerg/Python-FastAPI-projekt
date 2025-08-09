import json

class FileHandler:
    path = "kurzusok.json"

    def ReadKurzusok(self):
        try:
            with open(self.path, "r") as f:
                kurzusok = json.load(f)
                return kurzusok
        except FileNotFoundError:
            return []
        
    def UpdateKurzusok(self, kurzusok):
        with open(self.path, "w") as f:
            json.dump(kurzusok, f, indent=4)


