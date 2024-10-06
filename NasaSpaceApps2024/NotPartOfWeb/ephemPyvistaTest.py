import ephem
import numpy as np
import pyvista as pv
from datetime import datetime, timedelta

# Function to convert celestial coordinates (RA, DEC) to 3D cartesian coordinates
def celestial_to_cartesian(ra, dec, distance=1):
    ra = np.deg2rad(float(ra)) * 15  # RA is in hours, so convert to degrees first
    dec = np.deg2rad(float(dec))
    x = distance * np.cos(dec) * np.cos(ra)
    y = distance * np.cos(dec) * np.sin(ra)
    z = distance * np.sin(dec)
    return x, y, z

# Function to create a circular orbit path in 3D space
def create_orbit(radius, num_points=100):
    theta = np.linspace(0, 2 * np.pi, num_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
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
        'Neptune': 30
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
        'Neptune': 1.25
    }

    # Define colors for each planet
    planet_colors = {
        'Sun': (253, 184, 19),
        'Mercury': (183, 184, 185),
        'Venus': (165,124,27),
        'Earth': (107,147,214),
        'Mars': (193,68,14),
        'Jupiter': (216,202,157),
        'Saturn': (226,191,125),
        'Uranus': "lightblue",
        'Neptune': "darkblue"
    }

    # Create the Sun and planets as spheres
    for planet, position in positions.items():
        if planet == "Sun":
            sphere = pv.Sphere(radius=0.2, phi_resolution=30, theta_resolution=30)  # Larger radius for the Sun
            plotter.add_mesh(sphere.translate(position), color=planet_colors[planet], label=planet)
        else:
            sphere = pv.Sphere(radius=planet_sizes[planet], phi_resolution=20, theta_resolution=20)
            plotter.add_mesh(sphere.translate(position), color=planet_colors[planet], label=planet)

    # Add orbits for each planet
    for planet, radius in orbit_radii.items():
        orbit_points = create_orbit(radius)
        plotter.add_lines(orbit_points, color="blue")  # Draw the orbit as a blue line

    # Set plot view and labels
    plotter.add_axes()

    # Reset the camera to focus on the objects in the scene
    plotter.reset_camera()

    # Show the plot
    plotter.show()

date = "2024/10/05"

positions = compute_planet_positions(date)
visualize_planet_positions_and_orbits(positions)
