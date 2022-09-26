import pandas as pd
import numpy as np


# Costs by material

def nh3_costs(pipe_dist=99.57142, ship_dist=1.926, truck_dist=-83.0, convert=True, centralised=True, pipeline=True, max_pipeline_dist=2000):
    """Calculates the transport cost of NH3. Requires as input the distance that NH3 will be piped, shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(1.00, 1.02, 1.04)
        export = np.random.triangular(0.1, 0.11, 0.12)
        if centralised:
            reconversion = np.random.triangular(0.8, 0.85, 0.9)
        else:
            reconversion = np.random.triangular(1.10, 1.13, 1.16)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(2.32E-02, 2.323E-02, 2.326E-2) * np.log(ship_dist) - 1.523E-02
    if max_pipeline_dist > pipe_dist > 400:
        pipe = np.random.triangular(0.00065, 0.0007, 0.00075) * pipe_dist - 0.0697
    elif pipe_dist < 400:
        pipe = np.random.triangular(0.00065, 0.0007, 0.00075) * 400 - 0.0697
    else:
        pipe = np.nan

    if pipeline == False:
        pipe = np.nan

    truck = np.random.triangular(0.00075, 0.0008, 0.00085) * truck_dist + 0.0664

    total = conversion + export + ship + pipe + truck + reconversion

    return total


def h2_gas_costs(pipe_dist=-102.75, truck_dist=-106.0, pipeline=True, max_pipeline_dist=2000):
    """Calculates the transport cost of H2 gas. Requires as input the distance that H2 will be piped and
    trucked. Calculation values are drawn from triangular distributions."""

    if max_pipeline_dist > pipe_dist > 400:
        pipe = np.random.triangular(0.00035, 0.0004, 0.00045) * pipe_dist + 0.0424
    elif pipe_dist < 400:
        pipe = np.random.triangular(0.00035, 0.0004, 0.00045) * 400 + 0.0424
    else:
        pipe = np.nan

    if pipeline == False:
        pipe = np.nan

    truck = np.random.triangular(0.0025, 0.003, 0.0035) * truck_dist + 0.3319

    return pipe + truck


def lohc_costs(ship_dist=4.9699, truck_dist=-94.78571, convert=True, centralised=True):
    """Calculates the transport cost of LOHC. Requires as input the distance that LOHC will be shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(0.36, 0.41, 0.46)
        export = np.random.triangular(0.08, 0.10, 0.12)
        if centralised:
            reconversion = np.random.triangular(1, 1.1, 1.2)
        else:
            reconversion = np.random.triangular(2.3, 2.35, 2.4)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(3.4E-2, 3.404E-02, 3.408E-2) * np.log(ship_dist) - 5.458E-02
    truck = np.random.triangular(0.001, 0.0014, 0.0018) * truck_dist + 0.1327

    return conversion + export + ship + truck + reconversion


def h2_liq_costs(ship_dist=0.1915, truck_dist=-22.11666, convert=True, centralised=True):
    """Calculates the transport cost of liquid H2. Requires as input the distance that H2 will be shipped and
    trucked, as well as a boolean variable denominating if the distribution point is centralised or not.
    Calculation values are drawn from triangular distributions."""

    if convert == True:
        conversion = np.random.triangular(1, 1.03, 1.06)
        export = np.random.triangular(0.8, 0.88, 0.96)
        if centralised:
            reconversion = np.random.triangular(0.01, 0.02, 0.03)
        else:
            reconversion = np.random.triangular(0.01, 0.02, 0.03)
    else:
        conversion = 0
        reconversion = 0
        export = 0

    ship = np.random.triangular(0.135, 1.353E-01, 1.356E-1) * np.log(ship_dist) + 2.236E-01
    truck = np.random.triangular(0.005, 0.006, 0.007) * truck_dist + 0.1327

    return conversion + export + ship + truck + reconversion
