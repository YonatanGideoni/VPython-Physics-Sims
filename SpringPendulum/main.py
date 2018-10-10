from visual import *

# CONSTANTS #
ZERO_VECTOR = vector(0, 0, 0)
GRAPHS_ENABLED = false
DT = 1E-20
G = vector(0, -9.81, 0)

# STARTING TERMS #
t = 0


# CLASSES #
class Energy:
    def __init__(self, potential=0, kinetic=0):
        self.total = potential + kinetic
        self.potential = potential
        self.kinetic = kinetic


class SpringPendulum:
    def __init__(self, equilibrium_point=ZERO_VECTOR, start_pos=ZERO_VECTOR, end_pos=vector(0, -0.3, 0), mass=0.5,
                 spring_constant=5):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=0.1, color=color.green)
        self.spring_constant = spring_constant
        self.mass = mass
        self.weight_pos = end_pos
        self.pos = self.weight_pos
        self.energy = Energy()
        self.gravity_enabled = true
        self.acceleration = ZERO_VECTOR
        self.velocity = ZERO_VECTOR
        self.equilibrium_point = equilibrium_point
        self.weight = cylinder(pos=end_pos, axis=vector(0, (end_pos - start_pos).y / 5, 0), radius=0.1, color=color.red)

    def kinematics(self, dt=DT):  # Euler integration
        self.acceleration = ZERO_VECTOR
        if self.gravity_enabled:
            self.acceleration += self.mass * G

        self.acceleration += self.spring_constant * (self.weight_pos - self.equilibrium_point)
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt

    def update_pos(self):
        self.weight_pos = self.pos
        self.spring.axis = self.spring.pos - self.weight_pos
        self.weight.pos = self.weight_pos


# ANIMATION

test_spring = SpringPendulum()

while t < 5:
    t += DT

    rate(10)

    test_spring.kinematics()
    test_spring.update_pos()
