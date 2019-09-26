# Imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

from flask import Flask, jsonify

# Setup Database
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create an app
app = Flask(__name__)


# Flask routes
@app.route("/")
def index():
    return (
        f"<h2>Welcome to HI Climate API!</h2><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"The following 2 APIs require date input . . . (between 1/1/2010 & 8/23/2017)<br/>"
        f"Input a start, or start and end date in yyyy-mm-dd format<br/>"
        f"/api/v1.0/<i>start</i><br/>"
        f"/api/v1.0/<i>start/end</i><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Run the query
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=366) 
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).order_by(Measurement.date).all()
    session.close()

    # Create a dictionary from the precip data
    all_precip = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Run the query
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

 
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Run the query
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=366) 
    tempslast12 = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date > year_ago).all()
    
    session.close()

    return jsonify(tempslast12)

@app.route("/api/v1.0/<start_date>")
def start_only(start_date):
    session = Session(engine)
    temps =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()
    # Create a dictionary from the temps data
    all_temps = []
    for tmin, tavg, tmax in temps:
        temps_dict = {}
        temps_dict["tmin"] = tmin
        temps_dict["tavg"] = tavg
        temps_dict["tmax"] = tmax
        all_temps.append(temps_dict)
    return jsonify(all_temps)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    session = Session(engine)
    temps2 =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

 # Create a dictionary from the temps2 data
    all_temps2 = []
    for tmin, tavg, tmax in temps2:
        temps2_dict = {}
        temps2_dict["tmin"] = tmin
        temps2_dict["tavg"] = tavg
        temps2_dict["tmax"] = tmax
        all_temps2.append(temps2_dict)

    return jsonify(all_temps2)
    
    

# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
