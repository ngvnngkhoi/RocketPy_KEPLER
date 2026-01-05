from rocketpy import Environment, SolidMotor, Rocket, Flight
import numpy as np 
import matplotlib.pyplot as plt
from rocketpy.rocket.empirical_aero import EmpiricalAero
n3301 = SolidMotor(
    thrust_source='Cesaroni_19318N3301-P.eng',
    dry_mass=0,
    dry_inertia=(0,0,0),
    nozzle_radius=0.03675,
    grain_number=1,
    grain_density=1558,
    grain_outer_radius=0.049,
    grain_initial_inner_radius=0.0245,
    grain_initial_height=1.239,
    grain_separation=0,
    grains_center_of_mass_position=0,
    center_of_dry_mass_position=0,
    nozzle_position=-0.6195-0.03,
    throat_radius=0.0245,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)
Bluewren = Rocket(
    center_of_mass_without_motor=1.782,
    coordinate_system_orientation="nose_to_tail",
    power_off_drag="cfd_simple.csv",
    power_on_drag="cfd_simple.csv",
    inertia=(0.11328,0.11328,19.219),
    mass=23.67,
    radius=0.0715
)
Bluewren.add_motor(n3301,position=2.60187309030958)
nose_cone = Bluewren.add_nose(
    base_radius=0.0715,
    kind="von karman",
    length=0.91440,
    name='Nose cone',
    position=0,
)
fin_set = Bluewren.add_trapezoidal_fins(
    cant_angle=0,
    name="Fins (Filleted)",
    n=4,
    position=2.85,
    root_chord=0.35,
    span=0.1370,
    sweep_length=0.26317,
    tip_chord=0.070,
    thickness = 0.005
)
tail = Bluewren.add_tail(
    bottom_radius=0.05,
    length=0.17,
    name="Transition",
    position=3.09535,
    top_radius=0.0715
)
main = Bluewren.add_parachute(
    name="Main Parachute",
    # area=4.6698,
    # cd=2.2,
    cd_s=10.2736,
    lag=1,
    trigger=457.2,
    radius=1.22,
)
drogue = Bluewren.add_parachute(
    name="Drogue Parachute",
    # area=0.29186,
    # cd=2.2,
    cd_s=0.6420997,
    lag=1,
    trigger='apogee',
    radius=0.305
)
# Bluewren.plots.static_margin()
# Bluewren.draw()
Bluewren.define_kepler_values()
aero = EmpiricalAero(Bluewren)



import datetime
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env2 = Environment(
    latitude=33,
    longitude=-107,
    elevation=1401,
    max_expected_height=30000,
)
# from datetime import datetime
# import pytz
# aest = pytz.timezone("Australia/Sydney")
# env2.set_date(aest.localize(datetime(2022, 5, 14, 18)))
# env2.set_atmospheric_model(type="windy", file="GFS")


#################### PROCESS GFS ################################################
################################################
################################################
################################################
from rocketpy import Function
import re
import numpy as np
file_path = "GFSBluewrenSAC.txt"
with open(file_path, 'r') as file:
    atmos_data = file.read()
lines = atmos_data.split("\n")
# Process GSD format (https://rucsoundings.noaa.gov/raob_format.html)
# Extract elevation data
for line in lines:
    # Split line into columns
    columns = re.split(" +", line)[1:]
    if len(columns) > 0:
        if columns[0] == "1" and columns[5] != "99999":
            # Save elevation
            elevation = float(columns[5])
        else:
            # No elevation data available
            pass
# Extract pressure as a function of height
pressure_array = []
for line in lines:
    # Split line into columns
    columns = re.split(" +", line)[1:]
    if len(columns) >= 6:
        if columns[0] in ["4", "5", "6", "7", "8", "9"]:
            # Convert columns to floats
            columns = np.array(columns, dtype=float)
            # Select relevant columns
            columns = columns[[2, 1]]
            # Check if values exist
            if max(columns) != 99999:
                # Save value
                pressure_array.append(columns)
pressure_array = np.array(pressure_array)
# Extract temperature as a function of height
temperature_array = []
for line in lines:
    # Split line into columns
    columns = re.split(" +", line)[1:]
    if len(columns) >= 6:
        if columns[0] in ["4", "5", "6", "7", "8", "9"]:
            # Convert columns to floats
            columns = np.array(columns, dtype=float)
            # Select relevant columns
            columns = columns[[2, 3]]
            # Check if values exist
            if max(columns) != 99999:
                # Save value
                temperature_array.append(columns)
temperature_array = np.array(temperature_array)
# Extract wind speed and direction as a function of height
windSpeed_array = []
windDirection_array = []
for line in lines:
    # Split line into columns
    columns = re.split(" +", line)[1:]
    if len(columns) >= 6:
        if columns[0] in ["4", "5", "6", "7", "8", "9"]:
            # Convert columns to floats
            columns = np.array(columns, dtype=float)
            # Select relevant columns
            columns = columns[[2, 5, 6]]
            # Check if values exist
            if max(columns) != 99999:
                # Save value
                windDirection_array.append(columns[[0, 1]])
                windSpeed_array.append(columns[[0, 2]])
windSpeed_array = np.array(windSpeed_array)
windDirection_array = np.array(windDirection_array)
# Converts 10*hPa to Pa and save values
pressure_array[:, 1] = 10 * pressure_array[:, 1]
# Convert 10*C to K and save values
temperature_array[:, 1] = (
        temperature_array[:, 1] / 10 + 273.15
)  # Converts C to K
# Process wind-u and wind-v
windSpeed_array[:, 1] = (
        windSpeed_array[:, 1] * 1.852 / 3.6
)  # Converts Knots to m/s
windHeading_array = windDirection_array[:, :] * 1
windHeading_array[:, 1] = (
                                  windDirection_array[:, 1] + 180
                          ) % 360  # Convert wind direction to wind heading
windU = windSpeed_array[:, :] * 1
windV = windSpeed_array[:, :] * 1
windU[:, 1] = windSpeed_array[:, 1] * np.sin(
    windHeading_array[:, 1] * np.pi / 180
)
windV[:, 1] = windSpeed_array[:, 1] * np.cos(
    windHeading_array[:, 1] * np.pi / 180
)
# Save maximum expected height
max_expected_height = pressure_array[-1, 0]
pressure = Function(
    source=list(map(tuple, pressure_array))
)
temperature = Function(
    source=list(map(tuple, temperature_array))
)
wind_direction = Function(
    source=list(map(tuple, windDirection_array))
)
wind_heading = Function(
    source=list(map(tuple, windHeading_array))
)
wind_speed = Function(
    source=list(map(tuple, windSpeed_array))
)
windVelocityX = Function(
    source=list(map(tuple, windU))
)
windVelocityY = Function(
    source=list(map(tuple, windV))
)
################################################
################################################
################### PROCESS GFS #################################################

env2.process_custom_atmosphere(pressure=pressure, temperature=temperature, wind_u=windVelocityX, wind_v=windVelocityY)

wind_flight = Flight(
    rocket=Bluewren,
    aero = aero,
    environment=env2,
    rail_length=5.1816,
    inclination=90,
    heading=90
)



wind_flight.altitude.plot(0,45)
m_2_ft = 3.28084
print(f'Wind apogee: {(wind_flight.apogee - env2.elevation) * m_2_ft } ft')


# env2.plots.atmospheric_model()
from rocketpy.simulation import FlightDataExporter

exporter = FlightDataExporter(wind_flight)
exporter.export_data(
    "Bluewren_SAC_rocketpy.csv",
    "altitude",
    "x",
    "y",
    "z",
    "vx",
    "vy",
    "vz",
    "ax",
    "ay",
    "az",
    "speed",
    "acceleration",
    "mach_number",
    "angle_of_attack"
)