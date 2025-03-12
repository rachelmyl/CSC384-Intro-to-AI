 # Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.
		 
		 
var_ordering == a function with the following template
    var_ordering(csp)
        ==> returns Variable 

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.
   '''


import math


def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []                     # if no variable can be assigned
    for c in csp.get_cons_with_var(newVar): # go over each constraint
        if c.get_n_unasgn() == 0:           # get_n_unasgn() gets the # of variables that hasn't values
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())   # check condition of current assignment
            if not c.check(vals):
                return False, []            # enter if when all values are assigned
    return True, []


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return '''
    #IMPLEMENT
    
    prune = []
    
    if not newVar:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)
    
    for c in constraints:
        next_vars = c.get_unasgn_vars()
        
        if len(next_vars) == 1:
            next_var = next_vars[0]
            assigned_vars = [var for var in c.get_scope() if var != next_var]
            assigned_vals = []
            assigned_vars = c.get_scope()
            for var in assigned_vars:
                assigned_vals.append(var.get_assigned_value())   # check condition of current assignment
            for d in next_var.cur_domain():
                vals = []
                for var in c.get_scope():
                    if var == next_var:
                        vals.append(d) 
                    else:
                        vals.append(var.get_assigned_value())
                # get list of values that has been assigned and the next_var value
            
                if not c.check(vals):
                    prune.append((next_var, d))
                    next_var.prune_value(d)
                    # prune the value that doesn't satisfy constraints
                    
            if next_var.cur_domain_size() == 0:
                return False, prune
                   
    return True, prune



def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce 
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    
    prune = [] 
    
    if newVar is not None:
        queue = csp.get_cons_with_var(newVar)  
    else:
        queue = csp.get_all_cons() 
    
    
    while queue:
        constraint = queue.pop() 
        vars = constraint.get_scope()
        
        for var in vars:
            for value in var.cur_domain():
                if not constraint.has_support(var, value):
                    if var.in_cur_domain(value):  
                        var.prune_value(value)  
                        prune.append((var, value))
                        
                        # DWO
                        if var.cur_domain_size() == 0:
                            return False, prune
                        c = csp.get_cons_with_var(var)
                        for c_new in c:
                            if c_new != constraint and c_new not in queue:
                                queue.append(c_new)  # Add each constraint individually
    
    return True, prune  # Return success and the list of prunings
    '''
    if not newVar:
        queue = csp.get_all_cons()
    else:
        queue = csp.get_cons_with_var(newVar)
    
    prune = []

    while queue:
        c = queue.pop()
        for var in c.get_scope():
            for d in var.cur_domain():
                if not c.has_support(var, d):
                    prune.append((var, d))
                    var.prune_value(d)
            if var.cur_domain_size() == 0:
                return False, prune
            for c_new in csp.get_cons_with_var(var):
                if c_new != c and c_new not in queue:
                    queue.append(c_new)     # add new constraint to queue
                    
    return True, prune
    '''
    '''
    if not newVar:
        queue = csp.get_all_cons()
    else:
        queue = csp.get_cons_with_var(newVar)
    
    prune = []
    processed_constraints = set()  # Track processed constraints

    while queue:
        c = queue.pop()
        if c in processed_constraints:
            continue  # Skip already processed constraints
        processed_constraints.add(c)

        for var in c.get_scope():
            for d in var.cur_domain():
                if not c.has_support(var, d):
                    prune.append((var, d))
                    var.prune_value(d)
            if var.cur_domain_size() == 0:
                return False, prune
            for c_new in csp.get_cons_with_var(var):
                if c_new != c and c_new not in queue:
                    queue.append(c_new)  # Add new constraint to queue
                    
    return True, prune
    '''

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    #IMPLEMENT
    
    unassigned_vars = csp.get_all_unasgn_vars()
    min_domain_num = math.inf
    min_domain_var = None
    
    for var in unassigned_vars:
        if var.cur_domain < min_domain_num:
            min_domain_var = var
            min_domain_num = var.cur_domain()
    
    return min_domain_var