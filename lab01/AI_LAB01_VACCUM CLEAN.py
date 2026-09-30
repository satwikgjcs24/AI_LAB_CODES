# Creating the board
board = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9']
]

player = 'X'
win = 0

# Loop for 9 moves
for move in range(9):

    # Display the board
    print()
    print(board[0][0], "|", board[0][1], "|", board[0][2])
    print("--+---+--")
    print(board[1][0], "|", board[1][1], "|", board[1][2])
    print("--+---+--")
    print(board[2][0], "|", board[2][1], "|", board[2][2])

    # Get row and column
    row = int(input("Player " + player + " enter row (1-3): "))
    col = int(input("Player " + player + " enter column (1-3): "))

    # Put X or O
    board[row - 1][col - 1] = player

    # Check rows
    for i in range(3):
        if (board[i][0] == player and
            board[i][1] == player and
            board[i][2] == player):
            win = 1

    # Check columns
    for i in range(3):
        if (board[0][i] == player and
            board[1][i] == player and
            board[2][i] == player):
            win = 1

    # Check first diagonal
    if (board[0][0] == player and
        board[1][1] == player and
        board[2][2] == player):
        win = 1

    # Check second diagonal
    if (board[0][2] == player and
        board[1][1] == player and
        board[2][0] == player):
        win = 1

    # Check winning status
    if win == 1:
        print("\nPlayer", player, "wins!")
        break

    # Change player
    if player == 'X':
        player = 'O'
    else:
        player = 'X'


# Display final board
print()
print(board[0][0], "|", board[0][1], "|", board[0][2])
print("--+---+--")
print(board[1][0], "|", board[1][1], "|", board[1][2])
print("--+---+--")
print(board[2][0], "|", board[2][1], "|", board[2][2])

# Check draw
if win == 0:
    print("\nGame Draw!")
