import csv
import math

stadiums = [
    # club, stadium, city, lat, lon, capacity
    ("Arsenal", "Emirates Stadium", "London", 51.555000, -0.108611, 60704),
    ("Aston Villa", "Villa Park", "Birmingham", 52.509167, -1.884722, 42918),
    ("Bournemouth", "Vitality Stadium", "Bournemouth", 50.735278, -1.838333, 11364),
    ("Brentford", "Brentford Community Stadium", "London", 51.490715, -0.289048, 17250),
    ("Brighton & Hove Albion", "Falmer Stadium (Amex Stadium)", "Brighton and Hove", 50.861822, -0.083278, 31800),
    ("Chelsea", "Stamford Bridge", "London", 51.481667, -0.191111, 40343),
    ("Coventry City", "Coventry Building Society Arena", "Coventry", 52.448056, -1.495556, 32609),
    ("Crystal Palace", "Selhurst Park", "London", 51.398333, -0.085556, 25486),
    ("Everton", "Hill Dickinson Stadium", "Liverpool", 53.425100, -3.002800, 52769),
    ("Fulham", "Craven Cottage", "London", 51.475000, -0.221667, 29600),
    ("Hull City", "MKM Stadium", "Kingston upon Hull", 53.746111, -0.367778, 24983),
    ("Ipswich Town", "Portman Road", "Ipswich", 52.055061, 1.144831, 30056),
    ("Leeds United", "Elland Road", "Leeds", 53.777778, -1.572222, 37792),
    ("Liverpool", "Anfield", "Liverpool", 53.430819, -2.960828, 61276),
    ("Manchester City", "Etihad Stadium", "Manchester", 53.482989, -2.200292, 61038),
    ("Manchester United", "Old Trafford", "Manchester", 53.463056, -2.291389, 74310),
    ("Newcastle United", "St James' Park", "Newcastle upon Tyne", 54.975556, -1.621667, 52305),
    ("Nottingham Forest", "City Ground", "West Bridgford", 52.940000, -1.132778, 30404),
    ("Sunderland", "Stadium of Light", "Sunderland", 54.914400, -1.388200, 48707),
    ("Tottenham Hotspur", "Tottenham Hotspur Stadium", "London", 51.604252, -0.067007, 62850),
]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088  # mean Earth radius, km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

# Write stadiums CSV
with open("/workspaces/travelling_salesman_kenya/data/premier_league_stadiums.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["club", "stadium", "city", "latitude", "longitude", "capacity"])
    for row in stadiums:
        w.writerow(row)

# Write distance matrix CSV (km, straight-line/great-circle)
clubs = [s[0] for s in stadiums]
with open("/workspaces/travelling_salesman_kenya/data/distance_matrix_km.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([""] + clubs)
    for i, a in enumerate(stadiums):
        row = [a[0]]
        for j, b in enumerate(stadiums):
            d = 0.0 if i == j else haversine_km(a[3], a[4], b[3], b[4])
            row.append(round(d, 2))
        w.writerow(row)

# Long-format pairwise distances, sorted
pairs = []
for i in range(len(stadiums)):
    for j in range(i + 1, len(stadiums)):
        a, b = stadiums[i], stadiums[j]
        d = haversine_km(a[3], a[4], b[3], b[4])
        pairs.append((a[0], b[0], round(d, 2)))
pairs.sort(key=lambda x: x[2])

with open("/workspaces/travelling_salesman_kenya/data/distance_pairs_km.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["club_a", "club_b", "distance_km"])
    for row in pairs:
        w.writerow(row)

print("Closest 5 pairs:")
for p in pairs[:5]:
    print(p)
print("\nFarthest 5 pairs:")
for p in pairs[-5:]:
    print(p)
print(f"\nTotal clubs: {len(stadiums)}, total pairs: {len(pairs)}")
