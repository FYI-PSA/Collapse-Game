#!/bin/python3.10

from typing import List, Tuple, Callable
from numpy import typing as tp
from time import sleep
import numpy as np
import os
import sys
from termcolor import colored
from copy import deepcopy


# Just a headups:
#   The "black pieces" and "white pieces" refer to play 2 and player 1.
#   I didn't want to use "one" and "two" in the variable names
#   So I just went with Chess terminology
# Thanks for reading my code! more on: https://github.com/FYI-PSA/


class GameLogic:
    def __init__(self, rows: int = 5, coloumns: int = 5, board: List[List[int]] = []) -> None:
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.has_custom_board: bool = False
        # Not sure what to do with this
        # Unfortunately it's currently broken
        # Due to having no way of importing the pieces' colors into the game.
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
            self.board: List[List[int]] = [[0 for _j in range(coloumns)] for _i in range(rows)]

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

        return

    def tick(self) -> None:
        return

    def get_board(self) -> List[List[int]]:
        return self.board

    def get_board_size(self) -> Tuple[int, int]:
        return self.board_size

    def get_turn(self) -> str:
        if self.white_turn:
            return "White"
        return "Black"

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


class GameBox:

    def __init__(self, rows: int, coloumns: int, spaces: str = '  ', color_white: str = 'blue', color_black: str = 'red') -> None:
        self.spaces: str = spaces
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.color_white: str = color_white
        self.color_black: str = color_black
        self._ALPHABET_NAMING: List[str] = [chr(alpha) for alpha in range(ord('A'), ord('A')+rows)]
        self.WHITE_PIECES: List[str] = [' I ', 'I I', 'III', 'I V']
        # self.BLACK_PIECES: List[str] = [' ⚀ ', ' ⚁ ', ' ⚂ ', ' ⚃ ']
        self.BLACK_PIECES: List[str] = ['一 ', '二 ', '三 ', '四 ']
        if os.name == "nt":  # Is Windows
            self.clear_command = 'cls'
            os.system('color')
        else:
            self.clear_command = 'clear'
        return

    def draw(self, gameboard: List[List[int]], white_pieces: List[Tuple[int, int]], black_pieces: List[Tuple[int, int]], board_size: Tuple[int, int]) -> bool:
        try:
            if (self.rows, self.coloumns) != board_size:
                print(" BOARD DOESN'T MATCH WITH PROVIDED SIZES FOR THIS CLASS ")
                raise IndexError
            numberings: List[str] = []
            for num in range(0, board_size[0]):
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


def show_rules() -> None:
    print("=-+--> Moves should be formatted similar to \"A1\" or \"c 4\"")
    print("  |  ")
    print("  |--> One alphabet and one number")
    print("  |  ")
    print("  |--> The numbers start from 1")
    print("  |  ")
    print("  |---> The order, beging uppercase, and spaces between or around")
    print("  | \\-> does not matter.")
    print("  |")
    print("  |--> Press Control+C to quit")
    print(" -^- \n\n\n")
    input("--> Understood? ( Press \"Enter\" to play the game ) ")


def main(launch_args: List[str]) -> int:
    rows = 5
    coloumns = 5
    player_white_color = 'blue'
    player_black_color = 'yellow'
    MainGame: GameLogic = GameLogic(rows=rows, coloumns=coloumns)
    MainWindow: GameBox = GameBox(rows=rows, coloumns=coloumns, spaces=' '*4, color_white=player_white_color, color_black=player_black_color)

    board: List[List[int]] = MainGame.get_board()
    board_size: Tuple[int, int] = MainGame.get_board_size()
    whites: List[Tuple[int, int]] = MainGame.get_whites()
    blacks: List[Tuple[int, int]] = MainGame.get_blacks()
    MainWindow.draw(board, whites, blacks, board_size)

    show_rules()

    should_clear: bool = True
    for string in launch_args:
        string = string.strip().lower()
        if string == '--no-clear-screen':
            should_clear = False

    clear_method_: Callable = (MainWindow.clear_screen if should_clear else MainWindow.no_clear_screen)

    i_method_: Callable = MainWindow.terminal_input
    game_run: bool = True
    winner_white: bool = True
    ending_ticks: int = 6
    while game_run:
        clear_method_()
        MainWindow.draw(board, whites, blacks, board_size)
        turn: str = MainGame.get_turn()
        if not MainGame.next_autotick:
            if turn == 'White':
                print(colored("Player 1's turn", player_white_color))
            else:
                print(colored("Player 2's turn", player_black_color))
        MainGame.do_valid_move(i_method_)
        board: List[List[int]] = MainGame.get_board()
        board_size: Tuple[int, int] = MainGame.get_board_size()
        whites: List[Tuple[int, int]] = MainGame.get_whites()
        blacks: List[Tuple[int, int]] = MainGame.get_blacks()
        if (whites == [] and (not MainGame.first_move_white)):
            winner_white = False
            game_run = False
        elif (blacks == [] and (not MainGame.first_move_black)):
            winner_white = True
            game_run = False
    clear_method_()
    MainWindow.draw(board, whites, blacks, board_size)
    while ((ending_ticks > 0) and (MainGame.next_autotick)):
        MainGame.do_valid_move(i_method_)
        clear_method_()
        board: List[List[int]] = MainGame.get_board()
        board_size: Tuple[int, int] = MainGame.get_board_size()
        whites: List[Tuple[int, int]] = MainGame.get_whites()
        blacks: List[Tuple[int, int]] = MainGame.get_blacks()
        ending_ticks = ending_ticks - 1
        MainWindow.draw(board, whites, blacks, board_size)
    if winner_white:
        print(colored(" [PLAYER 1] WINS ! ", player_white_color))
    else:
        print(colored(" [PLAYER 2] WINS ! ", player_black_color))
    print('\n\n')
    return 0


# 死/四


if __name__ == '__main__':
    try:
        exit(main(sys.argv))
    except KeyboardInterrupt:
        print(colored("\n[#] Exiting game. Goodbye.\n\n", 'red'))
        exit(1)
