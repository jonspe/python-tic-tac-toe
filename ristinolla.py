# TIE-02101: Johdatus ohjelmointiin
# Skaalautuva käyttöliittymäprojekti 13.10.
# Joona Perasto
#
# Ristinollapeli, jossa pyritään saamaan viisi peräkkäistä pelimerkkiä.
# Vuoro vaihtuu aina siirron jälkeen, alareunassa näkyvä kuva ja teksti
# kertovat vuoron. Voittajan pelimerkit muuttavat väriä ja uuden pelin
# voi aloittaa ylhäällä olevaa nappia. Uuden pelin aloittaa edellisen pelin
# hävinnyt pelaaja. Tasapeli, jos lauta täynnä ilman voittoa, mikä on
# tavallisessa pelissä erittäin epätodennäköistä.
#
# Halutessaan pelin asetuksia voi muuttaa 'settings.py' tiedostosta.


from tkinter import *
from enum import Enum
from settings import *
import winsound


# Enum values convenient for getting player by turn: MarkerType(turn % 2)
class MarkerType(Enum):
    NONE = -1
    CROSS = 0
    CIRCLE = 1


# Enum used to determine the state the game is currently in
class GameState(Enum):
    PLAYING = 0
    WINNER = 1
    TIE = 2


def create_grid(size_x, size_y, default=None):
    """Create and return 2-dimensional grid filled with default value.

    :param size_x: int
    :param size_y: int
    :param default: value to fill
    :return: list[size_y][size_x]
    """
    return [[default for _x in range(size_y)] for _y in range(size_x)]


class ButtonBar(Frame):
    """GUI-component representing the top bar with button for new game."""

    def __init__(self, parent, app, *args, **kwargs):
        """Create button to start new game, link click event to app.

        :param parent: parent of frame
        :param app: the main Application
        :param args: arguments for base class
        :param kwargs: arguments for base class
        """
        Frame.__init__(self, parent, *args, **kwargs)
        self.pack_propagate(False)
        self.configure(bg=Color.MID_TONE, height=64)

        def new_game():
            app.reset_board()
            self.set_disabled(True)

        self.__button_new_game = Button(
            self,
            text="New Game",
            font=("Helvetica", 16, "normal"),
            activebackground=Color.MID_TONE,
            bg=Color.MID_TONE,
            bd=2,
            command=new_game
        )

        self.set_disabled(True)
        self.__button_new_game.pack(
            padx=(Pad.BORDER_PADDING, Pad.BORDER_PADDING),
            side=TOP, fill=BOTH, expand=1
        )

    def set_disabled(self, disabled):
        """Set button disabled or active according to bool argument.

        :param disabled: bool
        :return:
        """
        if disabled:
            self.__button_new_game.configure(state=DISABLED, text="Playing...")
        else:
            self.__button_new_game.configure(state=ACTIVE, text="New Game")


class Tile(Label):
    """GUI-component representing a single grid cell of the game board."""

    def __init__(self, x, y, parent, game, app, *args, **kwargs):
        """Creates tile at position x, y.

        Adds mouse-event listeners to Tile and links click event to app,
        so the app can respond to clicks.

        :param x: position y: int
        :param y: position y: int
        :param parent: parent of tile
        :param game: the game linked to app: Game
        :param app: the main application: Application
        :param args: arguments for base class
        :param kwargs: arguments for base class
        """
        Label.__init__(self, parent, *args, **kwargs)
        self.configure(bg=Color.MID_TONE)

        # Helper to create mouse-event listeners for tiles, so they don't
        # trigger when game has ended.
        def create_marker_listener(func):
            def listener(_event):
                if game.get_state() is GameState.PLAYING:
                    func(_event)

            return listener

        # Highlight tile when mouse is over it
        def mouse_over(_event):
            if game.get_tile(x, y) is MarkerType.NONE:
                self.configure(bg=Color.HIGH_TONE)

        # Return back to normal when mouse off
        def mouse_leave(_event):
            self.configure(bg=Color.MID_TONE)

        self.bind("<Enter>", create_marker_listener(mouse_over))
        self.bind("<Leave>", create_marker_listener(mouse_leave))
        self.bind("<Button-1>", create_marker_listener(
            lambda _e: app.grid_clicked(x, y)))
        self.bind("<ButtonRelease-1>",
                  create_marker_listener(mouse_leave))


class TileGrid(Frame):
    """GUI-component representing the middle game grid filled with tiles."""

    def __init__(self, parent, game, app, *args, **kwargs):
        """Creates the game board grid, where all the magic happens.

        :param parent: parent of frame
        :param game: the game linked to app: Game
        :param app: the main application: Application
        :param args: arguments for base class
        :param kwargs: arguments for base class
        """
        Frame.__init__(self, parent, *args, **kwargs)
        self.configure(bg=Color.DARK_TONE)

        self.__marker_images = {
            MarkerType.NONE: PhotoImage(file="images/e.gif"),
            MarkerType.CROSS: PhotoImage(file="images/x.gif"),
            MarkerType.CIRCLE: PhotoImage(file="images/o.gif"),
        }

        self.__tile_grid = create_grid(Settings.SIZE_X, Settings.SIZE_Y)

        for y in range(Settings.SIZE_Y):
            # Remove ugly left border of grid
            if y == 0:
                pad = (0, 0)
            else:
                pad = (Pad.GRID_LINE, 0)

            # Container to store a row of tiles horizontally
            row_container = Frame(self, bg=Color.DARK_TONE)
            row_container.pack(pady=pad)

            for x in range(Settings.SIZE_X):
                # Remove ugly top border of grid
                if x == 0:
                    pad = (0, 0)
                else:
                    pad = (Pad.GRID_LINE, 0)

                self.__tile_grid[y][x] = Tile(x, y, row_container, game, app)
                self.__tile_grid[y][x].pack(side=LEFT, padx=pad)

        # Init by setting blank images to all tiles
        self.clear_tiles()

    def highlight_tiles(self, tiles):
        """Highlight given tiles to signal the winning marks.

        :param tiles: list of tuples (x, y)
        :return:
        """
        for tile in tiles:
            self.set_tile_color(tile[0], tile[1], Color.WIN_COLOR)

    def clear_tiles(self):
        """Set all tile images to blank.

        :return:
        """
        for y in range(Settings.SIZE_Y):
            for x in range(Settings.SIZE_X):
                self.__tile_grid[y][x].configure(
                    image=self.__marker_images[MarkerType.NONE])

    def set_tile_color(self, x, y, color):
        """Set tile color at coordinates x, y to color.

        :param x: int: coord x
        :param y: int: coord y
        :param color: string in color hex format, ex. "#FFFFFF"
        :return:
        """
        self.__tile_grid[y][x].configure(bg=color)

    def set_tile_marker(self, x, y, marker):
        """Set tile image at coordinates x, y by enum MarkerType.

        :param x: coord x
        :param y: coord y
        :param marker: MarkerType marker to set tile image to
        :return:
        """
        self.__tile_grid[y][x].configure(image=self.__marker_images[marker])


class InfoBar(Frame):
    """GUI-component for displaying turn info at the bottom of the window.

    Notable features:
        InfoBar.show_results(game_state, winner, loser) -> void
            Display winner info by given MarkerType arguments.

        InfoBar.update_info(current_player, next_player) -> void
            Update turn info by given MarkerType arguments.
    """

    def __init__(self, parent, *args, **kwargs):
        """Create all necessary GUI-components for InfoBar.

        :param parent: parent of frame
        :param args: arguments for base class
        :param kwargs: arguments for base class
        """
        Frame.__init__(self, parent, *args, **kwargs)

        self.configure(bg=Color.MID_TONE)

        player_container = Frame(self, bg=Color.MID_TONE)

        player1_label = Label(self)
        player2_label = Label(self)

        self.__player_labels = {
            MarkerType.CROSS: player1_label,
            MarkerType.CIRCLE: player2_label
        }
        self.__turn_marker_label = Label(self)

        self.__marker_images_big = {
            MarkerType.NONE: PhotoImage(file="images/e_big.gif"),
            MarkerType.CROSS: PhotoImage(file="images/x_big.gif"),
            MarkerType.CIRCLE: PhotoImage(file="images/o_big.gif"),
        }
        self.__marker_images_big_win = {
            MarkerType.NONE: PhotoImage(file="images/e_big.gif"),
            MarkerType.CROSS: PhotoImage(file="images/x_big_win.gif"),
            MarkerType.CIRCLE: PhotoImage(file="images/o_big_win.gif"),
        }

        player1_label.configure(font=("Helvetica", 26, "bold"),
                                bg=Color.MID_TONE)
        player2_label.configure(font=("Helvetica", 26, "bold"),
                                bg=Color.MID_TONE)

        player_container.pack(side=LEFT, fill=Y)

        self.__turn_marker_label.configure(
            image=self.__marker_images_big[MarkerType.CROSS],
            bg=Color.MID_TONE
        )

        self.__turn_marker_label.pack(side=LEFT, padx=(0, Pad.BORDER_PADDING))

        player1_label.pack(side=TOP, anchor="nw", fill=Y)
        player2_label.pack(side=BOTTOM, anchor="sw", fill=Y)

        self.update_info(MarkerType.CROSS, MarkerType.CIRCLE)

    def show_results(self, game_state, winner, loser):
        """Display winner info by given MarkerType arguments.

        :param game_state: GameState
        :param winner: MarkerType
        :param loser: MarkerType
        :return:
        """
        if game_state is GameState.WINNER:
            self.__turn_marker_label.configure(
                image=self.__marker_images_big_win[winner])

            self.__player_labels[winner].configure(
                text=f"Player {winner.value+1} wins!", fg=Color.WIN_COLOR)
            self.__player_labels[loser].configure(
                text=f"Player {loser.value+1} loses.", fg=Color.DARK_TONE)
        elif game_state is GameState.TIE:
            self.__player_labels[MarkerType.CROSS].configure(
                text=f"It's a tie!", fg=Color.BLACK)
            self.__player_labels[MarkerType.CIRCLE].configure(text="")

    def update_info(self, current_player, next_player):
        """Update turn info by current player and next player.

        :param current_player: MarkerType
        :param next_player: MarkerType
        :return:
        """
        self.__player_labels[current_player].configure(
            text=f"Player {current_player.value+1}", fg=Color.BLACK)
        self.__player_labels[next_player].configure(
            text=f"Player {next_player.value+1}", fg=Color.DARK_TONE)

        self.__turn_marker_label.configure(
            image=self.__marker_images_big[current_player])


class Application:
    """The main application that drives all of the game and user interface.

    Notable features:
        Application.grid_clicked(x, y) -> void
            Make a move to x, y, increment turn and check for winner.

            Called when a tile has been clicked. If there is already something
            placed on the tile, color it red. If winner is found, end game and
            display winner info.

        Application.reset_board() -> void
            Clear game board contents and start new game.
            Should only be called when the game has ended.

        Application.loop() -> void
            Start UI loop.

    """

    def __init__(self, game):
        """Create application window and initiate necessary components.

        :param game: instance of Game
        """
        self.__game = game

        # Init root window
        self.__root = Tk()
        self.__root.title("Ristinolla")
        self.__root.resizable(width=False, height=False)
        self.__root.configure(bg=Color.MID_TONE)

        # Interface components
        self.__infobar = InfoBar(self.__root)
        self.__buttonbar = ButtonBar(self.__root, self)
        self.__tilegrid = TileGrid(self.__root, game, self)

        # Pack things up
        self.__buttonbar.pack(
            padx=(Pad.BORDER_PADDING, Pad.BORDER_PADDING),
            pady=(Pad.BORDER_PADDING, Pad.BORDER_PADDING),
            fill=X,
        )
        self.__tilegrid.pack(
            padx=(Pad.GRID_PADDING, Pad.GRID_PADDING),
            pady=(0, 0),
        )
        self.__infobar.pack(
            padx=(Pad.BORDER_PADDING, Pad.BORDER_PADDING),
            pady=(Pad.BORDER_PADDING, Pad.BORDER_PADDING),
            fill=X,
        )

    def grid_clicked(self, x, y):
        """Make a move to x, y, increment turn and check for winner.

        Called when a tile has been clicked. If there is already something
        placed on the tile, color it red. If winner is found, end game and
        display winner info.

        :param x: int
        :param y: int
        """
        if self.__game.get_tile(x, y) is MarkerType.NONE:
            player = self.__game.get_player()
            next_player = self.__game.get_next_player()

            # Next move the positions are swapped
            self.__infobar.update_info(next_player, player)

            self.__tilegrid.set_tile_marker(x, y, player)
            self.__tilegrid.set_tile_color(x, y, Color.DARK_TONE)

            state, winner, loser, win_tiles = self.__game.make_move(x, y)
            # Display winner info if found
            if state is GameState.WINNER:
                self.__infobar.show_results(state, winner, loser)
                self.__tilegrid.highlight_tiles(win_tiles)
                self.__buttonbar.set_disabled(False)
            elif state is GameState.TIE:
                self.__infobar.show_results(state, None, None)
                self.__buttonbar.set_disabled(False)

            # Play sound according to the player
            if player is MarkerType.CROSS:
                winsound.PlaySound("sound/click_x.wav", winsound.SND_ASYNC)
            else:
                winsound.PlaySound("sound/click_o.wav", winsound.SND_ASYNC)
        else:
            self.__tilegrid.set_tile_color(x, y, Color.FAIL_COLOR)

    def reset_board(self):
        """
        Clear game board contents and start new game.
        Should only be called when the game has ended.
        """

        for y in range(Settings.SIZE_Y):
            for x in range(Settings.SIZE_X):
                self.__tilegrid.set_tile_marker(x, y, MarkerType.NONE)
                self.__tilegrid.set_tile_color(x, y, Color.MID_TONE)

        if self.__game.get_state() == GameState.WINNER:
            winner = self.__game.get_winner()
            loser = self.__game.get_loser()
            self.__game.reset(loser)
            self.__infobar.update_info(loser, winner)

        elif self.__game.get_state() == GameState.TIE:
            self.__game.reset(MarkerType.CROSS)
            self.__infobar.update_info(MarkerType.CROSS, MarkerType.CIRCLE)

        else:
            # Should never happen, since button is disabled while playing.
            raise PermissionError(
                "Method reset_board was called while game hasn't ended.")

    def loop(self):
        """Start UI loop."""
        self.__root.mainloop()


class Game:
    """Class for handling the game logic.

    Notable features:
        Game.check_move(mark, move_x, move_y) -> (MarkerType, list)
            Checks if move is a winning move, if so, return winner MarkerType
            and list of tuples (x, y). If not, return MarkerType.NONE and
            an empty list.

        Game.reset(starting_player) -> void
            Reset the game board and give turn to starting player MarkerType.

        Game.make_move(x, y) -> (GameState, winner, loser, list)
            Checks if the game has ended after the move. If not, return
            GameState.PLAYING. If winner was found, return GameState.WINNER,
            winner, loser, win_tiles (list of tuples (x, y)). In the case of
            tie, return GameState.TIE. Gives turn to the next player if still
            playing.
    """
    def __init__(self):
        """Create game grid and set initial values."""
        self.__grid = create_grid(
            Settings.SIZE_X, Settings.SIZE_Y, MarkerType.NONE)

        self.__turn = 0
        self.__state = GameState.PLAYING
        self.__winner = MarkerType.NONE
        self.__loser = MarkerType.NONE

        # Separate counter for turns, because __turn depends on starting player
        self.__turns_played = 0

    def check_move(self, mark, move_x, move_y):
        """Returns relevant tiles and winner if found IN_A_ROW amount of marks.

        Checks if move is a winning move, if so, return winner MarkerType
        and list of tuples (x, y). If not, return MarkerType.NONE and
        an empty list.

        :param mark: the mark to be checked
        :param move_x: the X coordinate of the move
        :param move_y: the Y coordinate of the move
        :return: MarkerType winner, list of tuple (x, y)
        """

        # Check 4 possible directions: horizontal, vertical, 2 diagonals
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        # Tiles to mark yellow
        all_winning_tiles = []

        for check_dir in directions:
            count = 0
            winning_tiles = []

            # Go through markers going in the same direction
            for i in range(-Settings.IN_A_ROW + 1, Settings.IN_A_ROW):
                coord_x = move_x + check_dir[0] * i
                coord_y = move_y + check_dir[1] * i

                if self.get_tile(coord_x, coord_y) is mark:
                    count += 1
                    winning_tiles.append((coord_x, coord_y))
                else:
                    # If marker combo has ended, check if there's enough to win
                    if count >= Settings.IN_A_ROW:
                        all_winning_tiles += winning_tiles
                        break

                    # If not, reset combo
                    count = 0
                    winning_tiles = []

            if count >= Settings.IN_A_ROW:
                # Accounts for multiple win cases
                all_winning_tiles += winning_tiles

        # If we won, return the winning marker and tiles
        if len(all_winning_tiles) > 0:
            return mark, all_winning_tiles

        return MarkerType.NONE, []

    def reset(self, starting_player):
        """Reset the game board and give turn to starting player MarkerType.

        :param starting_player: MarkerType
        :return:
        """
        self.__turn = starting_player.value
        self.__turns_played = 0
        self.__winner = MarkerType.NONE
        self.__loser = MarkerType.NONE

        for y in range(Settings.SIZE_Y):
            for x in range(Settings.SIZE_X):
                self.__grid[y][x] = MarkerType.NONE

        self.__state = GameState.PLAYING

    def get_player(self):
        """Get the player of the current turn.

        :return: MarkerType player, current turn
        """
        return MarkerType(self.__turn % 2)

    def get_next_player(self):
        """Get the player MarkerType of the next turn.

        :return: MarkerType player, next turn
        """
        return MarkerType((self.__turn + 1) % 2)

    def get_tile(self, x, y):
        """Return MarkerType at x, y, MarkerType.NONE if out of bounds.

        :param x: coord x
        :param y: coord y
        :return: Tile tile at (x, y)
        """
        if x < 0 or x >= Settings.SIZE_X or y < 0 or y >= Settings.SIZE_Y:
            return MarkerType.NONE
        return self.__grid[y][x]

    def get_state(self):
        """Return game state: GameState

        :return: GameState game_state
        """
        return self.__state

    def get_winner(self):
        """Return game winner if game ended: MarkerType

        :return: MarkerType winner
        """
        return self.__winner

    def get_loser(self):
        """Return game loser if game ended: MarkerType

        :return: MarkerType loser
        """
        return self.__loser

    def make_move(self, x, y):
        """Make move at x, y for the current player.

        Checks if the game has ended after the move. If not, return
        GameState.PLAYING. If winner was found, return GameState.WINNER,
        winner, loser, win_tiles (list of tuples (x, y)). In the case of tie,
        return GameState.TIE.

        Gives turn to the next player if still playing.

        :param x: int, the X coordinate of the move
        :param y: int, the Y coordinate of the move
        :return: game_state, winner, loser, win_tiles
        """
        player = self.get_player()
        self.__grid[y][x] = player

        winner, win_tiles = self.check_move(self.get_player(), x, y)

        self.__turns_played += 1

        # Check if winner has been found
        if player == winner:
            loser = MarkerType(1 - winner.value)
            self.__winner = winner
            self.__loser = loser
            self.__state = GameState.WINNER
            return GameState.WINNER, winner, loser, win_tiles

        # Check if board is full and tie happens
        elif self.__turns_played >= Settings.SIZE_X * Settings.SIZE_Y:
            self.__state = GameState.TIE
            return GameState.TIE, MarkerType.NONE, MarkerType.NONE, []

        self.__turn += 1
        return GameState.PLAYING, MarkerType.NONE, MarkerType.NONE, []


def main():
    game = Game()

    app = Application(game)
    app.loop()


main()
