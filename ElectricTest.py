GlowScript 2.6 VPython


class PhysicsObject:  # main class for all physical objects
    def __init__(self, mass, velocity, acceleration, obj):
        self.v = velocity
        self.m = mass
        self.a = acceleration
        self.obj = obj()


class ElectricCharge(PhysicsObject):
    def __init__(self, Radius, charge, position):
        self.obj = sphere(pos=position, radius=Radius)
        self.charge = charge

        if self.charge < 0:
            self.obj.color = color.blue
        else:
            self.obj.color = color.red


# list of charged objects, for easier calculations with kinematics and stuff
chargeList = [electricCharge(0.5, 1, vector(-2, 0, 0)), electricCharge(0.5, -1, vector(2, 0, 0))]

####CONSTANTS #####
kCoulomb = 8.987551E+9


def kinematics(chargeList, obj):
    Force = vector(0, 0, 0)
    for chargeObj in chargelist:
        r = obj.pos - chargeObj.pos
        if mag(r) == 0:

        Force += kCoulomb * obj.charge * chargeObj.charge / mag(r) ** 2 * hat(r)  # coulomb's law