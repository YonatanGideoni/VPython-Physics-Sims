from visual import *
from visual.graph import *
import time

# Program forked off of ElectricTest for base functionality
# Test program to find out slab's charge density and distribution.

scene.width = scene.height = 800

######GRAPHS############
gdisplay(x=800, y=0, width=450, height=450, xtitle='t', ytitle='Ek')
energyK = gcurve(color=color.cyan)

gdisplay(x=800, y=0, width=450, height=450, xtitle='t', ytitle='Ep')
energyP = gcurve(color=color.magenta)

gdisplay(x=800, y=0, width=450, height=450, xtitle='t', ytitle='Etot')
energyTot = gcurve(color=color.green)


###OBJECT CLASSES###
class PhysicsObject:  # main class for all physical objects
    def __init__(self, mass, velocity, acceleration, obj):
        self.v = velocity
        self.m = mass
        self.a = acceleration
        self.storedEnergy = 0
        self.obj = obj(make_trail=False)  # has to be initialized to be activated later

    def initNullParams(self):
        self.v = vector(0, 0, 0)
        self.a = vector(0, 0, 0)
        self.m = 1
        self.storedEnergy = 0
        self.nextPos = self.obj.pos
        self.pos = self.nextPos


class ElectricCharge(PhysicsObject):  # main class for electric charges
    def __init__(self, Radius, charge, position):
        self.obj = sphere(pos=position, radius=Radius, make_trail=False)
        self.charge = charge
        self.initNullParams()

        if self.charge < 0:
            self.obj.color = color.blue
        else:
            self.obj.color = color.red


class TestCharge(ElectricCharge):  # class for drawing field and potential lines
    def __init__(self, position, Radius=0.000000000001):
        ElectricCharge.__init__(self, Radius, 1E-30, position)
        self.obj.color = color.white
        self.obj.make_trail = True

        self.initNullParams()

        self.m = 9.109E-31


class ChargedSlab(ElectricCharge):
    def __init__(self, center, Size, charge):
        self.obj = box(opacity=0.1, pos=center, size=Size)
        self.charge = charge
        self.xBorders = [center.x - self.obj.size.x / 2, center.x + self.obj.size.x / 2]
        self.yBorders = [center.y - self.obj.size.y / 2, center.y + self.obj.size.y / 2]
        self.zBorders = [center.z - self.obj.size.z / 2, center.z + self.obj.size.z / 2]
        self.volume = (self.xBorders[1] - self.xBorders[0]) * (self.yBorders[1] - self.yBorders[0]) * (
            self.zBorders[1] - self.zBorders[0])
        self.diagonalLength = sqrt(
            (self.xBorders[1] - self.xBorders[0]) ** 2 + (self.yBorders[1] - self.yBorders[0]) ** 2 + (
                self.zBorders[1] - self.zBorders[0]) ** 2)
        self.slabParticles = []
        self.perimeter = 4 * (
            self.xBorders[1] - self.xBorders[0] + self.yBorders[1] - self.yBorders[0] + self.zBorders[1] -
            self.zBorders[0])

    def populateCharges(self, numOfCharges):
        chargeNum = 0

        xPos = random.sample(numOfCharges)  # randomize position of charges. Non repeating to prevent intersection
        yPos = random.sample(numOfCharges)
        zPos = random.sample(numOfCharges)

        while chargeNum < numOfCharges:
            # various distributions of positive and negative charges
            # chargeSign = random.choice([-1, 1, 1, 1])  # 75% positive 25% negative
            # chargeSign = random.choice([-1, 1, 1, 1, 1, 1, 1, 1, 1, 1])  # 90% positive 10% negative
            # chargeSign = 1 if chargeNum % 2 == 0 else -1  # equally distribute positive and negative charges
            chargeSign = 1  # all positive

            chargePos = vector(xPos[chargeNum] * (self.xBorders[1] - self.xBorders[0]) * random.choice([-1, 1]),
                               yPos[chargeNum] * (self.yBorders[1] - self.yBorders[0]) * random.choice([-1, 1]),
                               zPos[chargeNum] * (self.zBorders[1] - self.zBorders[0]) * random.choice(
                                   [-1, 1])) * 0.5 + self.obj.pos

            self.slabParticles.append(
                ElectricCharge(0.3 * self.perimeter / numOfCharges, self.charge * chargeSign * 1.602E-19,
                               chargePos))
            self.slabParticles[-1].m = 9.109E-31
            chargeNum += 1

    def simulate(self, minEnergy):
        t = 0
        Ek = 1E-1

        lastUpdate = time.time()
        while t < 1000:
            rate(10000)

            if time.time() - lastUpdate > 3:
                updateRealPos(self.slabParticles)
                lastUpdate = time.time()

            if t < 2.5E-2:
                dt = max(2E-5, min((2E+9) * sqrt(Ek), 2E-4))
            elif 2.5E-2 < t < 1.5E-1:
                dt = max(1E-5, min((2E+9) * sqrt(Ek), 1E-4))
            else:
                dt = max(7E-6, min((2E+9) * sqrt(Ek), 1E-5))

            t += dt

            Ek = 0
            for particle in self.slabParticles:
                kinematics(self.slabParticles, particle, self.xBorders, self.yBorders, self.zBorders,
                           self.detectCollision,
                           dt)

                updatePos(self.slabParticles)

                Ek += 0.5 * particle.m * mag(particle.v) ** 2

            Ep = potentialEnergy(self.slabParticles)

            if Ek < minEnergy and t > 0.001:
                return

            energyP.plot(pos=(t, Ep))
            energyK.plot(pos=(t, Ek))
            energyTot.plot(pos=(t, Ek + Ep))

    def detectCollision(self, obj):
        if obj.pos.x < self.xBorders[0] or obj.pos.x > self.xBorders[1]:
            obj.v *= 0.7
            obj.v.x *= -1
            if obj.pos.x < self.xBorders[0]:  # stops out of bounds errors
                obj.pos.x = self.xBorders[0]
            else:
                obj.pos.x = self.xBorders[1]
        if obj.pos.y < self.yBorders[0] or obj.pos.y > self.yBorders[1]:
            obj.v *= 0.7
            obj.v.y *= -1
            if obj.pos.y < self.yBorders[0]:
                obj.pos.y = self.yBorders[0]
            else:
                obj.pos.y = self.yBorders[1]
        if obj.pos.z < self.zBorders[0] or obj.pos.z > self.zBorders[1]:
            obj.v *= 0.7
            obj.v.z *= -1
            if obj.pos.z < self.zBorders[0]:
                obj.pos.z = self.zBorders[0]
            else:
                obj.pos.z = self.zBorders[1]


####CONSTANTS#####
kCoulomb = 8.987551E+9
xMaxRange = [-5, 5]
yMaxRange = [-5, 5]
zMaxRange = [-5, 5]


###FUNCTIONS####
def kinematics(chargeList, obj, xRange, yRange, zRange, collisionFunc, dt=0):
    force = vector(0, 0, 0)
    for chargeObj in chargeList:
        if chargeObj.charge == 0:
            continue

        r = obj.pos - chargeObj.pos
        r_mag = mag(r)
        if r_mag == 0:
            continue

        r_hat = r / r_mag

        force += chargeObj.charge / r_mag ** 2 * r_hat  # coulomb's law

    force *= kCoulomb * obj.charge
    obj.a = force / obj.m

    if dt is not 0:
        obj.v += obj.a * dt
        collisionFunc(obj)
        obj.nextPos = obj.pos + obj.v * dt
    else:
        obj.v += obj.a * 5E-2  # default dt if not defined
        collisionFunc(obj)
        obj.nextPos = obj.pos + obj.v * 5E-2


def fieldKinematics(chargeList, obj, dt=0):
    force = vector(0, 0, 0)

    for chargeObj in chargeList:
        r = obj.obj.pos - chargeObj.obj.pos

        if mag(r) < chargeObj.obj.radius:  # in case for some reason objects intersect
            return False

        force += chargeObj.charge / mag(r) ** 2 * r / mag(r)  # coulomb's law

    force *= kCoulomb * obj.charge
    obj.a = force / obj.m

    if dt is not 0:
        obj.v = obj.a * dt
        obj.obj.pos += obj.v * dt
    else:
        obj.v = obj.a * 200  # default dt if not defined
        obj.obj.pos += obj.v * 200

    if mag(obj.v) < 1E-30:
        return False

    return True


def updatePos(objList):
    for obj in objList:
        obj.pos = obj.nextPos


def updateRealPos(objList):
    for obj in objList:
        obj.obj.pos = obj.nextPos


def detectCollision(obj, xRange, yRange, zRange):  # elastic collision with the face's
    if obj.pos.x < xRange[0] or obj.pos.x > xRange[1]:
        obj.v *= 0.7
        obj.v.x *= -1
        if obj.pos.x < xRange[0]:  # stops out of bounds errors
            obj.pos.x = xRange[0]
        else:
            obj.pos.x = xRange[1]
    if obj.pos.y < yRange[0] or obj.pos.y > yRange[1]:
        obj.v *= 0.7
        obj.v.y *= -1
        if obj.pos.y < yRange[0]:
            obj.pos.y = yRange[0]
        else:
            obj.pos.y = yRange[1]
    if obj.pos.z < zRange[0] or obj.pos.z > zRange[1]:
        obj.v *= 0.7
        obj.v.z *= -1
        if obj.pos.z < zRange[0]:
            obj.pos.z = zRange[0]
        else:
            obj.pos.z = zRange[1]


def inRange(obj, xRange, yRange, zRange):  # checks if obj is inside allowed range
    if xRange[1] > obj.pos.x > xRange[0] and yRange[1] > obj.pos.y > yRange[0] and zRange[1] > obj.pos.z > zRange[0]:
        return True
    return False


def potentialEnergy(chargeList):
    Ep = 0

    i = 0
    while i < len(chargeList):
        j = i + 1

        Ep += chargeList[i].storedEnergy

        if chargeList[i].charge == 0:  # skip neutral particles
            i += 1
            continue

        while j < len(chargeList):
            r_mag = mag(chargeList[i].pos - chargeList[j].pos)

            Ep += kCoulomb * chargeList[i].charge * chargeList[j].charge / r_mag

            j += 1
        i += 1
    return Ep


def setDt(objList):
    dt = 1000000000
    i = 0
    j = 0

    while i < len(objList):
        if objList[i].charge == 0:
            i += 1
            continue

        j = i + 1
        while j < len(objList):
            if objList[i].charge == 0:
                j += 1
                continue

            if mag(objList[i].obj.pos - objList[j].obj.pos) < dt and objList[i].charge * objList[j].charge < 0:
                dt = mag(objList[i].obj.pos - objList[j].obj.pos)
            elif mag(objList[i].obj.pos - objList[j].obj.pos) < dt / 5:
                dt = 5 * mag(objList[i].obj.pos - objList[j].obj.pos)

            j += 1
        i += 1
    return dt


def mergeCharges(particle1, particle2):
    particle1.storedEnergy = kCoulomb * particle1.charge * particle2.charge / mag(particle1.pos - particle2.pos)

    particle1.charge += particle2.charge

    if particle1.charge > 0:
        particle1.obj.color = color.red
    elif particle1.charge < 0:
        particle1.obj.color = color.blue
    else:
        particle1.obj.color = color.gray(0.5)

    particle1.m += particle2.m
    particle1.obj.radius = (particle1.obj.radius ** 3 + particle2.obj.radius ** 3) ** 0.333333
    # calculating new radius based on sum of volume's
    particle1.v = sqrt(
        (particle1.m * mag(particle1.v) ** 2 + particle2.m * mag(particle2.v) ** 2) / (particle1.m + particle2.m)) * ((
                                                                                                                          particle1.m * particle1.v + particle2.m * particle2.v) / (
                                                                                                                          particle1.m + particle2.m)) / mag(
        (particle1.m * particle1.v + particle2.m * particle2.v) / (particle1.m + particle2.m))
    # conservation of momentum
    particle1.pos = (particle1.m * particle1.pos + particle2.m * particle2.pos) / (
        particle1.m + particle2.m)
    particle1.nextPos = (particle1.m * particle1.nextPos + particle2.m * particle2.nextPos) / (
        particle1.m + particle2.m)

    # weighted average


def findParticlesToMerge(chargeList):
    i = 0
    while i < len(chargeList):
        j = i + 1
        if chargeList[i].charge == 0:
            i += 1
            continue

        while j < len(chargeList):
            if chargeList[i].charge * chargeList[j].charge >= 0:
                j += 1
                continue

            if mag(chargeList[i].pos - chargeList[j].pos) < 0.008:
                mergeCharges(chargeList[i], chargeList[j])
                chargeList[j].obj.visible = false
                del chargeList[j]

            j += 1
        i += 1


def negativeChargesExist(chargeList):
    for particle in chargeList:
        if particle.charge < 0:
            return true
    return false


def drawFieldOnObj(slab, chargeList, dt):
    for particle in chargeList:
        if random.random() < 0.5:
            continue
        if abs(particle.obj.pos.x - slab.xBorders[0]) < 0.01:
            drawField(vector(- particle.obj.radius * 1.01, 0, 0) + particle.obj.pos, chargeList, dt)
        if abs(particle.obj.pos.x - slab.xBorders[1]) < 0.01:
            drawField(vector(particle.obj.radius * 1.01, 0, 0) + particle.obj.pos, chargeList, dt)
        if abs(particle.obj.pos.y - slab.yBorders[0]) < 0.01:
            drawField(vector(0, - particle.obj.radius * 1.01, 0) + particle.obj.pos, chargeList, dt)
        if abs(particle.obj.pos.y - slab.yBorders[1]) < 0.01:
            drawField(vector(0, particle.obj.radius * 1.01, 0) + particle.obj.pos, chargeList, dt)
        if abs(particle.obj.pos.z - slab.zBorders[0]) < 0.01:
            drawField(vector(0, 0, - particle.obj.radius * 1.01) + particle.obj.pos, chargeList, dt)
        if abs(particle.obj.pos.z - slab.zBorders[1]) < 0.01:
            drawField(vector(0, 0, particle.obj.radius * 1.01) + particle.obj.pos, chargeList, dt)


def drawField(position, chargeList, dt):
    tracker = TestCharge(position)  # creates a tracking charge at the mouse position

    while inRange(tracker, xMaxRange, yMaxRange, zMaxRange) and fieldKinematics(chargeList, tracker, dt):
        rate(1000)


def setCharge(position, chargeList, dt):
    tracker = TestCharge(position)  # creates a charge at the mous position

    tracker.obj.trail_object.color = color.green
    tracker.obj.trail_object.retain = 10

    tracker.v = vector(0.0005, 0, 0)

    while inRange(tracker, xMaxRange, yMaxRange, zMaxRange):
        rate(100000)
        kinematics(chargeList, tracker, xMaxRange, yMaxRange, zMaxRange, dt)
        updateRealPos([tracker])
        updatePos([tracker])


def placeCharges(chargeList, dt):
    while True:
        ev = scene.waitfor('click keydown')
        if ev.event == 'click':
            setCharge(scene.mouse.pos, chargeList, dt)


def twoSlabs():
    topSlab = ChargedSlab(vector(0, 2, 0), vector(5, 1, 5), 5)
    topSlab.populateCharges(100)

    bottomSlab = ChargedSlab(vector(0, -2, 0), vector(5, 1, 5), -5)
    bottomSlab.populateCharges(100)

    bottomSlab.simulate(5E-27)
    topSlab.simulate(5E-27)

    chargedParticles = topSlab.slabParticles + bottomSlab.slabParticles

    drawFieldOnObj(topSlab, chargedParticles, 3E+2)

    placeCharges(chargedParticles, 1E+1)


def boxSim():
    slab = ChargedSlab(vector(0, 0, 0), vector(1, 1, 1), 1)
    slab.populateCharges(100)

    slab.simulate(1E-27)


def runSim(input):
    if input == 'twoSlabs':
        twoSlabs()
    elif input == 'box':
        boxSim()


if __name__ == "__main__":
    runSim(raw_input())
