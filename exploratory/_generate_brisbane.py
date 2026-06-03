"""
Genererer Brisbane.CSV med alle verdens hovedstæder parret med Brisbane, AU.

For hvert par:
  Path order 1 = Hovedstaden  (SVG: pil rettet mod Brisbane på Mercator-kortet)
  Path order 2 = Brisbane     (SVG: olympiske ringe – Brisbane 2032)

Pilens retning beregnes som den visuelle retning på Mercator-projektionen
(Greenwich i midten, x = -180° til +180°), IKKE den geografiske korteste vej.
Det betyder at hovedstæder i Americas peger mod højre (øst), selv om Brisbane
geografisk set er vestover via Stillehavet.

Kør fra roden af projektet:
  python exploratory/_generate_brisbane.py
"""

import csv
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Konstanter
# ---------------------------------------------------------------------------
BRISBANE_LAT = -27.47
BRISBANE_LON = 153.02
OUTPUT = Path(__file__).parent / "Brisbane.CSV"


# ---------------------------------------------------------------------------
# SVG-hjælpere
# ---------------------------------------------------------------------------

# Grundpil pegende mod højre (→), centreret i 22×22 viewBox.
# Roteres med SVG transform for at pege i alle 8 retninger.
_ARROW_PTS = "3,10 13,10 13,7 19,11 13,15 13,12 3,12"


def arrow_svg(angle_deg: float) -> str:
    """SVG-pil der peger i retningen angle_deg grader (0=højre/øst, 90=ned/syd)."""
    a = round(angle_deg)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22">'
        f'<polygon points="{_ARROW_PTS}" fill="#0078d4"'
        f' transform="rotate({a},11,11)"/>'
        "</svg>"
    )


OLYMPIC_RINGS = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 62 36">'
    # Øverste række: blå, sort, rød
    '<circle cx="9"  cy="13" r="7" fill="none" stroke="#0081c8" stroke-width="2.5"/>'
    '<circle cx="23" cy="13" r="7" fill="none" stroke="#000"    stroke-width="2.5"/>'
    '<circle cx="37" cy="13" r="7" fill="none" stroke="#ee334e" stroke-width="2.5"/>'
    # Nederste række: gul, grøn
    '<circle cx="16" cy="23" r="7" fill="none" stroke="#fcb131" stroke-width="2.5"/>'
    '<circle cx="30" cy="23" r="7" fill="none" stroke="#00a651" stroke-width="2.5"/>'
    "</svg>"
)


# ---------------------------------------------------------------------------
# Retningsberegning på Mercator-projektionen
# ---------------------------------------------------------------------------

def _mercator_y(lat_deg: float) -> float:
    lat_rad = math.radians(max(-89.9, min(89.9, lat_deg)))
    return math.log(math.tan(math.pi / 4 + lat_rad / 2))


def direction_deg(capital_lon: float, capital_lat: float) -> float:
    """
    Returnerer vinklen i grader fra hovedstaden mod Brisbane på Mercator-kortet.
    0° = højre (øst), 90° = ned (syd), 180° = venstre (vest), 270° = op (nord).

    screen_dy er i Mercator-radianer og skaleres til grader (×180/π) så
    akserne er sammenlignelige med longitude-grader.
    """
    dx = BRISBANE_LON - capital_lon
    # screen_dy positiv = Brisbane er syd for (under) hovedstaden på kortet
    screen_dy = (_mercator_y(capital_lat) - _mercator_y(BRISBANE_LAT)) * (180 / math.pi)
    return math.degrees(math.atan2(screen_dy, dx))


# ---------------------------------------------------------------------------
# Verdens hovedstæder: (by, land, breddegrad N, længdegrad E)
# ---------------------------------------------------------------------------
CAPITALS = [
    # ── Afrika ──────────────────────────────────────────────────────────────
    ("Algiers",                  "Algeria",                      36.74,   3.06),
    ("Luanda",                   "Angola",                       -8.84,  13.23),
    ("Porto-Novo",               "Benin",                         6.37,   2.42),
    ("Gaborone",                 "Botswana",                    -24.63,  25.90),
    ("Ouagadougou",              "Burkina Faso",                 12.36,  -1.53),
    ("Gitega",                   "Burundi",                      -3.43,  29.93),
    ("Praia",                    "Cabo Verde",                   14.93, -23.51),
    ("Yaoundé",                  "Cameroon",                      3.87,  11.52),
    ("Bangui",                   "Central African Republic",      4.36,  18.56),
    ("N'Djamena",                "Chad",                         12.10,  15.04),
    ("Moroni",                   "Comoros",                     -11.70,  43.26),
    ("Kinshasa",                 "DR Congo",                     -4.32,  15.32),
    ("Brazzaville",              "Republic of Congo",            -4.27,  15.28),
    ("Yamoussoukro",             "Côte d'Ivoire",                 6.82,  -5.28),
    ("Djibouti",                 "Djibouti",                     11.59,  43.15),
    ("Cairo",                    "Egypt",                        30.04,  31.24),
    ("Malabo",                   "Equatorial Guinea",             3.75,   8.78),
    ("Asmara",                   "Eritrea",                      15.34,  38.93),
    ("Mbabane",                  "Eswatini",                    -26.32,  31.14),
    ("Addis Ababa",              "Ethiopia",                      9.02,  38.75),
    ("Libreville",               "Gabon",                         0.39,   9.45),
    ("Banjul",                   "Gambia",                       13.45, -16.58),
    ("Accra",                    "Ghana",                         5.56,  -0.20),
    ("Conakry",                  "Guinea",                        9.54, -13.68),
    ("Bissau",                   "Guinea-Bissau",                11.86, -15.60),
    ("Nairobi",                  "Kenya",                        -1.29,  36.82),
    ("Maseru",                   "Lesotho",                     -29.32,  27.48),
    ("Monrovia",                 "Liberia",                       6.30, -10.80),
    ("Tripoli",                  "Libya",                        32.89,  13.18),
    ("Antananarivo",             "Madagascar",                  -18.91,  47.54),
    ("Lilongwe",                 "Malawi",                      -13.97,  33.79),
    ("Bamako",                   "Mali",                         12.65,  -8.00),
    ("Nouakchott",               "Mauritania",                   18.08, -15.97),
    ("Port Louis",               "Mauritius",                   -20.16,  57.50),
    ("Rabat",                    "Morocco",                      34.02,  -6.83),
    ("Maputo",                   "Mozambique",                  -25.97,  32.59),
    ("Windhoek",                 "Namibia",                     -22.56,  17.08),
    ("Niamey",                   "Niger",                        13.51,   2.12),
    ("Abuja",                    "Nigeria",                       9.06,   7.49),
    ("Kigali",                   "Rwanda",                       -1.94,  30.06),
    ("São Tomé",                 "São Tomé and Príncipe",         0.34,   6.73),
    ("Dakar",                    "Senegal",                      14.69, -17.44),
    ("Victoria",                 "Seychelles",                   -4.62,  55.46),
    ("Freetown",                 "Sierra Leone",                  8.49, -13.23),
    ("Mogadishu",                "Somalia",                       2.05,  45.34),
    ("Pretoria",                 "South Africa",                -25.74,  28.19),
    ("Juba",                     "South Sudan",                   4.86,  31.60),
    ("Khartoum",                 "Sudan",                        15.55,  32.53),
    ("Dodoma",                   "Tanzania",                     -6.17,  35.74),
    ("Lomé",                     "Togo",                          6.14,   1.22),
    ("Tunis",                    "Tunisia",                      36.82,  10.17),
    ("Kampala",                  "Uganda",                        0.32,  32.58),
    ("Lusaka",                   "Zambia",                      -15.41,  28.28),
    ("Harare",                   "Zimbabwe",                    -17.83,  31.05),
    # ── Asien ───────────────────────────────────────────────────────────────
    ("Kabul",                    "Afghanistan",                  34.53,  69.17),
    ("Yerevan",                  "Armenia",                      40.19,  44.50),
    ("Baku",                     "Azerbaijan",                   40.41,  49.87),
    ("Manama",                   "Bahrain",                      26.22,  50.59),
    ("Dhaka",                    "Bangladesh",                   23.72,  90.41),
    ("Thimphu",                  "Bhutan",                       27.47,  89.64),
    ("Bandar Seri Begawan",      "Brunei",                        4.94, 114.95),
    ("Phnom Penh",               "Cambodia",                     11.56, 104.93),
    ("Beijing",                  "China",                        39.91, 116.39),
    ("Nicosia",                  "Cyprus",                       35.16,  33.36),
    ("Tbilisi",                  "Georgia",                      41.69,  44.83),
    ("New Delhi",                "India",                        28.63,  77.22),
    ("Jakarta",                  "Indonesia",                    -6.21, 106.85),
    ("Tehran",                   "Iran",                         35.69,  51.42),
    ("Baghdad",                  "Iraq",                         33.34,  44.40),
    ("Jerusalem",                "Israel",                       31.77,  35.22),
    ("Tokyo",                    "Japan",                        35.69, 139.69),
    ("Amman",                    "Jordan",                       31.95,  35.93),
    ("Astana",                   "Kazakhstan",                   51.18,  71.45),
    ("Kuwait City",              "Kuwait",                       29.37,  47.98),
    ("Bishkek",                  "Kyrgyzstan",                   42.87,  74.59),
    ("Vientiane",                "Laos",                         17.97, 102.60),
    ("Beirut",                   "Lebanon",                      33.89,  35.50),
    ("Kuala Lumpur",             "Malaysia",                      3.14, 101.69),
    ("Malé",                     "Maldives",                      4.18,  73.51),
    ("Ulaanbaatar",              "Mongolia",                     47.91, 106.89),
    ("Naypyidaw",                "Myanmar",                      19.76,  96.08),
    ("Kathmandu",                "Nepal",                        27.71,  85.32),
    ("Pyongyang",                "North Korea",                  39.04, 125.76),
    ("Muscat",                   "Oman",                         23.61,  58.59),
    ("Islamabad",                "Pakistan",                     33.72,  73.06),
    ("Manila",                   "Philippines",                  14.60, 120.98),
    ("Doha",                     "Qatar",                        25.29,  51.53),
    ("Moscow",                   "Russia",                       55.75,  37.62),
    ("Riyadh",                   "Saudi Arabia",                 24.69,  46.72),
    ("Singapore",                "Singapore",                     1.35, 103.82),
    ("Seoul",                    "South Korea",                  37.57, 126.98),
    ("Sri Jayawardenepura Kotte","Sri Lanka",                     6.90,  79.92),
    ("Damascus",                 "Syria",                        33.51,  36.29),
    ("Taipei",                   "Taiwan",                       25.05, 121.53),
    ("Dushanbe",                 "Tajikistan",                   38.56,  68.77),
    ("Bangkok",                  "Thailand",                     13.75, 100.52),
    ("Dili",                     "Timor-Leste",                  -8.56, 125.58),
    ("Ankara",                   "Turkey",                       39.93,  32.86),
    ("Ashgabat",                 "Turkmenistan",                 37.95,  58.38),
    ("Tashkent",                 "Uzbekistan",                   41.30,  69.27),
    ("Hanoi",                    "Vietnam",                      21.03, 105.85),
    ("Sana'a",                   "Yemen",                        15.36,  44.21),
    # ── Europa ──────────────────────────────────────────────────────────────
    ("Tirana",                   "Albania",                      41.33,  19.82),
    ("Andorra la Vella",         "Andorra",                      42.51,   1.53),
    ("Vienna",                   "Austria",                      48.21,  16.37),
    ("Minsk",                    "Belarus",                      53.90,  27.57),
    ("Brussels",                 "Belgium",                      50.85,   4.35),
    ("Sarajevo",                 "Bosnia and Herzegovina",       43.85,  18.38),
    ("Sofia",                    "Bulgaria",                     42.70,  23.32),
    ("Zagreb",                   "Croatia",                      45.81,  15.98),
    ("Prague",                   "Czech Republic",               50.08,  14.44),
    ("Copenhagen",               "Denmark",                      55.68,  12.57),
    ("Tallinn",                  "Estonia",                      59.44,  24.75),
    ("Helsinki",                 "Finland",                      60.17,  24.94),
    ("Paris",                    "France",                       48.86,   2.35),
    ("Berlin",                   "Germany",                      52.52,  13.41),
    ("Athens",                   "Greece",                       37.98,  23.73),
    ("Budapest",                 "Hungary",                      47.50,  19.04),
    ("Reykjavik",                "Iceland",                      64.13, -21.82),
    ("Dublin",                   "Ireland",                      53.33,  -6.25),
    ("Rome",                     "Italy",                        41.90,  12.48),
    ("Pristina",                 "Kosovo",                       42.67,  21.17),
    ("Riga",                     "Latvia",                       56.95,  24.11),
    ("Vaduz",                    "Liechtenstein",                47.14,   9.52),
    ("Vilnius",                  "Lithuania",                    54.69,  25.28),
    ("Luxembourg",               "Luxembourg",                   49.61,   6.13),
    ("Valletta",                 "Malta",                        35.90,  14.51),
    ("Chișinău",                 "Moldova",                      47.01,  28.86),
    ("Monaco",                   "Monaco",                       43.74,   7.41),
    ("Podgorica",                "Montenegro",                   42.44,  19.26),
    ("Amsterdam",                "Netherlands",                  52.37,   4.90),
    ("Skopje",                   "North Macedonia",              42.00,  21.43),
    ("Oslo",                     "Norway",                       59.91,  10.75),
    ("Warsaw",                   "Poland",                       52.23,  21.01),
    ("Lisbon",                   "Portugal",                     38.72,  -9.14),
    ("Bucharest",                "Romania",                      44.43,  26.10),
    ("San Marino",               "San Marino",                   43.94,  12.46),
    ("Belgrade",                 "Serbia",                       44.80,  20.46),
    ("Bratislava",               "Slovakia",                     48.15,  17.11),
    ("Ljubljana",                "Slovenia",                     46.05,  14.51),
    ("Madrid",                   "Spain",                        40.42,  -3.70),
    ("Stockholm",                "Sweden",                       59.33,  18.07),
    ("Bern",                     "Switzerland",                  46.95,   7.45),
    ("Kyiv",                     "Ukraine",                      50.45,  30.52),
    ("London",                   "United Kingdom",               51.51,  -0.13),
    # Vatican udeladt – ikke IOC-medlem, deltager ikke i OL
    # ── Nord- og Mellemamerika + Caribien ───────────────────────────────────
    ("Saint John's",             "Antigua and Barbuda",          17.12, -61.85),
    ("Nassau",                   "Bahamas",                      25.08, -77.35),
    ("Bridgetown",               "Barbados",                     13.10, -59.62),
    ("Belmopan",                 "Belize",                       17.25, -88.77),
    ("Ottawa",                   "Canada",                       45.42, -75.70),
    ("San José",                 "Costa Rica",                    9.93, -84.08),
    ("Havana",                   "Cuba",                         23.14, -82.36),
    ("Roseau",                   "Dominica",                     15.30, -61.39),
    ("Santo Domingo",            "Dominican Republic",           18.48, -69.90),
    ("San Salvador",             "El Salvador",                  13.70, -89.22),
    ("Saint George's",           "Grenada",                      12.05, -61.75),
    ("Guatemala City",           "Guatemala",                    14.64, -90.51),
    ("Port-au-Prince",           "Haiti",                        18.54, -72.34),
    ("Tegucigalpa",              "Honduras",                     14.10, -87.21),
    ("Kingston",                 "Jamaica",                      18.00, -76.79),
    ("Mexico City",              "Mexico",                       19.43, -99.13),
    ("Managua",                  "Nicaragua",                    12.13, -86.29),
    ("Panama City",              "Panama",                        8.99, -79.52),
    ("Basseterre",               "Saint Kitts and Nevis",        17.30, -62.72),
    ("Castries",                 "Saint Lucia",                  13.99, -61.00),
    ("Kingstown",                "St. Vincent and the Grenadines",13.16,-61.22),
    ("Port of Spain",            "Trinidad and Tobago",          10.65, -61.52),
    ("Washington D.C.",          "United States",                38.91, -77.04),
    # ── Sydamerika ──────────────────────────────────────────────────────────
    ("Buenos Aires",             "Argentina",                   -34.61, -58.38),
    ("Sucre",                    "Bolivia",                     -19.04, -65.26),
    ("Brasília",                 "Brazil",                      -15.78, -47.92),
    ("Santiago",                 "Chile",                       -33.46, -70.65),
    ("Bogotá",                   "Colombia",                      4.71, -74.07),
    ("Quito",                    "Ecuador",                      -0.23, -78.52),
    ("Georgetown",               "Guyana",                        6.80, -58.16),
    ("Asunción",                 "Paraguay",                    -25.29, -57.65),
    ("Lima",                     "Peru",                        -12.04, -77.03),
    ("Paramaribo",               "Suriname",                      5.85, -55.20),
    ("Montevideo",               "Uruguay",                     -34.90, -56.19),
    ("Caracas",                  "Venezuela",                    10.48, -66.88),
    # ── Oceanien ────────────────────────────────────────────────────────────
    ("Canberra",                 "Australia",                   -35.31, 149.12),
    ("Suva",                     "Fiji",                        -18.14, 178.44),
    ("South Tarawa",             "Kiribati",                      1.33, 172.98),
    ("Majuro",                   "Marshall Islands",              7.09, 171.38),
    ("Palikir",                  "Micronesia",                    6.92, 158.16),
    ("Yaren",                    "Nauru",                        -0.55, 166.92),
    ("Wellington",               "New Zealand",                 -41.29, 174.78),
    ("Ngerulmud",                "Palau",                         7.50, 134.64),
    ("Port Moresby",             "Papua New Guinea",             -9.43, 147.18),
    # Samoa udeladt (ikke med i 2032-OL-scenariet)
    ("Honiara",                  "Solomon Islands",              -9.43, 159.95),
    # Tonga udeladt (ikke med i 2032-OL-scenariet)
    ("Funafuti",                 "Tuvalu",                       -8.52, 179.22),
    ("Port Vila",                "Vanuatu",                     -17.74, 168.33),
]


# ---------------------------------------------------------------------------
# Generér CSV
# ---------------------------------------------------------------------------

def main() -> None:
    header = ["Sted", "Land", "Path ID", "Path order", "Latitude", "Longitude", "Pil"]
    rows: list[list] = [header]

    for path_id, (city, country, lat, lon) in enumerate(CAPITALS, start=1):
        angle = direction_deg(lon, lat)
        rows.append([city,       country,     path_id, 1, lat,          lon,          arrow_svg(angle)])
        rows.append(["Brisbane", "Australia", path_id, 2, BRISBANE_LAT, BRISBANE_LON, OLYMPIC_RINGS])

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

    print(f"Skrev {len(rows)} rækker ({len(CAPITALS)} lande) til {OUTPUT}")

    # Vis et par eksempler på piletning
    print("\nEksempler på retning:")
    examples = [("Washington D.C.", -77.04, 38.91),
                ("Santiago",        -70.65, -33.46),
                ("Tokyo",           139.69,  35.69),
                ("Wellington",      174.78, -41.29),
                ("Suva",            178.44, -18.14)]
    for name, lon, lat in examples:
        a = direction_deg(lon, lat)
        print(f"  {name:<22} lon={lon:>8.2f}  angle={a:>7.1f}°")


if __name__ == "__main__":
    main()
