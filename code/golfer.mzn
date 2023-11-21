int : q;
int : w;
int : g;
int : p;

array[0..w,0..q, 0..g] of var 0..1: A;

%tout les golfeurs jouent une fois par semaine
constraint forall(i in 0..w-1, j in 0..q-1) (sum(k in 0..g-1) (A[i,j,k]) == 1);
%tout les groupes sont composé de p joueurs différents
constraint forall(i in 0..w-1, j in 0..g-1) (sum(k in 0..q-1) (A[i,k,j]) == p);
%chaque joueurs est au maximum 1 fois dans le même groupe qu'un autre
constraint forall(i in 0..q-1, j in 0..q-1) (if i != j then sum (k in 0..w-1, l in 0..g-1) (A[k,i,l]*A[k,j,l]) <= 1 else true endif);
solve satisfy;

output [
    "Element [" ++ show(i) ++ ", " ++ show(j) ++ ", " ++ show(k) ++ "] = " ++ show(A[i, j, k]) ++ "\n"
    | i in 0..w-1, j in 0..q-1, k in 0..g-1
];