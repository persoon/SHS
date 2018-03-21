# LB, UB = 0, 100
# temp = 0
# point_bounds = []
# temp_arr = [4, 0, 14, 12, 100, 85, 99, 97, 98, 15, 13, 1]


def add_bound(LB, UB, point_bounds, point, verbose=0):
    assert(LB < UB)
    point = round(point)

    if LB == point:
        # if [LB+0.5, LB+1.5] is already in list, replace with [LB, LB+1.5]
        # else add to beginning of list, ensure bounds are not out of range
        if len(point_bounds) > 0 and point_bounds[0][0] == point + 0.5:
            point_bounds[0][0] = LB
        else:
            point_bounds.insert(0, (LB, point + 0.5))
    elif point == UB:
        # if [UB-1.5, UB-0.5] is already in list, replace with [UB-1.5, UB]
        # else add to end of line, ensure bounds are not out of range
        if len(point_bounds) > 0 and point_bounds[len(point_bounds)-1][1] == point - 0.5:
            point_bounds[len(point_bounds) - 1][1] = UB
        else:
            point_bounds.insert(len(point_bounds), (point - 0.5, UB))
    else:  # find where new (lb, ub) belongs in sorted list point_bounds
        i = 0
        while True:
            if i >= len(point_bounds):
                # similar case to temp == UB, see above
                if len(point_bounds) > 0 and point_bounds[len(point_bounds) - 1][1] == point - 0.5:
                    point_bounds[len(point_bounds)-1] = (point_bounds[len(point_bounds)-1][0], point - 0.5)
                else:
                    point_bounds.insert(len(point_bounds), (point - 0.5, point + 0.5))
                break
            elif point_bounds[i][0] > point - 0.5:
                # if lower bounds of temp connects with a ub from list
                if point_bounds[i-1][1] == point - 0.5:
                    # if upper bounds of temp connects with a ub of list
                    if point_bounds[i][0] == point + 0.5:
                        point_bounds[i-1] = (point_bounds[i-1][0], point_bounds[i][1])
                        del point_bounds[i]
                    else:
                        point_bounds[i - 1] = (point_bounds[i-1][0], point + 0.5)
                else:
                    # if upper bounds of temp connects with a ub of list
                    if point_bounds[i][0] == point + 0.5:
                        point_bounds[i] = (point - 0.5, point_bounds[i][1])
                    else:  # most common case --- just add to list, maintaining sort
                        point_bounds.insert(i, (point - 0.5, point + 0.5))
                break
            i += 1
    if verbose == 1:
        print("----------------------------------------")
        print('adding', point)
        print('lb,ub:', point_bounds)
        print("----------------------------------------")
    return point_bounds
