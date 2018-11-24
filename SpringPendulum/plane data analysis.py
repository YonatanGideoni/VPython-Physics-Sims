# This code is to help analyze large amounts of experimental data obtained from testing a spring pendulum system.
# Specifically, during the spring pendulum's motion it changes between several main planes of motion in
# a continuous manner. Here, I analyze whether the angle between consecutive planes and the time it takes for
# the pendulum to change its plane of motion are constant.


import openpyxl as pyxl
import numpy as np
from scipy import stats

