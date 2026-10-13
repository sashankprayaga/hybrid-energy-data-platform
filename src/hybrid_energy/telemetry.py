import pandas as pd


def build_telemetry_dataframe(sim) -> pd.DataFrame:
    """Convert a completed FASTSim simulation into telemetry."""

    data = sim.to_dict()
    veh = data["veh"]
    hev = veh["pt_type"]["HEV"]

    vehicle = veh["history"]
    battery = hev["res"]["history"]
    engine = hev["fc"]["history"]
    motor = hev["em"]["history"]

    return pd.DataFrame({
        "step": vehicle["i"],
        "time_s": vehicle["time_seconds"],
        "speed_mps": vehicle["speed_ach_meters_per_second"],
        "distance_m": vehicle["dist_meters"],
        "battery_soc": battery["soc"],
        "battery_power_w": battery["pwr_out_electrical_watts"],
        "engine_power_w": engine["pwr_prop_watts"],
        "fuel_energy_j": engine["energy_fuel_joules"],
        "motor_power_w": motor["pwr_mech_prop_out_watts"],
    })