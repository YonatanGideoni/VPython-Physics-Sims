from visual import *
import xlwt

# CONSTANTS #
GRAPHS_ENABLED = false
real_dt = 0.03
DT = 1E-3 * real_dt
G = vector(0, -9.81, 0)

# STARTING TERMS #
t = 0

book = xlwt.Workbook('Data sheet')
sheet1 = book.add_sheet('Data')


# CLASSES #
class Energy:
    def __init__(self, potential=0, kinetic=0):
        self.total = potential + kinetic
        self.potential = potential
        self.kinetic = kinetic


class SpringPendulum:
    def __init__(self, equilibrium_length=0.2, start_pos=vector(0, 0, 0), end_pos=vector(0, -0.3, 0), mass=0.25,
                 spring_constant=30, trail_retain=5000, radius=0.1):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=radius, color=color.green)
        self.spring_constant = spring_constant
        self.mass = mass
        self.weight_pos = end_pos
        self.pos = self.weight_pos
        self.energy = Energy()
        self.gravity_enabled = true
        self.acceleration = vector(0, 0, 0)
        self.velocity = vector(0, 0, 0)
        self.equilibrium_length = equilibrium_length
        self.weight = cylinder(pos=end_pos, axis=vector(0, -radius, 0), radius=radius,
                               color=color.red,
                               make_trail=true, retain=trail_retain)

    def kinematics(self, dt=DT):  # Euler integration
        self.acceleration = vector(0, 0, 0)
        if self.gravity_enabled:
            self.acceleration += self.mass * G

        self.acceleration += -self.spring_constant * (
                mag(self.weight_pos) - self.equilibrium_length) * self.weight_pos / mag(self.weight_pos)
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt

    def update_pos(self):
        self.weight_pos = self.pos
        self.spring.axis = self.weight_pos - self.spring.pos
        self.weight.pos = self.weight_pos


# ANIMATION

test_spring = SpringPendulum(radius=0.05, end_pos=vector(0, -0.09, 0.04), mass=0.2, spring_constant=35,
                             equilibrium_length=0.17)
print('x y z t')
while true:
    t += DT

    if t % real_dt < DT:  # so it works with the slight floating point precision errors
        print(test_spring.pos.x, test_spring.pos.y, test_spring.pos.z, t)

    rate(1000)

    test_spring.kinematics()
    test_spring.update_pos()