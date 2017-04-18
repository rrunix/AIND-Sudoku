from itertools import groupby

assignments = []


def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [[r+c for r,c in zip(rows, cols)]] + [[r+c for r,c in zip(rows, reversed(cols))]]

unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def remove_posible_values(values, boxes, posibilities, exclude_boxes=[]):
    """
    Remove the possible values in the given boxes (ignoring the boxes in
    exclude_boxes)
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        boxes(array): Boxes in which we want to remove the posible values
        posibilities(array): Values to remove
        exclude_boxes(array): Boxes in the boxes array in which we don't want to
                       remove the possible values

    Returns:
        the values dictionary with the possible values removed from the given
        boxes.
    """
    for box in boxes:
        if box not in exclude_boxes:
            for positibility in posibilities:
                values[box] = values[box].replace(positibility, '')
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict(zip(boxes, [cols if c == '.' else c for c in grid]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    twins_units = []

    for units in (unitlist):

        #Group the boxes by the values (possible values a box can take)
        #So we get a tuple where the first item are the possible values a box
        #can take and the second item is the boxes with that values.

        #["A1": "23", "A2": "3", "A3": "23", "A4": "5"] =>
        #["23":["A1", "A3"], "3":["A2"], "5":["A4"]

        units_vals = sorted([(x, values[x]) for x in units], key = lambda x: x[1])
        units_vals = [(key, [x[0] for x in group]) for key, group in groupby(units_vals, key=lambda x: x[1])]

        #Filter the tuples in which the len of the first item differs from the
        #length of the second item.
        #We can only apply naked twins when the number of possible values
        #are the same as the number of boxes with tha values in a given unit.
        #(We filter those tuples where the lenght of the first item is 1 because
        #they are already fixed)

        #Ex.  ('27', ['B4', 'B7']) is naked twins wheareas
        #('27', ['B4']) or ('237', ['B4', 'B7']) is not.
        units_vals = filter(lambda x: len(x[0]) == len(x[1]) and len(x[0]) > 1, units_vals)

        if units_vals:
            twins_units.append((units, list(units_vals)))


    #Remove twins
    for twins_group in twins_units:
        units, units_vals = twins_group

        for twins in units_vals:
            values = remove_posible_values(values, units, twins[0], twins[1])

    return values

def eliminate(values):
    """Eliminate values using the eliminate strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        The values after applying the eliminate strategy
    """
    for cell in values:
        value = values[cell]
        if len(value) == 1:
            values = remove_posible_values(values, peers[cell], [value])
    return values

def only_choice(values):
    """Eliminate values using the only choice strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        The values after applying the only choice strategy
    """
    for unit in unitlist:
        for digit in cols:
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit

    return values

def reduce_puzzle(values):
    """

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Apply naked twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Use constrained DFS to search a sudoku solution

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        If the sudoku has been solved returns the sudoku values, false otherwise.
    """
    cell, posibilities = min(values.items(), key=lambda x: len(x[1]) if len(x[1]) > 1 else 11)

    if len(posibilities) == 1:
        return values
    else:
        for value in posibilities:
            values_copy = dict(values)
            values_copy[cell] = value

            reduced = reduce_puzzle(values_copy)

            if reduced:
                maybe_res = search(reduced)
                if maybe_res:
                    return maybe_res

    return False

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values_before = values.copy()

    values = search(values)

    if values:
        play_sudoku(values, values_before)
        return values

    return False

def play_sudoku(values, values_before):
    """
    Generate a sequence of assignments to go from the initial state (values_before)
    to the final state(value)
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
                      The final state of the sudoku

        values_before(dict): a dictionary of the form {'box_name': '123456789', ...}
                            The initial state of the sudoku
    """
    solved_boxes = [(box, values[box]) for box, value in values_before.items() if len(value) > 1]

    for box, value in solved_boxes:
        assign_value(values_before, box, value)

if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
        pass
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
