import argparse
import itertools
import sys
import time

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

    def printDomains(self):
        result = ""
        for w in range(self.W):
            result += str(self.domains[w][:]) + "\n"
        print(result)

    def printSchedule(self):
        result = ""
        for w in range(self.W):
            result += str(self.schedule[w][:]) + "\n"
        print(result)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def propagate_constraints(self):
        print("Domaines initiaux:\n")
        self.printDomains()
        for constraint in self.constraints:
            constraint.propagate(self.domains)

    def solve(self, time_delta):
        limit_time = datetime.now() + time_delta
        start_time = datetime.now()
        # reduction domaine
        print("W: " + str(self.W) + "\nG: " + str(self.G) + "\nP: " + str(self.P) + "\n")
        self.propagate_constraints()
        self.backtrack_domains = copy.deepcopy(self.domains)

        res_final = True
        self.printDomains()

        if self.consistence:
            res_final = self.forwardCheking(0, 0, 0, limit_time)
            print(res_final)
            return res_final[0], datetime.now() - start_time
        else:
            return -1, datetime.now() - start_time

    def updateDomains(self):

        self.domains = copy.deepcopy(self.backtrack_domains)
        # contrainte de la semaine
        for week in range(1, self.W):
            for group in range(0, self.G):
                for player in self.schedule[week][group]:
                    for group2 in range(0, self.G):
                        if group2 != group:
                            self.domains[week][group2] -= {player}

        # Maj de la liste des rencontres
        self.rencontres = {i: set() for i in range(self.P * self.G)}
        for i in range(0, self.G * self.P):
            for week in range(0, self.W):
                for group in range(0, self.G):
                    if i in self.schedule[week][group]:
                        for player in self.schedule[week][group]:
                            if player != i:
                                self.rencontres[i].add(player)

        # contrainte unicite des rencontres
        for player in range(0, self.G * self.P):
            for week in range(1, self.W):
                for group in range(0, self.G):
                    if player in self.schedule[week][group]:
                        to_remove = copy.deepcopy(self.rencontres[player])
                        for player2 in self.schedule[week][group]:
                            to_remove -= {player2}
                        self.domains[week][group] -= to_remove

    def forwardCheking(self, week, group, player, time_limit):

        print(" ---------- Forward Cheking ", week, " ", group, " ", player, "----------\n")
        print(str(time_limit) + " " + str(datetime.now()))
        if week == self.W:
            return 1, datetime.now()  # La solution est trouvée
        if datetime.now() > time_limit:
            print("je retourne")
            return 2, datetime.now()
        if group < self.G - 1 and player == self.P:
            return self.forwardCheking(week, group + 1, 0, time_limit)  # Passage au groupe suivant

        if group == self.G - 1 and player == self.P:
            return self.forwardCheking(week + 1, 0, 0, time_limit)  # Passage à la semaine suivante

        if player < len(self.schedule[week][group]):
            return self.forwardCheking(week, group, player + 1, time_limit)  # Passage au joueur suivant

        # recupere le dernier joueur placer dans le group
        last_player = -1
        for last in self.schedule[week][group]:
            last_player = last

        # Paarcour des joueur dispo dans le domaine et pas deja place et superieur au precedent joueur place (symetrie)
        for p in list(self.domains[week][group]):
            if p not in self.schedule[week][group] and p > last_player:
                # Si consistent on l ajoute et on met a jour les domaines
                if self.isConsistent():
                    self.schedule[week][group].append(p)
                    self.updateDomains()
                    self.printSchedule()
                    # On passe au joueur suivant par recursivité
                    res = self.forwardCheking(week, group, player + 1, time_limit)
                    if res[0] == 1:  # Récursion                        
                        return 1, datetime.now()
                    elif res[0] == 2:
                        return 2, datetime.now()

                    # Si inconsistence dans les prochain joueurs on suprime et on met a jour les domaines
                    self.schedule[week][group].remove(p)
                    self.updateDomains()

        return 0, datetime.now()  # Aucune assignation valide pour cette variable

    def isConsistent(self):
        # on stimule la maj du schedule et des domaines. Si certain domaines sont plut petit que P alors inconsistent
        domains_copy = copy.deepcopy(self.backtrack_domains)
        schedule_copy = copy.deepcopy(self.schedule)

        # schedule_copy[w][g].append(p)

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

        print("Si cardinalite d un groupe == P, alors modification des domaine des autres groupes:\n")
        self.golfer_solver.printDomains()
        print("Check cardinalité consistence = " + str(res) + "\n")
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


class SymetrieFixSem1:
    def __init__(self, golfer_solver, params=None):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        # Fix la upremière semaine
        for group in range(self.golfer_solver.G):
            self.golfer_solver.schedule[0][group] = [i for i in range(group * self.golfer_solver.P,
                                                                      (group + 1) * self.golfer_solver.P)]
            domains[0][group] = set((range(group * self.golfer_solver.P, (group + 1) * self.golfer_solver.P)))
        print("Symetrie premiere semaine fix:\n")
        self.golfer_solver.printDomains()


class SymetrieFixFirstPlayer:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        # fix les premiers joueurs de chaque groupe
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
        print("Symetrie premier joueur de chaque groupe fix:\n")
        self.golfer_solver.printDomains()


class SymetrieMinMaxFirstGroup:
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
        print("Symetrie min(w1)<min(w2) et max(w1)<max(w2)\n")
        print("Check min_max = " + str(res) + "\n")
        if res == False:
            self.golfer_solver.consistence = False
        self.golfer_solver.printDomains()


def main(argv: argparse.Namespace) -> None:
    W: int = argv.weeks
    G: int = argv.groups
    P: int = argv.participants
    symetry_breaking_bool: bool = argv.symmetry_breaking
    timeout: timedelta = timedelta(seconds=argv.timeout) \
        if argv.timeout is not None or argv.tiemut == 0 \
        else None

    check_validity: bool = argv.check_validity
    log: bool = argv.log

    solver = GolferConstraintSolver(W, G, P)
    symetrie_fix_sem_1 = SymetrieFixSem1(solver)
    symetrie_fix_first_player = SymetrieFixFirstPlayer(solver)
    symetrie_min_max = SymetrieMinMaxFirstGroup(solver)
    if symetry_breaking_bool:
        solver.add_constraint(symetrie_fix_sem_1)
        solver.add_constraint(symetrie_fix_first_player)
        solver.add_constraint(symetrie_min_max)

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
        solver.printSchedule()
        if check_validity:
            schedule_is_valid: bool = solver.isConsistent()
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
