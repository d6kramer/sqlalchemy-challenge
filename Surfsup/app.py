# Import the dependencies.
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

### Homepage (Home route)

@app.route("/")
def home():
    """List all available api routes"""
    return (
        f"Welcome to my Climate API! The following routes are available:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd <--- temperature min, max, and average starting from provided start date<br/>" 
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd <--- temperature min, max, and average for range of provided dates"
    )

### Precipiation Route

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, func.sum(Measurement.prcp)).\
    filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()

    session.close()

    prcp_results = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_results.append(prcp_dict)

    return jsonify(prcp_results)

### Stations Route

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))

    return jsonify(stations)

### Temperatures Route

@app.route("/api/v1.0/tobs")
def temperatures():
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).all()

    session.close()

    obsv_temps = list(np.ravel(results))
    
    return jsonify(obsv_temps)

### Selected Date(s) Route

@app.route("/api/v1.0/<start>")
def start_temps(start):
    temp_data = "Date not found."

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    if results[0][0] is not None:

        temp_data = list(np.ravel(results))
    

    session.close()
    return jsonify(temp_data)


    
@app.route("/api/v1.0/<start>/<end>")
def range_temps(start, end):
    temp_data = "This range of dates is not covered in the data!"

## Help from tutor Justin to set up validation message for user - did not finish, but confirms dates work!
    start_date = dt.date(*[int(x) for x in start.split("-")])
    end_date = dt.date(*[int(x) for x in end.split("-")])

    if start_date < end_date:
        print("valid range")
    
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()


    temp_data = list(np.ravel(results))

    session.close()
    return (temp_data)




if __name__ == '__main__':
    app.run(debug=True)