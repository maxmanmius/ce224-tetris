import random
import consts
import time

class State:
    def start_game(self):
        self.occupied = [[False for x in range(consts.WIDTH)] for y in range(consts.HEIGHT)]
        self.lost = False
        self.activate_random_piece()

    # Create a copy of the state
    def dup(self):
        new = State()
        new.lost = self.lost
        new.occupied = [line.copy() for line in self.occupied]
        new.active = self.active.copy()
        return new

    def __eq__(self,rhs):
        return self.occupied == rhs.occupied and self.active == rhs.active and self.lost == rhs.lost

    def __hash__(self):
        # definitely not efficient, but correct and good enough for now
        return str(self.occupied).__hash__() ^ str(self.active).__hash__()

    def activate_random_piece(self):
        self.active = []
        piece = consts.PIECES[random.randrange(0,len(consts.PIECES))]
        for y,line in enumerate(piece.split("\n")):
            for x,char in enumerate(line):
                if char != " ":
                    x_pos = x-1+consts.WIDTH//2
                    if self.occupied[y][x_pos]: self.lost = True
                    self.active.append((x_pos,y))

    # determine how good of a position we are in, higher = better
    def eval(self):
    
    # Calculate the height of the tallest column
        column_heights = [0 for _ in range(consts.WIDTH)]
        for x in range(consts.WIDTH):
            for y in range(consts.HEIGHT):
                if self.occupied[y][x]:
                    column_heights[x] = consts.HEIGHT - y
                    break

        # Count the number of holes
        num_holes = 0
        for x in range(consts.WIDTH):
            for y in range(consts.HEIGHT):
                if not self.occupied[y][x] and y > 0 and self.occupied[y-1][x]:
                    num_holes += 1

        # Calculate the bumpiness of the surface
        bumpiness = sum(abs(column_heights[i]-column_heights[i-1]) for i in range(1, consts.WIDTH))

        # Calculate the number of lines cleared in the last move
        lines_cleared = 0
        for y in range(consts.HEIGHT):
            if all(self.occupied[y]):
                lines_cleared += 1

        # Calculate the final evaluation score considering max column, number of holes, bumpiness of surface, and lines cleared
        return (consts.HEIGHT - max(column_heights)) - 5*num_holes - bumpiness + 10*lines_cleared

    # place the active piece and activate a random piece, possibly causing a loss
    def place(self):
        # place the active (todo Connor)
        for space in self.active:
            self.occupied[space[1]][space[0]] = True

        # remove solid lines (todo Connor)
        for row in self.occupied:
            if all(row) == True:
                del self.occupied[self.occupied.index(row)]
                row = []
                for i in range(len(self.occupied[0])):
                    row.append(False)
                self.occupied.insert(0,row)
        self.activate_random_piece()

    def display(self,screen):
        # print the game state (todo Max)
        board = []
        board.append([])
        count = 0

        for i in range(0,12):
            board[count].append('-')

        for i in self.occupied:
         count+=1
         board.append([])
         board[count].append('|')
         for y in i:
            if y == True:
                board[count].append('█')
            else:
                board[count].append(' ')
         board[count].append('|')

        count+=1
        board.append([])
        for i in range(0,12):
            board[count].append('-')

        for i in self.active:
            board[i[1]+1][i[0]+1]=('█')


        screen.clear()
        for i in board:
            screen.addstr("".join(i))
            screen.addstr("\n")

    def move(self,direction):
        # move or rotate the active piece (or leave same if invalid move)
        # a nested function to determine whether the new location is available
        def is_valid_move(new_positions):
            for x, y in new_positions:
                # if statement to make sure that the move does not move any part out of the board or into another occupied spot
                if x < 0 or x >= consts.WIDTH or y < 0 or y >= consts.HEIGHT or (y >= 0 and self.occupied[y][x]):
                    return False
            return True

        # a list to hold the new positions of the move
        new_positions = list(self.active)

        #print("Old position: ", self.active)

        # if statement to handle the inputs
        if direction == consts.LEFT:
            new_positions = [(x - 1, y) for x, y in self.active]
        elif direction == consts.RIGHT:
            new_positions = [(x + 1, y) for x, y in self.active]
        elif direction == consts.DOWN:
            new_positions = [(x, y + 1) for x, y in self.active]
        # if rotation, swap the x and y coords for 90 degree rotation
        elif direction == consts.ROT_CLOCK or direction == consts.ROT_COUNTER:
            pivot = self.active[1]  # Assuming the second block is the pivot
            for i, (x, y) in enumerate(self.active):
                rel_x, rel_y = x - pivot[0], y - pivot[1]
                if direction == consts.ROT_CLOCK:
                    new_positions[i] = (pivot[0] - rel_y, pivot[1] + rel_x)
                else:
                    new_positions[i] = (pivot[0] + rel_y, pivot[1] - rel_x)

        # if move is valid, update coords of active piece
        if is_valid_move(new_positions):
            self.active = new_positions
            #print("New position: ", self.active)
        #else:
            #print("Did not move.")

    def search(self):
        states = [self]
        stateMoves = {self:[]}

        highestEval = float("-inf")
        bestPosition = None


        while states:
            currentState = states.pop(0)

            for move in consts.POSSIBLE_MOVES:
                nextState = currentState.dup()
                nextState.move(move)

                dont_push = False
                if move==consts.DOWN and nextState==currentState:
                    nextState.place()
                    dont_push = True
                    if highestEval == None or nextState.eval() > highestEval:
                        highestEval = nextState.eval()
                        bestPosition = nextState

                if nextState not in stateMoves:
                    stateMoves[nextState] = stateMoves[currentState]+[move]
                    if not dont_push: states.append(nextState)

        return(stateMoves[bestPosition][0])
