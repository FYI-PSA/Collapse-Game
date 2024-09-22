#!/bin/python3.10

from typing import List, Tuple, Callable
from numpy import typing as tp
from time import sleep
import numpy as np
import os
import sys
from termcolor import colored
from copy import deepcopy


class GameLogic:
    def __init__(self, rows: int = 5, coloumns: int = 5, board: List[List[int]] = []) -> None:
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.has_custom_board: bool = False
        # Not sure what to do with this,
        #  but it should be fairly easy to edit the main function
        #  or import this file somewhere else
        #  and give the GameLogic your own 2D array this way if you need to
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
            sleep(0.25)
            self._spread()
            sleep(0.25)
            if self.four_pieces == []:
                self.next_autotick = False
                self.white_turn = not self.white_turn
            return
        pos: Tuple[int, int] = get_input_method(0)
        while not self.is_valid_move(pos):
            pos = get_input_method(1)
        self._do_move(pos)

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
        # Based on my references, even if a piece is 3 and has 2 others collapse into it,
        # it can at most turn into a four and explode like normal
        current_four_pieces: List[Tuple[int, int]] = deepcopy(self.four_pieces)
        for piece in current_four_pieces:
            r: int = piece[0]
            c: int = piece[1]

            # up
            r_1: int = r + 1
            c_1: int = c
            if not (r_1 < 0 or r_1 >= self.rows):
                self._add_to(position=(r_1, c_1))
                if piece in self.white_pieces:
                    if (r_1, c_1) in self.black_pieces:
                        self.black_pieces.remove((r_1, c_1))
                        self.white_pieces.append((r_1, c_1))
                    elif not (r_1, c_1) in self.white_pieces:
                        self.white_pieces.append((r_1, c_1))
                else:  # If it's reached 4 and it's not white it has to be black
                    if (r_1, c_1) in self.white_pieces:
                        self.white_pieces.remove((r_1, c_1))
                        self.black_pieces.append((r_1, c_1))
                    elif not (r_1, c_1) in self.white_pieces:
                        self.black_pieces.append((r_1, c_1))

            # down
            r_2: int = r - 1
            c_2: int = c
            if not (r_2 < 0 or r_2 >= self.rows):
                self._add_to(position=(r_2, c_2))
                if piece in self.white_pieces:
                    if (r_2, c_2) in self.black_pieces:
                        self.black_pieces.remove((r_2, c_2))
                        self.white_pieces.append((r_2, c_2))
                    elif not (r_2, c_2) in self.white_pieces:
                        self.white_pieces.append((r_2, c_2))
                else:  # If it's reached 4 and it's not white it has to be black
                    if (r_2, c_2) in self.white_pieces:
                        self.white_pieces.remove((r_2, c_2))
                        self.black_pieces.append((r_2, c_2))
                    elif not (r_2, c_2) in self.white_pieces:
                        self.black_pieces.append((r_2, c_2))

            # left
            r_3: int = r
            c_3: int = c - 1
            if not (c_3 < 0 or c_3 >= self.coloumns):
                self._add_to(position=(r_3, c_3))
                if piece in self.white_pieces:
                    if (r_3, c_3) in self.black_pieces:
                        self.black_pieces.remove((r_3, c_3))
                        self.white_pieces.append((r_3, c_3))
                    elif not (r_3, c_3) in self.white_pieces:
                        self.white_pieces.append((r_3, c_3))
                else:  # If it's reached 4 and it's not white it has to be black
                    if (r_3, c_3) in self.white_pieces:
                        self.white_pieces.remove((r_3, c_3))
                        self.black_pieces.append((r_3, c_3))
                    elif not (r_3, c_3) in self.white_pieces:
                        self.black_pieces.append((r_3, c_3))

            # right
            r_4: int = r
            c_4: int = c + 1
            if not (c_4 < 0 or c_4 >= self.coloumns):
                self._add_to(position=(r_4, c_4))
                if piece in self.white_pieces:
                    if (r_4, c_4) in self.black_pieces:
                        self.black_pieces.remove((r_4, c_4))
                        self.white_pieces.append((r_4, c_4))
                    elif not (r_4, c_4) in self.white_pieces:
                        self.white_pieces.append((r_4, c_4))
                else:  # If it's reached 4 and it's not white it has to be black
                    if (r_4, c_4) in self.white_pieces:
                        self.white_pieces.remove((r_4, c_4))
                        self.black_pieces.append((r_4, c_4))
                    elif not (r_4, c_4) in self.white_pieces:
                        self.black_pieces.append((r_4, c_4))

            self.board[r][c] = 0
            if self.white_turn:
                self.white_pieces.remove(piece)
            else:
                self.black_pieces.remove(piece)
            self.four_pieces.remove(piece)
        
        return


class GameBox:

    def __init__(self, rows: int, coloumns: int, spaces: str = '  ', color_1: str = 'blue', color_2: str = 'red') -> None:
        self.spaces: str = spaces
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.color_1: str = color_1
        self.color_2: str = color_2
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
                    your_i: Tuple[int, int] = (row_i, coloumn_i)
                    if your_i in white_pieces:
                        draw_element = colored(self.WHITE_PIECES[item-1], self.color_1)
                    elif your_i in black_pieces:
                        draw_element = colored(self.BLACK_PIECES[item-1], self.color_2)
                    print(draw_element, end='')
                    if coloumn_i == (board_size[1] - 1):
                        print('\n\n', end='')
                        continue
                    print(self.spaces, end='')
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


# BUG : WHEN TWO PIECES EXPLODE INTO EACH OTHER, ONE OF THEM TURNS INTO A FAKE FOUR
#  - VISUALLY ANNOYING AND GIVES WHOEVER'S COLOR IT BELONGS TO THE ABILITY TO PLACE ITSELF DOWN 


def main(launch_args: List[str]) -> int:
    rows = 5
    coloumns = 5
    p_1_c = 'blue'
    p_2_c = 'yellow'
    # custom_board: List[List[int]] = [[2 for j in range(5)] for i in range(5)]
    # MainGame: GameLogic = GameLogic(rows=Rows, coloumns=coloumns, board=custom_board)
    MainGame: GameLogic = GameLogic(rows=rows, coloumns=coloumns)
    MainWindow: GameBox = GameBox(rows=rows, coloumns=coloumns, spaces=' '*4, color_1=p_1_c, color_2=p_2_c)

    board: List[List[int]] = MainGame.get_board()
    board_size: Tuple[int, int] = MainGame.get_board_size()
    whites: List[Tuple[int, int]] = MainGame.get_whites()
    blacks: List[Tuple[int, int]] = MainGame.get_blacks()
    MainWindow.draw(board, whites, blacks, board_size)

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

    should_clear: bool = True
    for string in launch_args:
        string = string.strip().lower()
        if string == '--no-clear-screen':
            should_clear = False

    clear_method_: Callable = (MainWindow.clear_screen if should_clear else MainWindow.no_clear_screen)

    i_method_: Callable = MainWindow.terminal_input
    game_run: bool = True
    winner_white: bool = True
    while game_run:
        clear_method_()
        MainWindow.draw(board, whites, blacks, board_size)
        turn: str = MainGame.get_turn()
        if turn == 'White':
            print(colored("Player 1's turn", p_1_c))
        else:
            print(colored("Player 2's turn", p_2_c))
        MainGame.do_valid_move(i_method_)
        board: List[List[int]] = MainGame.get_board()
        board_size: Tuple[int, int] = MainGame.get_board_size()
        whites: List[Tuple[int, int]] = MainGame.get_whites()
        blacks: List[Tuple[int, int]] = MainGame.get_blacks()
        if whites == [] and not MainGame.first_move_white:
            winner_white = False
            game_run = False
        elif blacks == [] and not MainGame.first_move_black:
            winner_white = True
            game_run = False
    clear_method_()
    MainWindow.draw(board, whites, blacks, board_size)
    if winner_white:
        print(colored(" [PLAYER 1] WINS ! ", p_1_c))
    else:
        print(colored(" [PLAYER 2] WINS ! ", p_2_c))
    print('\n\n')
    return 0


# 死/四

if __name__ == '__main__':
    exit(main(sys.argv))
