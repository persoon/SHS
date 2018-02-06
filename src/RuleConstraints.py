# 1/11/2018
#
# Attaches rules to devices / state properties
# Attaches devices to various state property models (e.g. HVAC, solar)
import src.HVAC

# todo: make the rules sort themselves into locations, then apply the properties and whatnot like below:
class RuleConstraints:
    def __init__(self, model, mode_cons, rules):
        self.model = model
        self.rules = rules
        self.mode_cons = mode_cons

        # all rules are located in a room or a device
        # splits rules into the two groups and removes identifier
        # TODO: make the removal of identifier happen in Rule.py and have r_type (or loc_type) identify
        drules = []
        used = []
        rrules = []
        for r in rules:
            loc = r.location.split(":")
            if loc[0] == "d":
                r.location = loc[1]
                drules.append(r)
            else:
                r.location = loc[1]
                rrules.append(r)

        for r in drules:
            for i in range(len(mode_cons)):
                dev = mode_cons[i][0]
                name = dev.name
                dname = dev.device_name
                if dname == r.location:
                    # if device is used, add to list of used once so it can be added to state prop models later
                    if dev not in used:
                        used.append(dev)

                    mode_cons[i][1].add_rule_constraints(r)
                    print(name + " -------------------------")
                    print(r.to_string())
                    print(dname, dev.mode_name)
                    print("----------------------------")
                    del mode_cons[i]
                    break

        hrules = []
        for r in rrules:
            if r.sp == 'air_temp':
                hrules.append(r)

        if len(hrules) > 0: # at least one hvac related rule
            devices = []
            # find all active devices that affect air_temp
            # for d in used: # for now, using the 2-lines below because hvac isn't in used list...
            for i in range(len(mode_cons)):
                d = mode_cons[i][0]
                if d.mode_type == 'HVAC':
                    devices.append(d)

            devices.extend(used)
            # TODO: initialized hvac in all applicable rooms 2/2/2018
            hvac = src.HVAC.HVAC(model=self.model, rname='room', devices=devices)

            for r in hrules:
                hvac.add_active_rule(r)
