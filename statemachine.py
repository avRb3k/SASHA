import json

class iot_json:
    def __init__(self):
        self.file = "data.json"
    def check(self, name):
        with open(self.file) as f:
            data = json.load(f)
        f.close()
        Zustand = data["clients"]["name"== name]["bool_0"]
        print(Zustand)
        return Zustand
    def switch(self, topic , Zustand):
        with open(self.file) as f:
            data = json.load(f)
        if data["clients"]["topic" == topic]["bool_0"] != Zustand:
            data["clients"]["topic" == topic]["bool_0"] = Zustand
            with open(self.file, "w") as f:
                json.dump(data, f)
            f.close()
        else:
            f.close()

class scrape_json:
    def __init__(self):
        self.file = "data.json"
    def check(self, name):
        with open(self.file) as f:
            data = json.load(f)
        f.close()
        ersterWert = data["scraper"]["name"== name]["value_1"]
        zweiterWert = data["scraper"]["name" == name]["value_2"]
        dritterWert = data["scraper"]["name" == name]["value_3"]
        return ersterWert, zweiterWert, dritterWert
    def switch(self, name , ersterWert, zweiterWert):
        with open(self.file) as f:
            data = json.load(f)
            data["scraper"]["name" == name]["value_1"] = ersterWert
            data["scraper"]["name" == name]["value_2"] = zweiterWert
        with open(self.file, "w") as f:
            json.dump(data, f)
        f.close()
# test = state_json()
#
# y = test.check(name="Lampe")
















