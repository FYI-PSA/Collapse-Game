#!/bin/python3.10

from typing import List, Tuple, Callable
from numpy import typing as tp
from random import getrandbits
from time import sleep

import numpy as np
import sys
import os

from copy import deepcopy

try:
    from termcolor import colored  # type: ignore[pyright]
except ImportError:
    print("[#] Python couldn't find the 'termcolor' library.")
    print("[#] Running without colors.")
    sleep(1)

    def colored(text: str, color: str = 'white', attrs: List[str] = []):
        return text


# Just a headups:
#   The "black pieces" and "white pieces" refer to respectively player 2 and player 1.
#   I didn't want to use "one" and "two" in the variable names
#   So I just went with Chess terminology
# Thanks for reading my code! https://github.com/FYI-PSA/


class GameLogic:
    def __init__(self, rows: int = 5, coloumns: int = 5, board: List[List[int]] = []) -> None:
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.has_custom_board: bool = False
        # Not sure what to do with this
        # Unfortunately it's currently unimplemented
        # I don't want this in the game until someone asks
        # For the pieces I could make 1-4 be white and 5-8 be black
        _boardNumpyArray = tp.NDArray = np.array(board)
        if  (
                _boardNumpyArray.dtype != 'object'
                and
                np.shape(_boardNumpyArray) == (coloumns, rows)
                and
                all((all(isinstance(item, int) for item in row)) for row in board)
            ):

            self.board: List[List[int]] = board
            self.has_custom_board = True
        else:
            self.board: List[List[int]] = [[0]*coloumns for _ in range(rows)]

        self.board_size: Tuple[int, int] = (self.rows, self.coloumns)

        self.first_move_white: bool = True
        self.first_move_black: bool = True

        self.white_turn: bool = True
        # True for the first person's turn
        # False for the second person's turn

        self.next_autotick: bool = False
        # If a piece has reached 4 and will explode next frame

        self.four_pieces: List[Tuple[int, int]] = []
        # A list of all pieces that have reached 4

        self.white_pieces: List[Tuple[int, int]] = []
        self.black_pieces: List[Tuple[int, int]] = []

        try:
            assert (self.rows > 1) and (self.coloumns > 1)
        except AssertionError as assertion_error:
            raise ValueError("The game board must at least be 2x2") from assertion_error

        return

    def get_board(self) -> List[List[int]]:
        return self.board

    def get_board_size(self) -> Tuple[int, int]:
        return self.board_size

    def get_turn_word(self) -> str:
        if self.white_turn:
            return "White"
        return "Black"

    def get_white_turn(self) -> bool:
        """ Returns True if it's white's turn"""
        return self.white_turn

    def get_whites(self) -> List[Tuple[int, int]]:
        return self.white_pieces

    def get_blacks(self) -> List[Tuple[int, int]]:
        return self.black_pieces

    def is_valid_move(self, position: Tuple[int, int]) -> bool:
        """
            Args:
                position:
                    A tuple of (x, y)
                    x and y are zero-based indices
                    starts from top left of board
                    x gives row index, y gives coloumn index
            Returns:
                True/False for if it's a valid move
        """
        is_first_move: bool = True
        if self.white_turn:
            is_first_move = self.first_move_white
        else:
            is_first_move = self.first_move_black
        selected_piece: int = self.board[position[0]][position[1]]
        if is_first_move:
            if selected_piece == 0:
                return True
            return False

        if self.white_turn:
            return position in self.white_pieces
        else:
            return position in self.black_pieces

    def do_valid_move(self, get_input_method: Callable) -> None:
        # get_input_method needs to accept a parameter
        # that shows if it's the first time asking or second time
        if self.next_autotick:
            self._spread()
            sleep(0.5)
            if self.four_pieces == []:
                self.next_autotick = False
                self.white_turn = not self.white_turn
            return
        pos: Tuple[int, int] = get_input_method(0)
        while not self.is_valid_move(pos):
            pos = get_input_method(1)
        self._do_move(pos)
        return

    def _do_move(self, position: Tuple[int, int]) -> None:
        if self.first_move_white:
            self.board[position[0]][position[1]] = 3
            self.white_pieces.append(position)
            self.first_move_white = False
        elif self.first_move_black:
            self.board[position[0]][position[1]] = 3
            self.black_pieces.append(position)
            self.first_move_black = False
        else:
            if self._add_to(position) >= 4:
                return
            # If it needs to collapse to other pieces
            # then it shouldn't change turns until that is finished

        self.white_turn = not self.white_turn  # Toggles between True and False
        return

    def _add_to(self, position: Tuple[int, int]) -> int:
        self.board[position[0]][position[1]] += 1
        value: int = self.board[position[0]][position[1]]
        if value >= 4:
            self.next_autotick = True
            self.four_pieces.append(position)
        return value

    def _spread(self) -> None:
        # +1 c   + 1
        # -1 r   + 1
        # + 1 r  + 1
        # - 1 c  + 1

        # Side note:
        # Based on my references, even if a piece is 3 and has 2 others collapse into it,
        # it can at most turn into a four and explode like normal

        current_four_pieces: List[Tuple[int, int]] = deepcopy(self.four_pieces)
        for piece in current_four_pieces:
            r: int = piece[0]  # row
            c: int = piece[1]  # coloumn
            self.board[r][c] = 0
            self.four_pieces.remove(piece)
            if self.white_turn:
                try:
                    self.white_pieces.remove(piece)
                except ValueError:
                    pass
            else:
                try:
                    self.black_pieces.remove(piece)
                except ValueError:
                    pass

            # up
            r_2: int = r - 1
            c_2: int = c
            if not (r_2 < 0 or r_2 >= self.rows):
                self._handle_spread_adding((r_2, c_2))

            # down
            r_1: int = r + 1
            c_1: int = c
            if not (r_1 < 0 or r_1 >= self.rows):
                self._handle_spread_adding((r_1, c_1))

            # left
            r_3: int = r
            c_3: int = c - 1
            if not (c_3 < 0 or c_3 >= self.coloumns):
                self._handle_spread_adding((r_3, c_3))

            # right
            r_4: int = r
            c_4: int = c + 1
            if not (c_4 < 0 or c_4 >= self.coloumns):
                self._handle_spread_adding((r_4, c_4))

        return

    def _handle_spread_adding(self, position: Tuple[int, int]):
        self._add_to(position=position)
        if self.white_turn:
            if (position in self.black_pieces):
                self.black_pieces.remove(position)
            if (position not in self.white_pieces):
                self.white_pieces.append(position)
        else:
            if (position in self.white_pieces):
                self.white_pieces.remove(position)
            if (position not in self.black_pieces):
                self.black_pieces.append(position)
        return

    def check_gameover(self) -> int:
        if (self.white_pieces == [] and (not self.first_move_white)):
            return 2  # if black won
        elif (self.black_pieces == [] and (not self.first_move_black)):
            return 1  # if white won
        else:
            return 0  # if the game isn't over


class BoardStateData:
    # TODO:
    # -- Expand these to work with any NxM grid if N and M are provided
    #   -- Would let me use this in GameLogic for importing a board

    def __init__(self,
                 board: List[List[int]] = [[0]*5 for _ in range(5)],
                 white_pieces: List[Tuple[int, int]] = [],
                 black_pieces: List[Tuple[int, int]] = []) -> None:
        """
            Board starts as an empty 5x5 if not provided.
        """
        self.game_board = board
        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

    def set_board(self,
                  board: List[List[int]] = [[0]*5 for _ in range(5)],
                  white_pieces: List[Tuple[int, int]] = [],
                  black_pieces: List[Tuple[int, int]] = []) -> None:
        """
            Board is cleared to an empty 5x5 if not provided.
        """
        self.game_board = board
        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

    def get_board(self) -> Tuple[List[List[int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
            Returns in order: The board, White's pieces, Black's pieces.
        """
        return (self.game_board, self.white_pieces, self.black_pieces)

    def _base9_to_integer(self, b9number: int) -> int:
        result: int = 0
        right_most: int = 0
        nine_pow: int = 1
        for _ in range(25):
            b9number, right_most = divmod(b9number, 10)
            result += right_most * nine_pow
            nine_pow *= 9
        return result

    def encode_board(self, board: List[List[int]] | None, white_pieces: List[Tuple[int, int]] | None) -> bytes:
        """
            Arguments provided are optional and in the order of  The board  and  White's pieces
            If not provided, they'll use what's saved on this instance.
            Saves the board as a 25 digit base9 number, being at most 10 bytes
        """
        # Don't need to take black because if it's a piece on the board and not white, it'll just be black.
        if board is None:
            data_board: List[List[int]] = self.game_board
        else:
            data_board: List[List[int]] = board
        if white_pieces is None:
            data_white: List[Tuple[int, int]] = self.white_pieces
        else:
            data_white: List[Tuple[int, int]] = white_pieces

        number_string: int = 0
        significance: int = 1
        for indx in range(25):
            i: int = indx // 5
            j: int = indx % 5
            new_part: int = data_board[i][j]
            if (new_part > 0) and ((i, j) not in data_white):
                new_part += 4
            # no pieces: 0
            # white pieces: 1-4
            # black pieces: 5-8
            new_part *= significance
            significance *= 10
            number_string += new_part
        data: bytes = self._base9_to_integer(number_string).to_bytes(byteorder='big', length=10)
        return data

    def decode_board(self, board_10bytes: bytes) -> Tuple[List[List[int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
            Takes a 10 byte long encoded board and returns:
                The board, White's pieces, Black's pieces
        """
        board: List[List[int]] = [[0]*5 for _ in range(5)]
        white_pieces: List[Tuple[int, int]] = []
        black_pieces: List[Tuple[int, int]] = []
        encoded_num: int = int.from_bytes(board_10bytes, byteorder='big')
        data: List[int] = [0]*25
        for indx in range(25):
            if encoded_num == 0:
                continue
            encoded_num, digit = divmod(encoded_num, 9)
            data[indx] = digit
        for indx, digit in enumerate(data):
            i, j = divmod(indx, 5)
            if digit > 4:
                black_pieces.append((i, j))
                board[i][j] = digit - 4
            elif digit > 0:
                white_pieces.append((i, j))
                board[i][j] = digit
        return (board, white_pieces, black_pieces)


class AIPlayer:
    def __init__(self) -> None:
        self.board: List[List[int]] = []
        self.pieces: List[Tuple[int, int]] = []
        self.rows: int = 5
        self.coloumns: int = 5
        self.points_board: List[List[int]] = []

    def _update_board(self, new_board: List[List[int]], ai_pieces: List[Tuple[int, int]]):
        self.board = deepcopy(new_board)
        self.pieces = deepcopy(ai_pieces)
        self.rows = len(new_board)
        self.coloumns = len(new_board[0])
        self.points_board = [[0 if (i, j) in ai_pieces else -30 for j in range(self.coloumns)] for i in range(self.rows)]
        # I believe the lower bound for points on a tile is -23
        # Thus tiles unable to get picked will be -30

    def _on_edge_marker(self, point: Tuple[int, int]) -> int:
        marks: int = 0
        # points on the edge give less than 4 children so they're not very suitable
        if (point[0] == 0) or (point[0] == (self.rows - 1)):
            marks += 1
        if (point[1] == 0) or (point[1] == (self.coloumns - 1)):
            marks += 1
        return marks

    def _has_three_neighbouring_bonus(self, point: Tuple[int, int], tile: int) -> int:
        # the bonus only applies if you're a 3 and can explode onto an enemy
        if tile != 3:
            return 0
        x, y = point
        marks: int = 0
        if x > 0:
            if (self.board[x-1][y] == 3) and not ((x-1, y) in self.pieces):
                marks += 1
        if (x + 1) < self.coloumns:
            if (self.board[x+1][y] == 3) and not ((x+1, y) in self.pieces):
                marks += 1
        if y > 0:
            if (self.board[x][y-1] == 3) and not ((x, y-1) in self.pieces):
                marks += 1
        if (y + 1) < self.rows:
            if (self.board[x][y+1] == 3) and not ((x, y+1) in self.pieces):
                marks += 1
        return marks

    def _has_three_neighbouring_penalty(self, point: Tuple[int, int], tile: int) -> int:
        # the penalty only applies if you aren't a 3 so you can't explode into the 3s
        if tile == 3:
            return 0
        # this bonus applies only once
        x, y = point
        if x > 0:
            if self.board[x-1][y] == 3:
                return 1
        if (x + 1) < self.coloumns:
            if self.board[x+1][y] == 3:
                return 1
        if y > 0:
            if self.board[x][y-1] == 3:
                return 1
        if (y + 1) < self.rows:
            if self.board[x][y+1] == 3:
                return 1
        return 0

    def _qualifies_for_corner(self, point: Tuple[int, int]) -> bool:
        # neighbours should be only our colour or a 1
        x, y = point
        if x > 0:
            if (self.board[x-1][y] not in self.pieces) and (self.board[x-1][y] != 1):
                return True
        if (x + 1) < self.coloumns:
            if (self.board[x+1][y] not in self.pieces) and (self.board[x+1][y] != 1):
                return True
        if y > 0:
            if (self.board[x][y-1] not in self.pieces) and (self.board[x][y-1] != 1):
                return True
        if (y + 1) < self.rows:
            if (self.board[x][y+1] not in self.pieces) and (self.board[x][y+1] != 1):
                return True
        return False

    def _can_make_corner_full(self, point: Tuple[int, int], tile: int) -> int:
        # +2 if this is the corner to a 3, +1 if it's a corner to a 2, +0 if it's to a 1
        # the corners we want are the enemies
        # to make corner needs to not be 3
        if tile == 3:
            return 0
        if not self._qualifies_for_corner(point):
            return 0
        # it doesn't get a reward if it's a bad move
        marks: int = 0
        x, y = point
        target: Tuple[int, int] = (0, 0)
        if (x > 0) and (y > 0):
            # has top left corner
            target = (x-1, y-1)
            if target not in self.pieces:
                marks += max(0, self.board[x-1][y-1] - 1)  # if it's empty it just adds 0
        if (x > 0) and ((y + 1) < self.coloumns):
            # has top right corner
            target = (x-1, y+1)
            if target not in self.pieces:
                marks += max(0, self.board[x-1][y+1] - 1)  # if it's empty it just adds 0
        if ((x + 1) < self.rows) and (y > 0):
            # has bottom left corner
            target = (x+1, y-1)
            if target not in self.pieces:
                marks += max(0, self.board[x+1][y-1] - 1)  # if it's empty it just adds 0
        if ((x + 1) < self.rows) and ((y + 1) < self.coloumns):
            # has bottom right corner
            target = (x+1, y+1)
            if target not in self.pieces:
                marks += max(0, self.board[x+1][y+1] - 1)  # if it's empty it just adds 0
        return marks

    def _can_make_corner_burst(self, point: Tuple[int, int], tile: int) -> int:
        # -2 if this is the corner to a 3, -1 if it's a corner to a 2, -0 if it's to a 1
        # the corners we want are the enemies
        # to burst needs to be 3
        if tile != 3:
            return 0
        # I won't give the corner qualification to this because it'd still be a bad move.
        marks: int = 0
        x, y = point
        target: Tuple[int, int] = (0, 0)
        if (x > 0) and (y > 0):
            # has top left corner
            target = (x-1, y-1)
            if target not in self.pieces:
                marks += max(0, self.board[x-1][y-1] - 1)  # if it's empty it just adds 0
        if (x > 0) and ((y + 1) < self.coloumns):
            # has top right corner
            target = (x-1, y+1)
            if target not in self.pieces:
                marks += max(0, self.board[x-1][y+1] - 1)  # if it's empty it just adds 0
        if ((x + 1) < self.rows) and (y > 0):
            # has bottom left corner
            target = (x+1, y-1)
            if target not in self.pieces:
                marks += max(0, self.board[x+1][y-1] - 1)  # if it's empty it just adds 0
        if ((x + 1) < self.rows) and ((y + 1) < self.coloumns):
            # has bottom right corner
            target = (x+1, y+1)
            if target not in self.pieces:
                marks += max(0, self.board[x+1][y+1] - 1)  # if it's empty it just adds 0
        return marks

    def _assign_scores(self) -> None:
        for total_index in range(self.rows * self.coloumns):
            x: int = total_index // self.coloumns
            y: int = total_index % self.coloumns
            position: Tuple[int, int] = (x, y)
            if not (position in self.pieces):
                continue
            tile: int = self.board[x][y]
            current_score: int = deepcopy(self.points_board[x][y])
            # The way these marker functions work is that they either produce how many times the condition is met
            # 0 if the condition isn't met for a point and a natural number from 1 to however many times it was met
            # For example a point in the corner gets 2 on the edge marker
            # While a point on just an edge gets 1
            # A point in a corner gets -2 score. A point on only edges gets -1. A point in the middle gets 0
            # Some markers (like the penalty for placing next to a 3) only apply once so they just return 0 or 1
            # This also makes the code better looking than a bunch of conditions
            current_score -= 1 * self._on_edge_marker(position)  # Can apply twice
            current_score -= 3 * self._has_three_neighbouring_penalty(position, tile)  # Applices once
            current_score += 7 * self._has_three_neighbouring_bonus(position, tile)  # Applies once
            current_score += 1 * self._can_make_corner_full(position, tile)  # Applies differently based on tile
            current_score -= 1 * self._can_make_corner_burst(position, tile)  # Applies differently based on tile
            self.points_board[x][y] = deepcopy(current_score)

    def _decide_move(self) -> Tuple[int, int]:
        """
         (x, y) | x : row [up and down]
                | y : col [left and right]
        """
        if len(self.pieces) == 0:
            best_place: Tuple[int, int] = (self.rows//2, self.coloumns//2)
            if self.board[best_place[0]][best_place[1]] == 0:
                return best_place
            if (best_place[0] + 1) < self.coloumns:
                if (best_place[1] + 1) < self.rows:
                    return (best_place[0] + 1, best_place[1] + 1)
                elif best_place[1] > 0:
                    return (best_place[0] + 1, best_place[1] - 1)
            if (best_place[1] + 1) < self.rows:
                return (best_place[0] - 1, best_place[1] + 1)
            elif best_place[1] > 0:
                return (best_place[0] - 1, best_place[1] - 1)
            # This piece of code was sponsered by the assertion at the end of the GameLogic init function :)
        # This basically says that if the AI is starting,
        # pick the middle piece, biased towards the bottom right on even-tile boards.
        # Additional code to check for at least one of the corners aroud the starting position if the middle is taken
        # (In case of a small board like a 2x2)

        max_score: int = -32
        best_tiles: List[Tuple[int, int]] = []
        tile_values: List[int] = []
        for total_index in range(self.rows * self.coloumns):
            x: int = total_index // self.coloumns
            y: int = total_index % self.coloumns
            tile_position: Tuple[int, int] = (x, y)
            if not (tile_position in self.pieces):
                continue
            tile_value: int = self.board[x][y]
            tile_score: int = self.points_board[x][y]
            if tile_score == max_score:
                best_tiles.append(tile_position)
                tile_values.append(tile_value)
            elif tile_score > max_score:
                max_score = tile_score
                best_tiles.clear()
                tile_values.clear()
                best_tiles.append(tile_position)
                tile_values.append(tile_value)
        if len(best_tiles) == 1:
            return best_tiles[0]
        # If only 1 best piece, it gets the move.
        selection_tiles: List[Tuple[int, int]] = []
        for best_current_possible_value in [2, 1, 3]:
            for index, tile_value in enumerate(tile_values):
                if tile_value == best_current_possible_value:
                    selection_tiles.append(best_tiles[index])
            if len(selection_tiles) != 0:
                break
        if len(selection_tiles) == 1:
            return selection_tiles[0]
        # If having multiple best pieces of different ranks, the algorithm will do 2s as the best then 1s then 3s.
        i_mid: int = (self.rows//2)
        # if we have odd tiles, tile roof(count/2) with index floor(count/2) (what we get) is the mid.
        # if tiles are even then the one on the right of the midpoint is preferred since the midpoint is split between 2 tiles in even counts.
        # for verticals it'll be biased towards the tile below the midpoint.
        j_mid: int = (self.coloumns//2)
        minimum_distance: int = 10
        best_tile: Tuple[int, int] = (0, 0)  # This section will be biased towards the first least-distance pick in the order of counting.
        for position in selection_tiles:
            distance: int = abs(i_mid - position[0]) + abs(j_mid - position[1])
            if distance < minimum_distance:
                minimum_distance = distance
                best_tile = position
        return best_tile

    def play_turn(self, current_game_board: List[List[int]], ai_pieces: List[Tuple[int, int]]) -> Tuple[int, int]:
        self._update_board(new_board=current_game_board, ai_pieces=ai_pieces)
        self._assign_scores()
        return self._decide_move()


class ConsoleDisplay:

    # I'm sorry if colored print lines give you complaints from your type checker
    # It's fine as strings so long as you give it colors that the termcolor module recognises

    def __init__(self, rows: int, coloumns: int, spaces: str = '  ', color_white: str = 'blue', color_black: str = 'red', color_empty: str = 'dark_grey') -> None:
        self.spaces: str = spaces
        self.rows: int = rows
        self.coloumns: int = coloumns
        assert ((0 < coloumns) and (coloumns < 10))  # Ensure that the X axis doesn't go into double digits
        assert ((0 < rows) and (rows < 27))  # Ensure that the Y axis fits in the English alphabet
        assert ((rows + coloumns) > 2)  # Ensure there's at least a 1 by 2
        self.color_white: str = color_white
        self.color_black: str = color_black
        self.color_empty: str = color_empty
        self._ALPHABET_NAMING: List[str] = [chr(alpha) for alpha in range(ord('A'), ord('A')+rows)]
        # TODO:
        # -- MOST IMPORTANTLY: Start working on an actual window UI instead of terminal UI
        # - Make these styles options
        # - Add a few more options with 1234 and ۱۲۳۴
        # - Make players be able to chose with program arguments
        # - Add an "Unknwon mode" where both players run the same style and same colour
        # - Add a "Retro mode" where both players run only 1234 and IIIIIIIV and no colours. (For Powershell)
        self.WHITE_PIECES: List[str] = [' I ', 'I I', 'III', 'I V']
        # self.BLACK_PIECES: List[str] = [' ⚀ ', ' ⚁ ', ' ⚂ ', ' ⚃ ']
        self.BLACK_PIECES: List[str] = ['一 ', '二 ', '三 ', '四 ']
        if os.name == "nt":  # Is Windows
            self.clear_command: str = 'cls'
            self.win_text_attributes: List[str] = []
            try:
                os.system('color')
            except OSError:
                print('[#] The command prompt failed to set colors.')
                print('[#] Running without colors.')
                sleep(1)
        else:
            self.win_text_attributes: List[str] = ['bold']
            self.clear_command: str = 'clear'
        self.clear_method: Callable = self.no_clear_screen
        return

    def draw(self, gameboard: List[List[int]], white_pieces: List[Tuple[int, int]], black_pieces: List[Tuple[int, int]], board_size: Tuple[int, int]) -> bool:
        try:
            if (self.rows, self.coloumns) != board_size:
                print(" BOARD DOESN'T MATCH WITH PROVIDED SIZES FOR THIS CLASS ")
                raise IndexError
            numberings: List[str] = []
            for num in range(0, board_size[1]):
                n: str = str(num + 1)
                l: int = len(n)
                if l == 1:
                    n = ' ' + n + ' '
                elif l == 2:
                    n = n[0] + ' ' + n[1]
                numberings.append(n)
            first_line: str = self.spaces + "X" + self.spaces + "|" + self.spaces + self.spaces.join(numberings)
            print(first_line)
            print('-'*len(first_line))
            for row_i, row in enumerate(gameboard):
                print(self.spaces + self._ALPHABET_NAMING[row_i] + self.spaces + "|" + self.spaces, end='')
                for coloumn_i, item in enumerate(row):
                    draw_element: str = ' O '
                    piece_value: int = item - 1  # 1 2 3 4  -->  0 1 2 3
                    if piece_value > 3:
                        piece_value = 3
                    your_i: Tuple[int, int] = (row_i, coloumn_i)
                    if your_i in white_pieces:
                        draw_element = colored(self.WHITE_PIECES[piece_value], self.color_white)
                    elif your_i in black_pieces:
                        draw_element = colored(self.BLACK_PIECES[piece_value], self.color_black)
                    else:
                        draw_element = colored(draw_element, self.color_empty)
                    print(draw_element, end='')
                    if coloumn_i == (board_size[1] - 1):
                        print('\n\n', end='')
                        continue
                    print(self.spaces, end='')
            sys.stdout.flush()
            return True
        except IndexError:
            return False

    def clear_screen(self) -> None:
        try:
            os.system(self.clear_command)
            return
        except os.error:
            print("[#] CANT CLEAR SCREEN, LAUNCH WITH --no-clear-screen")
            exit(0)

    def no_clear_screen(self) -> None:
        print("\n\n")

    def figure_clearing_method(self, should_clear: bool = True) -> None:
        self.clear_method = (self.clear_screen if should_clear else self.no_clear_screen)
        return

    def draw_tick(self, GameLogicObject: GameLogic) -> None:
        board: List[List[int]] = GameLogicObject.get_board()
        board_size: Tuple[int, int] = GameLogicObject.get_board_size()
        whites: List[Tuple[int, int]] = GameLogicObject.get_whites()
        blacks: List[Tuple[int, int]] = GameLogicObject.get_blacks()
        self.clear_method()
        self.draw(board, whites, blacks, board_size)
        return

    def show_rules(self) -> None:
        print(r'=--+--> Moves should be formatted similar to   "A1"   "c 4"   "2 B"')
        print(r"   |  ")
        print(r"   |--> One alphabet and one number")
        print(r"   |  ")
        print(r"   |--> The numbers start from 1")
        print(r"   |  ")
        print(r"   |---> The order, beging uppercase, and spaces between or around")
        print(r"   |   \-> does not matter.")
        print(r"   |  ")
        print(r"   |--> Press Control+C to quit")
        print(r"   |  ")
        print(r"   |  ")
        print(r"   |  ")
        print(r"   |  ")
        print(r"  _^_ ")
        print(r"   \\------> Understood?")
        input(r'    \\------>  (Press "Enter" to play the game) ')
        return

    def give_win(self, white_won: bool) -> None:
        if white_won:
            print(colored(" [PLAYER 1] WINS ! ", self.color_white, attrs=self.win_text_attributes))
        else:
            print(colored(" [PLAYER 2] WINS ! ", self.color_black, attrs=self.win_text_attributes))

    def display_turn(self, is_white_turn: bool, is_autotick: bool) -> None:
        if not is_autotick:
            if is_white_turn:
                print(colored("Player 1's turn", self.color_white))
            else:
                print(colored("Player 2's turn", self.color_black))
        return

    def _handle_improper_input(self) -> Tuple[int, int]:
        return (-1, -1)

    def process_input(self, input_string: str) -> Tuple[int, int]:
        """
            Gets a string with only 2 valid characters
            as the index of the piece in question
            with an alphabetical index for the rows
            and a numerical index for the coloumns
            (spaces and tabs dont matter)
        """
        input_: str = input_string.upper()
        input_ = ''.join(input_.strip().split(' '))
        if len(input_) != 2:
            return self._handle_improper_input()
        first_char: str = input_[0]
        second_char: str = input_[1]
        first_i: int = -1
        second_i: int = -1
        first_was_alpha: bool = True

        try:
            first_i = self._ALPHABET_NAMING.index(first_char) + 1
        except ValueError:
            first_was_alpha = False
            try:
                first_i = self._ALPHABET_NAMING.index(second_char) + 1
            except ValueError:
                return self._handle_improper_input()

        if first_was_alpha:
            try:
                second_guy: int = int(second_char)
                # first one was rows, this is coloumns
                if second_guy > 0 and second_guy <= self.coloumns:
                    second_i = second_guy
                else:
                    raise ValueError
            except ValueError:  # From the cast of string to int
                return self._handle_improper_input()
        else:
            try:
                second_guy: int = int(first_char)
                # second one was rows, this is coloumns
                if second_guy > 0 and second_guy <= self.coloumns:
                    second_i = second_guy
                else:
                    raise ValueError
            except ValueError:  # From the cast of string to int
                return self._handle_improper_input()

        return (first_i, second_i)

    def _get_commandline_input(self, text: str = "Your Move: "):
        return input(text)

    def terminal_input(self, state: int = 0, def_text: str = "Your Move: ") -> Tuple[int, int]:
        """
         (x, y) | x : row [up and down]
                | y : col [left and right]
        """
        text: str = def_text
        bad_text: str = '[# Bad Input]\n' + def_text
        if state > 0:
            text = bad_text
        input_: str = self._get_commandline_input(text=text)
        output: Tuple[int, int] = self.process_input(input_)
        while output[0] == -1 or output[1] == -1:
            input_: str = self._get_commandline_input(text=bad_text)
            output = self.process_input(input_)
        output = (output[0] - 1, output[1] - 1)
        return output


def main(launch_args: List[str]) -> int:
    rows = 5
    coloumns = 5
    # Here's a visualisation of a 3 x 3 matrix with the row and coloumn indices:
    #  r1 c1  /  r1 c2  /  r1 c3
    #  r2 c1  /  r2 c2  /  r2 c3
    #  r3 c1  /  r3 c2  /  r3 c3
    player_white_color = 'blue'
    player_black_color = 'yellow'

    MainGame: GameLogic = GameLogic(rows=rows, coloumns=coloumns)
    MainDisplay: ConsoleDisplay = ConsoleDisplay(rows=rows, coloumns=coloumns, spaces=' '*4, color_white=player_white_color, color_black=player_black_color)

    should_clear: bool = True
    do_black_ai: bool = False
    do_white_ai: bool = False
    do_random_ai: bool = False
    for string in launch_args:
        string = string.strip().lower()
        if string == '--no-clear-screen':
            should_clear = False
        elif string == '--player2-ai':
            do_black_ai = True
        elif string == '--player1-ai':
            do_white_ai = True
        elif string == '--ai':
            do_random_ai = True

    MainDisplay.figure_clearing_method(should_clear=should_clear)

    MainDisplay.draw_tick(GameLogicObject=MainGame)
    MainDisplay.show_rules()

    i_method_: Callable = MainDisplay.terminal_input
    if do_random_ai:
        # I can also add 'or (do_black_ai and do_white_ai)' but I think it'll be fun to see how AIs play each other
        do_black_ai = (getrandbits(1) == 1)
        do_white_ai = not do_black_ai
    white_ai: AIPlayer = AIPlayer()
    black_ai: AIPlayer = AIPlayer()
    ai_move: Tuple[int, int] = (0, 0)
    # These won't do anything unless an AI is active from the launch params

    game_run: bool = True
    winner_white: bool = True
    ending_ticks: int = 10

    while game_run:
        MainDisplay.draw_tick(GameLogicObject=MainGame)

        MainDisplay.display_turn(is_white_turn=MainGame.get_white_turn(), is_autotick=MainGame.next_autotick)

        # TODO:
        # -- Move the "AI is thinking" to a proper function in ConsoleDisplay

        if MainGame.next_autotick:
            MainGame.do_valid_move(i_method_)
        elif MainGame.get_white_turn() and do_white_ai:
            print("AI is thinking.", end='', flush=True)
            sleep(0.333)
            print('.', end='', flush=True)
            sleep(0.333)
            print('.', end='', flush=True)
            sleep(0.333)
            ai_move = white_ai.play_turn(current_game_board=MainGame.get_board(), ai_pieces=MainGame.get_whites())
            dummy_input: Callable = lambda _: ai_move
            MainGame.do_valid_move(dummy_input)
        elif (not MainGame.get_white_turn()) and do_black_ai:
            print("AI is thinking.", end='', flush=True)
            sleep(0.333)
            print('.', end='', flush=True)
            sleep(0.333)
            print('.', end='', flush=True)
            sleep(0.333)
            ai_move = black_ai.play_turn(current_game_board=MainGame.get_board(), ai_pieces=MainGame.get_blacks())
            dummy_input: Callable = lambda _: ai_move
            MainGame.do_valid_move(dummy_input)
        else:
            MainGame.do_valid_move(i_method_)

        winner: int = MainGame.check_gameover()
        match winner:
            case 1:  # White win
                game_run = False
                winner_white = True
            case 2:  # Black win
                game_run = False
                winner_white = False
            case _:  # Game Continues
                pass

    # Continue for a few more ticks after the game is over for the potentially satisfying spread animation!
    MainDisplay.draw_tick(GameLogicObject=MainGame)
    while ((ending_ticks > 0) and (MainGame.next_autotick)):
        MainGame.do_valid_move(i_method_)
        MainDisplay.draw_tick(GameLogicObject=MainGame)
        ending_ticks = ending_ticks - 1

    MainDisplay.give_win(winner_white)

    print('\n\n')

    return 0


# 死/四


if __name__ == '__main__':
    try:
        exit(main(sys.argv))
    except KeyboardInterrupt:
        print(colored("\n[#] Exiting game. Goodbye.\n\n", 'red'))
        exit(1)
