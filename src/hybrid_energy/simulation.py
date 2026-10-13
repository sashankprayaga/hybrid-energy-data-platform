import fastsim

def run_simulation(vehicle_resource: str, cycle_resource: str) -> dict:
    """
    Run a simulation for the given vehicle and cycle resources.

    Args:
        vehicle_resource (str): The resource path for the vehicle configuration.
        cycle_resource (str): The resource path for the driving cycle data.

    Returns:
        dict: A dictionary containing the simulation results.
    """
    vehicle = fastsim.Vehicle.from_resource(vehicle_resource)
    cycle = fastsim.Cycle.from_resource(cycle_resource)

    sim = fastsim.SimDrive(vehicle, cycle)
    sim.run()

    return sim