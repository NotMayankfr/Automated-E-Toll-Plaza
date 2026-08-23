from pathlib import Path

from etoll.simulation import export_simulation_results


if __name__ == "__main__":
    destination = Path(__file__).resolve().parent / "data" / "simulation_results.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    results = export_simulation_results(destination, count=150)
    print("Simulation complete.")
    print(results["summary"])
