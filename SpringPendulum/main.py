from visual import *

# CONSTANTS #
ZERO_VECTOR = vector(0, 0, 0)


class SpringPendulum:
    def __init__(self, start_pos=ZERO_VECTOR, end_pos=vector(0, -0.3, 0), mass=0.5, spring_constant=5):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=0.1, color=color.green)
        self.spring_constant = spring_constant
        self.mass = mass
        self.weight_pos = end_pos
        self.pos = self.weight_pos
        self.energy = object
        self.energy.total = 0
        self.energy.potential = 0
        self.energy.kinetic = 0
        self.gravity = false
        self.acceleration = ZERO_VECTOR
        self.velocity = ZERO_VECTOR
        self.weight = cylinder(pos=end_pos, axis=vector(0, (end_pos - start_pos).y / 5, 0), radius=0.1, color=color.red)


SpringPendulum()
