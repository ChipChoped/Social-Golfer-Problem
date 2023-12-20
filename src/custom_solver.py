import argparse
import itertools
import sys
import time
from ctypes import c_int

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import TextIO

import random
import copy


class GolferConstraintSolver:
    def __init__(self, W, G, P):
        self.W = W
        self.G = G
        self.P = P
        self.schedule = [[[] for _ in range(G)] for _ in range(W)]
        self.domains = [[set(range(G * P)) for _ in range(G)] for _ in range(W)]
        self.rencontres = {i: set() for i in range(self.P * self.G)}
        self.constraints = []
        self.consistence = True
        self.backtrack_domains = [[set(range(G * P)) for _ in range(G)] for _ in range(W)]
        # self.backtrack_schedule = copy.deepcopy(self.schedule)

    def print_domains(self):
        result = ""
        for w in range(self.W):
            result += str(self.domains[w][:]) + "\n"
        print(result)

    def print_schedule(self):
        result = ""
        for w in range(self.W):
            result += str(self.schedule[w][:]) + "\n"
        print(result)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def propagate_constraints(self):
        print("Initial domains:\n")
        self.print_domains()
        for constraint in self.constraints:
            constraint.propagate(self.domains)

    def solve(self, time_delta):
        limit_time = datetime.now() + time_delta if time_delta is not None else None
        start_time = datetime.now()
        # Domain reduction
        print("W: " + str(self.W) + "\nG: " + str(self.G) + "\nP: " + str(self.P) + "\n")
        self.propagate_constraints()
        self.backtrack_domains = copy.deepcopy(self.domains)

        res_final = True
        self.print_domains()

        if self.consistence:
            res_final = self.forward_checking(0, 0, 0, limit_time)
            print(res_final)
            return res_final[0], datetime.now() - start_time
        else:
            return -1, datetime.now() - start_time

    def update_domains(self):

        self.domains = copy.deepcopy(self.backtrack_domains)
        # Week constraint
        for week in range(1, self.W):
            for group in range(0, self.G):
                for player in self.schedule[week][group]:
                    for group2 in range(0, self.G):
                        if group2 != group:
                            self.domains[week][group2] -= {player}

        # Meeting list update
        self.rencontres = {i: set() for i in range(self.P * self.G)}
        for i in range(0, self.G * self.P):
            for week in range(0, self.W):
                for group in range(0, self.G):
                    if i in self.schedule[week][group]:
                        for player in self.schedule[week][group]:
                            if player != i:
                                self.rencontres[i].add(player)

        # Meeting unicity constraint
        for player in range(0, self.G * self.P):
            for week in range(1, self.W):
                for group in range(0, self.G):
                    if player in self.schedule[week][group]:
                        to_remove = copy.deepcopy(self.rencontres[player])
                        for player2 in self.schedule[week][group]:
                            to_remove -= {player2}
                        self.domains[week][group] -= to_remove

    def forward_checking(self, week, group, player, time_limit):

        print(" ---------- Forward Checking ", week, " ", group, " ", player, "----------\n")
        print(str(time_limit) + " " + str(datetime.now()))
        if week == self.W:
            return 1, datetime.now()  # Solution is found
        if time_limit is not None:
            if datetime.now() > time_limit:  # Timeout
                print("Return")
                return 2, datetime.now()
        if group < self.G - 1 and player == self.P:
            return self.forward_checking(week, group + 1, 0, time_limit)  # Go to the next group

        if group == self.G - 1 and player == self.P:
            return self.forward_checking(week + 1, 0, 0, time_limit)  # Go to the next week

        if player < len(self.schedule[week][group]):
            return self.forward_checking(week, group, player + 1, time_limit)  # Go to the next player

        # Gets the last player placed in the group
        last_player = -1
        for last in self.schedule[week][group]:
            last_player = last

        # Browsing available players in the domain and
        # not already placed and superior to the last placed player (symmetry)
        for p in list(self.domains[week][group]):
            if p not in self.schedule[week][group] and p > last_player:
                # If consistent, add it and update the domains
                if self.is_consistent():
                    self.schedule[week][group].append(p)
                    self.update_domains()
                    self.print_schedule()

                    # Recursively pass to the next player
                    res = self.forward_checking(week, group, player + 1, time_limit)
                    if res[0] == 1:  # Recursion
                        return 1, datetime.now()
                    elif res[0] == 2:
                        return 2, datetime.now()

                    # If consistent for the next players, remove it and update the domains
                    self.schedule[week][group].remove(p)
                    self.update_domains()

        return 0, datetime.now()  # No assignation valid for this variable

    def is_consistent(self):
        # Stimulate the update of the schedule and domains.
        # If some domains are smaller than P then inconsistent
        domains_copy = copy.deepcopy(self.backtrack_domains)
        schedule_copy = copy.deepcopy(self.schedule)

        for week in range(1, self.W):
            for group in range(0, self.G):
                for player in schedule_copy[week][group]:
                    for group2 in range(0, self.G):
                        if group2 != group:
                            domains_copy[week][group2] -= {player}

        rencontres_copy = {i: set() for i in range(self.P * self.G)}
        for i in range(0, self.G * self.P):
            for week in range(0, self.W):
                for group in range(0, self.G):
                    if i in schedule_copy[week][group]:
                        for player in schedule_copy[week][group]:
                            if player != i:
                                rencontres_copy[i].add(player)

        for player in range(0, self.G * self.P):
            for week in range(1, self.W):
                for group in range(0, self.G):
                    if player in schedule_copy[week][group]:
                        to_remove = copy.deepcopy(rencontres_copy[player])
                        for player2 in schedule_copy[week][group]:
                            to_remove -= {player2}
                        domains_copy[week][group] -= to_remove

        for week in range(1, self.W):
            for group in range(0, self.G):
                if len(domains_copy[week][group]) < self.P:
                    return False

        for week in range(self.W):
            dom = set()
            for group in range(self.G):
                dom |= domains_copy[week][group]
            if len(dom) != self.P * self.G:
                return False

        return True


class PPlayerPerGroupConstraint:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        res = True
        for week in range(self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                if len(domains[week][group]) == self.golfer_solver.P:
                    for group2 in range(self.golfer_solver.G):
                        if group2 != group:
                            domains[week][group2] -= domains[week][group]

        for week in range(self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                if len(domains[week][group]) < self.golfer_solver.P:
                    res = False

        print("If a group cardinality == P, then modify other groups domains:\n")
        self.golfer_solver.print_domains()
        print("Check cardinality consistence = " + str(res) + "\n")
        if res == False:
            self.golfer_solver.consistence = False


class Week_constraint:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        res = True
        for week in range(self.golfer_solver.W):
            dom = set()
            for group in range(self.golfer_solver.G):
                dom |= domains[week][group]
            if len(dom) != self.golfer_solver.P * self.golfer_solver.G:
                res = False
        print("Check week consistence = " + str(res) + "\n")
        if res == False:
            self.golfer_solver.consistence = False


class SymmetryFirstWeek:
    def __init__(self, golfer_solver, params=None):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        # Fix the first week
        for group in range(self.golfer_solver.G):
            self.golfer_solver.schedule[0][group] = [i for i in range(group * self.golfer_solver.P,
                                                                      (group + 1) * self.golfer_solver.P)]
            domains[0][group] = set((range(group * self.golfer_solver.P, (group + 1) * self.golfer_solver.P)))
        print("First week symmetry fix:\n")
        self.golfer_solver.print_domains()


class SymmetryFirstPlayerFix:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        # Fix the first player of each group
        group1 = domains[0][0]
        for week in range(1, self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                if group < self.golfer_solver.P:
                    self.golfer_solver.schedule[week][group].append(group)
                    group1.remove(group)
                    domains[week][group] -= group1
                    group1.add(group)
                else:
                    domains[week][group] -= group1
        print("First player of each group fix:\n")
        self.golfer_solver.print_domains()


class SymmetryMinMaxFirstGroup:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        res = True
        for w2 in range(self.golfer_solver.W - 1, 1, -1):
            if len(domains[w2][0]) > 1:
                max_w2 = max(domains[w2][0])
                for w1 in range(w2 - 1, 0, -1):
                    max_to_remove = set()
                    for i in domains[w1][0]:
                        if i >= max_w2:
                            max_to_remove.add(i)
                    domains[w1][0] -= max_to_remove
            else:
                res = False

        for w1 in range(1, self.golfer_solver.W - 1):
            if len(domains[w1][0]) > 1:
                copy_g1 = copy.deepcopy(domains[w1][0])
                copy_g1 -= {0}
                min_w1 = min(copy_g1)
                for w2 in range(w1 + 1, self.golfer_solver.W):
                    min_to_remove = set()
                    for i in domains[w2][0]:
                        if i <= min_w1 and i != 0:
                            min_to_remove.add(i)
                    domains[w2][0] -= min_to_remove
            else:
                res = False
        print("Symetry min(w1) < min(w2) and max(w1) < max(w2)\n")
        print("Check min_max = " + str(res) + "\n")
        if not res:
            self.golfer_solver.consistence = False
        self.golfer_solver.print_domains()


def main(argv: argparse.Namespace) -> None:
    W: int = argv.weeks
    G: int = argv.groups
    P: int = argv.participants
    symetry_breaking_bool: bool = argv.symmetry_breaking
    timeout: timedelta = timedelta(seconds=argv.timeout) \
        if argv.timeout is not None or argv.timeout == 0 \
        else None

    check_validity: bool = argv.check_validity
    log: bool = argv.log

    solver = GolferConstraintSolver(W, G, P)
    symmetry_first_week_fix = SymmetryFirstWeek(solver)
    symmetry_first_player_fix = SymmetryFirstPlayerFix(solver)
    symmetry_min_max = SymmetryMinMaxFirstGroup(solver)
    if symetry_breaking_bool:
        solver.add_constraint(symmetry_first_week_fix)
        solver.add_constraint(symmetry_first_player_fix)
        solver.add_constraint(symmetry_min_max)

    constraint_P_player_per_group = PPlayerPerGroupConstraint(solver)
    constraint_week = Week_constraint(solver)
    solver.add_constraint(constraint_P_player_per_group)
    solver.add_constraint(constraint_week)

    status, solving_time = solver.solve(timeout)

    if log:
        current_time: str = str(time.strftime("%Y-%m-%d_%H-%M-%S"))

        symmetry: str = "_sym" if symetry_breaking_bool else ""

        Path("../log").mkdir(parents=True, exist_ok=True)
        file: TextIO = open("../log/solution" +
                            "_w" + str(W) + "_g" + str(G) + "_p" + str(P) +
                            symmetry + "_" + current_time + ".txt", "a")

        default_stdout = sys.stdout
        sys.stdout = file
    if status == 1:
        print("Solution\n")
        solver.print_schedule()
        if check_validity:
            schedule_is_valid: bool = solver.is_consistent()
            print("\nThe schedule is valid\n\n") if schedule_is_valid else print("The schedule is invalid\n\n")
    elif status == 2:
        print("Timeout reached\n")
    else:
        print("No solution found\n")
    print("Solving time:", round(solving_time.total_seconds(), 3), "seconds")

    if log:
        file.close()
        sys.stdout == default_stdout

        if status == 2:
            print("Timeout reached\n")
        elif status <= 0:
            print("No solution found\n")
        print("solving time:", round(solving_time.total_seconds(), 3), "seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Social Golfer Problem Solver',
        description='This solver finds one or multiple schedules for a social golfer problem instance')

    parser.add_argument('-w', '--weeks', type=int, required=True,
                        help="Number of weeks")
    parser.add_argument('-g', '--groups', type=int, required=True,
                        help="Number of groups")
    parser.add_argument('-p', '--participants', type=int, required=True,
                        help="Number of golfers per group")
    parser.add_argument('-s', '--symmetry-breaking', action='store_true', default=False,
                        help="Flag to use symmetry breaking (False by default)")
    parser.add_argument('-t', '--timeout', type=int, default=None,
                        help="Timeout in seconds (None by default)")

    parser.add_argument('-c', '--check-validity', action='store_true', default=False,
                        help='Flag to check the validity of a schedule (False by default)')
    parser.add_argument('-l', '--log', action='store_true', default=False,
                        help='Flag to log the solver output (False by default)')

    args: argparse.Namespace = parser.parse_args()
    print(args)
    print()

    main(args)
