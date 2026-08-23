from etoll.routing import a_star, build_sample_network, dijkstra


def test_dijkstra_time_path_reaches_airport():
    network = build_sample_network()
    path, cost = dijkstra(network, "Entry-North", "Airport", optimize_for="time")
    assert path[0] == "Entry-North"
    assert path[-1] == "Airport"
    assert cost > 0


def test_a_star_matches_fast_path_destination():
    network = build_sample_network()
    path, cost = a_star(network, "Entry-North", "Airport")
    assert path == ["Entry-North", "Hub-East", "Airport"]
    assert cost > 0
