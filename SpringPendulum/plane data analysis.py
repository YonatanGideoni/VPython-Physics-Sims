# This code is to help analyze large amounts of experimental data obtained from testing a spring pendulum system.
# Specifically, during the spring pendulum's motion it changes between several main planes of motion in
# a continuous manner. Here, I analyze whether the angle between consecutive planes and the time it takes for
# the pendulum to change its plane of motion are constant.

# Things that the code needs to do, in order:
# 0. Create x(z) chart, add to results (optional)
# 1. Calculate "instability" data, AKA distance from origin for every point.
# 2. Find all local maximum instability points.
# 3. Find local maximums' local maximum points.
# 4. Use these points to identify time-ranges during which the pendulum is swinging in a certain plane.
# 5. Calculate average instability.
# 6. Use average instability to filter out close points (say, all points with under-average stability) as they
#    do not represent well what plane the pendulum is swinging in.
# 7. Get lists of points per plane.
# 8. Use SciPy linear regression to find slope and r^2 of plane.
# 9. Calculate angle of every plane.
# 10. Calculate change of angle between planes.
# 11. Print to results slope, r^2, plane angle, change of angle between planes, and transition time between planes.
# 12. Graph change of angle between planes and transition time, add to results.
# 13. Save excel file and hope that the physics works just as well as the code.

# IMPORTS
import openpyxl as pyxl
import numpy as np
from scipy import stats  # used only for linear regression, to estimate angle of plane.
from math import *

# CONSTANTS
dt = 0.03  # based on system settings


# OBJECTS
class PointData:
    def __init__(self, x, y, time=0):
        self.point = np.array([x, y])
        self.mag = np.linalg.norm(self.point)
        self.time = time

    def __str__(self):
        return 'time: ' + str(self.time) + ' x,y: ' + str(self.point) + ' mag: ' + str(self.mag)


# FUNCTIONS
def cell_to_variable(cell):
    return cell.value


cell_to_variable = np.vectorize(cell_to_variable)
# ANALYSIS

wb = pyxl.load_workbook('test_motion_data.xlsx')
results_sheet = wb.create_sheet('Results')
data_sheet = wb.get_sheet_by_name('Data')

x_col = np.array(cell_to_variable(data_sheet['B']))[1:].astype(np.float)
z_col = np.array(cell_to_variable(data_sheet['D']))[1:].astype(np.float)

temp_t = 0

xz_data = np.array(np.vectorize(PointData)(x_col[1:], z_col[1:]))

for data in xz_data:
    data.time = temp_t
    temp_t += dt

del temp_t
