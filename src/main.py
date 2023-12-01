import itertools

from minizinc import Instance, Model, Solver, Result


def print_schedule(schedule: list) -> None:
    for i in range(0, len(schedule)):
        print("Week", i, end="")

        for j in range(0, len(schedule[i])):
            print(" |", set(schedule[i][j]), end="")

        print()


def find_schedule(n_weeks: int, n_groups: int, n_participant: int, find_all_solutions: bool = True) -> list:
    model: Model = Model("../model/model_1.mzn")
    solver: Solver = Solver.lookup("gecode")

    instance: Instance = Instance(solver, model)
    instance["W"] = n_weeks
    instance["G"] = n_groups
    instance["P"] = n_participant

    result: Result = instance.solve(all_solutions=find_all_solutions)

    if find_all_solutions:
        solution: list = [result.solution[i].S for i in range(len(result.solution))]
    else:
        solution: list = result.solution.S

    return solution


def verify_schedule(schedule: list, n_group: int, n_participant: int) -> bool:
    def find_subsets(set_: set, subset_size: int):
        return list(itertools.combinations(set_, subset_size))

    flat_schedule: list = [item for sublist in schedule for item in sublist]

    for week in schedule:
        # Check if all participants are present in a given week
        if len(set().union(*week)) != n_group * n_participant:
            print("Not all participants are present in a given week:", week)
            return False

        # Check if all groups have the same number of participants
        for group in week:
            if len(group) != n_participant:
                print("Not all groups have the same number of participants:", group)
                return False

        # Check if each pair of golfers is present at most once
        for group in week:
            for pair in find_subsets(group, 2):
                flat_schedule_copy: list = flat_schedule.copy()
                flat_schedule_copy.remove(group)

                for other_group in flat_schedule_copy:
                    if pair in find_subsets(other_group, 2):
                        print("Pair", pair, "is present in more than one group:", group, other_group)
                        return False

    return True


def main() -> None:
    n_weeks: int = 2
    n_groups: int = 2
    n_participant: int = 2
    find_all_solutions: bool = True

    schedule: list = find_schedule(n_weeks, n_groups, n_participant, find_all_solutions)

    if find_all_solutions:
        for i in range(len(schedule)):
            print("Solution", i)
            print_schedule(schedule[i])

            schedule_is_valid: bool = verify_schedule(schedule[i], n_groups, n_participant)
            print("\nThe schedule is valid\n\n") if schedule_is_valid else print("The schedule is invalid\n\n")
    else:
        print_schedule(schedule)

        schedule_is_valid: bool = verify_schedule(schedule, n_groups, n_participant)
        print("\nThe schedule is valid\n\n") if schedule_is_valid else print("The schedule is invalid\n\n")


if __name__ == "__main__":
    main()
