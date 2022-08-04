

class ParameterSet:
    def __init__(self):
        # parameter initialisation
        self.longitude = 0
        self.latitude = 0
        self.demand = 0
        self.year = 2020
        self.centralised = False
        self.pipeline = False
        self.max_dist = 0
        self.iterations = 0
        self.electrolyzer_type = 'alkaline'

    # getter functions to be called by run_single_model because the signal can't pass on all the
    # parameters as arguments

    def get_long(self):
        return self.longitude

    def get_lat(self):
        return self.latitude

    def get_demand(self):
        return self.demand

    def get_year(self):
        return self.year

    def get_allow_centralised(self):
        return self.centralised

    def get_allow_pipeline(self):
        return self.pipeline

    def get_max_pipe_dist(self):
        return self.max_dist

    def get_iterations(self):
        return self.iterations

    def get_elec_type(self):
        return self.electrolyzer_type
