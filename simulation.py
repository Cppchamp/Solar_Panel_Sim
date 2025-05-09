from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import time


# Global variables
sun_pulse = 0  # For animation
panel_angle_x = 0
panel_angle_y = 0
sun_angle_x = 0
sun_angle_y = 0

# Function to initialize GLUT
def init_glut():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Setup display mode
    glutInitWindowSize(1280, 960)  # Set window size
    glutCreateWindow("Solar Panel Simulation".encode('ascii'))  # Create the window
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)

def update(value):
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # roughly 60 FPS

def menu_func(value):
    global panel_angle_x, panel_angle_y, sun_angle_x, sun_angle_y

    if 180 <= value < 360:  # Panel X
        panel_angle_x = value - 180
    elif 540 <= value < 720:  # Panel Y
        panel_angle_y = value - 540
    elif 900 <= value < 1080:  # Sun X
        sun_angle_x = value - 900
    elif 1260 <= value < 1440:  # Sun Y
        sun_angle_y = value - 1260

    glutPostRedisplay()

def draw_sun():
    global sun_angle_x, sun_angle_y, sun_pulse

    glPushMatrix()

    # Position and rotate the sun
    glTranslatef(0.0, 8.0, -10.0)
    glRotatef(sun_angle_x, 1.0, 0.0, 0.0)
    glRotatef(sun_angle_y, 0.0, 1.0, 0.0)
    # Update pulsing radius using a sine wave
    pulse_radius = 2.0 + 0.05 * math.sin(time.time() * 2)  # pulsates between 1.8 and 2.2

    # Lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    light_pos = [0.0, 0.0, 0.0, 1.0]
    light_diffuse = [1.0, 1.0, 0.0, 1.0]
    light_specular = [1.0, 1.0, 0.0, 1.0]
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


def draw_solar_panel():
    global panel_angle_x, panel_angle_y

    glPushMatrix()

    # --- Stand base ---
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0.0, -2.5, 0.0)
    glScalef(2.0, 0.2, 2.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Vertical pole ---
    glColor3f(0.4, 0.4, 0.4)
    glPushMatrix()
    glTranslatef(0.0, -1.25, 0.0)
    glScalef(0.2, 2.5, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()

    # --- Panel rotation around Y-axis (tracking) ---
    glTranslatef(0.0, 0.0, 0.0)
    glRotatef(panel_angle_y, 0.0, 1.0, 0.0)

    # --- Panel tilt ---
    glRotatef(panel_angle_x, 1.0, 0.0, 0.0)

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

# Display function for GLUT
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen
    draw_sun()  # Call the function to draw the sun
    draw_solar_panel()  # Call the function to draw the solar panel
    glutSwapBuffers()  # Swap buffers to display the rendered scene

# Function to start simulation (initialize GLUT and run the main loop)
def sim_start():
    init_glut()  # Initialize GLUT, create window

    # Set up perspective view
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)  # Move the camera back so we can see everything

    # Register the display callback
    glutDisplayFunc(display)
    glutTimerFunc(0, update, 0)  # Start animation

    def create_angle_submenu(base_id, label):
        submenu_id = glutCreateMenu(menu_func)
        for angle in range(0, 181, 15):
            glutAddMenuEntry(f"{label} {angle}°", base_id + angle)
        return submenu_id

    # Submenus for Solar Panel
    panel_x_menu = create_angle_submenu(180, "X")
    panel_y_menu = create_angle_submenu(540, "Y")

    # Submenus for Sun
    sun_x_menu = create_angle_submenu(900, "X")
    sun_y_menu = create_angle_submenu(1260, "Y")

    # Create top-level submenus
    panel_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("X Axis", panel_x_menu)
    glutAddSubMenu("Y Axis", panel_y_menu)

    sun_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("X Axis", sun_x_menu)
    glutAddSubMenu("Y Axis", sun_y_menu)

    # Main menu
    main_menu = glutCreateMenu(menu_func)
    glutAddSubMenu("Solar Panel Angle", panel_menu)
    glutAddSubMenu("Sun Angle", sun_menu)

    glutAttachMenu(GLUT_RIGHT_BUTTON)

    # Start the GLUT main loop
    glutMainLoop()

if __name__ == "__main__":
    sim_start()
