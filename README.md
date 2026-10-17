# NearbyGo

A web-based local place discovery and one-day visit planner for Panadura, built
from the NearbyGo Software Requirements Specification v1.0 (ITE2953 Programming
Group Project, P.A.R.T. Palihawadana, E2410817).

Visitors browse places within 25 km of Panadura, filter them by category, read
practical details, see them on a map and put the ones they like into an ordered
one-day plan. Administrators manage categories and places through a secured
Django admin.

## Features

| Area | What it does |
|---|---|
| Browse | Home page with a centred welcome banner and place cards (name, category, distance, summary). |
| Filter | Category chips with counts, "All places", "Clear filter" and a no-results message. |
| Details | Description, hours, fee, recommended visit time, best time, facilities, accessibility, transport, families, student discount and tips. Unknown fields say "Not available"; unchecked information is labelled "Not yet verified". |
| Map | Leaflet + OpenStreetMap, coloured markers by category, popups linking to details, a text list underneath and a message if map images can't load. |
| Plan | Add, remove, move earlier or later, optional arrival time, total visiting time, numbered map of stops, clear with confirmation. Plans are anonymous and kept for the browser session. |
| Admin | Create, edit, activate, deactivate and delete categories and places; 25 km radius check; timestamps; idle sign-out after 30 minutes. |

## Technology

Python 3.10 or later, Django 5.2 LTS, MySQL 8.0 (via `mysqlclient`), Django
templates, Bootstrap 5.3, Bootstrap Icons, Leaflet 1.9 and OpenStreetMap tiles.
Bootstrap, Leaflet, the icons and the Jost and Roboto fonts are bundled in
`static/vendor/`, so pages work without a CDN.

## Project structure

```
nearbygo/
├── config/                 Project settings, URLs, WSGI/ASGI
├── places/                 Categories, places, map, help page, admin
│   ├── models.py           Category, Place, validation and radius rules
│   ├── geo.py              Haversine distance-checking method
│   ├── admin.py            Admin screens and activate/deactivate actions
│   ├── middleware.py       Admin idle sign-out
│   ├── seed_data.py        The 10 approved places (DR-07)
│   ├── management/commands seed_places, check_radius
│   └── tests/              Model, view, admin and command tests
├── planner/                One-day visit plan (VisitPlan, PlanItem)
│   ├── services.py         Add, remove, reorder, clear
│   └── management/commands cleanup_plans
├── templates/              Django templates (base, places, planner, admin, 404, 500)
├── static/                 CSS, JavaScript, favicon and bundled libraries
├── docs/TRACEABILITY.md    Requirement → implementation → test table
├── requirements.txt
└── .env.example
```

## Setting up on your computer

### 1. Install the prerequisites

- Python 3.10 or later (`python --version`)
- MySQL Server 8.0 (MySQL Installer on Windows, `brew install mysql` on macOS, or your Linux package manager)

### 2. Create a virtual environment and install packages

Windows (PowerShell):

```powershell
cd nearbygo
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS or Linux:

```bash
cd nearbygo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `mysqlclient` fails to install on macOS or Linux, install the MySQL client
headers first (`brew install mysql pkg-config`, or `sudo apt install
default-libmysqlclient-dev pkg-config build-essential`) and run the command again.

### 3. Create the database and user

Open the MySQL command line as root (`mysql -u root -p`) and run:

```sql
CREATE DATABASE nearbygo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nearbygo'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON nearbygo.* TO 'nearbygo'@'localhost';
-- Needed only to run the automated tests, which create a test_nearbygo database:
GRANT ALL PRIVILEGES ON test_nearbygo.* TO 'nearbygo'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configure the environment

Copy `.env.example` to `.env` and fill in at least:

```
DJANGO_SECRET_KEY=<paste a generated key>
DJANGO_DEBUG=True
DB_PASSWORD=choose-a-strong-password
```

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Optionally set your private reference location so the system also checks each
place's coordinates against the 25 km radius:

```
NEARBYGO_REFERENCE_LAT=6.7xxxxx
NEARBYGO_REFERENCE_LNG=79.9xxxxx
```

These values stay on the server. They are never sent to templates, JavaScript or
the browser (NFR-SE-07). Keep `.env` out of version control.

### 5. Create the tables, load the places and create an administrator

```bash
python manage.py migrate
python manage.py seed_places
python manage.py createsuperuser
```

### 6. Run the site

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 for the visitor site and http://127.0.0.1:8000/admin/
for administration.

### Quick trial without MySQL

For a quick look only, set `DB_ENGINE=sqlite` in `.env`, then run steps 5 and 6.
The submitted system should use MySQL as required by the SRS.

## Before you submit or demonstrate

The ten seed places use the verified distances from SRS Section 6.1. Their
coordinates are approximate public locations, and the visiting information is
cautious: some hours and fees are left blank, and every place starts as
"Not yet verified". In the admin:

1. Check each place's coordinates on the map and adjust them if a marker is off.
2. Confirm opening hours, fees and facilities with each venue, fill them in and
   set **Practical info verified on**. The "Not yet verified" notice then becomes
   a "Checked with the venue on …" note.
3. Upload your own or properly licensed photos with alt text and a credit (OR-04).
4. Run `python manage.py check_radius` to review every place against the radius.

## Running the tests

```bash
python manage.py test
```

There are 101 automated tests. Most test names start with the requirement ID
they check, for example `test_fr_vp_05_move_earlier`. See
`docs/TRACEABILITY.md` for the full mapping and the manual acceptance checklist.

## Management commands

| Command | Purpose |
|---|---|
| `python manage.py seed_places` | Load the 5 categories and 10 places. Safe to run again; add `--update` to overwrite edited places with the seed text. |
| `python manage.py check_radius` | List every place with its recorded distance and, if the reference point is set, its straight-line distance. Flags anything outside 25 km. |
| `python manage.py clearsessions` | Django's built-in command to remove expired sessions. |
| `python manage.py cleanup_plans` | Remove visit plans whose session has expired. Run after `clearsessions`, for example daily. |

## Distance-checking method (SRS 2.5)

Every place stores an administrator-verified approximate distance, which must be
25 km or less for the place to be active. When the private reference point is
configured, the system also calculates the straight-line (haversine) distance
from it to the place's coordinates and refuses to activate a place outside the
radius. A straight line is never longer than the road distance, so a place that
fails this check is certainly outside the radius. See `places/geo.py`.

## Decisions on the SRS "To Be Determined" items

| Item | Decision in this build |
|---|---|
| TBD-01 Hosting provider and domain | Still open. The app runs on any host with Python and MySQL (see deployment below). |
| TBD-02 Colour palette, logo, mock-ups | Travel theme inspired by the Travela template: royal navy `#13357b`, near-black `#14141f` footer, light grey `#f3f5f9` background, pill-shaped buttons, Jost headings and Roboto body text, white map-pin logo. Colours are at the top of `static/css/nearbygo.css`. |
| TBD-03 Reordering on touch screens | "Move earlier" and "Move later" buttons. They are large enough for touch, work with a keyboard and need no JavaScript. |
| TBD-04 Map tile endpoint | `MAP_TILE_URL` setting, defaulting to the standard OpenStreetMap tiles. For a public site with real traffic, follow the OSM tile usage policy or switch to a tile provider and keep the attribution. |
| TBD-05 Plan storage | Plans are stored anonymously in MySQL (`VisitPlan`, `PlanItem`), linked to the browser session. No personal details are collected. |

## Deploying to a public server

1. Set `DJANGO_DEBUG=False`, a long random `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`
   and `DJANGO_CSRF_TRUSTED_ORIGINS` (for example `https://nearbygo.example.lk`).
2. Serve the site over HTTPS and set `USE_HTTPS=True` (and `BEHIND_PROXY=True` if
   Nginx or a platform proxy handles HTTPS). This turns on HTTPS redirects,
   secure cookies and HSTS.
3. Run `python manage.py collectstatic` and serve `staticfiles/` and `media/`
   from the web server.
4. Run Django with a production server such as Gunicorn (Linux) or Waitress
   (Windows), for example `gunicorn config.wsgi`.
5. Run `python manage.py check --deploy`. The only remaining notes should be
   about HSTS subdomains and preload, which are left off on purpose.

## Licences of bundled files

Bootstrap and Bootstrap Icons (MIT), Leaflet (BSD-2-Clause) and the Jost and
Roboto fonts (SIL Open Font Licence 1.1). Licence files are in each folder under
`static/vendor/`. Map data © OpenStreetMap contributors (ODbL).
