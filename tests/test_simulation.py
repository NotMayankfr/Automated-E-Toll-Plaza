from etoll.simulation import TollSimulator


def test_automation_beats_manual_processing():
    simulator = TollSimulator(seed=7)
    results = simulator.run(count=60)
    assert results["summary"]["automated_avg_minutes"] < results["summary"]["manual_avg_minutes"]
    assert results["summary"]["wait_time_reduction_pct"] >= 50
