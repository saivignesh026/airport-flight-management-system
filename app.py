from flask import Flask, render_template, redirect, url_for, request
from collections import Counter
from dotenv import load_dotenv
import os
from db import fetch_all, fetch_one

load_dotenv()

from routes.Airports import Airports_bp
from routes.Airlines import Airlines_bp
from routes.Aircrafts import Aircrafts_bp
from routes.Runways import Runways_bp
from routes.Terminals import Terminals_bp
from routes.Gates import Gates_bp
from routes.Departments import Departments_bp
from routes.Roles import Roles_bp
from routes.Employees import Employees_bp
from routes.Flights import Flights_bp
from routes.Flight_Instances import Flight_Instances_bp
from routes.Passengers import Passengers_bp
from routes.Bookings import Bookings_bp

app = Flask(__name__)

app.register_blueprint(Airports_bp)
app.register_blueprint(Airlines_bp)
app.register_blueprint(Aircrafts_bp)
app.register_blueprint(Runways_bp)
app.register_blueprint(Terminals_bp)
app.register_blueprint(Gates_bp)
app.register_blueprint(Departments_bp)
app.register_blueprint(Roles_bp)
app.register_blueprint(Employees_bp)
app.register_blueprint(Flights_bp)
app.register_blueprint(Flight_Instances_bp)
app.register_blueprint(Passengers_bp)
app.register_blueprint(Bookings_bp)

app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_for_testing')

@app.route('/')
def Home():
    stats = {
        'airports': fetch_one('SELECT COUNT(*) AS count FROM Airport')['count'],
        'flights': fetch_one('SELECT COUNT(*) AS count FROM Flight')['count'],
        'instances': fetch_one('SELECT COUNT(*) AS count FROM Flight_Instance')['count'],
        'passengers': fetch_one('SELECT COUNT(*) AS count FROM Passenger')['count'],
        'bookings': fetch_one("SELECT COUNT(*) AS count FROM Booking WHERE Booking_Status = 'Confirmed'")['count'],
        'employees': fetch_one("SELECT COUNT(*) AS count FROM Employee WHERE Employee_Status = 'Active'")['count']
    }
    live_flights = fetch_all('SELECT * FROM Flight_Operational_Details ORDER BY Scheduled_Departure DESC')
    booking_overview = fetch_all('SELECT * FROM Booking_Status_Details ORDER BY Booking_ID DESC')
    infrastructure = fetch_all('SELECT * FROM Airport_Infrastructure')

    # Keep the homepage summary derived from the same operational records shown
    # below, so its status mix cannot drift from the detailed flight list.
    status_counts = Counter(str(f.get('Instance_Status') or 'Unknown') for f in live_flights)
    flight_status_summary = []
    for label, tone in (
        ('On Time', 'success'), ('Scheduled', 'info'), ('Boarding', 'boarding'),
        ('Delayed', 'warning'), ('Departed', 'departed'), ('Arrived', 'arrived'),
        ('Cancelled', 'danger'), ('Unknown', 'unknown')
    ):
        count = status_counts.get(label, 0)
        if count:
            flight_status_summary.append({
                'label': label,
                'count': count,
                'percent': round(count * 100 / len(live_flights)),
                'tone': tone
            })

    infrastructure_summary = [
        {
            'label': 'Terminals',
            'count': len({(i.get('IATA_Code') or i.get('Airport_Name') or i.get('Airport'), i.get('Terminal_Number')) for i in infrastructure if i.get('Terminal_Number') is not None}),
            'tone': 'cyan'
        },
        {
            'label': 'Gates',
            'count': len({(i.get('IATA_Code') or i.get('Airport_Name') or i.get('Airport'), i.get('Terminal_Number'), i.get('Gate_Number')) for i in infrastructure if i.get('Gate_Number') is not None}),
            'tone': 'amber'
        },
        {
            'label': 'Runways',
            'count': len({(i.get('IATA_Code') or i.get('Airport_Name') or i.get('Airport'), i.get('Runway_Code')) for i in infrastructure if i.get('Runway_Code') is not None}),
            'tone': 'violet'
        }
    ]
    return render_template(
        'Home.html',
        stats=stats,
        live_flights=live_flights,
        booking_overview=booking_overview,
        infrastructure=infrastructure,
        flight_status_summary=flight_status_summary,
        infrastructure_summary=infrastructure_summary
    )

if __name__ == "__main__":
    app.run(debug=True)
