import streamlit as st
import numpy as np
import random
import time
from openai import OpenAI
import pyvista as pv
from pyvista import examples
from stpyvista import stpyvista
import ephem
import numpy as np
import pyvista as pv
from datetime import datetime, timedelta
pv.global_theme.interactive = True



# Function to convert celestial coordinates (RA, DEC) to 3D cartesian coordinates
def celestial_to_cartesian(ra, dec, distance=1):
    ra = np.deg2rad(float(ra)) * 15  # RA is in hours, so convert to degrees first
    dec = np.deg2rad(float(dec))
    x = distance * np.cos(dec) * np.cos(ra)
    y = distance * np.cos(dec) * np.sin(ra)
    z = distance * np.sin(dec)
    return x, y, z

# Function to create a circular orbit path in 3D space
def create_orbit(semi_major_axis, eccentricity, num_points=100):
    theta = np.linspace(0, 2 * np.pi, num_points)
    r = semi_major_axis * (1 - eccentricity**2) / (1 + eccentricity * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros(num_points)  # Keep orbit in the x-y plane for simplicity
    return np.column_stack((x, y, z))


# Compute and store planet positions
def compute_planet_positions(d):
    positions = {}

    # Sun
    sun = ephem.Sun()
    sun.compute(d)
    positions['Sun'] = celestial_to_cartesian(sun.ra, sun.dec, distance=0)  # Place sun at origin

    # Mercury
    mercury = ephem.Mercury()
    mercury.compute(d)
    positions['Mercury'] = celestial_to_cartesian(mercury.ra, mercury.dec, distance=0.4)  # Arbitrary distance for visualization

    # Venus
    venus = ephem.Venus()
    venus.compute(d)
    positions['Venus'] = celestial_to_cartesian(venus.ra, venus.dec, distance=0.7)

    positions['Earth'] = celestial_to_cartesian(0, 0, distance=1)

    # Mars
    mars = ephem.Mars()
    mars.compute(d)
    positions['Mars'] = celestial_to_cartesian(mars.ra, mars.dec, distance=1.5)

    # Jupiter
    jupiter = ephem.Jupiter()
    jupiter.compute(d)
    positions['Jupiter'] = celestial_to_cartesian(jupiter.ra, jupiter.dec, distance=5)

    # Saturn
    saturn = ephem.Saturn()
    saturn.compute(d)
    positions['Saturn'] = celestial_to_cartesian(saturn.ra, saturn.dec, distance=9)

    # Uranus
    uranus = ephem.Uranus()
    uranus.compute(d)
    positions['Uranus'] = celestial_to_cartesian(uranus.ra, uranus.dec, distance=19)

    # Neptune
    neptune = ephem.Neptune()
    neptune.compute(d)
    positions['Neptune'] = celestial_to_cartesian(neptune.ra, neptune.dec, distance=30)

    # Ceres
    ceres = ephem.EllipticalBody()
    ceres._epoch = ephem.J2000
    ceres._a = 2.766  # semi-major axis in AU
    ceres._e = 0.0758  # eccentricity
    ceres._inc = np.deg2rad(10.59)  # inclination in radians
    ceres._Om = np.deg2rad(80.33)  # longitude of the ascending node in radians
    ceres._om = np.deg2rad(73.57)  # argument of perihelion in radians
    ceres._M = np.deg2rad(198.88)  # mean anomaly in radians
    ceres.compute(d)
    positions['Ceres'] = celestial_to_cartesian(ceres.ra, ceres.dec, distance=ceres.sun_distance)

    # Pallas
    pallas = ephem.EllipticalBody()
    pallas._epoch = ephem.J2000
    pallas._a = 2.772  # semi-major axis in AU
    pallas._e = 0.2302  # eccentricity
    pallas._inc = np.deg2rad(34.83)  # inclination in radians
    pallas._Om = np.deg2rad(173.00)  # longitude of the ascending node in radians
    pallas._om = np.deg2rad(179.32)  # argument of perihelion in radians
    pallas._M = np.deg2rad(267.24)  # mean anomaly in radians
    pallas.compute(d)
    positions['Pallas'] = celestial_to_cartesian(pallas.ra, pallas.dec, distance=pallas.sun_distance)

    # Vesta
    vesta = ephem.EllipticalBody()
    vesta._epoch = ephem.J2000
    vesta._a = 2.361  # semi-major axis in AU
    vesta._e = 0.0889  # eccentricity
    vesta._inc = np.deg2rad(7.14)  # inclination in radians
    vesta._Om = np.deg2rad(103.80)  # longitude of the ascending node in radians
    vesta._om = np.deg2rad(151.14)  # argument of perihelion in radians
    vesta._M = np.deg2rad(272.24)  # mean anomaly in radians
    vesta.compute(d)
    positions['Vesta'] = celestial_to_cartesian(vesta.ra, vesta.dec, distance=vesta.sun_distance)

    # Hygiea
    hygiea = ephem.EllipticalBody()
    hygiea._epoch = ephem.J2000
    hygiea._a = 3.180  # semi-major axis in AU
    hygiea._e = 0.192  # eccentricity
    hygiea._inc = np.deg2rad(48.23)  # inclination in radians
    hygiea._Om = np.deg2rad(224.90)  # longitude of the ascending node in radians
    hygiea._om = np.deg2rad(268.93)  # argument of perihelion in radians
    hygiea._M = np.deg2rad(270.48)  # mean anomaly in radians
    hygiea.compute(d)
    positions['Hygiea'] = celestial_to_cartesian(hygiea.ra, hygiea.dec, distance=hygiea.sun_distance)

    # Eros
    eros = ephem.EllipticalBody()
    eros._epoch = ephem.J2000
    eros._a = 1.458  # semi-major axis in AU
    eros._e = 0.2232  # eccentricity
    eros._inc = np.deg2rad(10.86)  # inclination in radians
    eros._Om = np.deg2rad(185.18)  # longitude of the ascending node in radians
    eros._om = np.deg2rad(242.85)  # argument of perihelion in radians
    eros._M = np.deg2rad(193.80)  # mean anomaly in radians
    eros.compute(d)
    positions['Eros'] = celestial_to_cartesian(eros.ra, eros.dec, distance=eros.sun_distance)

    # Itokawa
    itokawa = ephem.EllipticalBody()
    itokawa._epoch = ephem.J2000
    itokawa._a = 1.225  # semi-major axis in AU
    itokawa._e = 0.172  # eccentricity
    itokawa._inc = np.deg2rad(12.84)  # inclination in radians
    itokawa._Om = np.deg2rad(249.72)  # longitude of the ascending node in radians
    itokawa._om = np.deg2rad(157.86)  # argument of perihelion in radians
    itokawa._M = np.deg2rad(224.82)  # mean anomaly in radians
    itokawa.compute(d)
    positions['Itokawa'] = celestial_to_cartesian(itokawa.ra, itokawa.dec, distance=itokawa.sun_distance)

    # Bennu
    bennu = ephem.EllipticalBody()
    bennu._epoch = ephem.J2000
    bennu._a = 1.123  # semi-major axis in AU
    bennu._e = 0.2049  # eccentricity
    bennu._inc = np.deg2rad(6.08)  # inclination in radians
    bennu._Om = np.deg2rad(279.34)  # longitude of the ascending node in radians
    bennu._om = np.deg2rad(129.81)  # argument of perihelion in radians
    bennu._M = np.deg2rad(172.36)  # mean anomaly in radians
    bennu.compute(d)
    positions['Bennu'] = celestial_to_cartesian(bennu.ra, bennu.dec, distance=bennu.sun_distance)

    # 2002 AA69
    aa69 = ephem.EllipticalBody()
    aa69._epoch = ephem.J2000
    aa69._a = 0.983  # semi-major axis in AU
    aa69._e = 0.189  # eccentricity
    aa69._inc = np.deg2rad(8.33)  # inclination in radians
    aa69._Om = np.deg2rad(157.87)  # longitude of the ascending node in radians
    aa69._om = np.deg2rad(325.26)  # argument of perihelion in radians
    aa69._M = np.deg2rad(168.11)  # mean anomaly in radians
    aa69.compute(d)
    positions['2002 AA69'] = celestial_to_cartesian(aa69.ra, aa69.dec, distance=aa69.sun_distance)

    # 2004 BL86
    bl86 = ephem.EllipticalBody()
    bl86._epoch = ephem.J2000
    bl86._a = 1.057  # semi-major axis in AU
    bl86._e = 0.257  # eccentricity
    bl86._inc = np.deg2rad(19.19)  # inclination in radians
    bl86._Om = np.deg2rad(165.64)  # longitude of the ascending node in radians
    bl86._om = np.deg2rad(147.87)  # argument of perihelion in radians
    bl86._M = np.deg2rad(237.23)  # mean anomaly in radians
    bl86.compute(d)
    positions['2004 BL86'] = celestial_to_cartesian(bl86.ra, bl86.dec, distance=bl86.sun_distance)

    # 2014 UR116
    ur116 = ephem.EllipticalBody()
    ur116._epoch = ephem.J2000
    ur116._a = 1.017  # semi-major axis in AU
    ur116._e = 0.452  # eccentricity
    ur116._inc = np.deg2rad(13.04)  # inclination in radians
    ur116._Om = np.deg2rad(273.28)  # longitude of the ascending node in radians
    ur116._om = np.deg2rad(114.21)  # argument of perihelion in radians
    ur116._M = np.deg2rad(114.77)  # mean anomaly in radians
    ur116.compute(d)
    positions['2014 UR116'] = celestial_to_cartesian(ur116.ra, ur116.dec, distance=ur116.sun_distance)

    # Define Halley's Comet
    halley = ephem.EllipticalBody()
    halley._epoch = ephem.J2000
    halley._a = 17.834  # semi-major axis in AU
    halley._e = 0.96714  # eccentricity
    halley._inc = np.deg2rad(162.26)  # inclination in radians
    halley._Om = np.deg2rad(58.42)  # longitude of the ascending node in radians
    halley._om = np.deg2rad(111.33)  # argument of perihelion in radians
    halley._M = np.deg2rad(20.88)  # mean anomaly in radians
    halley.compute(d)
    positions['Halley\'s comet'] = celestial_to_cartesian(halley.ra, halley.dec, distance=halley.sun_distance)
   
    return positions

# Visualize planet positions and orbits using PyVista
def visualize_planet_positions_and_orbits(positions):
    plotter = pv.Plotter()

    # Set the background to black to make the planets and orbits visible
    plotter.set_background("black")
    # Orbits radii (for visualization purposes)
    orbit_radii = {
        'Mercury': 0.4,
        'Venus': 0.7,
        'Earth': 1,
        'Mars': 1.5,
        'Jupiter': 5,
        'Saturn': 9,
        'Uranus': 19,
        'Neptune': 30,
        'Ceres': 2.766,
        'Pallas': 2.772,
        'Vesta': 2.361,
        'Hygiea': 3.180,
        'Eros': 1.458,
        'Itokawa': 1.225,
        'Bennu': 1.123,
        '2002 AA69': 0.983,
        '2004 BL86': 1.057,
        '2014 UR116': 1.017,
        'Halley\'s comet': 17.834
    }

    # Planet sizes: smaller for inner planets, bigger for outer planets
    planet_sizes = {
        'Mercury': 0.06,  # Small inner planets
        'Venus': 0.15,
        'Earth': 0.16,
        'Mars': 0.0825,
        'Jupiter': 1.675,  # Larger outer planets
        'Saturn': 1.4,
        'Uranus': 1.25,
        'Neptune': 1.25,
        'Ceres': 0.015,
        'Pallas': 0.015,
        'Vesta': 0.015,
        'Hygiea': 0.015,
        'Eros': 0.015,
        'Itokawa': 0.015,
        'Bennu': 0.015,
        '2002 AA69': 0.015,
        '2004 BL86': 0.015,
        '2014 UR116': 0.015,
        'Halley\'s comet': 0.2
    }

    # Define colors for each planet
    planet_colors = {
        'Sun': (253, 184, 19),
        'Mercury': examples.planets.download_mercury_surface(texture=True),
        'Venus': examples.planets.download_venus_surface(texture=True),
        'Earth': examples.load_globe_texture(),
        'Mars': examples.planets.download_mars_surface(texture=True),
        'Jupiter': examples.planets.download_jupiter_surface(texture=True),
        'Saturn': examples.planets.download_saturn_surface(texture=True),
        'Uranus': examples.planets.download_uranus_surface(texture=True),
        'Neptune': examples.planets.download_neptune_surface(texture=True),
        'Ceres': (255, 50, 50),
        'Pallas': (255, 50, 50),
        'Vesta': (255, 50, 50),
        'Hygiea': (255, 50, 50),
        'Eros': (255, 50, 50),
        'Itokawa': (255, 50, 50),
        'Bennu': (255, 50, 50),
        '2002 AA69': (255, 50, 50),
        '2004 BL86': (255, 50, 50),
        '2014 UR116': (255, 50, 50),
        'Halley\'s comet': (255, 50, 50)
    }

    inner = 1.4 + 0.2
    outer = 1.4 + 1.5
    saturn_rings = examples.planets.load_saturn_rings(inner=inner, outer=outer, c_res=50)
    mercury = examples.planets.load_mercury(radius=0.06)
    venus = examples.planets.load_venus(radius=0.15)
    earth = examples.planets.load_earth(radius=0.16)
    mars = examples.planets.load_mars(radius=0.0825)
    jupiter = examples.planets.load_jupiter(radius=1.675)
    saturn = examples.planets.load_saturn(radius=1.4)
    uranus = examples.planets.load_uranus(radius=1.5)
    neptune = examples.planets.load_neptune(radius=1.5)

    # Add planets to Plotter.
    sun = pv.Sphere(radius=0.2, phi_resolution=30, theta_resolution=30)  # Larger radius for the Sun
    plotter.add_mesh(sun.translate(positions['Sun']), color=planet_colors['Sun'], smooth_shading=True)
    plotter.add_mesh(mercury.translate(positions['Mercury']), name="Mercury",texture=planet_colors['Mercury'], smooth_shading=True)
    plotter.add_mesh(venus.translate(positions['Venus']), texture=planet_colors['Venus'], smooth_shading=True)
    plotter.add_mesh(earth.translate(positions['Earth']), texture=planet_colors['Earth'], smooth_shading=True)
    plotter.add_mesh(mars.translate(positions['Mars']), texture=planet_colors['Mars'], smooth_shading=True)
    plotter.add_mesh(jupiter.translate(positions['Jupiter']), texture=planet_colors['Jupiter'], smooth_shading=True)
    plotter.add_mesh(saturn.translate(positions['Saturn']), texture=planet_colors['Saturn'], smooth_shading=True)
    plotter.add_mesh(saturn_rings.translate(positions['Saturn']), texture=examples.planets.download_saturn_rings(texture=True), smooth_shading=True)
    plotter.add_mesh(uranus.translate(positions['Uranus']), texture=planet_colors['Uranus'], smooth_shading=True)
    plotter.add_mesh(neptune.translate(positions['Neptune']), texture=planet_colors['Neptune'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Ceres']).translate(positions['Ceres']), color=planet_colors['Ceres'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Pallas']).translate(positions['Pallas']), color=planet_colors['Pallas'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Vesta']).translate(positions['Vesta']), color=planet_colors['Vesta'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Hygiea']).translate(positions['Hygiea']), color=planet_colors['Hygiea'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Eros']).translate(positions['Eros']), color=planet_colors['Eros'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Itokawa']).translate(positions['Itokawa']), color=planet_colors['Itokawa'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Bennu']).translate(positions['Bennu']), color=planet_colors['Bennu'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['2002 AA69']).translate(positions['2002 AA69']), color=planet_colors['2002 AA69'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['2004 BL86']).translate(positions['2004 BL86']), color=planet_colors['2004 BL86'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['2014 UR116']).translate(positions['2014 UR116']), color=planet_colors['2014 UR116'], smooth_shading=True)
    plotter.add_mesh(pv.Sphere(radius=planet_sizes['Halley\'s comet']).translate(positions['Halley\'s comet']), color=planet_colors['Halley\'s comet'], smooth_shading=True)

    # Add orbits for each planet
    # Add orbits for each planet
    orbit_eccentricities = {
        'Mercury': 0.02056,
        'Venus': 0.0068,
        'Earth': 0.0167,
        'Mars': 0.00934,
        'Jupiter': 0.0489,
        'Saturn': 0.0538,
        'Uranus': 0.00472,
        'Neptune': 0.0086,
        'Ceres': 0.0758,
        'Pallas': 0.2302,
        'Vesta': 0.0889,
        'Hygiea': 0.192,
        'Eros': 0.2232,
        'Itokawa': 0.172,
        'Bennu': 0.2049,
        '2002 AA69': 0.189,
        '2004 BL86': 0.257,
        '2014 UR116': 0.452,
        'Halley\'s comet': 0.96714
    }

    for planet, radius in orbit_radii.items():
        if planet in ['Ceres', 'Pallas', 'Vesta', 'Hygiea', 'Eros', 'Itokawa', 'Bennu', '2002 AA69', '2004 BL86', '2014 UR116', '2014 UR116', 'Halley\'s comet']:
            # Get the semi-major axis and eccentricity of the object
            semi_major_axis = orbit_radii[planet]
            eccentricity = orbit_eccentricities[planet]
            # Create an elliptical orbit path
            orbit_points = create_orbit(semi_major_axis, eccentricity)
            #plotter.add_lines(orbit_points, color="white", width=0.7)
        else:
            # Create a circular orbit path
            eccentricity = orbit_eccentricities[planet]
            orbit_points = create_orbit(radius, eccentricity)
            plotter.add_lines(orbit_points, color="white", width=0.7)  # Adjust the width as needed    # Set plot view and labels
    plotter.add_axes()

    # Reset the camera to focus on the objects in the scene
    plotter.reset_camera()

    # Show the plot
    stpyvista(plotter)

st.set_page_config(layout="wide")
col1, col2 = st.columns(2)
with col1:
    st.write("""
    # Our Orrery Web App showing planets and NEO's in the solar system""")
with col2:
    BackIsClicked = st.button("Back", use_container_width=True)
if BackIsClicked:
    st.switch_page("Home_Page.py")
year = st.slider('year', min_value=1900, max_value=2100, value= 2024)
week = st.slider('week', min_value=1, max_value=52, value= 40)

d = f"{year}/{week//4.18}/{week%4.18}"

positions = compute_planet_positions(d)
visualize_planet_positions_and_orbits(positions)
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    st.button('Sun', use_container_width=True)
with col2:
    st.button('Mercury', use_container_width=True)
with col3:
    st.button('Venus', use_container_width=True)
with col4:
    st.button('Earth', use_container_width=True)
with col5:
    st.button('Mars', use_container_width=True)
with col1:
    st.button('Jupiter', use_container_width=True)
with col2:
    st.button('Saturn', use_container_width=True)
with col3:
    st.button('Uranus', use_container_width=True)
with col4:
    st.button('Neptune', use_container_width=True)
with col5:
    st.button('Halley\'s comet', use_container_width=True)
with col1:
    st.button('Ceres', use_container_width=True)
with col2:
    st.button('Pallas', use_container_width=True)
with col3:
    st.button('Vesta', use_container_width=True)
with col4:
    st.button('Hygiea', use_container_width=True)
with col5:
    st.button('Eros', use_container_width=True)
with col1:
    st.button('Itokawa', use_container_width=True)
with col2:
    st.button('Bennu', use_container_width=True)
with col3:
    st.button('2002 AA69', use_container_width=True)
with col4:
    st.button('2004 BL86', use_container_width=True)
with col5:
    st.button('2014 UR116', use_container_width=True)
