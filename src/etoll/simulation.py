from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import random
from statistics import mean
from typing import Dict, List

from etoll.routing import a_star, build_sample_network, dijkstra


@dataclass
class Vehicle:
    vehicle_id: str
    vehicle_class: str
    origin: str
    destination: str
    prepaid: bool


@dataclass
class TripResult:
    vehicle_id: str
    recommended_path: List[str]
    routing_cost: float
    routing_mode: str
    wait_time_minutes: float
    payment_time_minutes: float
    total_processing_minutes: float


class TollSimulator:
    def __init__(self, seed: int = 42) -> None:
        self.network = build_sample_network()
        self.random = random.Random(seed)

    def identify_vehicle(self, vehicle: Vehicle) -> float:
        return 0.3 if vehicle.prepaid else 1.2

    def process_manual_vehicle(self, vehicle: Vehicle) -> float:
        verification = 2.4 if vehicle.vehicle_class == "truck" else 1.7
        payment = 1.8 if not vehicle.prepaid else 0.8
        return verification + payment + self.random.uniform(0.4, 1.0)

    def process_automated_vehicle(self, vehicle: Vehicle) -> float:
        identification = self.identify_vehicle(vehicle)
        payment = 0.25 if vehicle.prepaid else 0.75
        return identification + payment + self.random.uniform(0.1, 0.35)

    def recommend_route(self, vehicle: Vehicle) -> tuple[List[str], float, str]:
        if vehicle.vehicle_class == "truck":
            path, cost = dijkstra(self.network, vehicle.origin, vehicle.destination, optimize_for="cost")
            return path, cost, "dijkstra-cost"
        if vehicle.prepaid:
            path, cost = a_star(self.network, vehicle.origin, vehicle.destination)
            return path, cost, "a*-time"
        path, cost = dijkstra(self.network, vehicle.origin, vehicle.destination, optimize_for="time")
        return path, cost, "dijkstra-time"

    def run(self, count: int = 120) -> Dict[str, object]:
        vehicles = self._generate_vehicles(count)
        manual_results = [self._simulate_trip(vehicle, automated=False) for vehicle in vehicles]
        automated_results = [self._simulate_trip(vehicle, automated=True) for vehicle in vehicles]

        manual_avg = mean(item.total_processing_minutes for item in manual_results)
        automated_avg = mean(item.total_processing_minutes for item in automated_results)
        reduction_pct = ((manual_avg - automated_avg) / manual_avg) * 100.0

        return {
            "summary": {
                "vehicle_count": count,
                "manual_avg_minutes": round(manual_avg, 2),
                "automated_avg_minutes": round(automated_avg, 2),
                "wait_time_reduction_pct": round(reduction_pct, 2),
            },
            "manual_results": [asdict(result) for result in manual_results],
            "automated_results": [asdict(result) for result in automated_results],
        }

    def _simulate_trip(self, vehicle: Vehicle, automated: bool) -> TripResult:
        path, cost, mode = self.recommend_route(vehicle)
        payment_time = self.process_automated_vehicle(vehicle) if automated else self.process_manual_vehicle(vehicle)
        queue_multiplier = 0.35 if automated else 1.15
        wait_time = payment_time * queue_multiplier

        return TripResult(
            vehicle_id=vehicle.vehicle_id,
            recommended_path=path,
            routing_cost=round(cost, 2),
            routing_mode=mode,
            wait_time_minutes=round(wait_time, 2),
            payment_time_minutes=round(payment_time, 2),
            total_processing_minutes=round(wait_time + payment_time, 2),
        )

    def _generate_vehicles(self, count: int) -> List[Vehicle]:
        classes = ["car", "bus", "truck"]
        destinations = ["City-Center", "Industrial-Belt", "Airport"]
        vehicles = []
        for index in range(1, count + 1):
            vehicles.append(
                Vehicle(
                    vehicle_id=f"VH-{index:03d}",
                    vehicle_class=self.random.choices(classes, weights=[0.68, 0.12, 0.20])[0],
                    origin="Entry-North",
                    destination=self.random.choice(destinations),
                    prepaid=self.random.random() < 0.72,
                )
            )
        return vehicles


def export_simulation_results(destination: Path, count: int = 120) -> Dict[str, object]:
    simulator = TollSimulator()
    results = simulator.run(count=count)
    destination.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
