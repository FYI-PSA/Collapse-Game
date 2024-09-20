#!/bin/python3.11

from typing import List, Tuple, Callable
from numpy import typing as tp
import numpy as np


class GameLogic:

    def __init__(self, rows: int = 5, coloumns: int = 5, board: List[List[int]] = []) -> None:
        self.rows: int = rows
        self.coloumns: int = coloumns
        self.has_custom_board: bool = False  # NOT IMPLEMENTED YET
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
            self.board: List[List[int]] = [[0 for j in range(coloumns)] for i in range(rows)]

        self.first_move_white: bool = True
        self.first_move_black: bool = True

        self.white_turn: bool = True
        # True for the first person's turn
        # False for the second person's turn

        self.white_pieces: List[Tuple[int, int]] = []
        self.black_pieces: List[Tuple[int, int]] = []

        return

    def tick(self) -> None:
        return

    def get_board(self) -> List[List[int]]:
        return self.board

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
            pass
        else:
            pass

        self.white_turn = not self.white_turn  # Toggles between True and False
        return True

    def do_valid_move(self, get_input_method: Callable):
        pos: Tuple[int, int] = get_input_method()
        while not self.is_valid_move(pos):
            pos = get_input_method()
        self._do_move(pos)

    def _do_move(self, position: Tuple[int, int]):
        if self.first_move_white:
            self.board[position[0]][position[1]] = 3
            self.white_pieces.append(position)
            self.first_move_white = False
        elif self.first_move_black:
            self.board[position[0]][position[1]] = 3
            self.black_pieces.append(position)
            self.first_move_black = False
        else:
            print(" not implemented yet ")


class GameBox:

    def __init__(self, rows: int, coloumns: int, spaces: str = '  ') -> None:
        self.spaces: str = spaces
        self.rows: int = rows
        self.coloumns: int = coloumns
        self._ALPHABET_NAMING: List[str] = [chr(alpha) for alpha in range(ord('A'), ord('A')+rows)]
        self.WHITE_PIECES: List[str] = ['1', '2', '3', '4']
        self.BLACK_PIECES: List[str] = ['一', '二', '三', '四']
        return

    def draw(self, gameboard: List[List[int]], white_pieces: List[Tuple[int, int]], black_pieces: List[Tuple[int, int]]) -> bool:
        try:
            board_shape: tp.ArrayLike = np.shape(np.array(gameboard))
            if (self.rows, self.coloumns) != tuple(board_shape):
                print(" BOARD DOESN'T MATCH WITH PROVIDED SIZES FOR THIS CLASS ")
                raise IndexError
            numberings: List[str] = [str(i+1) for i in range(0, board_shape[0])]
            first_line: str = self.spaces + "X" + self.spaces + "|" + self.spaces + self.spaces.join(numberings)
            print(first_line)
            print('-'*len(first_line))
            for row_i, row in enumerate(gameboard):
                print(self.spaces + self._ALPHABET_NAMING[row_i] + self.spaces + "|" + self.spaces, end='')
                for coloumn_i, item in enumerate(row):
                    draw_element: str = 'O'
                    your_i: Tuple[int, int] = (row_i, coloumn_i)
                    if your_i in white_pieces:
                        draw_element = self.WHITE_PIECES[item-1]
                    elif your_i in black_pieces:
                        draw_element = self.BLACK_PIECES[item-1]
                    print(draw_element, end='')
                    if coloumn_i == (board_shape[1] - 1):
                        print('\n\n', end='')
                        continue
                    print(self.spaces, end='')
            return True
        except IndexError:
            return False

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

    def terminal_input(self, text: str = "Your Move: ") -> Tuple[int, int]:
        """
         (x, y) | x : row [up and down]
                | y : col [left and right]
        """
        input_: str = self._get_commandline_input(text=text)
        output: Tuple[int, int] = self.process_input(input_)
        while output[0] == -1 or output[1] == -1:
            input_: str = self._get_commandline_input(text=text)
            output = self.process_input(input_)
        output = (output[0] - 1, output[1] - 1)
        return output


# TODO:
    # Add a "command line input" method for GameBox
    # done
    #  > receive infinite input until it satisfies process_input and adjust them for starting from 0 for A and 1
    # done
    # Add a "play move" function to the main file, uses the above method + the process_input function + checking for valid moves using the GameLogic
    #  to make the player have to chose a move until it's a valid move and then play it (and maybe draw it afterwise)


def main() -> None:
    rows = 5
    coloumns = 5
    # custom_board: List[List[int]] = [[2 for j in range(5)] for i in range(5)]
    # MainGame: GameLogic = GameLogic(rows=Rows, coloumns=coloumns, board=custom_board)
    MainGame: GameLogic = GameLogic(rows=rows, coloumns=coloumns)
    MainWindow: GameBox = GameBox(rows=rows, coloumns=coloumns, spaces=' '*4)

    board: List[List[int]] = MainGame.get_board()
    whites: List[Tuple[int, int]] = MainGame.get_whites()
    blacks: List[Tuple[int, int]] = MainGame.get_blacks()
    MainWindow.draw(board, whites, blacks)

    print("=-+--> Moves should be formatted similar to \"A1\" or \"c 4\"")
    print("  |--> One alphabet and one number")
    print("  |--> The numbers start from 1")
    print("  |--> The order, beging uppercase, and spaces between or around")
    print("  |--> does not matter.")
    print("  |")
    print("  |--> Press Control+C to quit")
    print(" -^- \n\n")

    i_method_ = MainWindow.terminal_input
    for _ in range(0, 200):
        MainGame.do_valid_move(i_method_)
        board: List[List[int]] = MainGame.get_board()
        whites: List[Tuple[int, int]] = MainGame.get_whites()
        blacks: List[Tuple[int, int]] = MainGame.get_blacks()
        MainWindow.draw(board, whites, blacks)
    return


if __name__ == '__main__':
    main()
