from generation_costs import *
from print_results import *
from plot_results import *
import timeit


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


class Computing:
    def __init__(self, parameter_set):
        self.parameter_set = parameter_set

    def compute(self, end_tuple, h2_demand, year, centralised, pipeline, max_pipeline_dist):
        """Executes a single run of the complete model. Takes the desired end location [lat, long], the H2 demand (
        kt/yr), the year, if redistribution is centralised or not, if pipelines are allowed, and the maximum allowed
        pipeline distance (km) as input. Calculates the minimum of (transport + generation) cost for all possible start
        locations to determine the cheapest source of renewable H2. """

        df = pd.read_csv('Data/renewables.csv', index_col=0)

        # Calculate generation and transport costs
        print('Calculating generation costs...')
        df = generation_costs(df, h2_demand, year=year)
        print('Calculating transport costs...')
        df = transport_costs(df, end_tuple, h2_demand, centralised=centralised, pipeline=pipeline,
                             max_pipeline_dist=max_pipeline_dist)

        df['Total Yearly Cost'] = df['Yearly gen. cost'] + df['Yearly Transport Cost']
        df['Total Cost per kg H2'] = df['Gen. cost per kg H2'] + df['Transport Cost per kg H2']

        df.to_csv('Results/' + str(round(end_tuple[0])) + ',' + str(round(end_tuple[1])) + '.csv')

        return df

    def run_single_model(self):
        # get parameters for the main model
        latitude = self.parameter_set.get_lat()
        longitude = self.parameter_set.get_lat()

        end_tuple = (latitude, longitude)  # [lat, long]

        demand = self.parameter_set.get_demand()
        year = self.parameter_set.get_year()
        centralised = self.parameter_set.get_allow_centralised()
        pipeline = self.parameter_set.get_allow_pipeline()
        max_dist = self.parameter_set.get_max_pipe_dist()

        # start timer
        start = timeit.default_timer()

        df = self.compute(end_tuple, demand, year, centralised, pipeline, max_dist)

        df.to_csv('Results/final_df.csv')

        # stop timer
        stop = timeit.default_timer()
        print('Total Time: ', stop - start)

        print_basic_results(df)

        get_path(df, end_tuple, centralised, pipeline)

        #return df
