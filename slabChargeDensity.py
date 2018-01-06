from visual import *
from visual.graph import *

# Program forked off of ElectricTest for base functionality
# Test program to find out slab's charge density and distribution.
#
#
#

scene.width = scene.height = 800

gdisplay(x=750, y=0, width=450, height=450, xtitle='t', ytitle='Ek')
energyK = gcurve(color=color.cyan)


###OBJECT CLASSES###
class PhysicsObject:  # main class for all physical objects
    def __init__(self, mass, velocity, acceleration, obj):
        self.v = velocity
        self.m = mass
        self.a = acceleration
        self.obj = obj(make_trail=False)  # has to be initialized to be activated later

    def initNullParams(self):
        self.v = vector(0, 0, 0)
        self.a = vector(0, 0, 0)
        self.m = 1
        self.nextPos = self.obj.pos


class ElectricCharge(PhysicsObject):  # main class for electric charges
    def __init__(self, Radius, charge, position):
        self.obj = sphere(pos=position, radius=Radius, make_trail=False)
        self.charge = charge
        self.initNullParams()

        if self.charge < 0:
            self.obj.color = color.blue
        else:
            self.obj.color = color.red


class ChargedSlab(ElectricCharge):
    def __init__(self, center, Size, charge):
        self.obj = box(opacity=0.1, pos=center, size=Size)
        self.charge = charge
        self.xBorders = [center.x - self.obj.size.x / 2, center.x + self.obj.size.x / 2]
        self.yBorders = [center.y - self.obj.size.y / 2, center.y + self.obj.size.y / 2]
        self.zBorders = [center.z - self.obj.size.z / 2, center.z + self.obj.size.z / 2]
        self.volume = (self.xBorders[1] - self.xBorders[0]) * (self.yBorders[1] - self.yBorders[0]) * (
            self.zBorders[1] - self.zBorders[0])
        self.slabParticles = []

    def populateCharges(self, numOfCharges):
        chargeNum = 0

        xPos = random.sample(numOfCharges)  # randomize position of charges. Non repeating to prevent intersection
        yPos = random.sample(numOfCharges)
        zPos = random.sample(numOfCharges)

        while chargeNum < numOfCharges:
            chargeSign = random.choice([-1, 1, 1, 1])  # 1 if chargeNum % 2 == 0 else -1  # equally distribute positive and negative charges

            chargePos = vector(xPos[chargeNum] * (self.xBorders[1] - self.xBorders[0]) * random.choice([-1, 1]),
                               yPos[chargeNum] * (self.yBorders[1] - self.yBorders[0]) * random.choice([-1, 1]),
                               zPos[chargeNum] * (self.zBorders[1] - self.zBorders[0]) * random.choice(
                                   [-1, 1])) * 0.5 + self.obj.pos

            self.slabParticles.append(
                ElectricCharge(2 * self.volume / numOfCharges, chargeSign * 1E-7 * self.charge / self.volume,
                               chargePos))

            chargeNum += 1


#####STARTING PARAMETERS######
t = 0

####CONSTANTS#####
kCoulomb = 8.987551E+9
xMaxRange = [-5, 5]
yMaxRange = [-5, 5]
zMaxRange = [-5, 5]
dt = 0.003
springConst = 1E-20


###FUNCTIONS####
def kinematics(chargeList, obj, xRange, yRange, zRange, dt=0):
    force = vector(0, 0, 0)
    for chargeObj in chargeList:
        r = obj.obj.pos - chargeObj.obj.pos
        r_mag = mag(r)
        r_hat = r / r_mag

        if r_mag == 0:
            continue

        if r_mag < 2 * obj.obj.radius:
            force += springConst * r_hat * (r_mag - 2 * obj.obj.radius)  # hooke's law

        force += chargeObj.charge / r_mag ** 2 * r_hat  # coulomb's law

    force *= kCoulomb * obj.charge
    obj.a = force / obj.m

    if dt is not 0:
        obj.v += obj.a * dt
        detectCollision(obj, xRange, yRange, zRange)
        obj.nextPos = obj.obj.pos + obj.v * dt
    else:
        obj.v += obj.a * 0.005  # default dt=0.1 if not defined
        detectCollision(obj, xRange, yRange, zRange)
        obj.nextPos = obj.obj.pos + obj.v * 0.005

    if mag(obj.v) < 0.0005:
        return False

    if mag(obj.v) > 100:
        obj.v /= 10

    return True


def updatePos(objList):
    for obj in objList:
        obj.obj.pos = obj.nextPos


def detectCollision(obj, xRange, yRange, zRange):   # elastic collision with the face's
    if obj.obj.pos.x < xRange[0] or obj.obj.pos.x > xRange[1]:
        obj.v *= 0.9
        obj.v.x *= -1
        if obj.obj.pos.x < xRange[0]:   # stops out of bounds errors
            obj.obj.pos.x = xRange[0]
        else:
            obj.obj.pos.x = xRange[1]
    if obj.obj.pos.y < yRange[0] or obj.obj.pos.y > yRange[1]:
        obj.v *= 0.9
        obj.v.y *= -1
        if obj.obj.pos.y < yRange[0]:
            obj.obj.pos.y = yRange[0]
        else:
            obj.obj.pos.y = yRange[1]
    if obj.obj.pos.z < zRange[0] or obj.obj.pos.z > zRange[1]:
        obj.v *= 0.9
        obj.v.z *= -1
        if obj.obj.pos.z < zRange[0]:
            obj.obj.pos.z = zRange[0]
        else:
            obj.obj.pos.z = zRange[1]


def inRange(obj, xRange, yRange, zRange):  # checks if obj is inside allowed range
    if xRange[1] > obj.obj.pos.x > xRange[0] and yRange[1] > obj.obj.pos.y > yRange[0] and zRange[1] > obj.obj.pos.y > \
            zRange[0]:
        return True
    return False


slab = ChargedSlab(vector(0, 0, 0), vector(1, 1, 1), 100)
slab.populateCharges(100)

while t < 10:
    rate(10000000)
    t += dt

    if 1.5 > t > 0.3:
        dt = 0.0005
    elif t > 1.5:
        dt = 0.0001

    Ek = 0
    for particle in slab.slabParticles:
        kinematics(slab.slabParticles, particle, slab.xBorders, slab.yBorders, slab.zBorders, dt)
        updatePos(slab.slabParticles)
        Ek += 0.5 * particle.m * mag(particle.v) ** 2

    energyK.plot(pos=(t, Ek))
