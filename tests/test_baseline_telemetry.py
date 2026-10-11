from pathlib import Path

import pandas as pd


def test_baseline_telemetry():
    path = Path("data/processed/baseline_udds.parquet")

    assert path.exists(), "Baseline Parquet file is missing"

    df = pd.read_parquet(path)

    assert len(df) == 1370
    assert df.shape[1] == 9

    assert df["step"].is_unique
    assert not df.isna().any().any()

    assert df["time_s"].is_monotonic_increasing
    assert (df["speed_mps"] >= 0).all()
    assert df["distance_m"].is_monotonic_increasing
    assert df["fuel_energy_j"].is_monotonic_increasing

    assert df["battery_soc"].between(0.35, 0.90).all()