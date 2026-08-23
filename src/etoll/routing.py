from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class Node:
    name: str
    x: float
    y: float


@dataclass(frozen=True)
class Edge:
    target: str
    distance_km: float
    toll_cost: float
    avg_speed_kmph: float

    @property
    def travel_minutes(self) -> float:
        return (self.distance_km / self.avg_speed_kmph) * 60.0


class RoadNetwork:
    def __init__(self, nodes: Iterable[Node], adjacency: Dict[str, List[Edge]]) -> None:
        self.nodes = {node.name: node for node in nodes}
        self.adjacency = adjacency

    def heuristic_minutes(self, current: str, goal: str) -> float:
        current_node = self.nodes[current]
        goal_node = self.nodes[goal]
        euclidean_km = math.dist((current_node.x, current_node.y), (goal_node.x, goal_node.y))
        return (euclidean_km / 70.0) * 60.0


def _reconstruct_path(previous: Dict[str, str | None], goal: str) -> List[str]:
    path: List[str] = []
    cursor: str | None = goal
    while cursor is not None:
        path.append(cursor)
        cursor = previous[cursor]
    path.reverse()
    return path


def dijkstra(network: RoadNetwork, start: str, goal: str, optimize_for: str = "time") -> Tuple[List[str], float]:
    queue: List[Tuple[float, str]] = [(0.0, start)]
    best_cost: Dict[str, float] = {start: 0.0}
    previous: Dict[str, str | None] = {start: None}

    while queue:
        cost, current = heapq.heappop(queue)
        if current == goal:
            return _reconstruct_path(previous, goal), cost
        if cost > best_cost.get(current, float("inf")):
            continue

        for edge in network.adjacency.get(current, []):
            weight = edge.travel_minutes if optimize_for == "time" else edge.toll_cost
            new_cost = cost + weight
            if new_cost < best_cost.get(edge.target, float("inf")):
                best_cost[edge.target] = new_cost
                previous[edge.target] = current
                heapq.heappush(queue, (new_cost, edge.target))

    raise ValueError(f"No path found from {start} to {goal}")


def a_star(network: RoadNetwork, start: str, goal: str) -> Tuple[List[str], float]:
    open_set: List[Tuple[float, str]] = [(0.0, start)]
    g_score: Dict[str, float] = {start: 0.0}
    previous: Dict[str, str | None] = {start: None}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return _reconstruct_path(previous, goal), g_score[goal]

        for edge in network.adjacency.get(current, []):
            tentative = g_score[current] + edge.travel_minutes
            if tentative < g_score.get(edge.target, float("inf")):
                previous[edge.target] = current
                g_score[edge.target] = tentative
                priority = tentative + network.heuristic_minutes(edge.target, goal)
                heapq.heappush(open_set, (priority, edge.target))

    raise ValueError(f"No path found from {start} to {goal}")


def build_sample_network() -> RoadNetwork:
    nodes = [
        Node("Entry-North", 0, 8),
        Node("Hub-West", 2, 6),
        Node("Hub-East", 7, 7),
        Node("City-Center", 8, 3),
        Node("Industrial-Belt", 4, 1),
        Node("Airport", 10, 1),
    ]
    adjacency = {
        "Entry-North": [
            Edge("Hub-West", 12, 2.5, 72),
            Edge("Hub-East", 11, 3.0, 80),
        ],
        "Hub-West": [
            Edge("City-Center", 8, 3.5, 45),
            Edge("Industrial-Belt", 9, 2.0, 65),
        ],
        "Hub-East": [
            Edge("City-Center", 5, 4.0, 55),
            Edge("Airport", 10, 6.5, 90),
        ],
        "Industrial-Belt": [
            Edge("Airport", 7, 1.5, 60),
            Edge("City-Center", 6, 1.0, 40),
        ],
        "City-Center": [
            Edge("Airport", 9, 2.5, 50),
        ],
        "Airport": [],
    }
    return RoadNetwork(nodes, adjacency)
