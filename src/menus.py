import pygame

from src.assets import Assets


class MainMenu:

    def __init__(
        self,
        assets: Assets
    ) -> None:
        self.cursor = 1
        self.assets = assets

    def menu_action(
        self,
        key_pressed
    ) -> int:
        if key_pressed[pygame.K_RETURN]:
            if self.cursor == 1:
                return (1)
            elif self.cursor == 2:
                return (2)
        elif key_pressed[pygame.K_DOWN]:
            if self.cursor < 2:
                self.cursor += 1
            else:
                self.cursor = 1
        elif key_pressed[pygame.K_UP]:
            if self.cursor > 1:
                self.cursor -= 1
            else:
                self.cursor = 2
        return (0)

    def display_menu(
        self,
        surface: pygame.Surface,
        ticking: int
    ) -> None:

        play_button = self.assets.get_asset("play_button.png")
        settings_button = self.assets.get_asset("settings_button.png")

        play_button_cursor = self.assets.get_asset("play_button_cursor.png")
        settings_button_cursor = self.assets.get_asset("settings_button_cursor.png")

        play_button.resize_asset(surface.get_width() / 5, surface.get_height() / 15)
        settings_button.resize_asset(surface.get_width() / 5, surface.get_height() / 15)

        play_button_cursor.resize_asset(surface.get_width() / 5, surface.get_height() / 15)
        settings_button_cursor.resize_asset(surface.get_width() / 5, surface.get_height() / 15)

        pos_x_play_button = surface.get_width() / 2 - play_button.image.get_width() / 2
        pos_y_play_button = surface.get_height() / 2 - play_button.image.get_height() / 2

        pos_x_settings_button = surface.get_width() / 2 - settings_button.image.get_width() / 2
        pos_y_settings_button = surface.get_height() / 1.6 - settings_button.image.get_height() / 2

        if ticking < 45:
            if self.cursor == 1:
                surface.blit(play_button_cursor.image, (pos_x_play_button, pos_y_play_button))
                surface.blit(settings_button.image, (pos_x_settings_button, pos_y_settings_button))
            elif self.cursor == 2:
                surface.blit(play_button.image, (pos_x_play_button, pos_y_play_button))
                surface.blit(settings_button_cursor.image, (pos_x_settings_button, pos_y_settings_button))
        else:
            surface.blit(play_button.image, (pos_x_play_button, pos_y_play_button))
            surface.blit(settings_button.image, (pos_x_settings_button, pos_y_settings_button))
