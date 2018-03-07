import random
import sys, os
from contextlib import contextmanager


def get_rand(json):
    mode_names = []
    for k in json.keys():
        mode_names.append(k)
    print(mode_names)
    return random.choice(mode_names)


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def suppress_sol_out(solver):
    solver.set_log_stream(None)
    solver.set_error_stream(None)
    solver.set_warning_stream(None)
    solver.set_results_stream(None)
    '''
    try:
        yield
    finally:
        solver.set_log_stream(None)
        solver.set_error_stream(None)
        solver.set_warning_stream(None)
        solver.set_results_stream(None)
    '''