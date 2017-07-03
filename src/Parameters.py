# 6_21_2017
#
# parameters used across multiple files in the program


class Parameters:

    def __init__(self):
        self.horizon = 24
        self.mult = int(self.horizon / 24)

        '''
        price_schema = [
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

        self.price_schema = []
        for k in range(0, len(self.old_ps)):
            for p in range(0, self.mult):
                self.price_schema.append(self.old_ps[k])
