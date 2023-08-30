bounds = [(1,1000), (1,1000)]

# Define the constraint functions for bounds
def constraint_x0(x):
    return x[0] - bounds[0][0]  # Lower bound for x[0]

def constraint_x1(x):
    return bounds[0][1] - x[0]  # Upper bound for x[0]

def constraint_x2(x):
    return x[1] - bounds[1][0]  # Lower bound for x[1]

def constraint_x3(x):
    return bounds[1][1] - x[1]  # Upper bound for x[1]

# Create a constraints list
cons = (
    {'type': 'ineq', 'fun': constraint_x0},
    {'type': 'ineq', 'fun': constraint_x1},
    {'type': 'ineq', 'fun': constraint_x2},
    {'type': 'ineq', 'fun': constraint_x3}
)