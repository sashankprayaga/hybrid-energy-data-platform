import fastsim
import pandas as pd
from pathlib import Path


vehicle = fastsim.Vehicle.from_resource(
    "2021_Hyundai_Sonata_Hybrid_Blue_thrml.yaml"
)

cycle = fastsim.Cycle.from_resource("udds.csv")

sim = fastsim.SimDrive(vehicle, cycle)
sim.run()

data = sim.to_dict()

veh = data["veh"]
hev = veh["pt_type"]["HEV"]

histories = {
    "vehicle": veh["history"],
    "battery": hev["res"]["history"],
    "engine": hev["fc"]["history"],
    "motor": hev["em"]["history"],
}

print("\n=== TELEMETRY ALIGNMENT CHECK ===")

for name, history in histories.items():
    print(
        f"{name}: "
        f"{len(history['i'])} records"
    )

record_counts = {
    name: len(history["i"])
    for name, history in histories.items()
}

print("\nAll record counts match:",
      len(set(record_counts.values())) == 1)


print("\n=== SIMULATION STEP ALIGNMENT ===")

reference_indices = histories["vehicle"]["i"]

for name, history in histories.items():
    indices = history["i"]

    aligned = indices == reference_indices

    print(f"{name} aligned: {aligned}")
    print(f"  First 5 indices: {indices[:5]}")
    print(f"  Last 5 indices: {indices[-5:]}")

print("\n=== SIMULATION INDEX QUALITY ===")

indices = histories["vehicle"]["i"]

print("Total records:", len(indices))
print("Unique indices:", len(set(indices)))

print("Duplicate indices:", len(indices) - len(set(indices)))

print(
    "Indices consecutive:",
    all(
        indices[j] == indices[j - 1] + 1
        for j in range(1, len(indices))
    )
)

print("First index:", indices[0])
print("Last index:", indices[-1])

import pandas as pd

vehicle_history = histories["vehicle"]
battery_history = histories["battery"]
engine_history = histories["engine"]
motor_history = histories["motor"]

telemetry_df = pd.DataFrame({
    "step": vehicle_history["i"],
    "time_s": vehicle_history["time_seconds"],
    "speed_mps": vehicle_history["speed_ach_meters_per_second"],
    "distance_m": vehicle_history["dist_meters"],
    "battery_soc": battery_history["soc"],
    "battery_power_w": battery_history["pwr_out_electrical_watts"],
    "engine_power_w": engine_history["pwr_prop_watts"],
    "fuel_energy_j": engine_history["energy_fuel_joules"],
    "motor_power_w": motor_history["pwr_mech_prop_out_watts"],
})

print("\n=== UNIFIED TELEMETRY DATAFRAME ===")
print("Shape:", telemetry_df.shape)
print("\nColumns:")
print(telemetry_df.columns.tolist())

print("\nFirst five rows:")
print(telemetry_df.head())

print("\nMissing values:")
print(telemetry_df.isna().sum())


print("\n=== TELEMETRY QUALITY VALIDATION ===")

# 1. No missing values
assert not telemetry_df.isna().any().any(), \
    "Telemetry contains missing values"

# 2. Simulation steps are unique
assert telemetry_df["step"].is_unique, \
    "Duplicate simulation steps detected"

# 3. Timestamps increase
assert telemetry_df["time_s"].is_monotonic_increasing, \
    "Timestamps are not increasing"

# 4. Speed cannot be negative
assert (telemetry_df["speed_mps"] >= 0).all(), \
    "Negative vehicle speed detected"

# 5. SOC stays within configured limits
assert telemetry_df["battery_soc"].between(
    0.35, 0.90
).all(), "Battery SOC limit violation"

# 6. Distance never decreases
assert telemetry_df["distance_m"].is_monotonic_increasing, \
    "Distance decreased"

# 7. Cumulative fuel energy never decreases
assert telemetry_df["fuel_energy_j"].is_monotonic_increasing, \
    "Cumulative fuel energy decreased"

print("All telemetry quality checks passed!")
print("Validated rows:", len(telemetry_df))


output_path = Path("data/processed/baseline_udds.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Write validated telemetry
telemetry_df.to_parquet(
    output_path,
    engine="pyarrow",
    index=False,
)

# Read it back to verify the artifact
loaded_df = pd.read_parquet(
    output_path,
    engine="pyarrow",
)

pd.testing.assert_frame_equal(
    telemetry_df,
    loaded_df,
)

print("\n=== PARQUET EXPORT VALIDATION ===")
print("File:", output_path)
print("Rows:", len(loaded_df))
print("Columns:", len(loaded_df.columns))
print("File size (KB):", round(output_path.stat().st_size / 1024, 2))
print("Round-trip validation: PASSED")