# TIE-02101: Johdatus ohjelmointiin
# Joona Perasto, opiskelijanumero 272725
# Käyttöliittymäprojekti 13.10.
# Tiedosto, joka sisältää erilaisia ohjelman asetuksia.
#
# Edellisestä projektista vähennettiin pisteitä globaalilla näkyvyysalueella
# olevista muuttujista, jotka ovat const-arvoja, joten yritetään tällä tavalla.


class Settings:
    SIZE_X = 12
    SIZE_Y = 12
    IN_A_ROW = 5  # How many marks in a row to win


class Pad:
    GRID_LINE = 2
    BORDER_PADDING = 24
    GRID_PADDING = 48


class Color:
    HIGH_TONE = "#FF7060"
    MID_TONE = "#FF4040"
    DARK_TONE = "#BB3030"

    FAIL_COLOR = "#FF0000"
    WIN_COLOR = "#FFCC33"

    BLACK = "#000000"
