#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

struct Edge {
    std::string target;
    double distance_km;
    double toll_cost;
    double avg_speed_kmph;
};

using Graph = std::unordered_map<std::string, std::vector<Edge>>;

double travel_minutes(const Edge& edge) {
    return (edge.distance_km / edge.avg_speed_kmph) * 60.0;
}

std::pair<std::vector<std::string>, double> dijkstra(const Graph& graph, const std::string& start, const std::string& goal) {
    using QueueItem = std::pair<double, std::string>;
    std::priority_queue<QueueItem, std::vector<QueueItem>, std::greater<QueueItem>> pq;
    std::unordered_map<std::string, double> dist;
    std::unordered_map<std::string, std::string> previous;

    pq.push({0.0, start});
    dist[start] = 0.0;

    while (!pq.empty()) {
        const auto [cost, node] = pq.top();
        pq.pop();

        if (node == goal) {
            break;
        }
        if (cost > dist[node]) {
            continue;
        }

        for (const auto& edge : graph.at(node)) {
            const double next = cost + travel_minutes(edge);
            if (!dist.count(edge.target) || next < dist[edge.target]) {
                dist[edge.target] = next;
                previous[edge.target] = node;
                pq.push({next, edge.target});
            }
        }
    }

    if (!dist.count(goal)) {
        throw std::runtime_error("No route found from " + start + " to " + goal);
    }

    std::vector<std::string> path;
    for (std::string cursor = goal; !cursor.empty();) {
        path.push_back(cursor);
        if (!previous.count(cursor)) {
            break;
        }
        cursor = previous[cursor];
    }
    std::reverse(path.begin(), path.end());
    return {path, dist[goal]};
}

int main() {
    Graph graph = {
        {"Entry-North", {{"Hub-West", 12, 2.5, 72}, {"Hub-East", 11, 3.0, 80}}},
        {"Hub-West", {{"City-Center", 8, 3.5, 45}, {"Industrial-Belt", 9, 2.0, 65}}},
        {"Hub-East", {{"City-Center", 5, 4.0, 55}, {"Airport", 10, 6.5, 90}}},
        {"Industrial-Belt", {{"Airport", 7, 1.5, 60}}},
        {"City-Center", {{"Airport", 9, 2.5, 50}}},
        {"Airport", {}},
    };

    const auto [path, minutes] = dijkstra(graph, "Entry-North", "Airport");
    std::cout << "Route: ";
    for (const auto& node : path) {
        std::cout << node << " ";
    }
    std::cout << "\nTravel minutes: " << minutes << "\n";
    return 0;
}
