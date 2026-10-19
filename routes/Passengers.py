from flask import Blueprint, render_template, redirect, request, url_for
from db import fetch_all, fetch_one, execute

Passengers_bp=Blueprint(

    'Passengers',
    __name__,
    url_prefix='/Passenger'

)


@Passengers_bp.route('/')
def Display_Passenger():
    
    return render_template('Passenger.html')