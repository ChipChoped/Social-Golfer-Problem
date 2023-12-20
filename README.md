# The Social Golfer Problem

## Getting started

### Prerequisites

A version of Python 3.10 or higher is required to run this program.

### Running the program

To run the program, run the following commands in the src directory of the project:

#### Minizinc models with Gecode solver:

```bash
python3 minizinc_gecode_solver.py -w 3 -g 3 -p 2 [OPTION]
```

#### Custom solver:

```bash
python3 custom_solver.py -w 3 -g 3 -p 2 [OPTION]
```

You can use the $--help$ option to see the list of available options.

### Generating a scv file of multiple instances results

To generate a csv file of the results of multiple instances, run the following command in the src directory of the project:

#### Minizinc models with Gecode solver:

```bash
python3 minizinc_gecode_solver_generator.py 8 5
```

#### Custom solver:

```bash
python3 custom_solver_generator.py 8 5
```

The first argument is the number of weeks and the second argument is the timeout in seconds.
(Here all the instances to 8 weeks with a timeout of 5 seconds will be generated, groups and participants <= weeks)