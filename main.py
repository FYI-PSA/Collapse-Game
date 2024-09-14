#!/bin/python3.10
from typing import List


class GameLogic:
    Rows: int = 5
    Coloumns: int = 5
    Board: List[List[int]] = []

    def __init__(self) -> None:
        return

    def tick(self) -> None:
        print(self.Board)
        return


class GameRenderer:
    def __init__(self) -> None:
        return


def main() -> None:
    MainGame: GameLogic = GameLogic()
    MainWindow: GameRenderer = GameRenderer()
    MainGame.tick()

    type(MainGame)
    type(MainWindow)
    return


if __name__ == '__main__':
    main()
