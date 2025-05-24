from source import *

class App:
    def __init__(self, initialize: bool):
        self.initialize = initialize

        espn = ESPNDepthChart()

        if self.initialize:
            ndp = NDPDepthChart([2024])
            schedules = Schedules([2025])
        else:
            ndp = NDPDepthChart.__new__(NDPDepthChart)
            schedules = Schedules.__new__(Schedules)

        statistics = Statistics([2024])

        self.data = [espn, ndp, schedules, statistics]

    def run(self):
        for data in self.data:
            data.run()

    def save(self):
        db = SQLiteCacheManager()

        for data in self.data:
            data.save_to_db(db)
        
        db.close()
    
    def load(self):
        db = SQLiteCacheManager()

        for data in self.data:
            data.load_from_db(db)
                        
        db.close()

    def output(self):
        excel = Excel()

        for data in self.data:
            excel.output_dfs(data.cache, data.__class__.__name__)

        excel.close()