import minizinc
from minizinc import Instance, Model, Solver


def print_solution(solution: list) -> None:
    for i in range(0, len(solution)):
        print("Week", i, end="")

        for j in range(0, len(solution[i])):
            print(" |", set(solution[i][j]), end="")

        print()


def find_schedule(n_weeks: int, n_groups: int, n_participant: int) -> list:
    model = Model("../model/model_1.mzn")
    solver = Solver.lookup("gecode")

    instance = Instance(solver, model)
    instance["W"] = n_weeks
    instance["G"] = n_groups
    instance["P"] = n_participant

    result = instance.solve()
    solution = result.solution.S

    print_solution(solution)

    return solution


if __name__ == "__main__":
    find_schedule(5, 4, 4)
