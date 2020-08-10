import sys

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
                        w, h = draw.textsize(letters[i][j], font=font)
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

    def enforce_node_consistency(self):  
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables: # var is variable
            for value in self.crossword.words:
                if len(value) != var.length:
                    self.domains[var].remove(value)

    

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        # If x, y are not neighbors, then no need to revise.
        overlap = self.crossword.overlaps[x, y] 
        if overlap is None:
            return False

        # If they are neighbors
        else:
            i, j = overlap
        for word_X in self.domains[x]:
            possible = False
            for word_Y in self.domains[y]:
                if word_X != word_Y and word_X[i] == word_Y[j]: # If find a possible corresponding value
                    possible = True
                    break
            if possible is False: # If no possible corresponding value
                self.domains[x].remove(word_X)
                return True
        return False 



    def ac3(self, arcs=None): 
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If `arcs` is None, begin with initial list of all arcs in the problem.
        if arcs == None:
            arcs = []
            for var1 in self.crossword.variables:
                for var2 in self.crossword.neighbors(var1):
                    arcs.append((var1, var2))
                

        for x, y in arcs:
            if self.revise(x, y):
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))
        if self.domains[x] == None: # Return False if one or more domains end up empty
            return False
        else: # Return True if arc consistency is enforced and no domains are empty
            return True

    def assignment_complete(self, assignment): 
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys(): # If the variable is not in assignment keys
                return False
            if assignment[var] not in self.crossword.words: # If the assignment value for the variable is not in data of words
                return False
        return True

    def consistent(self, assignment): 
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var1 in assignment:
            value1 = assignment[var1]
            if var1.length != len(value1): # If not consistent with unary constraint (length)
                return False 

            for var2 in assignment:
                value2 = assignment[var2]
                if var2 != var1:
                    if value2 == value1:  # If two variables' values are the same, false
                        return False

                    overlap = self.crossword.overlaps[var1, var2]
                    if overlap != None:
                        i, j = overlap
                        if value1[i] != value2[j]: # If the overlap letter is not the same
                            return False
        return True 


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = self.domains[var]
        neighbors = self.crossword.neighbors(var)  # set of neighboring variables
        counts = [] # List of number of ruled out values
        for value in values:
            count = 0
            for neighbor in neighbors:
                neighbor_values = self.domains[neighbor]
                overlaps = self.crossword.overlaps[var, neighbor]
                i, j = overlaps
                for neighbor_value in neighbor_values:
                    if neighbor_value not in assignment:
                        if value[i] != neighbor_value[j]: # If a value is ruled out
                            count += 1
                        if value == neighbor_value:
                            count += 1
            counts.append((value, count))
        counts = sorted(counts, key = lambda s: s[1]) # Sorting according to numbers of ruled out
        sorted_value = []
        for i in range(len(counts)):
            sorted_value.append(counts[i][0]) 
        return sorted_value

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        
        counts = []
        for var in self.crossword.variables:
            if var not in assignment.keys():
                num_remaining = len(self.domains[var])
                num_neighbors = -len(self.crossword.neighbors(var))  # Negative because we are going to choose the bigger one
                counts.append((var, num_remaining, num_neighbors))
        counts = sorted(counts, key = lambda s: (s[1], s[2]))  # Sort the number of remaining values first and then number of neighbors
        # sorted(s, key = lambda x: (x[1], x[2]))
        sorted_var = []
        for i in range(len(counts)):
            sorted_var.append(counts[i][0]) # Pick out the variable
        return sorted_var[0]
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is None:
                    assignment[var] = None
                else:
                    return result

        return None


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

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()


