import src.ActionDuration
import src.Parameters
import src.Utilities as util
from cplex.exceptions import CplexError

# All that a device should store is:
#   device_name, mode_name, mode_type, dID,
#   mode_type defines what other information must be found in a device:
#   if mode_type is...
#       'action_duration' then:
#           phases = {(duration1, kWh1), (dur2, kWh2), (dur3, kWh3), ... }
#       'action' then:
#           kWh --- TODO: going to have to do something for state properties and their change over time

class Device:
    def __init__(self, device, mode_type, device_name, mode_name, dID, device_type='unspecified'):
        self.device_name = device_name
        self.mode_name = mode_name
        self.mode_type = mode_type
        self.device_type = device_type
        self.params = src.Parameters.Parameters()
        self.device = device
        self.sp = device['properties']
        # self.name = str(dID)+'_'+device['name']  # puts the dID in front of each name so there is a unique ID
        self.name = 'd' + str(dID)
        self.mode = device['modes'][mode_name]
        self.phases = [None] * len(self.mode)
        self.dvars = []  # <-- power schedule variables for device

        # total duration
        self.duration = 0
        ratio = 60.0 / (float(self.params.horizon) / 24.0)
        for i in range(len(self.mode)):
            if ratio < self.mode[i]['duration']:
                self.mode[i]['kWh'] *= ratio
                self.mode[i]['duration'] = int(round(self.mode[i]['duration'] / ratio, 0))
            else:
                self.mode[i]['kWh'] *= self.mode[i]['duration']
                self.mode[i]['duration'] = 1

            self.duration += self.mode[i]['duration']

    def to_string(self):
        return 'dID: ' + self.name + '\tdevice: ' + self.device_name + '\ttype: ' + self.device_type + '\n\tmode: ' + str(self.mode_name) + '\ttype: ' + '\ttotal duration: ' + str(self.duration)


    def add_variables(self):
        max_kWh = 0.0
        for i in range(len(self.mode)):
            self.phases[i] = int(self.mode[i]['duration']), float(self.mode[i]['kWh']), self.name+'_p'+str(i)
            # self.phases[i] = 3, float(mode[i]['kWh']), str(dID) + '_' + mode[i]['name']
            # self.phases[i] = 3, float(self.mode[i]['kWh']), self.name + '_' + 'p' + str(i)
            max_kWh = max(max_kWh, float(self.mode[i]['kWh']))

        horizon = self.params.horizon

        # creating a variable for each timestep from 0 to horizon-1
        # this is our device schedule -- used later to aggregate power consumption per timestep
        self.params.model.variables.add(
            names=[self.name + '_' + str(k) for k in range(horizon)],
            types=[self.params.model.variables.type.continuous] * horizon,
            lb=[0.0] * horizon,
            ub=[max_kWh * 1.05] * horizon
            # obj=params.price_schema
        )

        for k in range(horizon):
            self.dvars.append(self.name + '_' + str(k))

        self.window = src.ActionDuration.ActionDuration(phases=self.phases, name=self.name)

        print(self.phases)

    def add_constraints(self, rule):
        self.variables = self.window.add_rule_constraints(rule)
        self.variables.insert(0, self.dvars)
        return self.variables




''' PRINTING STUFF <-- Look at me later to add this to other place
    def print_variables(self, solution):
        try:
            # device power schedule
            print()
            print(self.variables[0][0])
            for j in range(len(self.variables[0])):
                print(solution.get_values(self.variables[0][j]), end='\t\t')
            print()
            print()

            # when each phase starts
            for j in range(len(self.variables[1])):
                print(self.variables[1][j], end='\t')
            print()
            for j in range(len(self.variables[1])):
                print(abs(solution.get_values(self.variables[1][j])), end='\t\t')
            print()
            print()

            # on/off schedule for each phase
            for i in range(2, len(self.variables)):
                for j in range(len(self.variables[i])):
                    print(self.variables[i][j][0], end='\t')
                print()
                for j in range(len(self.variables[i])):
                    print(abs(solution.get_values(self.variables[i][j][0])), end='\t\t\t')
                print()
                print()

        except CplexError as exc:
            print(exc)

    def get_schedule(self, solution):
        try:
            return solution.get_values(self.variables[0])
        except CplexError as exc:
            print(exc)

    def get_info(self):
        info = ""
        info += str(self.device_name) + "\t"
        info += str(self.name) + "\t"
        info += str(self.mode_name) + "\n"
        return info

    def get_phase_sched(self, solution):
        s = self.variables[2][0][0].replace('d', '').replace('p', '').split('_')
        device_id = s[0]
        j = 0
        output = ''  #device_id + '\t'
        for i in range(2, len(self.variables)):
            s = self.variables[i][0][0].replace('d','').replace('p','').split('_')
            device_id = s[0]
            phase_id = s[1]
            start = int(s[2])
            e = self.variables[i][len(self.variables[i])-1][0].replace('d','').replace('p','').split('_')
            end = int(e[2])
            #print(device_id + '\t' + phase_id, end='\t')

            # output = device_id + '\t'
            # output += phase_id + '\t'

            while j != self.params.horizon:
                if j < start or j > end:
                    #print('0', end='\t')
                    output += '- '
                    j += 1
                else:
                    if int(abs(solution.get_values(self.variables[i][j-start][0]))) == 1:
                        for k in range(self.phases[int(s[1])][0]):
                            #print('1', end='\t')
                            output += s[1] + ' '
                        j += self.phases[int(s[1])][0]
                        for k in range(j, self.params.horizon):
                            output += '- '
                        output += '\n'
                        for k in range(j):
                            output += '- '
                        break
                    else:
                        output += '- '
                        j += 1

        output += '\n'

        return output
'''