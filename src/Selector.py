# 3/29/2018 --- Bill


# This function returns a 2D-array of every combination of indexes from a matrix of size |B|
#   one 1D-array for every index combination
def selector(B, A=None):
    if A is None:
        A = [[]]

    A2 = []
    for a in A:
        for b in range(len(B[0])-1):
            A2.append(a + [b])

    if len(B) == 1:
        return A2
    else:
        return selector(B[1:], A2)


def select_bounds(A_x, i):
    lb = A_x[i][1]
    ub = A_x[i+1][0]
    return [lb, ub]


def get_bounds(B):
    A = selector(B)
    C = []
    for a in A:
        C.append([])
        for i in range(len(a)):
            C[len(C)-1].append(select_bounds(B[i], a[i]))

    return C

""" |B| = 4 """
''' EXAMPLE: '''
'''
B = [
    [[ 1,  2], [ 3,  4], [ 5,  6]],
    [[ 7,  8], [ 9, 10], [11, 12], [13, 14], [15, 16]],
    [[17, 18], [19, 20], [21, 22], [23, 24]],
    [[25, 26], [27, 28]],
    ]

D = get_bounds(B)

for d in D:
    print(d)
'''
