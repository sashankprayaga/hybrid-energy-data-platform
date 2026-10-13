import pandas as pd


def validate_telemetry(
    df: pd.DataFrame,
    min_soc: float,
    max_soc: float,
) -> None:
    """Validate the quality of a FASTSim telemetry dataset."""

    if df.empty:
        raise ValueError("Telemetry DataFrame is empty")

    if df.isna().any().any():
        raise ValueError("Telemetry contains missing values")

    if not df["step"].is_unique:
        raise ValueError("Duplicate simulation steps detected")

    if df["step"].tolist() != list(range(len(df))):
        raise ValueError("Simulation steps are missing or out of order")

    if not df["time_s"].is_monotonic_increasing:
        raise ValueError("Timestamps are not ordered")

    if not (df["speed_mps"] >= 0).all():
        raise ValueError("Negative vehicle speed detected")

    if not df["distance_m"].is_monotonic_increasing:
        raise ValueError("Distance decreased")

    if not df["fuel_energy_j"].is_monotonic_increasing:
        raise ValueError("Cumulative fuel energy decreased")

    if not df["battery_soc"].between(min_soc, max_soc).all():
        raise ValueError("Battery SOC limit violation")