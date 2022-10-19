import pandas as pd
import numpy as np


# Costs by material
# values taken from non mc-program, boundaries are 90% (lower) and 110% (upper) of the initial value
# except H2 liquefaction conversion cost where different boundaries were found in the literature

def nh3_costs(pipe_dist=99.57142, ship_dist=1.926, truck_dist=-83.0, convert=True, centralised=True, pipeline=True, max_pipeline_dist=2000):
    """Calculates the transport cost of NH3. Requires as input the distance that NH3 will be piped, shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(0.918, 1.02, 1.122)
        export = np.random.triangular(0.099, 0.11, 0.121)
        if centralised:
            reconversion = np.random.triangular(0.765, 0.85, 0.935)
        else:
            reconversion = np.random.triangular(1.017, 1.13, 1.243)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(2.0907E-02, 2.323E-02, 2.5553E-2) * np.log(ship_dist) - 1.523E-02
    if max_pipeline_dist > pipe_dist > 400:
        pipe = np.random.triangular(0.00063, 0.0007, 0.00077) * pipe_dist - 0.0697
    elif pipe_dist < 400:
        pipe = np.random.triangular(0.00063, 0.0007, 0.00077) * 400 - 0.0697
    else:
        pipe = np.nan

    if pipeline == False:
        pipe = np.nan

    truck = np.random.triangular(0.00072, 0.0008, 0.00088) * truck_dist + 0.0664

    total = conversion + export + ship + pipe + truck + reconversion

    return total


def h2_gas_costs(pipe_dist=-102.75, truck_dist=-106.0, pipeline=True, max_pipeline_dist=2000):
    """Calculates the transport cost of H2 gas. Requires as input the distance that H2 will be piped and
    trucked. Calculation values are drawn from triangular distributions."""

    if max_pipeline_dist > pipe_dist > 400:
        pipe = np.random.triangular(0.00036, 0.0004, 0.00044) * pipe_dist + 0.0424
    elif pipe_dist < 400:
        pipe = np.random.triangular(0.00036, 0.0004, 0.00044) * 400 + 0.0424
    else:
        pipe = np.nan

    if pipeline == False:
        pipe = np.nan

    truck = np.random.triangular(0.0027, 0.003, 0.0033) * truck_dist + 0.3319

    return pipe + truck


def lohc_costs(ship_dist=4.9699, truck_dist=-94.78571, convert=True, centralised=True):
    """Calculates the transport cost of LOHC. Requires as input the distance that LOHC will be shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(0.369, 0.41, 0.451)
        export = np.random.triangular(0.09, 0.1, 0.11)
        if centralised:
            reconversion = np.random.triangular(0.99, 1.1, 1.21)
        else:
            reconversion = np.random.triangular(2.115, 2.35, 2.585)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(3.0636E-2, 3.404E-02, 3.7444E-2) * np.log(ship_dist) - 5.458E-02
    truck = np.random.triangular(0.00126, 0.0014, 0.00154) * truck_dist + 0.1327

    return conversion + export + ship + truck + reconversion


def h2_liq_costs(ship_dist=0.1915, truck_dist=-22.11666, convert=True, centralised=True):
    """Calculates the transport cost of liquid H2. Requires as input the distance that H2 will be shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(0.92, 1.03, 1.38)
        export = np.random.triangular(0.792, 0.88, 0.968)
        if centralised:
            reconversion = np.random.triangular(0.018, 0.02, 0.022)
        else:
            reconversion = np.random.triangular(0.018, 0.02, 0.022)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(0.12177, 1.353E-01, 1.4883E-1) * np.log(ship_dist) + 2.236E-01
    truck = np.random.triangular(0.0054, 0.006, 0.0066) * truck_dist + 0.1327

    return conversion + export + ship + truck + reconversion
