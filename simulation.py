import math
import random
import time

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def compute_solar_efficiency(panel_normal, sun_direction):
    # Normalize both vectors
    def normalize(v):
        length = np.linalg.norm(v)
        return v / length if length != 0 else v

    panel_normal = normalize(np.array(panel_normal))
    sun_direction = normalize(np.array(sun_direction))

    # Dot product (clipped between 0 and 1)
    efficiency = max(0.0, np.dot(panel_normal, sun_direction))
    return efficiency


def get_sun_direction(altitude_deg, azimuth_deg):
    alt_rad = math.radians(altitude_deg)
    az_rad = math.radians(azimuth_deg)

    x = math.cos(alt_rad) * math.sin(az_rad)
    y = math.sin(alt_rad)
    z = math.cos(alt_rad) * math.cos(az_rad)

    return [x, y, z]


battery_level = [0.0 for _ in range(5)]
battery_capacity = 100.0  # Max storage (for simplicity)
consumption_rate = 0.02  # Power consumed per frame

# Camera variables
camera_yaw = 0.0  # Horizontal rotation (left/right)
camera_pitch = 20.0  # Vertical rotation (up/down), start slightly above horizon
mouse_left_down = False
mouse_x = 0
mouse_y = 0
camera_distance = 50  # Distance of camera from origin


def mouse(button, state, x, y):
    global mouse_left_down, mouse_x, mouse_y, camera_distance

    mods = glutGetModifiers()
    shift_pressed = (mods & GLUT_ACTIVE_SHIFT) != 0

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_left_down = True
            mouse_x = x
            mouse_y = y
        elif state == GLUT_UP:
            mouse_left_down = False

    elif button in (3, 4) and state == GLUT_DOWN:  # Mouse wheel scroll
        if shift_pressed:
            zoom_speed = 1.0
            if button == 3:  # Scroll up
                camera_distance -= zoom_speed
            elif button == 4:  # Scroll down
                camera_distance += zoom_speed

            camera_distance = max(5.0, min(camera_distance, 100))
            glutPostRedisplay()


def mouse_motion(x, y):
    global mouse_left_down, mouse_x, mouse_y, camera_yaw, camera_pitch
    if mouse_left_down:
        dx = x - mouse_x
        dy = y - mouse_y

        # Sensitivity factor for rotation speed
        sensitivity = 0.3

        camera_yaw -= dx * sensitivity
        camera_pitch += dy * sensitivity

        # Clamp camera_pitch to avoid flipping (e.g. -89 to 89 degrees)
        camera_pitch = max(-89, min(89, int(camera_pitch)))

        mouse_x = x
        mouse_y = y

        glutPostRedisplay()


# Sun variables
sun_pos = [0, 0, 0]
sun_pulse = 0  # For animation
sun_pos_x = -10
latitude = 40.0  # Example latitude (in degrees)
declination = -23.5  # Starting point, can be calculated based on date
time_of_day = 12  # 12:00 PM, for example (you can adjust this based on the current time)

# Convert angles to radians
latitude = math.radians(latitude)
declination = math.radians(declination)

# Hour angle: how many degrees the sun is from noon
hour_angle = 15 * (time_of_day - 12)  # 15 degrees per hour difference from noon

# Sun Altitude (in degrees) - Angle above the horizon
altitude = math.asin(math.sin(latitude) * math.sin(declination) + math.cos(latitude) * math.cos(declination) * math.cos(
    math.radians(hour_angle)))

# Sun Azimuth (in degrees) - Direction of the sun on the horizontal plane
if altitude > 0:  # Sun above horizon
    azimuth = math.atan2(-math.cos(declination) * math.sin(math.radians(hour_angle)),
                         math.sin(altitude))
else:
    azimuth = 0  # If the sun is below the horizon, azimuth is irrelevant.

# Convert to degrees
sun_altitude = math.degrees(altitude)  # Sun's tilt angle above the horizon
sun_azimuth = math.degrees(azimuth)  # Sun's direction along the horizon

# Panel variables
tilt_angle = 0
azimuth_angle = 0
panel_pos_x = -5
battery_enabled = True

p_in = 0
p_out = 0
ipo = 0
efficiency = 0


def get_panel_normal(tilt_deg, azimuth_deg):
    tilt_rad = math.radians(tilt_deg)
    azimuth_rad = math.radians(azimuth_deg)

    nx = math.sin(tilt_rad) * math.sin(azimuth_rad)
    ny = math.cos(tilt_rad)
    nz = math.sin(tilt_rad) * math.cos(azimuth_rad)

    return [nx, ny, nz]


panel_pos = get_panel_normal(30, 45)

# def angle_between(v1, v2):
#     cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
#     angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))  # Clip for numerical stability
#     return np.degrees(angle) if np.degrees else angle


# angle_deg = angle_between(sun_pos, panel_norm)

# print(angle_deg)

sun_dir = get_sun_direction(sun_altitude, sun_azimuth)


# Function to initialize GLUT
def init_glut():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Setup display mode
    glutInitWindowSize(1280, 960)  # Set window size
    glutCreateWindow("Solar Panel Simulation".encode('ascii'))  # Create the window
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    # glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
    light_pos = [10.0, 10.0, 10.0, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glShadeModel(GL_SMOOTH)
    glutMouseFunc(mouse)
    glutMotionFunc(mouse_motion)
    glClearColor(1.0, 0.5, 0.0, 1.0)


def update(value):
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # roughly 60 FPS


def menu_func(value):
    global tilt_angle, azimuth_angle, sun_pos_x, sun_altitude, sun_azimuth, panel_pos_x

    if 180 <= value < 361:  # Panel X (-90 to 90)
        tilt_angle = (value - 180) - 90
    elif 540 <= value < 721:  # Panel Y (-90 to 90)
        azimuth_angle = (value - 540) - 90
    elif 900 <= value < 921:  # Panel Position X (-10 to 10)
        panel_pos_x = (value - 900) - 10
    elif 1000 <= value < 1021:  # Sun Position X (-10 to 10)
        sun_pos_x = (value - 1000) - 10
    elif 945 <= value < 1021:  # Sun Altitude (-45 to 45)
        sun_altitude = value - 945
    elif 1000 <= value < 1061:  # Sun Azimuth (0 to 90)
        sun_azimuth = value - 1000

    glutPostRedisplay()  # Force redraw after updating
    return 0  # callback error without it


def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 1, 100)
    glMatrixMode(GL_MODELVIEW)


def draw_sun():
    global sun_altitude, sun_azimuth, sun_pulse, sun_pos_x

    glPushMatrix()
    sun_pos_world = np.array(sun_dir) * 20 + np.array([sun_pos_x, 8.0, -10.0])
    glTranslatef(*sun_pos_world)
    glRotatef(sun_azimuth, 0, 1, 0)  # Rotate the sun for azimuth
    glRotatef(sun_altitude, 1, 0, 0)  # Apply altitude angle

    # Update pulsing radius using a sine wave
    pulse_radius = 2.0 + 0.05 * math.sin(time.time() * 2)

    # Lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    light_pos = [0.0, 0.0, 0.0, 1.0]
    light_diffuse = [1.0, 0.5, 0.0, 1.0]
    light_specular = [1.0, 0.5, 0.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Emission for glowing effect
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0])

    # Draw pulsing sun sphere
    glutSolidSphere(pulse_radius, 50, 50)

    glDisable(GL_LIGHTING)

    # Glow layers
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    for i in range(3):
        glow_alpha = 0.15 / (i + 1)
        glow_radius = pulse_radius + 0.3 + i * 0.2
        glColor4f(1.0, 1.0, 0.0, glow_alpha)
        glutSolidSphere(glow_radius, 50, 50)
    glDisable(GL_BLEND)

    # Sun rays
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_LINES)
    for i in range(0, 360, 15):
        angle_rad = math.radians(i)
        x = math.cos(angle_rad) * (pulse_radius + 1.5)
        y = math.sin(angle_rad) * (pulse_radius + 1.5)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(x, y, 0.0)
    glEnd()

    glPopMatrix()


def draw_field():
    glPushMatrix()
    glDisable(GL_LIGHTING)  # Disable lighting for flat color

    glColor3f(0.2, 0.6, 0.2)  # Grass green
    glBegin(GL_QUADS)
    glVertex3f(-50.0, -2.6, -50.0)
    glVertex3f(50.0, -2.6, -50.0)
    glVertex3f(50.0, -2.6, 50.0)
    glVertex3f(-50.0, -2.6, 50.0)
    glEnd()

    glEnable(GL_LIGHTING)  # Re-enable lighting
    glPopMatrix()


def draw_house():
    def draw_window_frame(x, y, z, width, height):
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x, y, z)
        glVertex3f(x + width, y, z)
        glVertex3f(x + width, y + height, z)
        glVertex3f(x, y + height, z)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(x, y + height / 2, z)
        glVertex3f(x + width, y + height / 2, z)
        glVertex3f(x + width / 2, y, z)
        glVertex3f(x + width / 2, y + height, z)
        glEnd()

    def draw_window_glass(x, y, z, width, height, alpha=0.4):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.6, 0.8, 1.0, alpha)

        glBegin(GL_QUADS)
        glVertex3f(x, y, z)
        glVertex3f(x + width, y, z)
        glVertex3f(x + width, y + height, z)
        glVertex3f(x, y + height, z)
        glEnd()
        glDisable(GL_BLEND)

    def draw_window_reflection(x, y, z, width, height):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 1.0, 0.2)
        glBegin(GL_TRIANGLES)
        glVertex3f(x, y + height, z)
        glVertex3f(x + width * 0.4, y + height, z)
        glVertex3f(x + width, y + height * 0.4, z)
        glEnd()
        glDisable(GL_BLEND)

    glPushMatrix()
    glTranslatef(25.0, -2.6, -5.0)
    glScalef(4.0, 4.0, 4.0)

    # House base
    glColor3f(0.6, 0.3, 0.23)
    glBegin(GL_QUADS)
    # Front
    glVertex3f(-2, 0, 2)
    glVertex3f(2, 0, 2)
    glVertex3f(2, 2, 2)
    glVertex3f(-2, 2, 2)
    # Back
    glVertex3f(-2, 0, -2)
    glVertex3f(2, 0, -2)
    glVertex3f(2, 2, -2)
    glVertex3f(-2, 2, -2)
    # Left
    glVertex3f(-2, 0, -2)
    glVertex3f(-2, 0, 2)
    glVertex3f(-2, 2, 2)
    glVertex3f(-2, 2, -2)
    # Right
    glVertex3f(2, 0, -2)
    glVertex3f(2, 0, 2)
    glVertex3f(2, 2, 2)
    glVertex3f(2, 2, -2)
    # Bottom
    glVertex3f(-2, 0, -2)
    glVertex3f(2, 0, -2)
    glVertex3f(2, 0, 2)
    glVertex3f(-2, 0, 2)
    glEnd()

    # Roof
    glColor3f(0.3, 0.15, 0.1)
    glBegin(GL_TRIANGLES)
    # Front
    glVertex3f(-2, 2, 2)
    glVertex3f(2, 2, 2)
    glVertex3f(0, 3.5, 2)
    # Back
    glVertex3f(-2, 2, -2)
    glVertex3f(2, 2, -2)
    glVertex3f(0, 3.5, -2)
    glEnd()

    glBegin(GL_QUADS)
    # Left roof slope
    glVertex3f(-2, 2, -2)
    glVertex3f(-2, 2, 2)
    glVertex3f(0, 3.5, 2)
    glVertex3f(0, 3.5, -2)
    # Right roof slope
    glVertex3f(2, 2, -2)
    glVertex3f(2, 2, 2)
    glVertex3f(0, 3.5, 2)
    glVertex3f(0, 3.5, -2)
    glEnd()

    # Door (on front face)
    glColor3f(0.4, 0.2, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-0.3, 0.0, 2.01)
    glVertex3f(0.5, 0.0, 2.01)
    glVertex3f(0.5, 1, 2.01)
    glVertex3f(-0.3, 1, 2.01)
    glEnd()

    # Add window to the front
    draw_window_glass(-1.5, 1.2, 2.01, 1, 0.6)
    draw_window_frame(-1.5, 1.2, 2.02, 1, 0.6)
    draw_window_reflection(-1.5, 1.2, 2.03, 1, 0.6)

    draw_window_glass(0.8, 1.2, 2.01, 1, 0.6)
    draw_window_frame(0.8, 1.2, 2.02, 1, 0.6)
    draw_window_reflection(0.8, 1.2, 2.03, 1, 0.6)

    glPopMatrix()


def draw_cube(w, h, d):
    glPushMatrix()
    glScalef(w, h, d)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_outline(w, h, d):
    glPushMatrix()
    glScalef(w, h, d)
    glColor3f(0, 0, 0)
    glutWireCube(1.001)
    glPopMatrix()


def draw_battery_bank(battery_levels, max_capacity):
    def draw_battery_3d(bat_level, capacity):
        width = 2
        depth = 3
        height_max = 3.0
        num_cells = 6  # number of visual cells

        charge_ratio = bat_level / capacity
        height = max(0.01, charge_ratio * height_max)

        # --- Draw battery outer container ---
        glPushMatrix()
        glColor3f(0.3, 0.3, 0.1)  # metallic grey
        draw_cube(width, height_max, depth)
        draw_outline(width, height_max, depth)
        glPopMatrix()

        # --- Cell fill properties ---
        cell_height = height_max / num_cells
        inner_width = width - 0.2
        inner_depth = depth - 0.2

        for i in range(num_cells):
            # Y position of current cell center
            cell_center_y = -height_max / 2 + (i + 0.5) * cell_height

            # Determine how full this cell is
            cell_fill_ratio = (charge_ratio * num_cells) - i
            cell_fill_ratio = max(0.0, min(cell_fill_ratio, 1.0))

            if cell_fill_ratio <= 0.0:
                continue  # skip empty cells

            # Set color based on overall charge level

            if charge_ratio > 0.6:
                glColor3f(0.0, 0.8, 0.0)  # green
            elif charge_ratio > 0.3:
                glColor3f(0.9, 0.9, 0.0)  # yellow
            else:
                glColor3f(0.9, 0.0, 0.0)  # red

            # --- Draw filled part of the cell ---
            glPushMatrix()
            glTranslatef(0, cell_center_y - (1 - cell_fill_ratio) * cell_height / 2, 0.2)
            draw_cube(inner_width, cell_height * cell_fill_ratio - 0.05, inner_depth)
            glPopMatrix()

    start_x = 2.0  # starting X position
    spacing = 2.5  # space between batteries

    glPushMatrix()
    glTranslatef(15.0, -1.0, -13.0)  # Position the whole bank
    glRotatef(-90, 0.0, 1.0, 0.0)  # Rotate around Y axis

    for i, level in enumerate(battery_levels):
        bat_x = start_x + i * spacing
        glPushMatrix()
        glTranslatef(bat_x, 0.0, 0.0)
        draw_battery_3d(level, max_capacity)
        glPopMatrix()
    glPopMatrix()


def draw_grasses():
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glColor3f(0.1, 0.5, 0.1)

    random.seed(45)  # For consistent results; remove if you want different every run

    for i in range(-45, 50, 2):
        for j in range(-45, 50, 2):
            if random.random() < 5:  # Sparse distribution
                x = i + random.uniform(-0.5, 0.5)
                z = j + random.uniform(-0.5, 0.5)
                height = random.uniform(0.3, 1.5)
                angle = random.uniform(-10, 10)

                glPushMatrix()
                glTranslatef(x, -2.6, z)
                glRotatef(angle, 0, 0, 1)
                glBegin(GL_TRIANGLES)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(-0.05, height, 0.0)
                glVertex3f(0.05, height, 0.0)
                glEnd()
                glPopMatrix()

    glEnable(GL_LIGHTING)
    glPopMatrix()


def draw_cloud(x, y, z, scale=1.0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Soft blueish white with semi-transparency
    colors = [
        [0.8, 0.85, 1.0, 0.5],  # light pastel blue
        [0.75, 0.8, 0.95, 0.45],  # slightly darker blue
        [0.7, 0.78, 0.9, 0.45],  # more saturated blue
        [0.75, 0.82, 0.92, 0.4],
        [0.78, 0.83, 0.97, 0.4],
        [0.72, 0.8, 0.95, 0.35],
    ]

    positions = [
        (0.0, 0.0, 0.0),
        (0.8, 0.2, 0.0),
        (-0.8, 0.2, 0.0),
        (0.3, 0.5, 0.3),
        (-0.3, 0.5, -0.3),
        (0.0, 0.3, -0.5),
    ]

    for pos, col in zip(positions, colors):
        glPushMatrix()
        glTranslatef(*pos)
        glColor4f(*col)
        glutSolidSphere(1.0, 40, 40)
        glPopMatrix()

    glDisable(GL_BLEND)
    glPopMatrix()


def draw_sky_with_clouds():

    # Draw clouds at different positions and sizes
    draw_cloud(5, 20, -5, 1.5)
    draw_cloud(-7, 19, -12, 1.2)
    draw_cloud(0, 17.5, -18, 1.7)
    draw_cloud(8, 18.5, -20, 1.0)
    draw_cloud(-10, 21, -7, 1.3)
    draw_cloud(12, 22, -10, 1.4)
    draw_cloud(-3, 18, -15, 1.6)
    draw_cloud(4, 21, -13, 1.1)
    draw_cloud(-6, 20.5, -5, 1.2)
    draw_cloud(10, 19, -18, 1.3)

    draw_cloud(-15, 21, -25, 1.4)
    draw_cloud(-10, 22, -20, 1.3)
    draw_cloud(-5, 19.5, -18, 1.5)
    draw_cloud(0, 20, -15, 1.6)
    draw_cloud(5, 21, -12, 1.4)
    draw_cloud(10, 19.8, -10, 1.3)
    draw_cloud(15, 20.5, -8, 1.5)

    draw_cloud(-12, 18, -22, 1.2)
    draw_cloud(-7, 19, -17, 1.3)
    draw_cloud(-2, 21, -14, 1.7)
    draw_cloud(3, 18.5, -11, 1.1)
    draw_cloud(8, 19.5, -9, 1.4)
    draw_cloud(13, 20, -6, 1.2)
    draw_cloud(18, 19.7, -4, 1.3)
    draw_cloud(22, 20.3, -2, 1.5)


def draw_horizon():
    glPushMatrix()
    glDisable(GL_LIGHTING)

    glBegin(GL_QUADS)

    # Bottom of the sky (deep orange)
    glColor3f(1.0, 0.4, 0.0)
    glVertex3f(-50.0, -2.6, -49.0)
    glVertex3f(50.0, -2.6, -49.0)

    # Top of the sky (light orange / peach)
    glColor3f(1.0, 0.7, 0.3)
    glVertex3f(50.0, 30.0, -49.0)
    glVertex3f(-50.0, 30.0, -49.0)

    glEnd()

    glEnable(GL_LIGHTING)
    glPopMatrix()


def draw_solar_panel():
    def draw_inverter():
        inverter_x = panel_pos_x  # same X as panel
        inverter_y = -0.8  # a bit below panel center
        inverter_z = 0.2  # behind the pole

        glPushMatrix()
        glTranslatef(inverter_x, inverter_y, inverter_z)

        # Main inverter body - light gray box
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glScalef(1.0, 0.50, 0.20)
        glutSolidCube(1.0)
        glPopMatrix()

        # Front display panel - dark rectangle
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0.05, 0.085)  # slightly in front
        glScalef(0.6, 0.3, 0.04)
        glutSolidCube(1.0)
        glPopMatrix()

        # Vents - thin horizontal lines on front below display
        glColor3f(0.3, 0.3, 0.3)
        for i in range(-2, 3):
            glPushMatrix()
            glTranslatef(0, -0.05 + i * 0.03, 0.086)
            glScalef(0.70, 0.02, 0.04)
            glutSolidCube(1.0)
            glPopMatrix()

        # Indicator lights - small colored spheres
        light_positions = [(-0.15, 0.15, 0.086), (0.0, 0.15, 0.086), (0.15, 0.15, 0.086)]
        light_colors = [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]  # red, yellow, green
        for pos, color in zip(light_positions, light_colors):
            glColor3f(*color)
            glPushMatrix()
            glTranslatef(*pos)
            glutSolidSphere(0.03, 12, 12)
            glPopMatrix()

        glPopMatrix()

    global tilt_angle, azimuth_angle, panel_pos_x

    glPushMatrix()

    # --- Stand base ---
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(panel_pos_x, -2.5, 0.0)
    glScalef(2.0, 0.2, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Vertical pole ---
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(panel_pos_x, -1.25, 0.0)
    glScalef(0.2, 2.5, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    draw_inverter()

    # --- Panel rotation around Y-axis (tracking) ---
    glTranslatef(panel_pos_x, 0.0, 0.0)
    glRotatef(azimuth_angle, 0.0, 1.0, 0.0)

    # --- Panel tilt ---
    glRotatef(tilt_angle, 1.0, 0.0, 0.0)

    # --- Panel base ---
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glScalef(6.0, 0.1, 4.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Solar cell surface ---
    glPushMatrix()
    glTranslatef(0.0, 0.06, 0.0)
    glColor3f(0.0, 0.3, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(-3.0, 0.0, 2.0)
    glVertex3f(3.0, 0.0, 2.0)
    glVertex3f(3.0, 0.0, -2.0)
    glVertex3f(-3.0, 0.0, -2.0)
    glEnd()

    # --- Grid lines ---
    glColor3f(0.8, 0.8, 0.8)
    glLineWidth(1)
    glBegin(GL_LINES)
    for x in range(-2, 3):
        glVertex3f(x, 0.01, 2.0)
        glVertex3f(x, 0.01, -2.0)
    for z in range(-1, 2):
        glVertex3f(-3.0, 0.01, z)
        glVertex3f(3.0, 0.01, z)
    glEnd()

    glPopMatrix()  # End of solar panel
    glPopMatrix()  # Reset overall


def draw_cable(start, end, thickness=0.05):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    if length == 0:
        return  # no cable if same point

    ax = 57.2957795 * math.acos(dz / length)  # angle in degrees
    if dz < 0:
        ax = -ax
    # Cross product for rotation axis
    rx = -dy * dz
    ry = dx * dz
    rz = 0

    glPushMatrix()
    glTranslatef(*start)

    # If cable is vertical, no rotation needed
    if dz < length:
        glRotatef(ax, rx, ry, rz)

    # Draw cylinder along z-axis
    quad = gluNewQuadric()
    glColor3f(0.1, 0.1, 0.1)  # cable color: dark gray
    gluCylinder(quad, thickness, thickness, length, 8, 1)
    gluDeleteQuadric(quad)

    glPopMatrix()


def draw_cables_to_batteries(battery_levels, max_capacity):
    # Inverter position (matches your draw_inverter inside draw_solar_panel)
    inverter_pos = (panel_pos_x, -0.8, 0.2)

    # Battery bank base and orientation (same as in draw_battery_bank)
    base_pos = (15.0, -1.0, -13.0)
    spacing = 2.5
    start_x = 2.0

    glPushMatrix()
    glTranslatef(*base_pos)
    glRotatef(-90, 0, 1, 0)

    # For each battery, compute battery center position and draw cable
    for i in range(len(battery_levels)):
        bat_x = start_x + i * spacing
        # Batteries are at y=0, z=0 in local battery bank coords
        battery_pos = (bat_x, 0.0, 0.0)
        draw_cable(inverter_pos, battery_pos)

    glPopMatrix()


def draw_text(x, y, text, font=globals()["GLUT_BITMAP_HELVETICA_18"]):
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


# Display function for GLUT
def display():
    global battery_level, battery_capacity, efficiency, p_in, p_out, ipo, sun_dir, sun_pos_x

    # Calculate the sun's position based only on sun parameters (altitude and azimuth)
    sun_world_pos = np.array(sun_dir) * 20 + np.array([sun_pos_x, 8.0, -10.0])  # Keep sun_pos_x separate
    panel_world_pos = np.array([panel_pos_x, 0.0, 0.0])

    # Sun direction relative to the panel
    sun_dir = sun_world_pos - panel_world_pos
    sun_dir = sun_dir / np.linalg.norm(sun_dir)

    # Get panel normal based on its tilt and azimuth
    panel_norm = get_panel_normal(tilt_angle, azimuth_angle)

    # Calculate the efficiency of the solar panel
    efficiency = compute_solar_efficiency(panel_norm, sun_dir)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Dynamic solar power calculations
    I = 1000  # Solar irradiance in W/m²
    A = 2  # Panel area in m²
    eta = 0.18  # Panel efficiency

    # Power incident on the panel surface
    p_in = I * A * efficiency  # Only effective irradiance based on angle
    p_out = eta * p_in  # Power output from panel
    ipo = p_out / (I * A) if I * A != 0 else 0  # Instantaneous power output ratio

    power_generated = efficiency * 0.1  # Shared generation input for now

    if battery_enabled:
        for i in range(len(battery_level)):
            # Random solar efficiency per battery (simulate partial shading or dirt)
            individual_efficiency = efficiency * random.uniform(0.4, 1.1)  # way more variance

            # Random fluctuation in sunlight power per battery
            fluctuation = random.uniform(0.05, 0.15)

            # Random chance to *not* receive sunlight (like a passing cloud)
            if random.random() < 0.1:  # 10% chance of total shadow
                individual_efficiency = 0.0

            power_generated = individual_efficiency * fluctuation

            # Random consumption (maybe a connected device turns on)
            random_consumption = random.uniform(0.005, 0.02)

            # Random sudden drain (simulate battery stress or faulty circuit)
            if random.random() < 0.05:  # 5% chance of extra power loss
                random_consumption += random.uniform(0.01, 0.05)

            # Apply to battery
            battery_level[i] += power_generated
            battery_level[i] -= random_consumption
            battery_level[i] = max(0.0, min(battery_level[i], battery_capacity))

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Calculate camera position based on spherical coordinates
    cam_x = camera_distance * math.cos(math.radians(camera_pitch)) * math.sin(math.radians(camera_yaw))
    cam_y = camera_distance * math.sin(math.radians(camera_pitch))
    cam_z = camera_distance * math.cos(math.radians(camera_pitch)) * math.cos(math.radians(camera_yaw))

    gluLookAt(cam_x, cam_y, cam_z,  # default values 0, 15, 50,
              0, 0, 0,  # Look at point
              0, 1, 0)  # Up vector

    # Draw everything in the scene
    glEnable(GL_LIGHTING)
    draw_horizon()
    draw_field()
    draw_grasses()
    draw_sun()
    draw_solar_panel()
    draw_battery_bank(battery_level, battery_capacity)
    draw_cables_to_batteries(battery_level, battery_capacity)
    draw_house()
    draw_sky_with_clouds()


    # Display power and efficiency stats
    glColor3f(1, 1, 1)
    draw_text(950, 940, f"Sun Altitude: {sun_altitude:.1f}°")
    draw_text(950, 920, f"Sun Azimuth: {sun_azimuth:.1f}°")
    draw_text(950, 900, f"Panel Tilt: {tilt_angle:.1f}°")
    draw_text(950, 880, f"Panel Azimuth: {azimuth_angle:.1f}°")
    draw_text(950, 860, f"Efficiency: {efficiency * 100:.1f}%")
    draw_text(950, 840, f"Incident Power: {p_in:.2f} W")
    draw_text(950, 820, f"Output Power: {p_out:.2f} W")
    average_battery = sum(battery_level) / 5
    draw_text(950, 800, f"Battery Level: {average_battery:.1f}%")
    glutSwapBuffers()  # Swap buffers to display the rendered scene


# Function to start simulation (initialize GLUT and run the main loop)
def sim_start():
    init_glut()  # Initialize GLUT, create window

    # Set up GLUT callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(16, update, 0)

    # Set up perspective view
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)  # Move the camera back so we can see everything

    # Register the display callback
    glutDisplayFunc(display)
    glutTimerFunc(0, update, 0)  # Start animation

    def create_angle_submenu(base_id, label):
        """Creates a submenu for angles from -90 to +90."""
        submenu_id = glutCreateMenu(menu_func)
        for angle in range(-90, 91, 15):  # Allows from -90 to +90 in steps of 15°
            menu_value = base_id + (angle + 90)  # Offset to make it positive
            glutAddMenuEntry(f"{label} {angle}°", menu_value)
        return submenu_id

    def create_pos_submenu(base_id, label):
        """Creates a submenu for positions from -10 to +10."""
        submenu_id = glutCreateMenu(menu_func)
        for pos in range(-10, 11):  # Positions from -10 to +10
            menu_value = base_id + (pos + 10)
            glutAddMenuEntry(f"{label} {pos}", menu_value)
        return submenu_id

    # Submenus for Solar Panel
    panel_x_menu = create_angle_submenu(180, "Tilt X")  # Panel Tilt X
    panel_y_menu = create_angle_submenu(540, "Tilt Y")  # Panel Tilt Y
    panel_pos_x_menu = create_pos_submenu(900, "Panel Position X")  # Panel Position X

    # Submenus for Sun (Position and Angle)
    sun_pos_x_menu = create_pos_submenu(1000, "Sun Position X")  # Sun Position X
    sun_altitude_menu = glutCreateMenu(menu_func)
    for i in range(-45, 46, 5):  # Altitude from -45° to 45°
        glutAddMenuEntry(f"Altitude {i}°", i + 945)  # (i + 900 + 45)

    sun_azimuth_menu = glutCreateMenu(menu_func)
    for i in range(0, 91, 5):  # Azimuth from 0° to 90°
        glutAddMenuEntry(f"Azimuth {i}°", i + 1000)

    # Create top-level submenus for the solar panel and sun
    panel_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("Panel Tilt X", panel_x_menu)
    glutAddSubMenu("Panel Tilt Y", panel_y_menu)

    sun_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("Sun Position X", sun_pos_x_menu)
    glutAddSubMenu("Sun Altitude", sun_altitude_menu)  # New Altitude submenu
    glutAddSubMenu("Sun Azimuth", sun_azimuth_menu)  # New Azimuth submenu

    # Main menu
    main_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("Solar Panel", panel_menu)
    glutAddSubMenu("Panel Position X", panel_pos_x_menu)
    glutAddSubMenu("Sun", sun_menu)

    # Attach the main menu to the right mouse button
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    # Start the GLUT main loop
    glutMainLoop()


if __name__ == "__main__":
    sim_start()
