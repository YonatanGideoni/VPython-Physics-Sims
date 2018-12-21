import random
from visual import *
from visual.graph import *
import xlwt


# FUNCTIONS #
def change_vector_length(old_vector, new_length):
    return new_length * old_vector / old_vector.mag


# CONSTANTS #
real_dt = 0.03
DT = 1E-2 * real_dt
G = vector(0, -9.81, 0)
end_time = 1500
rod_length = 0.17

# STARTING TERMS #
t = 0
col_y = 0
start_pos = vector(-0.0453, -0.418, 0.0506)
starting_velocity = change_vector_length(vector(-0.04, -0.26, 0.01), start_pos.mag / (start_pos.mag + rod_length))


# CLASSES #
class ExcelSheet:
    class DataObject:
        def __init__(self, x, y, data):
            self.x = x
            self.y = y
            self.data = data

    def __init__(self, sheet_name='Data'):
        self.book = xlwt.Workbook(encoding="utf-8")
        self.sheets = []
        self.sheets.append(self.book.add_sheet(sheet_name))

    def write_to_sheet(self, data, sheet=0):
        for data_obj in data:
            self.sheets[sheet].write(data_obj.y, data_obj.x, data_obj.data)

    @staticmethod
    def create_data_objects(lists):
        _ret_list = []
        for _list in lists:
            _ret_list.append(ExcelSheet.DataObject(_list[0], _list[1], _list[2]))
        return _ret_list

    def save_file(self, file_name='Data sheet'):
        self.book.save(file_name + '.csv')


class Energy:
    def __init__(self, potential=0, kinetic=0):
        self.total = potential + kinetic
        self.potential = potential
        self.kinetic = kinetic


class SpringPendulum:

    def __init__(self, equilibrium_length=0.2, start_pos=vector(0, 0, 0), end_pos=vector(0, -0.3, 0), mass=0.25,
                 spring_constant=30., trail_retain=10000, radius=0.1, starting_velocity=vector(0, 0, 0),
                 random_force=True):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=radius, color=color.green)
        self.spring_constant = spring_constant
        self.mass = mass
        self.weight_pos = end_pos
        self.pos = self.weight_pos
        self.energy = Energy()
        self.gravity_enabled = true
        self.acceleration = vector(0, 0, 0)
        self.velocity = starting_velocity
        self.equilibrium_length = equilibrium_length
        self.graphs = {}
        self.random_action = random_force
        self.force = vector(0, 0, 0)
        self.weight = cylinder(pos=end_pos, axis=vector(0, -radius, 0), radius=radius,
                               color=color.red,
                               make_trail=true, retain=trail_retain)

    def random_force(self):
        if self.random_action:
            return vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)) * 5E-3
        return vector(0, 0, 0)

    def kinematics(self, dt=DT):  # Euler integration
        self.force = self.random_force()
        if self.gravity_enabled:
            self.force += self.mass * G

        self.force += -self.spring_constant * (
                mag(self.weight_pos) - self.equilibrium_length) * self.weight_pos / mag(self.weight_pos)
        self.acceleration = self.force / self.mass
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt

    def update_pos(self):
        self.weight_pos = self.pos
        self.spring.axis = self.weight_pos - self.spring.pos
        self.weight.pos = self.weight_pos

    def add_energy_graphs(self, total=False, potential=False, kinetic=False):
        if total:
            gdisplay(x=800, y=0, width=450, height=450, xtitle='time', ytitle='Total Energy')
            self.graphs['total energy'] = gcurve(color=color.green)

        if potential:
            gdisplay(x=800, y=0, width=450, height=450, xtitle='time', ytitle='Potential Energy')
            self.graphs['potential energy'] = gcurve(color=color.cyan)

        if kinetic:
            gdisplay(x=800, y=0, width=450, height=450, xtitle='time', ytitle='Kinetic Energy')
            self.graphs['kinetic energy'] = gcurve(color=color.magenta)

    def add_xyz_graphs(self, xy=False, xz=False, yz=False):
        if xy:
            gdisplay(x=800, y=0, width=450, height=450, xtitle='x', ytitle='y')
            self.graphs['xy'] = gcurve(color=color.red)

        if xz:
            gdisplay(x=800, y=0, width=450, height=450, xtitle='x', ytitle='z')
            self.graphs['xz'] = gcurve(color=color.yellow)

    def __calculate_energy(self):
        self.energy.potential = self.mass * G.mag * self.pos.y + \
                                0.5 * self.spring_constant * (self.weight_pos.mag - self.equilibrium_length) ** 2
        self.energy.kinetic = 0.5 * self.mass * self.velocity.mag2
        self.energy.total = self.energy.kinetic + self.energy.potential

    def update_graph(self, t=t, graph_name='total energy'):
        if 'energy' in graph_name:
            self.__calculate_energy()
            self.graphs[graph_name].plot(pos=(t,
                                              {'total energy': self.energy.total,
                                               'potential energy': self.energy.potential,
                                               'kinetic energy': self.energy.kinetic}[graph_name]))
        elif graph_name == 'xy':
            self.graphs['xy'].plot(pos=(self.pos.x, self.pos.y))
        elif graph_name == 'xz':
            self.graphs['xz'].plot(pos=(self.pos.x, self.pos.z))


# ANIMATION

test_spring = SpringPendulum(radius=0.05,
                             end_pos=change_vector_length(start_pos, start_pos.mag - 0.177),
                             mass=0.2622, spring_constant=35.77,
                             equilibrium_length=0.177, starting_velocity=starting_velocity, random_force=True)
test_spring.add_energy_graphs(total=True, potential=True, kinetic=True)
test_spring.add_xyz_graphs(xz=True)

# Defining the Excel data file.
data_sheet = ExcelSheet('Data')
headers = ExcelSheet.create_data_objects(
    [[0, 0, 'x'], [1, 0, 'y'], [2, 0, 'z'], [3, 0, 't']])
experiment_constants = ExcelSheet.create_data_objects([[5, 0, 'mass'], [5, 1, test_spring.mass],
                                                       [6, 0, 'spring constant'], [6, 1, test_spring.spring_constant],
                                                       [7, 0, 'equilibrium length'],
                                                       [7, 1, test_spring.equilibrium_length]])
data_sheet.write_to_sheet(headers)
data_sheet.write_to_sheet(experiment_constants)

while t <= end_time + DT:
    if t % real_dt < DT:  # so it works with the slight floating point precision errors
        col_y += 1
        print_vector = change_vector_length(test_spring.pos, test_spring.pos.mag + rod_length)
        data_list = ExcelSheet.create_data_objects(
            [[0, col_y, print_vector.x], [1, col_y, print_vector.y], [2, col_y, print_vector.z],
             [3, col_y, round(t, 2)]])
        data_sheet.write_to_sheet(data_list)
    rate(1000)

    t += DT
    test_spring.update_graph(t, 'total energy')
    test_spring.update_graph(t, 'potential energy')
    test_spring.update_graph(t, 'kinetic energy')
    test_spring.update_graph(graph_name='xz')
    test_spring.kinematics()
    test_spring.update_pos()

data_sheet.save_file()
