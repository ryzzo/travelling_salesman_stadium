#!/usr/bin/env python3
"""
Shortest commute to every Premier League stadium from a given starting point.

Solves an *open-path* travelling salesman problem (start fixed, no return leg)
over the 20 stadiums in data/premier_league_stadiums.csv, using great-circle
(haversine) distance. Construction is nearest-neighbour, refined by 2-opt and
Or-opt local search across several random restarts -- near-optimal at this
size (21 nodes), not a brute-force-proven optimum.

Usage:
    python3 tsp_solver.py --lat 51.5074 --lon -0.1278 --label "London"
    python3 tsp_solver.py --city Leeds
"""
import argparse
import csv
import math
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "premier_league_stadiums.csv")

# A small gazetteer for --city; for anywhere else, pass --lat/--lon directly.
CITIES = {
    "london": (51.5074, -0.1278), "birmingham": (52.4862, -1.8904),
    "manchester": (53.4808, -2.2426), "leeds": (53.8008, -1.5491),
    "glasgow": (55.8642, -4.2518), "sheffield": (53.3811, -1.4701),
    "liverpool": (53.4084, -2.9916), "bristol": (51.4545, -2.5879),
    "newcastle upon tyne": (54.9783, -1.6178), "nottingham": (52.9548, -1.1581),
    "edinburgh": (55.9533, -3.1883), "cardiff": (51.4816, -3.1791),
    "belfast": (54.5973, -5.9301), "coventry": (52.4068, -1.5197),
    "southampton": (50.9097, -1.4044), "oxford": (51.7520, -1.2577),
    "cambridge": (52.2053, 0.1218), "york": (53.9600, -1.0873),
    "brighton": (50.8225, -0.1372), "bournemouth": (50.7192, -1.8808),
    "ipswich": (52.0567, 1.1482), "hull": (53.7676, -0.3274),
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_stadiums():
    with open(DATA_PATH, newline="") as f:
        return list(csv.DictReader(f))


def path_length(order, start):
    total = 0.0
    prev_lat, prev_lon = start
    for row in order:
        total += haversine_km(prev_lat, prev_lon, float(row["latitude"]), float(row["longitude"]))
        prev_lat, prev_lon = float(row["latitude"]), float(row["longitude"])
    return total


def nearest_neighbor(start, stadiums):
    remaining = stadiums[:]
    order = []
    cur_lat, cur_lon = start
    while remaining:
        best_i, best_d = 0, math.inf
        for i, row in enumerate(remaining):
            d = haversine_km(cur_lat, cur_lon, float(row["latitude"]), float(row["longitude"]))
            if d < best_d:
                best_d, best_i = d, i
        nxt = remaining.pop(best_i)
        order.append(nxt)
        cur_lat, cur_lon = float(nxt["latitude"]), float(nxt["longitude"])
    return order


def two_opt(start, order):
    best, best_len = order[:], path_length(order, start)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                length = path_length(cand, start)
                if length < best_len - 1e-9:
                    best, best_len, improved = cand, length, True
    return best, best_len


def or_opt(start, order):
    best, best_len = order[:], path_length(order, start)
    improved = True
    while improved:
        improved = False
        for seg_len in (1, 2, 3):
            for i in range(len(best) - seg_len + 1):
                seg = best[i:i + seg_len]
                rest = best[:i] + best[i + seg_len:]
                for j in range(len(rest) + 1):
                    cand = rest[:j] + seg + rest[j:]
                    length = path_length(cand, start)
                    if length < best_len - 1e-9:
                        best, best_len, improved = cand, length, True
    return best, best_len


def optimize(start, order):
    cur, cur_len = order[:], path_length(order, start)
    changed = True
    while changed:
        changed = False
        o2, l2 = two_opt(start, cur)
        if l2 < cur_len - 1e-9:
            cur, cur_len, changed = o2, l2, True
        o3, l3 = or_opt(start, cur)
        if l3 < cur_len - 1e-9:
            cur, cur_len, changed = o3, l3, True
    return cur, cur_len


def solve(start, stadiums, restarts=10, seed=None):
    rng = random.Random(seed)
    best_order, best_len = optimize(start, nearest_neighbor(start, stadiums))
    for _ in range(restarts):
        shuffled = stadiums[:]
        rng.shuffle(shuffled)
        order, length = optimize(start, shuffled)
        if length < best_len:
            best_order, best_len = order, length
    return best_order, best_len


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lat", type=float, help="starting latitude")
    ap.add_argument("--lon", type=float, help="starting longitude")
    ap.add_argument("--city", type=str, help="a UK city from the built-in list, e.g. Leeds")
    ap.add_argument("--label", type=str, default=None, help="display name for the start point")
    ap.add_argument("--restarts", type=int, default=10)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    if args.city:
        key = args.city.strip().lower()
        if key not in CITIES:
            ap.error(f"unknown --city '{args.city}'. Known: {', '.join(sorted(CITIES))}. Use --lat/--lon instead.")
        start = CITIES[key]
        label = args.label or args.city.title()
    elif args.lat is not None and args.lon is not None:
        start = (args.lat, args.lon)
        label = args.label or f"{args.lat:.4f}, {args.lon:.4f}"
    else:
        ap.error("pass either --city NAME or both --lat and --lon")

    stadiums = load_stadiums()
    order, total = solve(start, stadiums, restarts=args.restarts, seed=args.seed)

    print(f"Starting point: {label} ({start[0]:.4f}, {start[1]:.4f})\n")
    print(f"{'#':<3} {'Club':<24} {'Leg (km)':>9} {'Cumulative (km)':>17}")
    prev = start
    cum = 0.0
    for i, row in enumerate(order, 1):
        d = haversine_km(prev[0], prev[1], float(row["latitude"]), float(row["longitude"]))
        cum += d
        print(f"{i:<3} {row['club']:<24} {d:>9.1f} {cum:>17.1f}")
        prev = (float(row["latitude"]), float(row["longitude"]))
    print(f"\nTotal route distance: {total:.1f} km (great-circle; heuristic 2-opt/Or-opt solve, {args.restarts} restarts)")


if __name__ == "__main__":
    main()
