import sys
import pandas as pd

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())


# TODO --------------------

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        for var in self.domains:
                self.domains[var] = {word for word in self.domains[var] if len(word) == var.length}     
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps.get((x, y))
        if not overlap:
            # No overlap means nothing to revise.
            return False

        x_index, y_index = overlap
        original_domain = self.domains[x].copy()  # Keep a copy for comparison.
        
        # Only keep those x_values that have a corresponding y_value.
        self.domains[x] = {
            x_value for x_value in self.domains[x]
            if any(x_value[x_index] == y_value[y_index] for y_value in self.domains[y])
        }
        
        # Return True only if the domain was revised.
        return original_domain != self.domains[x]
            

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # Initialize queue with all arcs if no initial arcs provided
        if arcs is None:
            arcs = [
                (x, y) for x in self.domains 
                    for y in self.domains
                        if x != y 
                        and (self.crossword.overlaps.get((x, y)) is not None or self.crossword.overlaps.get((y, x)) is not None)
            ]
       
        # for arc in arcs:
        #     x, y = arc
        #     if (self.crossword.overlaps.get((x, y)) is None or self.crossword.overlaps.get((y, x)) is None):
        #         arcs.remove(arc)
        
        print(arcs)
        while arcs:
            #dequeue elemenet (FIFO) and get x and y vars
            x, y = arcs.pop(0)
            
            # If changes were made to x, proceed
            if self.revise(x, y):
                
                if len(self.domains[x]) == 0:
                    # No possible solution exists
                    return False
                
                # Enqueue all neibhgours of x - x changed so all its neighbours need to be rechecked
                neighbours_x = self.crossword.neighbors(x)  
                for z in neighbours_x:
                    if z != y:
                        arcs.append((z, x))                        
        
        domains_list = [(str(variable), values) for variable, values in self.domains.items()]
        df = pd.DataFrame(domains_list, columns=["VAR", "VALUES"])
        print(df)
        return True
                        
            
            
            


        
        
        # raise NotImplementedError


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # print(f"\nIN ASSIGNMENT_COMPLETE: \n")

        if assignment.keys() != self.domains.keys():
            # print("Dict's keys are not the same as total number of vars")
            return False
        else: 
            # print("Assignment has same number of keys. \n")
            # print(assignment, "\n")
            for var in assignment:
                print("VALUE: ", var, assignment[var])
                if not assignment[var]:
                    # print("Value is not valid")
                    return False
            return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # # NO NEED TO CHECK IF ALL VALUES OF THE DOMAIN ARE PRESENT IN "assignment" here.
        # this is being done in 'self.assignment_complete(assignment)':=

        # CHECK IF VALUES ARE UNIQUE
        values = assignment.values()
        is_unique = len(values) == len(set(values)) and not any(value == None for value in values)
        if not is_unique:
            return False

        # CHECK IF LENGTH OF VALUES CORRESPOND TO THEIR VAR'S ASSIGNED LENGTH
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        

        # CHECK IF ALL BINARY CONSTRAINTS ARE MET
        for x in assignment:
            for y in assignment:
                if x != y:
                    overlap = self.crossword.overlaps.get((x, y))
                    # Ensures overlap exists
                    if overlap is not None:  
                        index_x, index_y = overlap
                        if assignment[x][index_x] != assignment[y][index_y]:  
                            return False  # Mismatch in overlapping letters

        # If all checks are PASS, return True
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        values_x = [v for v in self.domains[var]]

        def rule_out_counter(value):
            # Initialise counter
            rule_out_count = 0

            # Iterate through all neibhouring variables of var
            neighbouring_vars = self.crossword.neighbors(var)
            for var_y in neighbouring_vars:
                values_y = [v for v in self.domains[var_y]]
                
                # Check if var crosses with var_y
                overlapping_indexes = self.crossword.overlaps.get((var, var_y))
                if overlapping_indexes:
                    index_x, index_y = overlapping_indexes

                    for value_y in values_y:
                        if value[index_x] != value_y[index_y]:
                            rule_out_count+=1 # Ruling out of word happened, update counter

            # print(f"The count for value {value} is {rule_out_count}")
            return rule_out_count
        
        return sorted(values_x, key=lambda x: rule_out_counter(x))


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Initialise assignment
        if not assignment:
            for var in self.domains:
                if len(self.domains[var]) == 1:
                    stringified = str(next(iter(self.domains[var])))
                    assignment[var] = stringified
                else:
                    assignment[var] = None

        # self.assignment_complete(assignment)
        # self.consistent(assignment)
        vars = [var for var in self.domains]
        self.order_domain_values(vars[0], assignment)

        ## PSEUDOCODE ##
        # if assignment complete:
        #     return assignment
        # var = Select-Unassigned-Var(assignment, csp)
        # for value in Domain-Values(var, assignment, csp):
        #     if value consistent with assignment:
        #         add {var = value} to assignment
        #         inferences = Inference(assignment, csp)
        #         if inferences ≠ failure:
        #             add inferences to assignment
        #         result = Backtrack(assignment, csp)
        #         if result ≠ failure:
        #             return result
        #         remove {var = value} and inferences from assignment
        # return failure

        return False
        # raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # # Print result
    # if assignment is None:
    #     print("No solution.")
    # else:
    #     creator.print(assignment)
    #     if output:
    #         creator.save(assignment, output)

if __name__ == "__main__":
    main()
