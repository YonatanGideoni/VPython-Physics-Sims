GlowScript 2.6 VPython


scene.width = scene.height = 800

###OBJECT CLASSES###
class PhysicsObject:  # main class for all physical objects
    def __init__(self, mass, velocity, acceleration, obj):
        self.v = velocity
        self.m = mass
        self.a = acceleration
        self.obj = obj(make_trail=False) #has to be initialized to be activated later
        
    def initNullParams(self):
        self.v = vector(0,0,0)
        self.a = vector(0,0,0)
        self.m = 1

class ElectricCharge(PhysicsObject):
    def __init__(self, Radius, charge, position):
        self.obj = sphere(pos=position, radius=Radius, make_trail=False)
        self.charge = charge

        if self.charge < 0:
            self.obj.color = color.blue
        else:
            self.obj.color = color.red

class TestCharge(ElectricCharge):   
    def __init__(self, position, Radius=0.00001):
        ElectricCharge.__init__(self,Radius, 1E-10, position)
        self.obj.color = color.white
        self.obj.make_trail = True
        
        self.initNullParams()
        
# list of charged objects, for easier calculations with kinematics and stuff
chargeList = [ElectricCharge(0.5, 1, vector(-2, 0, 0)), ElectricCharge(0.5, 1, vector(2, 0, 0)), ElectricCharge(0.5, -1, vector(0, -2, 0)),ElectricCharge(0.5, -1, vector(0, 2, 0))]

####CONSTANTS#####
kCoulomb = 8.987551E+9
xRange = [-5,5]
yRange = [-5,5]
zRange = [-5,5]
dt = 0.2


###FUNCTIONS####
def fieldKinematics(chargeList, obj, dt=0):
    force = vector(0, 0, 0)
    for chargeObj in chargeList:
        r = obj.obj.pos - chargeObj.obj.pos
        
        if mag(r) < chargeObj.obj.radius: #in case for some reason objects intersect
            return False
        
        force += kCoulomb * obj.charge * chargeObj.charge / mag(r) ** 2 * hat(r)  # coulomb's law
    
    obj.a = force/obj.m
    
    if dt is not 0:
        obj.v = obj.a*dt
        obj.obj.pos += obj.v*dt
    else:
        obj.v = obj.a*0.2  #default dt=0.1 if not defined
        obj.obj.pos += obj.v*0.2
    
    if mag(obj.v) < 0.0001:
        return False
        
    return True
        
def kinematics(chargeList, obj, dt=0):
    force = vector(0, 0, 0)
    for chargeObj in chargeList:
        r = obj.obj.pos - chargeObj.obj.pos
        
        if mag(r) < chargeObj.obj.radius: #in case for some reason objects intersect
            return False
              
        force += kCoulomb * obj.charge * chargeObj.charge / mag(r) ** 2 * hat(r)  # coulomb's law
        
    obj.a = force/obj.m
        
    if dt is not 0:
        obj.v += obj.a*dt
        obj.obj.pos += obj.v*dt
    else:
        obj.v += obj.a*0.005  #default dt=0.1 if not defined
        obj.obj.pos += obj.v*0.005
    
    if mag(obj.v) < 0.0005:
        return False
        
    return True

def inRange(obj):   #checkes if obj is inside allowed range
    if obj.obj.pos.x > xRange[0] and obj.obj.pos.x < xRange[1] and obj.obj.pos.y > yRange[0] and obj.obj.pos.y < yRange[1] and obj.obj.pos.z > zRange[0] and obj.obj.pos.z < zRange[1]:
        return True
    return False

def forceInEdgeOfRange(baseVect, spanningVect, mul=1): #forces vector to be inside allowed range
    squeezedVect = baseVect + spanningVect*mul
    
    while squeezedVect.x > xRange[0] and squeezedVect.x < xRange[1] and squeezedVect.y > yRange[0] and squeezedVect.y < yRange[1] and squeezedVect.z > zRange[0] and squeezedVect.z < zRange[1]:
        mul *= 1.05
        squeezedVect = baseVect + spanningVect*mul
    
    return baseVect + spanningVect*mul/1.05
    

def setCharge(position):
    global dt
    tracker = TestCharge(position) #creates a charge at the mous position
    t = 0
    
    tracker.obj.trail_color = color.green
    
    while inRange(tracker) and kinematics(chargeList, tracker):
        rate(1000)
        t += dt
        
def drawField(position):
    global dt
    tracker = TestCharge(position)
    t = 0
    
    while inRange(tracker) and fieldKinematics(chargeList, tracker, dt):
        rate(1000)
        t += dt

for particle in chargeList:
    angleXY = 0
    while angleXY < 2*pi:    #draws the fields around the positive charge
        angleXZ = 0
        while angleXZ < 2*pi:
            if particle.charge > 0:       
                    chargePos = particle.obj.pos + particle.obj.radius*1.05*vector(cos(angleXY)*cos(angleXZ),sin(angleXY),sin(angleXZ))            
            else:
                chargePos = forceInEdgeOfRange(particle.obj.pos, vector(cos(angleXY)*cos(angleXZ),sin(angleXY),sin(angleXZ)))
            drawField(chargePos)
            angleXZ += pi/4
        angleXY += pi/4
    

while True:
    ev = scene.waitfor('click keydown')
    if ev.event == 'click':
         setCharge(scene.mouse.pos)
