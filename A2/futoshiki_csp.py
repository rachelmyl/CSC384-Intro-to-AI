# Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary
      all-different constraints for both the row and column constraints.
    
    The input board is specified as a list of n lists. Each of the n lists
    represents a row of the board. If a 0 is in the list it represents an empty
    cell. Otherwise if a number between 1--n is in the list then this
    represents a pre-set board position.

    Each list is of length 2n-1, with each space on the board being separated
    by the potential inequality constraints. '>' denotes that the previous
    space must be bigger than the next space; '<' denotes that the previous
    space must be smaller than the next; '.' denotes that there is no
    inequality constraint.

    E.g., the board

    -------
    | > |2|
    | | | |
    | | < |
    -------
    would be represented by the list of lists

    [[0,>,0,.,2],
     [0,.,0,.,0],
     [0,.,0,<,0]]

'''
import cspbase
import itertools


def futoshiki_csp_model_1(futo_grid):
    ##IMPLEMENT
    '''
    A model of a Futoshiki grid built using only binary not-equal constraints 
    for both the row and column constraints.
   
    All models need to return a CSP object, and a list of lists of Variable objects
    representing the board. The returned list of lists is used to access the
    solution.
    
    Input: futo_grid: 2d list
    
    Ouput: 
    - CSP
    - list of variable objects
    '''
    
    csp = cspbase.CSP("Futoshiki_1")
    vars = []
    n = len(futo_grid)
    
    for i in range(n):
        row = []
        for j in range(n):
            if futo_grid[i][2*j] != 0:  # for those predetermined values 
                domain = [futo_grid[i][2*j]]  # Wrap the value in a list
            else:
                domain = list(range(1, n+1))  # Full domain for empty cells
            var = cspbase.Variable(f"Row{i}, Col{2*j}", domain)
            row.append(var)
            csp.add_var(var)
        vars.append(row)
    
    for i in range(n):
        for j in range(n):
            for k in range(j+1, n):
                # same row values not equal
                constraint = cspbase.Constraint(f"Row_{i}_Variable Col{j} and {k}", [vars[i][j], vars[i][k]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[i][k].domain() if x != y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)
            
            for k in range(i+1, n):
                # same column values not equal
                constraint = cspbase.Constraint(f"Col_{j}_Variable Row{i} and {k}", [vars[i][j], vars[k][j]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[k][j].domain() if x != y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)
            
    for i in range(n):
        for j in range(n-1):
            if futo_grid[i][2*j+1] == '>':
                constraint = cspbase.Constraint(f"Inequality > Row_{i}_Variable Col{2*j} and {2*j+2}", [vars[i][j], vars[i][j+1]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[i][j+1].domain() if x > y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)
            elif futo_grid[i][2*j+1] == '<':
                constraint = cspbase.Constraint(f"Inequality < Row_{i}_Variable Col{2*j} and {2*j+2}", [vars[i][j], vars[i][j+1]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[i][j+1].domain() if x < y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)
                
    return csp, vars



def futoshiki_csp_model_2(futo_grid):
    ##IMPLEMENT
    '''
    A model of a Futoshiki grid built using only n-ary
    all-different constraints for both the row and column constraints.
   
    All models need to return a CSP object, and a list of lists of Variable objects
    representing the board. The returned list of lists is used to access the
    solution.
    
    Input: futo_grid: 2d list
    
    Ouput: 
    - CSP
    - list of variable objects
    '''
    
    csp = cspbase.CSP("Futoshiki_2")
    vars = []
    n = len(futo_grid)
    
    for i in range(n):
        row = []
        for j in range(n):
            if futo_grid[i][2*j] != 0:  # for those predetermined values 
                domain = [futo_grid[i][2*j]]
            else:
                domain = list(range(1, n+1))
            var = cspbase.Variable(f"Row{i}, Col{2*j}", domain)
            row.append(var)
            csp.add_var(var)
        vars.append(row)
        
    for i in range(n):
        # Row constraints
        row_vars = vars[i]
        constraint = cspbase.Constraint(f"Row_{i}", row_vars)
        tuples = list(itertools.permutations(range(1, n + 1), n))
        constraint.add_satisfying_tuples(tuples)
        csp.add_constraint(constraint)
        
        # Column constraints
        col_vars = [vars[j][i] for j in range(n)]
        constraint = cspbase.Constraint(f"Col_{i}", col_vars)
        tuples = list(itertools.permutations(range(1, n + 1), n))
        constraint.add_satisfying_tuples(tuples)
        csp.add_constraint(constraint)

    # Add inequality constraints based on the grid
    for i in range(n):
        for j in range(n - 1):
            if futo_grid[i][2 * j + 1] == '>':
                constraint = cspbase.Constraint(f"Ineq_Row_{i}_{j}_>", [vars[i][j], vars[i][j + 1]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[i][j + 1].domain() if x > y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)
            elif futo_grid[i][2 * j + 1] == '<':
                constraint = cspbase.Constraint(f"Ineq_Row_{i}_{j}_<", [vars[i][j], vars[i][j + 1]])
                tuples = [(x, y) for x in vars[i][j].domain() for y in vars[i][j + 1].domain() if x < y]
                constraint.add_satisfying_tuples(tuples)
                csp.add_constraint(constraint)

    return csp, vars