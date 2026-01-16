from backend import *

class App:
    def __init__(self):
       self.db = SQLService()
       self.caches = {}
    
    def run(self):
        instances = [ESPNDepthChart(), NDPDepthChart([2024]), Schedules([2025]), Statistics([2024])]

        for instance in instances:
            instance.run()
            self.caches[instance.__class__.__name__] = instance.get_cache()
        
    def save(self):
        for name, cache in self.caches.items():
            self.db.save_to_db(cache, name)

    def load(self):
        instances = [ESPNDepthChart.__new__(ESPNDepthChart), NDPDepthChart.__new__(NDPDepthChart), Schedules.__new__(Schedules), Statistics.__new__(Statistics)]
        
        for instance in instances:
            name = instance.__class__.__name__
            self.caches[name] = self.db.load_from_db(instance.get_keys(), name)

    def output(self):
        excel = Excel()

        for name, cache in self.caches.items():
            excel.output_dfs(cache, name)

        excel.close()