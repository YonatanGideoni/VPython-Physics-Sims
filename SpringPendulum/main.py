from visual import *

ZERO_VECTOR = vector(0, 0, 0)


class SpringPendulum:
    def __init__(self, start_pos=ZERO_VECTOR, end_pos=vector(0, 0.3, 0), mass=0.5, spring_constant=5):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=0.1)
        self.spring_constant = spring_constant
        self.mass = mass
        self.acceleration = ZERO_VECTOR
        self.velocity = ZERO_VECTOR
        # self.weight = cylinder(pos=end_pos, axis=(end_pos - start_pos).y / 5)


SpringPendulum()
