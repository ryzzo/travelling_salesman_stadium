# travelling_salesman_stadium

Shortest-route planning for the 2026–27 Premier League's 20 stadiums, solved as an open-path
travelling salesman problem (start fixed, no return leg), using great-circle distance.

## Data

- `data/premier_league_stadiums.csv` — club, stadium, city, lat/lon, capacity
- `data/distance_matrix_km.csv` — full 20×20 great-circle distance matrix
- `data/distance_pairs_km.csv` — all 190 stadium pairs, sorted nearest first
- `data/build_distances.py` — regenerates the three files above from the stadium list

## Solving a route

`tsp_solver.py` computes the shortest commute to all 20 stadiums from any starting point,
using nearest-neighbour construction refined by 2-opt and Or-opt local search across several
random restarts (near-optimal at this size, not a brute-force-proven optimum):

```bash
python3 tsp_solver.py --city London
python3 tsp_solver.py --lat 53.9600 --lon -1.0873 --label York
```

## Interactive version

[Premier League Atlas](https://claude.ai/code/artifact/c2c37797-de10-4226-bc98-acebde6fe0d8) — map of
all 20 grounds; enter a starting point (search a city, drop coordinates, click the map, or use your
device location) to see the optimized route, or explore straight-line distances between any two clubs.
