import random

class GolferConstraintSolver:
    def __init__(self, W, G, P):
        self.W = W
        self.G = G
        self.P = P
        self.schedule = [[ [] for _ in range(G)]for _ in range(W)]
        self.domains = [[set(range(G*P)) for _ in range(G)]for _ in range(W)]
        self.rencontres = {i: set() for i in range(self.P*self.G)}
        self.constraints = []
        self.consistence = True

    def __str__(self) -> str:
        result = ""
        for w in range(self.W):
            result += str(self.domains[w][:]) + "\n"
        return result

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def propagate_constraints(self):
        print("Domaines initiaux:\n")
        print(self)
        for constraint in self.constraints:
            constraint.propagate(self.domains)
        
    def solve(self):
        # reduction domaine
        print("W: "+str(self.W)+"\nG: "+str(self.G)+"\nP: "+str(self.P)+"\n")
        self.propagate_constraints()
        if self.consistence:
            self.glouton()
            self.local_search()

    
    def updateDomains(self,w,g,p):

        for group in range(g+1,self.G):
            self.domains[w][group]-={p}

        for player in range(0,self.G*self.P):
            for week in range(1,self.W):
                for group in range(0,self.G):
                    if player in self.schedule[week][group]:
                        to_remove = self.rencontres[player].copy()
                        for player2 in self.schedule[week][group]:
                            to_remove-={player2}
                        self.domains[week][group]-=to_remove


    def glouton(self):
        
        print(" ---------- Glouton ---------- \n")
        for i in range(0,self.G*self.P):
            for week in range(0,self.W):
                for group in range(0,self.G):
                    if i in self.schedule[week][group]:
                        for player in self.schedule[week][group]:
                            if player != i:
                                self.rencontres[i].add(player)

        # Remplis le schedule en respectant les contrainte et en mettant a jour les domaines
        # Le tableau peut ne pas etre complet
        for week in range(0,self.W):
            for group in range(0,self.G):
                len_group = len(self.schedule[week][group])
                if len_group == self.P:
                       pass
                else:
                    for i in range(len_group,self.P):
                        if i<len(self.domains[week][group]):
                            player = list(self.domains[week][group])[i]
                            for player2 in self.schedule[week][group]:
                                self.rencontres[player].add(player2)
                                self.rencontres[player2].add(player)
                            self.schedule[week][group].append(player)
                            self.updateDomains(week,group,player)

        print("Tableau incomplet mais contrainte repecté\n")
        result = ""
        for w in range(self.W):
            result += str(self.schedule[w][:]) + "\n"
        print(result)

        # Complete le tableau incomplet et donne une soluition invalide
        all_players = [i for i in range(self.G*self.P)]
        for week in range(0,self.W):
            tab = []
            for group in range(0,self.G):
                tab += self.schedule[week][group]
            tab = list(set(all_players) - set(tab))
            for group in range(0,self.G):
                while len(self.schedule[week][group])<self.P:
                    self.schedule[week][group].append(tab.pop())
        
        print("Tableau completé aléatoirement mais contrainte non repecté\n")
        result = ""
        for w in range(self.W):
            result += str(self.schedule[w][:]) + "\n"
        print(result)


    
    def check_constraints(self,schedule):
        # Vérifier si chaque équipe joue au plus une fois contre une autre équipe
        list_groups = []
        for week in schedule:
            for group in week:
                list_groups.append(group)

        for g1 in range(self.W*self.G-1):
            for g2 in range(g1+1 , self.W*self.G):
                intersect = set(list_groups[g1]) & set(list_groups[g2])
                if len(intersect) > 1:
                    return False
                    
        for week in schedule:
            teams_played = set()
            for period in week:
                teams_played |=  set(period)
                if len(period)!=self.P:
                    return False
            if len(teams_played)!=self.G*self.P:
                return False

        return True

    def cost(self,schedule):
        pena=0
        list_groups = []
        for week in schedule:
            for group in week:
                list_groups.append(group)

        for g1 in range(self.W*self.G-1):
            for g2 in range(g1+1 , self.W*self.G):
                intersect = set(list_groups[g1]) & set(list_groups[g2])
                if len(intersect) > 1:
                    pena+=1
                    
        for week in schedule:
            teams_played = set()
            for period in week:
                teams_played |=  set(period)
                if len(period)!=self.P:
                    pena+=1
            if len(teams_played)!=self.G*self.P:
                pena+=1

        return pena

    def local_search(self, max_iterations=100000):
        print(" ---------- Recherche local ---------- \n")
        current_schedule = self.schedule
        current_cost = self.cost(current_schedule)
        iteration = 0
        trouver = False
        while iteration != max_iterations and trouver == False :
            iteration+=1
            # Sélectionner un voisin aléatoire en échangeant deux équipes dans une période aléatoire
            new_schedule = [week[:] for week in current_schedule]
            week_to_change = random.randint(1, self.W - 1)
            period_to_change_1,period_to_change_2 = random.sample(range(0, self.P),2)
            teams_1 = random.choice(new_schedule[week_to_change][period_to_change_1][1:])
            teams_2 = random.choice(new_schedule[week_to_change][period_to_change_2][1:])
            
            new_schedule[week_to_change][period_to_change_1].remove(teams_1)
            new_schedule[week_to_change][period_to_change_2].remove(teams_2)
            new_schedule[week_to_change][period_to_change_1].append(teams_2)
            new_schedule[week_to_change][period_to_change_2].append(teams_1)
            new_cost = self.cost(new_schedule)

            # Accepter le voisin si le coût diminue ou avec une certaine probabilité
            if new_cost < current_cost:
                current_schedule = new_schedule
                current_cost = new_cost

            # Vérifier si la solution actuelle respecte les contraintes
            if self.check_constraints(current_schedule):
                print("Solution trouvée après", iteration, "itérations \n")
                trouver = True

        if trouver == False:
            print("Aucune solution trouvée après", max_iterations, "itérations \n")
        result = ""
        for w in range(self.W):
            result += str(current_schedule[w][:]) + "\n"
        print(result)

class PPlayerPerGroupConstraint:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        res=True
        for week in range(self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                 if len(domains[week][group])==self.golfer_solver.P:
                     for group2 in range(self.golfer_solver.G) :
                         if group2!=group:
                            domains[week][group2]-=domains[week][group]

        for week in range(self.golfer_solver.W):
            for group in range(self.golfer_solver.G):
                if len(domains[week][group]) < self.golfer_solver.P:
                    res = False

        print("Si cardinalite d un groupe == P, alors modification des domaine des autres groupes:\n")
        print(self.golfer_solver)
        print("Check cardinalité consistence = "+str(res)+"\n")
        if res == False:
            self.golfer_solver.consistence=False
            print("Pas de soluition")
    
class Week_constraint:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        res=True
        for week in range(self.golfer_solver.W):
            dom = set()
            for group in range(self.golfer_solver.G):
                dom |= domains[week][group]
            if len(dom) != self.golfer_solver.P*self.golfer_solver.G:
                res= False
        print("Check week consistence = "+str(res)+"\n")
        if res == False:
            self.golfer_solver.consistence=False
            print("Pas de soluition")   

class SymetrieFixSem1:
    def __init__(self, golfer_solver,params=None):
        self.golfer_solver = golfer_solver

    def propagate(self,domains):
        # Fix la upremière semaine
        for group in range(self.golfer_solver.G):
            self.golfer_solver.schedule[0][group] = [i for i in range(group * self.golfer_solver.P, (group + 1) * self.golfer_solver.P)]
            domains[0][group] = set((range(group * self.golfer_solver.P, (group + 1) * self.golfer_solver.P)))
        print("Symetrie premiere semaine fix:\n")
        print(self.golfer_solver)

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
                    domains[week][group]-=group1
                    group1.add(group)
                else:
                    domains[week][group]-=group1
        print("Symetrie premier joueur de chaque groupe fix:\n")
        print(self.golfer_solver)

class SymetrieMinMaxFirstGroup:
    def __init__(self, golfer_solver):
        self.golfer_solver = golfer_solver

    def propagate(self, domains):
        for w2 in range(self.golfer_solver.W-1,1,-1):
            max_w2=max(domains[w2][0])
            for w1 in range(w2-1,0,-1):
                max_to_remove=set()
                for i in domains[w1][0]:
                    if i >= max_w2:
                        max_to_remove.add(i)
                domains[w1][0]-=max_to_remove

        for w1 in range(1,self.golfer_solver.W-1):
            copy_g1 = domains[w1][0].copy()
            copy_g1-={0}
            min_w1=min(copy_g1)
            for w2 in range(w1+1,self.golfer_solver.W):
                min_to_remove=set()
                for i in domains[w2][0]:
                    if i <= min_w1 and i!=0:
                        min_to_remove.add(i)
                domains[w2][0]-=min_to_remove
        print("Symetrie min(w1)<min(w2) et max(w1)<max(w2)\n")
        print(self.golfer_solver)




# 4 2 2 -> impossible

solver = GolferConstraintSolver(W=4, G=3, P=3)

symetrie_fix_sem_1 = SymetrieFixSem1(solver)
symetrie_fix_first_player = SymetrieFixFirstPlayer(solver)
symetrie_min_max = SymetrieMinMaxFirstGroup(solver)
solver.add_constraint(symetrie_fix_sem_1)
solver.add_constraint(symetrie_fix_first_player)
solver.add_constraint(symetrie_min_max)

constraint_P_player_per_group = PPlayerPerGroupConstraint(solver)
constraint_week = Week_constraint(solver)
solver.add_constraint(constraint_P_player_per_group)
solver.add_constraint(constraint_week)

solver.solve()
