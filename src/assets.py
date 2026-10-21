import pygame


class Asset():

    def __init__(
        self,
        path: str,
    ) -> None:
        self.name: str = path
        self.image = self._load_asset()

    def _load_asset(self) -> pygame.Surface:
        return (pygame.image.load("assets/" + self.name))

    def resize_asset(
        self,
        width: int,
        height: int
    ) -> None:
        self.image = pygame.transform.scale(self.image, (width, height))

    def rotate_asset(
        self,
        angle: int
    ) -> None:
        self.image = pygame.transform.rotate(self.image, angle)


class Assets:

    def __init__(self, paths: list[str]) -> None:
        self.assets = []
        for path in paths:
            self.assets.append(Asset(path))

    def get_asset(self, name: str) -> Asset:
        for asset in self.assets:
            if (asset.name == name):
                return (asset)
        return (None)
