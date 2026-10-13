
from pathlib import Path

import pandas as pd

from src.hybrid_energy.simulation import run_simulation
from src.hybrid_energy.telemetry import build_telemetry_dataframe
from src.hybrid_energy.validation import validate_telemetry


VEHICLE_RESOURCE = "2021_Hyundai_Sonata_Hybrid_Blue_thrml.yaml"
CYCLE_RESOURCE = "udds.csv"

OUTPUT_PATH = Path("data/processed/baseline_udds.parquet")


def main():
    # Step 1: Run FASTSim simulation
    print("Running FASTSim baseline simulation...")

    sim = run_simulation(
        vehicle_resource=VEHICLE_RESOURCE,
        cycle_resource=CYCLE_RESOURCE,
    )

    print("Simulation completed successfully!")

    # Step 2: Build unified telemetry DataFrame
    telemetry_df = build_telemetry_dataframe(sim)

    print("\n=== TELEMETRY DATAFRAME ===")
    print("Shape:", telemetry_df.shape)
    print("\nColumns:")
    print(telemetry_df.columns.tolist())

    print("\nFirst five rows:")
    print(telemetry_df.head())

    # Step 3: Validate telemetry quality
    print("\n=== TELEMETRY QUALITY VALIDATION ===")

    assert not telemetry_df.empty, "Telemetry DataFrame is empty"

    assert len(telemetry_df) == 1370, \
        "Unexpected number of telemetry records"

    assert telemetry_df.shape[1] == 9, \
        "Unexpected number of telemetry columns"

    assert not telemetry_df.isna().any().any(), \
        "Telemetry contains missing values"

    assert telemetry_df["step"].is_unique, \
        "Duplicate simulation steps detected"

    assert telemetry_df["step"].tolist() == list(range(1370)), \
        "Simulation steps are missing or out of order"

    assert telemetry_df["time_s"].is_monotonic_increasing, \
        "Timestamps are not increasing"

    assert (telemetry_df["speed_mps"] >= 0).all(), \
        "Negative vehicle speed detected"

    assert telemetry_df["distance_m"].is_monotonic_increasing, \
        "Distance decreased"

    assert telemetry_df["fuel_energy_j"].is_monotonic_increasing, \
        "Cumulative fuel energy decreased"

    # Read SOC limits from the actual vehicle configuration
    vehicle_data = sim.to_dict()["veh"]
    battery = vehicle_data["pt_type"]["HEV"]["res"]

    min_soc = battery["min_soc"]
    max_soc = battery["max_soc"]

    assert telemetry_df["battery_soc"].between(
        min_soc, max_soc
    ).all(), "Battery SOC limit violation"

    print("All telemetry quality checks passed!")

    # Step 4: Export validated telemetry to Parquet
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    telemetry_df.to_parquet(
        OUTPUT_PATH,
        engine="pyarrow",
        index=False,
    )

    print("\n=== PARQUET EXPORT ===")
    print("File:", OUTPUT_PATH)
    print("File size (KB):", round(OUTPUT_PATH.stat().st_size / 1024, 2))

    # Step 5: Read Parquet back and validate
    loaded_df = pd.read_parquet(
        OUTPUT_PATH,
        engine="pyarrow",
    )

    pd.testing.assert_frame_equal(
        telemetry_df,
        loaded_df,
    )

    print("\n=== FINAL VALIDATION ===")
    print("Rows:", len(loaded_df))
    print("Columns:", len(loaded_df.columns))
    print("Parquet round-trip validation: PASSED")

    print("\nBaseline telemetry pipeline completed successfully!")

    # Retrieve SOC limits from the simulated vehicle
    vehicle_data = sim.to_dict()["veh"]
    battery = vehicle_data["pt_type"]["HEV"]["res"]

    # Validate telemetry using the reusable module
    validate_telemetry(
        telemetry_df,
        min_soc=battery["min_soc"],
        max_soc=battery["max_soc"],
    )

    print("Telemetry quality validation: PASSED")

    
if __name__ == "__main__":
    main()
