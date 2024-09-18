import random
import copy

class TeekoPlayer:
    """ An object representation for an AI game player for the game Teeko.
    """
    board = [[' ' for j in range(5)] for i in range(5)]
    pieces = ['b', 'r']

    def __init__(self):
        """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]


    def heuristic_game_value(self, state):
        if self.game_value(state) == 1 or self.game_value(state) == -1:
            return self.game_value(state) * 1000  # Emphasize terminal states

        myscore = 0
        myoppscore = 0

        for i in range(5):
            for j in range(5):
                if state[i][j] == self.my_piece:
                    myscore += self.evaluate_positions(state, i, j, self.my_piece)
                elif state[i][j] == self.opp:
                    myoppscore += self.evaluate_positions(state, i, j, self.opp)

        final_score = myscore - myoppscore
        final_score = final_score / 12  # Adjust based on max possible score
        return final_score

    def evaluate_positions(self, state, row, col, piece):
        totalscore = 0
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
        for dx, dy in directions:
            line_score = 0
            for dist in range(1, 3):  # Check up to two spaces in each direction
                nx, ny = row + dx * dist, col + dy * dist
                if 0 <= nx < 5 and 0 <= ny < 5:
                    if state[nx][ny] == piece:
                        line_score += 1
                    elif state[nx][ny] != ' ':
                        line_score -= 0.5  # Penalize if opponent blocks the line
                else:
                    line_score -= 0.5  # Boundary edge, reduce potential score slightly
            totalscore += line_score

        # Central control
        if row == 2 and col == 2:
            totalscore += 2  # Center piece gets additional score
        elif abs(row - 2) <= 1 and abs(col - 2) <= 1:
            totalscore += 1  # Near-center pieces get a bonus

        return totalscore


        


    def make_move(self, state):
        """ Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """

        # Detect drop phase
        total_pieces = sum(row.count(self.my_piece) + row.count(self.opp) for row in state)
        drop_phase = total_pieces < 8

        if not drop_phase:
            # Move phase
            best_score, best_state = self.max_value(copy.deepcopy(state), 0, float('-inf'), float('inf'))
            move = []
            for i in range(5):
                for j in range(5):
                    if state[i][j] != best_state[i][j]:
                        if state[i][j] == self.my_piece and best_state[i][j] == ' ':
                            source_row, source_col = i, j
                        elif state[i][j] == ' ' and best_state[i][j] == self.my_piece:
                            dest_row, dest_col = i, j
            move.append((dest_row, dest_col))
            move.append((source_row, source_col))
            return move
        else:
            # Drop phase
            possible_moves = [(i, j) for i in range(5) for j in range(5) if state[i][j] == ' ']
            chosen_move = random.choice(possible_moves)
            return [chosen_move]


    

    def succ(self, state):
        """ Generate all legal successors of the given board state.

        Args:
            state (list of lists): the current state of the game board.

        Returns:
            list of lists: a list of all legal board states that can result from the next move.
        """
        list_succs = []
        size = len(state)  # Assuming the board is square
        piece_count = sum(row.count(self.my_piece) for row in state)

        if piece_count < 4:  # Drop phase: add a new piece of the current player's type to any empty spot
            for i in range(size):
                for j in range(size):
                    if state[i][j] == ' ':
                        temp_board = copy.deepcopy(state)
                        temp_board[i][j] = self.my_piece
                        list_succs.append(temp_board)
        else:  # Move phase: move any one of the current player's pieces to an adjacent unoccupied location
            loc_my_pieces = [(i, j) for i in range(size) for j in range(size) if state[i][j] == self.my_piece]
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

            for x, y in loc_my_pieces:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size and state[nx][ny] == ' ':
                        temp_board = copy.deepcopy(state)
                        temp_board[x][y] = ' '
                        temp_board[nx][ny] = self.my_piece
                        list_succs.append(temp_board)

        return list_succs

        

    def max_value(self, state, depth, alpha, beta):
        terminal_value = self.game_value(state)
        if terminal_value != 0 or depth == 3:  # Terminal state or maximum depth reached
            return self.heuristic_game_value(state), state

        best_score = float('-inf')
        best_state = None
        for successor in self.succ(state):
            score, _ = self.min_value(successor, depth + 1, alpha, beta)
            if score > best_score:
                best_score = score
                best_state = successor
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break  # Beta cutoff
        return best_score, best_state

    def min_value(self, state, depth, alpha, beta):
        terminal_value = self.game_value(state)
        if terminal_value != 0 or depth == 3:  # Terminal state or maximum depth reached
            return self.heuristic_game_value(state), state

        worst_score = float('inf')
        worst_state = None
        for successor in self.succ(state):
            score, _ = self.max_value(successor, depth + 1, alpha, beta)
            if score < worst_score:
                worst_score = score
                worst_state = successor
            beta = min(beta, worst_score)
            if alpha >= beta:
                break  # Alpha cutoff
        return worst_score, worst_state


    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    def game_value(self, state):
        """ Checks the current board status for a win condition

        Args:
            state (list of lists): either the current state of the game as saved in
                this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner
        """

        size = len(state)  # Assuming square board for simplicity

        # Helper function to check lines of four pieces
        def check_line(start, delta_x, delta_y):
            x, y = start
            pieces = []
            try:
                for _ in range(4):
                    if state[x][y] == ' ':
                        return 0
                    pieces.append(state[x][y])
                    x += delta_x
                    y += delta_y
                if all(p == self.my_piece for p in pieces):
                    return 1
                if all(p == self.opp for p in pieces):
                    return -1
            except IndexError:
                return 0  # Out of bounds, no valid win
            return 0

        # Check all rows and columns
        for i in range(size):
            for j in range(size - 3):  # Only need to start checks up to the last possible start index
                result = check_line((i, j), 0, 1)  # Horizontal
                if result != 0:
                    return result
                result = check_line((j, i), 1, 0)  # Vertical
                if result != 0:
                    return result

        # Check diagonals and boxes
        for i in range(size - 3):
            for j in range(size - 3):
                result = check_line((i, j), 1, 1)  # \ diagonal
                if result != 0:
                    return result
                result = check_line((i, j + 3), 1, -1)  # / diagonal
                if result != 0:
                    return result
                # Check box wins
                if state[i][j] != ' ' and state[i][j] == state[i][j + 1] == state[i + 1][j] == state[i + 1][j + 1]:
                    return 1 if state[i][j] == self.my_piece else -1

        return 0  # No winner found


############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()
