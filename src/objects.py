import pygame

from src.assets import Asset


class Objects:

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset
    ) -> None:
        self.x = x
        self.y = y
        self.asset = asset


class Static(Objects):

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset,
        score_given: int
    ) -> None:
        super().__init__(x, y, asset)
        self.score_given = score_given


class Pacgum(Static):

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset,
        score_given: int,
    ) -> None:
        super().__init__(x, y, asset, score_given)


class SuperPacgum(Pacgum):

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset,
        score_given: int
    ) -> None:
        super().__init__(x, y, asset, score_given)


class Moving(Objects):

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset,
        direction: int
    ) -> None:
        super().__init__(x, y, asset)
        self.direction = direction


class Player(Moving):

    def __init__(
        self,
        x: int,
        y: int,
        asset: Asset,
        direction: int
    ) -> None:
        super().__init__(x, y, asset, direction)

    def display_player(
        self,
        surface: pygame.Surface
    ) -> None:
        self.asset.resize_asset(20, 20)
        surface.blit(self.asset.image, (0, 0))
