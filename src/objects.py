import pygame


class Asset():

    def __init__(
        self,
        asset_path: str,
        size_w: int = None,
        size_h: int = None
    ) -> None:
        self.asset_path : str = asset_path
        self.size_w: int = size_w
        self.size_h: int = size_h
        self.asset = self._load_asset()

    def _load_asset(self) -> None:
        image = pygame.image.load(self.asset_path)
        if (self.size_w) and (self.size_h):
            image = pygame.transform.scale(image, (self.size_w, self.size_h))
        return (image)

    def resize_asset(
        self,
        width: int,
        height: int
    ) -> None:
        self.asset = pygame.transform.scale(self.asset, (width, height))

    def display_asset(
        self,
        surface: pygame.Surface,
        display_x: int,
        display_y: int
    ) -> None:
        surface.blit(self.asset, (surface.get_width() / display_x - self.asset.get_width() / 2, surface.get_height() / display_y - self.asset.get_height() / 2))

class Objects():

    def __init__(self, x: int, y: int, asset: Asset) -> None:
        self.x : int = x
        self.y : int = y
        self.asset : str = asset


class Static(Objects):

    def __init__(self, x: int, y: int, asset: Asset, score: int) -> None:
        super().__init__(x, y, asset)
        self.active : bool = True
        self.score : int = score


class PacGum(Static):

    def __init__(self, x: int, y: int, asset: Asset) -> None:
        super().__init__(x, y, asset, 100)


class SuperPacGum(Static):

    def __init__(x: int, y: int, asset: Asset) -> None:
        super.__init__(x, y, asset, 500)


class Moving(Objects):

    def __init__(self, x: int, y: int, asset: Asset) -> None:
        super().__init__(x, y, asset)
        self.startx : int = x
        self.starty : int = y


class Ghost(Moving):

    def __init__(x: int, y: int, asset: Asset) -> None:
        super.__init__(x, y, asset)

    def routineBase() -> None:
        print("test")  #routine de deplacement fantomes

    def routineScared() -> None:
        print("test")#routine de deplacement fantomes

class Pacman(Moving):

    def __init__(self, x: int, y: int, asset: Asset) -> None:
        super().__init__(x, y, asset)
        self.direction : int = 0

    def pacmove(self, key_pressed: int, width_wall: int, height_wall: int, maze) -> None:
        if key_pressed == 0 and maze.can_go(self.x, self.y, 0):
            self.y -= height_wall
        if key_pressed == 1 and maze.can_go(self.x, self.y, 1):
            self.x += width_wall
        if key_pressed == 2 and maze.can_go(self.x, self.y, 2):
            self.y += height_wall
        if key_pressed == 3 and maze.can_go(self.x, self.y, 3):
            self.x -= width_wall

    #direction: up = 0, right = 1, down = 2, left = 3
    def set_direction(dir: int) -> None:
        if (dir < 0 or dir > 3):
            print("invalid direction value")
        else:
            self.direction = dir
        

#    def routine():
#        match self.direction:
#            case 0:
#            case 1:
#            case 2:
#            case 3:
#
#
#dans le programme principal, tous les cycles, appeler toutes les routines
