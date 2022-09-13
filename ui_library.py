from generation_costs import *
from print_results import *
from plot_results import *
import timeit


class Computing:
    def __init__(self, parameter_set):
        self.parameter_set = parameter_set

    def compute(self, end_tuple, h2_demand, year, elec, centralised, pipeline, max_pipeline_dist):
        """Executes a single run of the complete model. Takes the desired end location [lat, long], the H2 demand (
        kt/yr), the year, if redistribution is centralised or not, if pipelines are allowed, and the maximum allowed
        pipeline distance (km) as input. Calculates the minimum of (transport + generation) cost for all possible start
        locations to determine the cheapest source of renewable H2. """

        df = pd.read_csv('Data/renewables.csv', index_col=0)

        # Calculate generation and transport costs
        print('Calculating generation costs...')
        df = generation_costs(df, h2_demand, year=year, type=elec)
        print('Calculating transport costs...')
        df = transport_costs(df, end_tuple, h2_demand, centralised=centralised, pipeline=pipeline,
                             max_pipeline_dist=max_pipeline_dist)

        df['Total Yearly Cost'] = df['Yearly gen. cost'] + df['Yearly Transport Cost']
        df['Total Cost per kg H2'] = df['Gen. cost per kg H2'] + df['Transport Cost per kg H2']

        df.to_csv('Results/' + str(end_tuple[0]) + ',' + str(end_tuple[1]) + '.csv')

        return df

    def run_single_model(self):
        # get parameters for the main model
        latitude = self.parameter_set.get_lat()
        longitude = self.parameter_set.get_long()

        end_tuple = (latitude, longitude)  # [lat, long]

        demand = self.parameter_set.get_demand()
        year = self.parameter_set.get_year()
        centralised = self.parameter_set.get_allow_centralised()
        pipeline = self.parameter_set.get_allow_pipeline()
        max_dist = self.parameter_set.get_max_pipe_dist()
        elec = self.parameter_set.get_elec_type()

        # start timer
        start = timeit.default_timer()

        df = self.compute(end_tuple, demand, year, elec, centralised, pipeline, max_dist)

        df.to_csv('Results/final_df.csv')

        # stop timer
        stop = timeit.default_timer()
        print('Total Time: ', stop - start)

        min_cost, mindex, cheapest_source, cheapest_medium, cheapest_elec = print_basic_results(df)

        final_path = get_path(df, end_tuple, centralised, pipeline)

        return min_cost, mindex, cheapest_source, cheapest_medium, cheapest_elec, final_path