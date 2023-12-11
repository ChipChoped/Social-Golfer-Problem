class GolferConstraintSolver:
    def __init__(self, W, G, P):
        self.W = W
        self.G = G
        self.P = P

        self.domains = [[set(range(P)) for _ in range(G)]for _ in range(W)]
        self.constraints = []

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def propagate_constraints(self):
        for constraint in self.constraints:
            constraint.propagate(self.domains)

    def solve(self):
        # reduction domaine
        self.propagate_constraints()
        # algo de recherche (ex. glouton)

class oneConstraint:
    def __init__(self, golfer_solver,params=None):
        self.golfer_solver = golfer_solver

    def propagate(self):
        for week in range(self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                # maj des domaines
                pass

# Example Usage
solver = GolferConstraintSolver(W=3, G=3, P=3)
constraint = oneConstraint(solver)
solver.add_constraint(constraint)
solver.solve()
