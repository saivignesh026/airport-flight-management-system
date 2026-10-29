# Airport Flight Management System (AFMS)

A web-based database management system designed to streamline and centralize airport operations, flight logistics, passenger reservations, infrastructure, and staff administration. Built with **Python (Flask)** and **MySQL**, featuring a responsive, Apple-inspired interface with dark/light theming, client-side pagination, and searchable dropdown controls.

---

## Table of Contents

- [Features](#features)
- [System Architecture & Modules](#system-architecture--modules)
- [Tech Stack](#tech-stack)
- [Project Directory Structure](#project-directory-structure)
- [Database Setup & Views](#database-setup--views)
- [Installation & Local Setup](#installation--local-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)

---

## Features

- **Live Operations Dashboard:** High-level operational metrics (active staff, scheduled flights, confirmed bookings, passenger counts) and real-time flight operation boards.
- **Flight Operations & Scheduling:** Manage recurring flight routes and schedule specific flight instances linked to aircraft, runways, and gates.
- **Infrastructure Management:** Complete tracking of airports, terminals, gates, and runway specifications with operational status indicators.
- **Full Passenger Lifecycle:** Comprehensive management of passengers, booking transactions with new passenger details and payments, plus separate airport check-in, boarding, and baggage pages. Related writes use transactions.
- **Passenger Manifests:** Searchable, filterable flight manifests sortable by flight number, origin, and destination airport.
- **HR & Staff Administration:** Department hierarchical breakdowns, role allocations, and employee status tracking.
- **Refined Frontend Experience:**
  - Modern Apple-style design system with GPU-accelerated motion and zero layout-shift transitions.
  - Native zero-flash Light/Dark mode via `localStorage` and View Transitions API.
  - Automatic split-view layout for large desktop screens (tables and forms side-by-side).
  - Searchable drop-downs and instant table search/pagination.

---

## System Architecture & Modules

The application is structured into modular **Flask Blueprints**:

| Module | Route Prefix | Description |
| :--- | :--- | :--- |
| **Home** | `/` | Operational dashboard with live flight boards and booking/baggage overviews. |
| **Airports** | `/Airport` | Manage airport entries, IATA codes, cities, and countries. |
| **Airlines** | `/Airline` | Manage airlines with IATA and ICAO designation codes. |
| **Aircraft** | `/Aircraft` | Fleet management, capacity tracking, and carrier assignments. |
| **Runways** | `/Runway` | Runway code allocation, length specifications, and maintenance statuses. |
| **Terminals** | `/Terminal` | Terminal assignments and operational statuses across airports. |
| **Gates** | `/Gate` | Gate allocations linked to specific terminals and airports. |
| **Flights** | `/Flight` | Recurring route definitions and origin/destination schedules. |
| **Flight Instances** | `/FlightInstance` | Specific scheduled instances mapping flights to aircraft, gates, and runways. |
| **Passengers** | `/Passenger` | Passenger demographic and passport data, plus flight manifest lookups. |
| **Bookings** | `/Booking` | Creates passenger, ticket, and payment together. |
| **Check-in** | `/CheckIn` | Passenger check-in and boarding CRUD. |
| **Baggage** | `/Baggage` | Individual baggage registration, editing, and deletion. |
| **Departments** | `/Department` | Administrative organizational units. |
| **Roles** | `/Role` | Job titles and duties mapped to departments. |
| **Employees** | `/Employee` | Active/resigned staff details, contacts, and roles. |

---

## Tech Stack

- **Backend:** Python 3.10+, Flask
- **Database:** MySQL 8.0+
- **Database Driver:** `mysql-connector-python`
- **Environment Management:** `python-dotenv`
- **Frontend:** Semantic HTML5, Vanilla JavaScript (ES6+), Modern CSS (CSS Variables, Flexbox, CSS Grid)

---

## Project Directory Structure

```text
airport-flight-management-system/
├── app.py                      # Flask application and core dashboard route
├── db.py                       # Database connections, helper queries, and transaction contexts
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (git-ignored)
├── .gitignore                  # Git ignore rules
│
├── routes/                     # Blueprint route controllers
│   ├── Aircrafts.py
│   ├── Airlines.py
│   ├── Airports.py
│   ├── Baggage.py
│   ├── CheckIns.py
│   ├── Bookings.py
│   ├── Departments.py
│   ├── Employees.py
│   ├── Flight_Instances.py
│   ├── Flights.py
│   ├── Gates.py
│   ├── Passengers.py
│   ├── Roles.py
│   ├── Runways.py
│   └── Terminals.py
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Main layout wrapper
│   ├── Home.html               # Primary operational dashboard
│   ├── PassengerManifest.html  # Manifest reporting template
│   ├── components/             # Reusable partials (navbar, footer)
│   ├── Update/                 # Edit/Update views for each entity
│   └── [Entity].html           # List and create views for each entity
│
└── static/                     # Static assets
    ├── css/
    │   └── style.css           # Design tokens, Apple-inspired UI, themes, and motion
    └── js/
        ├── navbar.js           # Theme switcher, scroll observer, mobile drawer, split views
        ├── searchable-select.js# Custom keyboard-accessible searchable dropdowns
        ├── table-pagination.js # Client-side pagination, instant filter, and status pills
        └── theme-init.js       # Fast early head script preventing dark-mode flash

```

## Database Setup & Views

Create the MySQL database and install the tables, views, and stored procedures used
in `routes/` before running the application. Import your MySQL initialization dump first; an empty database alone is insufficient. For an existing database, execute the SQL provided in the project conversation
before using check-in and baggage. SQL scripts are intentionally kept outside
this repository. These routes use `Booking_Check_In_Details`, `Check_In_Details`,
`Baggage_Details`, and the `Add_*`, `Update_*`, `Delete_*`, and `*_To_Edit` stored procedures. Flask commits or rolls back
each operation; the procedures do not commit independently.

Required views include `Flight_Operational_Details`, `Booking_Status_Details`,
`Booking_Details`, `Airport_Infrastructure`, `Aircraft_Details`, `Flight_Details`,
`Runway_Details`, `Terminal_Details`, `Gate_Details`, `Employee_Details`, and
`Passenger_Manifest`. CRUD routes also depend on their `Add_*`, `Update_*`,
`Delete_*`, and `*_To_Edit` stored procedures.

## Installation & Local Setup

From the project directory, create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Environment Configuration

Create a git-ignored `.env` file in the project directory:

```dotenv
DB_USER=root
DB_HOST=localhost
DB_PASSWORD=your_mysql_password
DB_PORT=3306
DB_NAME=AF_DB
SECRET_KEY=replace_with_a_random_persistent_secret
```

Set a persistent `SECRET_KEY` to preserve sessions across application restarts
and workers. Without one, the application generates a temporary key at startup.

## Running the Application

```bash
python app.py
```

Open http://127.0.0.1:5000/. For local debugging, set `FLASK_DEBUG=1` explicitly.

## Verification

```bash
python -m unittest discover -s tests -v
```

The regression suite mocks database access. It checks route rendering, missing
records, booking updates, manifest queries, time formatting, and database cleanup
and rollback. It does not replace integration testing against the configured
MySQL schema and stored procedures.

To run the optional integration check against an isolated MySQL instance, supply
your dump, an initialized temporary data directory, and the SQL update saved
outside the repository:

```bash
python tests/mysql_workflow.py /path/to/AFMS.sql /tmp/afms-test-db /path/to/update.sql
```

This test uses only the temporary database and does not read database credentials
from `.env`.
