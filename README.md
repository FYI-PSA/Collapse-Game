# Collapse Game
 A game found on the internet commonly as "Chain Reaction" 

 My version is based on some mobile apps like ["2 Player Games: The Challenge"](https://play.google.com/store/apps/details?id=com.JindoBlu.TwoPlayerGamesChallenge) and ["1 2 3 4 Player Games"](https://play.google.com/store/apps/details?id=com.JindoBlu.FourPlayers) (On those apps it's named "Color Wars")

## Rules
 - First move for both players they can place their piece anywhere (except the other person's first piece)
 - On all other moves a player must only place on their own already placed pieces
 - Once a peace reaches 4, it will explode into it's 4 neighbours (Up Left Right Down) and will add 1 to them
    - This action also makes the peice yours, so watch out for your enemey!
 - **You win once you capture all of your enemy's pieces**

## Usage
- Clone the project, install the requirements, and run the project: 
    - Clone the repository and enter the directory:
    ```sh
    git clone https://github.com/FYI-PSA/Collapse-Game.git && cd Collapse-Game
    ```
    - Install the required python packages:
    ```sh
    python -m pip install -r ./requirements.txt
    ```
    - Then run the file:
    ```sh
    python main.py
    ```
