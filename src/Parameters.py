# 6_21_2017
#
# parameters used across multiple files in the program


class Parameters:

    def __init__(self):
        self.horizon = 24


        self.old_ps = [
            0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198, 0.198,
            0.225, 0.225, 0.225, 0.225,
            0.249, 0.249,
            0.849, 0.849, 0.849, 0.849,
            0.225, 0.225, 0.225, 0.225,
            0.198, 0.198
        ]

        '''
        self.old_ps = [
            0.198, 0.849, 0.849, 0.198, 0.849, 0.198, 0.849, 0.198,
            0.225, 0.225, 0.225, 0.225,
            0.249, 0.249,
            0.849, 0.849, 0.849, 0.849,
            0.225, 0.225, 0.849, 0.225,
            0.198, 0.198
        ]
        '''
        self.price_schema = []


    def scale_factor(self, file_horizon):
        scale = int(self.horizon / file_horizon)
        for k in range(0, len(self.old_ps)):
            for p in range(0, scale):
                self.price_schema.append(self.old_ps[k])
        return scale