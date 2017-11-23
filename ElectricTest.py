GlowScript 2.6 VPython


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
    def __init__(self, position, Radius=0.001):
        ElectricCharge.__init__(self,Radius, 1E-10, position)
        self.obj.color = color.white
        self.obj.make_trail = True
        
        self.initNullParams()
        
# list of charged objects, for easier calculations with kinematics and stuff
chargeList = [ElectricCharge(0.5, 1, vector(-2, 0, 0)), ElectricCharge(0.5, -1, vector(2, 0, 0))]

####CONSTANTS#####
kCoulomb = 8.987551E+9
xRange = [-3,3]
yRange = [-3,3]

###FUNCTIONS####
def kinematics(chargeList, obj, dt=0):
    force = vector(0, 0, 0)
    for chargeObj in chargeList:
        r = obj.obj.pos - chargeObj.obj.pos
        
        if mag(r) == 0: #in case for some reason objects intersect
            r = vector(0.01,0.01,0.01)
            
            
        force += kCoulomb * obj.charge * chargeObj.charge / mag(r) ** 2 * hat(r)  # coulomb's law
        
    obj.a = force/obj.m
    
    if dt is not 0:
        obj.v += obj.a*dt
        obj.obj.pos += obj.v*dt
    else:
        obj.v += obj.a*0.1  #default dt=0.1 if not defined
        obj.obj.pos += obj.v*0.1
        

def inRange(obj):
    if obj.obj.pos.x > xRange[0] and obj.obj.pos.x < xRange[1] and obj.obj.pos.y > yRange[0] and obj.obj.pos.y < yRange[1]:
        return True
    return False

def setCharge(ev):
    tracker = TestCharge(scene.mouse.pos) #creates a tracking charge at the mous position
    dt = 0.0001
    t = 0
    
    while inRange(tracker) and t < 1:
        kinematics(chargeList, tracker, dt)
        t += dt
        
scene.bind("mouseup", setCharge) #actually makes it do the thing

tracker = TestCharge(vector(0,1,0)) #creates a tracking charge at the mous position
dt = 0.00001
t = 0

while inRange(tracker) and t<1:
    kinematics(chargeList, tracker, dt)
    t += dt
