% The Social Golfer Problem
% Parameters
int: W; % The number of weeks
int: G; % The number of groups
int: P; % The number of golfers per group


% Variables
int: Q = G * P; % The number of golfers
int: T = W * G; % The number of matches
set of int: Golfers = 0..Q-1;
set of int: Weeks = 0..W-1;
set of int: Groups = 0..G-1;
array[Weeks, Groups] of var set of Golfers: S; % The schedule matrix
array[0..T-1] of var set of Golfers: M; % The array of all match, corresponding to the matrix S transformed in 1D array matrix

% Constraints
% P golfers per group
constraint forall(w in Weeks, g in Groups) (
    card(S[w,g]) = P
);

% All golfers play exactly one time in a week
constraint forall(w in Weeks) (
    card(array_union([S[w,g] | g in Groups])) = Q

);

% Correspondence between M and S
constraint forall(w in Weeks, g in Groups) (
    M[w*G+g] = S[w,g]
);

% A golfer meets at most one time each golfer
constraint forall(m1 in 0..T-2, m2 in 1..T-1 where m1 < m2) (
    card(M[m1] intersect M[m2]) <= 1
);

% Symmetry-breaking constraint for the first week
constraint forall(g in Groups) (
    forall(i in 0..P-1) (
        S[0, g] = S[0, g] union {g*P + i}
    )
);

% Symmetry-breaking constraint for the first player of all group after week 0
constraint forall(w in 1..W-1) (
    forall(g in Groups where g<P) (
          S[w, g] intersect {g} = {g} 
    )
);

% Solve
solve satisfy;

% Output

