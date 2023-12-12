# The Social Golfer Problem

## Model

### Parameters

- $W$ : The number of weeks
- $G$ : The number of groups
- $P$ : The number of golfers per group

### Variable

- $Q$  = $G \times P$: The number of golfers 
- $T$ = $W \times  G$ : The number of matches
- $S$ : The $W \times G$ matrix for the schedule where each element is a set of golfers $q \in [0..Q-1]$ with a cardinality of $P$
- $M$ : The array of all matches, corresponding to the matrix S transformed in 1D array

### Necessary Constraints

- P golfers per group
    - $|S_{w,g}| = P,\ \forall w \in [0..W-1],\ \forall g \in [0..G-1]$

- All golfers play exactly one time in a week (golfer unicity and group divercity)
    - $|\bigcup_{g=0}^{G-1} S_{w,g}| = Q,\ \forall w \in [0..W-1]$

- Correspondence between M and S
    - $M_{w*G+g} = S_{w,g} \ \forall w \in [0..W-1],\ \forall g \in [0..G-1]$

- A golfer meets at most one time each golfers
    - $|M_{m1} \bigcap M_{m2}| \le 1,\ \forall m1 \in [0..T-2],\ m2 \in [1..T-1],\ m1 < m2$
