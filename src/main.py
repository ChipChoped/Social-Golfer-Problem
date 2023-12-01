import itertools

from minizinc import Instance, Model, Solver, Result


def print_schedule(schedule: list) -> None:
    for i in range(0, len(schedule)):
        print("Week", i, end="")

        for j in range(0, len(schedule[i])):
            print(" |", set(schedule[i][j]), end="")

        print()


def find_schedule(n_weeks: int, n_groups: int, n_participant: int) -> list:
    model: Model = Model("../model/model_1.mzn")
    solver: Solver = Solver.lookup("gecode")

    instance: Instance = Instance(solver, model)
    instance["W"] = n_weeks
    instance["G"] = n_groups
    instance["P"] = n_participant

    result: Result = instance.solve()
    solution: list = result.solution.S

    return solution


def verify_schedule(schedule: list, n_weeks: int, n_group: int, n_participant: int) -> bool:
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
    schedule: list = find_schedule(5, 4, 4)
    print_schedule(schedule)

    schedule_is_valid: bool = verify_schedule(schedule, 5, 4, 4)
    print("\nThe schedule is valid") if schedule_is_valid else print("The schedule is invalid")


if __name__ == "__main__":
    main()
