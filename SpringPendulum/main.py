from dataclasses import dataclass
from random import uniform
from vpython import *
import xlwt


# FUNCTIONS #
def change_vector_length(old_vector, new_length):
    return new_length * old_vector / old_vector.mag


# CONSTANTS #
real_dt = 0.03
DT = 1E-2 * real_dt
g = vector(0, -9.79234, 0)
end_time = 1000 * real_dt
button_from_hook_length = 0.17
rod_length = 0.14
rod_mass = 0.1135
weight_mass = 0.2622 - rod_mass
spring_mass = 0.0414
effective_mass = weight_mass + rod_mass + spring_mass / 3
k = 29.0237
rod_center_of_mass_from_hook = 0.125
big_weight_height = 0.0115
small_weight_height = 0.0085
weight_center_of_mass_from_hook = rod_length - (
        2. / 3 * weight_mass * big_weight_height / 2 +
        1. / 3 * weight_mass * (big_weight_height + small_weight_height / 2)) \
                                  / weight_mass
spring_weightless_length = 0.18
spring_equilibrium_length = spring_weightless_length + (effective_mass + spring_mass / 6) * g.mag / k
rod_weights_center_of_mass = (rod_mass * rod_center_of_mass_from_hook + weight_mass * weight_center_of_mass_from_hook) \
                             / (weight_mass + rod_mass)
center_of_mass_at_equilibrium = ((weight_mass + rod_mass) * (rod_weights_center_of_mass + spring_equilibrium_length) +
                                 spring_mass * spring_equilibrium_length / 2) \
                                / (rod_mass + weight_mass + spring_mass)

spring_length = lambda total_length: total_length - rod_length
center_of_mass = lambda spring_length: \
    ((weight_mass + rod_mass) * (rod_weights_center_of_mass + spring_length) + spring_mass * spring_length / 2) \
    / (rod_mass + weight_mass + spring_mass)

# STARTING TERMS #
t = 0
col_y = 0
start_pos = vector(0, -0.425, -0.003)
starting_velocity = vector(-0.02333, 0.33167, -0.105)
starting_velocity = change_vector_length(starting_velocity,
                                         starting_velocity.mag * center_of_mass(
                                             spring_length(start_pos.mag)) / start_pos.mag)
start_pos = change_vector_length(start_pos, start_pos.mag + (rod_weights_center_of_mass - button_from_hook_length))


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
        file_name += '.csv'
        self.book.save(file_name)
        print(f'Saved file to {file_name}')


@dataclass
class SpringPendulumEnergy:
    spring: float = 0
    gravity: float = 0
    kinetic: float = 0

    @property
    def total(self):
        return self.potential + self.kinetic

    @property
    def potential(self):
        return self.spring + self.gravity


@dataclass
class SpringPendulumPower:
    spring: float = 0
    gravity: float = 0


class SpringPendulum:
    def __init__(self, equilibrium_length=0.2, start_pos=vector(0, 0, 0), end_pos=vector(0, -0.3, 0),
                 effective_mass=0.25, spring_mass=0.05,
                 spring_constant=30., trail_retain=10000, radius=0.1, starting_velocity=vector(0, 0, 0),
                 random_force=True):
        self.spring = helix(pos=start_pos, axis=end_pos - start_pos, radius=radius, color=color.green)
        self.spring_constant = spring_constant
        self.effective_mass = effective_mass
        self.spring_mass = spring_mass
        self.weight_pos = end_pos
        self.pos = self.weight_pos

        self.energy = SpringPendulumEnergy()
        self.power = SpringPendulumPower()

        self.gravity_enabled = True
        self.random_action = random_force

        self.acceleration = vector(0, 0, 0)
        self.velocity = starting_velocity
        self.equilibrium_length = equilibrium_length
        self.graphs = {}
        self.force = vector(0, 0, 0)
        self.weight = cylinder(pos=end_pos, axis=vector(0, -radius, 0), radius=radius,
                               color=color.red,
                               make_trail=True, retain=trail_retain, trail_color=color.white)

        self.spring_energy_offset = None
        self.gravitational_energy_offset = None

    def random_force(self):
        if self.random_action:
            return vector(uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)) * 1E-3
        return vector(0, 0, 0)

    def kinematics(self, dt=DT):  # Euler integration
        gravity = (self.effective_mass + self.spring_mass / 6) * g if self.gravity_enabled else vector(0, 0, 0)

        spring_force = -self.spring_constant * \
                       (mag(self.weight_pos) - self.equilibrium_length) * self.weight_pos / mag(self.weight_pos)
        self.force = self.random_force() + gravity + spring_force
        self.acceleration = self.force / self.effective_mass
        self.velocity += self.acceleration * dt
        self.pos += self.velocity * dt

        # update power
        self.power.spring = spring_force.dot(self.velocity)
        self.power.gravity = gravity.dot(self.velocity)

    def update_pos(self):
        self.weight_pos = self.pos
        self.spring.axis = self.weight_pos - self.spring.pos
        self.weight.pos = self.weight_pos

    def update_all_graphs(self, t):
        for graph_name in self.graphs:
            self.update_graph(t, graph_name)

    def add_energy_graphs(self, total=False, potential=False, kinetic=False):
        if total:
            graph(title='Total Energy Over Time', xtitle='Time[s]', ytitle='Energy[J]')
            self.graphs['total energy'] = gcurve(color=color.green, label='Total Energy')

        if potential:
            graph(title='Potential Energy Over Time', xtitle='Time[s]', ytitle='Energy[J]')
            self.graphs['potential energy'] = gcurve(color=color.cyan, label='Potential Energy')
            graph(title='Potential Energies Over Time', xtitle='Time[s]', ytitle='Energy[J]')
            self.graphs['potential spring energy'] = gcurve(color=color.orange, label='Potential Spring Energy')
            self.graphs['potential gravitational energy'] = gcurve(color=color.magenta,
                                                                   label='Potential Gravitational Energy')

        if kinetic:
            graph(title='Kinetic Energy Over Time', xtitle='Time[s]', ytitle='Energy[J]')
            self.graphs['kinetic energy'] = gcurve(color=color.magenta, label='Kinetic Energy')

    def add_power_graph(self):
        graph(title='Power Supplied By Different Forces Over Time', xtitle='Time[s]', ytitle='Power[W]')
        self.graphs['spring power'] = gcurve(color=color.orange, label='Spring Power')
        self.graphs['gravitational power'] = gcurve(color=color.magenta, label='Gravitational Power')

    def add_xyz_graphs(self, xy=False, xz=False, yz=False):
        if xy:
            graph(title='y Over x', xtitle='x[m]', ytitle='y[m]')
            self.graphs['xy'] = gcurve(color=color.red)

        if xz:
            graph(title='x Over z', xtitle='x[m]', ytitle='z[m]')
            self.graphs['xz'] = gcurve(color=color.orange)

    def add_momentum_graphs(self, linear=False, angular=False):
        if angular:
            graph(title='Angular Momentum Over Time', xtitle='Time[s]', ytitle='Angular Momentum[kg∙m^2/s]')
            self.graphs['angular momentum'] = gcurve(color=color.purple)

    def __calculate_energy(self):
        self.energy.gravity = self.effective_mass * g.mag * self.pos.y
        self.energy.spring = 0.5 * self.spring_constant * (self.weight_pos.mag - self.equilibrium_length) ** 2
        self.energy.kinetic = 0.5 * (self.effective_mass + self.spring_mass / 6) * self.velocity.mag2

        if self.spring_energy_offset is None:
            self.spring_energy_offset = self.energy.spring
        if self.gravitational_energy_offset is None:
            self.gravitational_energy_offset = self.energy.gravity

    def update_graph(self, t=t, graph_name='total energy'):
        if 'energy' in graph_name:
            self.__calculate_energy()
            self.graphs[graph_name] \
                .plot(pos=(t,
                           {'total energy': self.energy.total,
                            'potential energy': self.energy.potential,
                            'kinetic energy': self.energy.kinetic,
                            'potential spring energy': self.energy.spring - self.spring_energy_offset,
                            'potential gravitational energy': self.energy.gravity - self.gravitational_energy_offset}[
                               graph_name]))
        elif 'power' in graph_name:
            self.graphs[graph_name] \
                .plot(pos=(t,
                           {'spring power': self.power.spring,
                            'gravitational power': self.power.gravity}[graph_name]))
        elif graph_name == 'xy':
            self.graphs['xy'].plot(pos=(self.pos.x, self.pos.y))
        elif graph_name == 'xz':
            self.graphs['xz'].plot(pos=(self.pos.x, self.pos.z))
        elif graph_name == 'angular momentum':
            self.graphs['angular momentum'].plot(pos=(t, mag(self.effective_mass * self.pos.cross(self.velocity))))


# ANIMATION

print(f'Eq. length: {spring_equilibrium_length:.3f}[m], effective mass: {effective_mass:.3f}[kg]')

test_spring = SpringPendulum(radius=0.05,
                             end_pos=start_pos,
                             effective_mass=effective_mass, spring_mass=spring_mass, spring_constant=k,
                             trail_retain=600,
                             equilibrium_length=spring_equilibrium_length, starting_velocity=starting_velocity,
                             random_force=False)
test_spring.add_power_graph()
test_spring.add_energy_graphs(total=True, potential=True, kinetic=True)
test_spring.add_xyz_graphs(xz=True, xy=False)
test_spring.add_momentum_graphs(angular=True)

# Defining the Excel data file.
data_sheet = ExcelSheet('Data')
headers = ExcelSheet.create_data_objects(
    [[0, 0, 'x'], [1, 0, 'y'], [2, 0, 'z'], [3, 0, 't']])
experiment_constants = ExcelSheet.create_data_objects([[5, 0, 'effective mass'], [5, 1, test_spring.effective_mass],
                                                       [6, 0, 'spring constant'], [6, 1, test_spring.spring_constant],
                                                       [7, 0, 'equilibrium length'],
                                                       [7, 1, test_spring.equilibrium_length]])
data_sheet.write_to_sheet(headers)
data_sheet.write_to_sheet(experiment_constants)

while t <= end_time + DT:
    if t % real_dt < DT:  # so it works with the slight floating point precision errors
        col_y += 1
        print_vector = change_vector_length(test_spring.pos, test_spring.pos.mag - (
                rod_weights_center_of_mass - button_from_hook_length))
        data_list = ExcelSheet.create_data_objects(
            [[0, col_y, print_vector.x], [1, col_y, print_vector.y], [2, col_y, print_vector.z],
             [3, col_y, round(t, 2)]])
        data_sheet.write_to_sheet(data_list)
    rate(1000)

    t += DT

    # update
    test_spring.update_all_graphs(t)
    test_spring.kinematics()
    test_spring.update_pos()

data_sheet.save_file()
