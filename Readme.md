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
- **Full Passenger Lifecycle:** Comprehensive management of passengers, booking transactions, automated multi-table check-in records, baggage tracking, and payments wrapped inside transactional rollbacks.
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
| **Home** | `/` | Operational dashboard with live flight boards, baggage overviews, and infrastructure stats. |
| **Airports** | `/Airport` | Manage airport entries, IATA codes, cities, and countries. |
| **Airlines** | `/Airline` | Manage airlines with IATA and ICAO designation codes. |
| **Aircraft** | `/Aircraft` | Fleet management, capacity tracking, and carrier assignments. |
| **Runways** | `/Runway` | Runway code allocation, length specifications, and maintenance statuses. |
| **Terminals** | `/Terminal` | Terminal assignments and operational statuses across airports. |
| **Gates** | `/Gate` | Gate allocations linked to specific terminals and airports. |
| **Flights** | `/Flight` | Recurring route definitions and origin/destination schedules. |
| **Flight Instances** | `/FlightInstance` | Specific scheduled instances mapping flights to aircraft, gates, and runways. |
| **Passengers** | `/Passenger` | Passenger demographic and passport data, plus flight manifest lookups. |
| **Bookings** | `/Booking` | Orchestrates atomic inserts across `Booking`, `Payment`, `Check_In`, and `Baggage`. |
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
├── app.py                      # Flask application factory and core dashboard route
├── db.py                       # Database connection pooling, helper queries, and transaction contexts
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (git-ignored)
├── .gitignore                  # Git ignore rules
│
├── routes/                     # Blueprint route controllers
│   ├── Aircrafts.py
│   ├── Airlines.py
│   ├── Airports.py
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


Database Configuration

The application expects a running MySQL database (default name: AF_DB). Ensure your database is initialized with the required tables, relational constraints, and the following views and stored procedures:

    Views:

        Flight_Operational_Details

        Booking_Status_Details / Booking_Details

        Airport_Infrastructure

        Aircraft_Details

        Employee_Details

        Passenger_Manifest

    Stored Procedures:

        Aircraft_To_Edit(id)

        Runway_To_Edit(id)

        Terminal_To_Edit(id)

        Role_To_Edit(id)

        Employee_To_Edit(id)

        Booking_To_Edit(id)

Installation & Setup
1. Clone the Repository
Bash

git clone [https://github.com/your-username/airport-flight-management-system.git](https://github.com/your-username/airport-flight-management-system.git)
cd airport-flight-management-system

2. Set Up a Virtual Environment
Bash

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

3. Install Dependencies
Bash

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the root directory:
Code snippet

DB_USER=root
DB_HOST=localhost
DB_PASSWORD=your_mysql_password
DB_PORT=3306
DB_NAME=AF_DB
SECRET_KEY=your_secret_key

5. Run the Application
Bash

python app.py

The application will be accessible at http://127.0.0.1:5000/.