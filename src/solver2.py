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

        self.backtrack_domains = self.domains.copy()
        self.backtrack_schedule = self.schedule.copy()

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

        # Met a jour la liste des rencontres pour les matchs deja fixé (de par les contraintes de symetrie)
        for i in range(0,self.G*self.P):
            for week in range(0,self.W):
                for group in range(0,self.G):
                    if i in self.schedule[week][group]:
                        for player in self.schedule[week][group]:
                            if player != i:
                                self.rencontres[i].add(player)

        
        if self.consistence:
            
            self.forwardCheking()

        print("Solution:\n")
        result = ""
        for w in range(self.W):
            result += str(self.schedule[w][:]) + "\n"
        print(result)

    
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


    def forwardCheking(self):
        
        print(" ---------- Forward Cheking ---------- \n")
        

        print(self)
        # Remplis le schedule en respectant les contrainte et en mettant a jour les domaines
        # Le tableau peut ne pas etre complet
        is_consistent = True
        
        for week in range(0,self.W):
            for group in range(0,self.G):
                domains_copy = self.domains[week][group].copy()
                nb_joueur_affecte = len(self.schedule[week][group])
                if is_consistent:
                    if nb_joueur_affecte == self.P:
                        pass
                    else:
                        last_player = None
                        nb_player_manquant = self.P-nb_joueur_affecte
                        for i in range(nb_player_manquant):
                            
                            if len(self.domains[week][group])<nb_joueur_affecte+nb_player_manquant:
                                is_consistent = False
                                if last_player == None:
                                    self.backtrack(week,group,player)
                                else:
                                    self.domains[week][group] = domains_copy
                                    self.domains[week][group] -= {last_player}
                                    self.schedule[week][group].remove(last_player)
                                    self.forwardCheking()
                                
                            else:
                                player = list(self.domains[week][group])[nb_joueur_affecte+i]
                                for player2 in self.schedule[week][group]:
                                    self.rencontres[player].add(player2)
                                    self.rencontres[player2].add(player)
                                self.schedule[week][group].append(player)
                                self.updateDomains(week,group,player)
                                last_player = player
                                print("Choix player: ",player)
                                print("Domains update:\n",self)

        
        

    def backtrack(self,week,group,player):
        pass
        #TODO

        

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
