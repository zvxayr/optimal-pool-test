def p(p1, n):
  return 1 - (1 - p1) ** n

def eval(p1, vector):
  prod = 1
  coeff = []
  for i in vector:
    prod *= i
    coeff.append(prod)

  sample_size = prod

  probs = [p(p1, prod)]
  for i, val in enumerate(vector[0:-1]):
    probs.append(p(p1, prod / val))
    prod = prod / val

  total = 1
  for i in range(len(vector)):
    total += coeff[i] * probs[i]
  
  return total / sample_size

from functools import reduce
from gekko import GEKKO

def minimize(p1, dim=1):
  m = GEKKO() # Initialize gekko
  m.options.SOLVER=1  # APOPT is an MINLP solver

  # optional solver settings with APOPT
  m.solver_options = ['minlp_maximum_iterations 500', \
                      # minlp iterations with integer solution
                      'minlp_max_iter_with_int_sol 40', \
                      # treat minlp as nlp
                      'minlp_as_nlp 0', \
                      # nlp sub-problem max iterations
                      'nlp_maximum_iterations 100', \
                      # 1 = depth first, 2 = breadth first
                      'minlp_branch_method 1', \
                      # maximum deviation from whole number
                      'minlp_integer_tol 1.0', \
                      # covergence tolerance
                      'minlp_gap_tol 0.01']

  # Initialize variables
  vars = [m.Var(value=2, lb=2, integer=True) for i in range(dim)]

  #m.Equation(reduce(lambda a, b: a * b, vars)<=100) # Uncomment for constrained optimization
  m.Obj(eval(p1, vars)) # Objective
  m.solve(disp=False) # Solve

  return {
      'ratio': m.options.objfcnval,
      'values': [int(var.value[0]) for var in vars]
  }

def optimize(p1):
  solution = minimize(p1, 1)
  history = [solution]

  nextDim = 2
  while True:
    try:
      newSolution = minimize(p1, nextDim)
    except:
      break
      
    if newSolution['ratio'] > solution['ratio']:
      break
    
    history.append(newSolution)
    solution = newSolution
    nextDim += 1
  
  return history

history = []
optimal_ratios = []
for i in range(1, 307):
  solutions = optimize(i / 1000)
  history.append(solutions)
  optimal_ratios.append(solutions[-1]['ratio'])
  print(f"{i/10:>4}: [{', '.join(str(x) for x in solutions[-1]['values']):^18}] | ratio: {optimal_ratios[-1]}")
