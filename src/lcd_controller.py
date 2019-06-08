"""
Module for managing the home and away LCD displays.

"""

import os
import os.path

import pigpio
from PIL import Image
from decouple import config
from typing import Dict

from src.game_overview import GameOverview
from src.lcd_display import LCDDisplay


class LcdController:
    """
    LCD display controller.

    Attributes:
        home_display (LCDDisplay): Home LCD display
        away_display (LCDDisplay): Away LCD display
        logos (Dict[str, Image]): Team name -> team logo for all logos

    """

    def __init__(self):
        # type: () -> None
        """
        Initialize LCD displays.

        """
        # Configure the home and away LCD displays.
        self.home_display = LCDDisplay(
            config('HOME_LCD_RESET_PIN', cast=int),
            config('HOME_LCD_SPI_DEVICE', cast=int),
            config('LCD_SPI_PORT', cast=int),
            config('HOME_LCD_PWM_PIN', cast=int),
            config('LCD_DC_PIN', cast=int),
            config('LCD_SPI_CLOCK_SPEED', cast=int),
            pigpio.pi(),
            config('LCD_WIDTH', cast=int),
            config('LCD_HEIGHT', cast=int)
        )  # type: LCDDisplay
        self.away_display = LCDDisplay(
            config('AWAY_LCD_RESET_PIN', cast=int),
            config('AWAY_LCD_SPI_DEVICE', cast=int),
            config('LCD_SPI_PORT', cast=int),
            config('AWAY_LCD_PWM_PIN', cast=int),
            config('LCD_DC_PIN', cast=int),
            config('LCD_SPI_CLOCK_SPEED', cast=int),
            pigpio.pi(),
            config('LCD_WIDTH', cast=int),
            config('LCD_HEIGHT', cast=int)
        )  # type: LCDDisplay
        # Format path where logos are stored.
        logo_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), config('LOGO_DIR')))
        # Load all logos into logos attribute.
        self.logos = self._get_images(logo_path)  # type: Dict[str, Image]

    def _turn_on_displays(self):
        # type: () -> None
        """
        Turn both displays' backlights on.

        """
        self.home_display.backlight.turn_on()
        self.away_display.backlight.turn_on()

    def _turn_off_displays(self):
        # type: () -> None
        """
        Turn both displays' backlights off.

        """
        self.home_display.backlight.turn_off()
        self.away_display.backlight.turn_off()

    def exit(self):
        # type: () -> None
        """
        Prepare displays for script exit.

        """
        # Turn off displays.
        self._turn_off_displays()
        # Exit the displays.
        self.home_display.exit()
        self.away_display.exit()

    @staticmethod
    def _get_images(path):
        # type: (str) -> Dict[str, Image]
        """
        Get all jpg images in a directory.

        Args:
            path (str): Directory to look in

        Returns:
            Dict[str, Image]: Images in directory as image name -> image object

        """
        return {
            item.split('.jpg')[0]: Image.open(os.path.join(path, item))
            for item in os.listdir(path) if item.endswith('.jpg')
        }

    def _display_images(self, home_image, away_image):
        # type: (Image, Image) -> None
        """
        Display images on the home and away displays.

        Args:
            home_image (Image): Image to show on home display
            away_image (Image): Image to show on away display

        """
        self.home_display.display_image(home_image)
        self.away_display.display_image(away_image)
        # Ensure backlights are on.
        self._turn_on_displays()

    def display_team_logos_final(self, home_team, away_team, home_wins):
        # type: (str, str, bool) -> None
        """
        Display team logos with win message for a game that is final.

        Notes:
            TODO: Display Cubs 'W' logo here.

        Args:
            home_team (str): Name of home team
            away_team (str): Name of away team
            home_wins (bool): Whether or not the home team won

        """
        # Get copies of team logos.
        home_logo = self.logos[home_team].copy()
        away_logo = self.logos[away_team].copy()
        # Add win message to the team that won's logo.
        if home_wins:
            home_logo = self.home_display.add_winner_text(home_team, home_logo)
        else:
            away_logo = self.away_display.add_winner_text(away_team, away_logo)
        self._display_images(home_logo, away_logo)

    def display_team_logos(self, game_overview):
        # type: (GameOverview) -> None
        """
        Display logos for an overview.

        Notes:
            Displays win message for games that are final.

        Args:
            game_overview (GameOverview): Overview of game

        """
        # If final, display logos with annotation.
        if game_overview.is_final():
            self.display_team_logos_final(
                game_overview.home_team_name,
                game_overview.away_team_name,
                game_overview.home_team_runs > game_overview.away_team_runs
            )
        # Else, display normal logos.
        else:
            self._display_images(self.logos[game_overview.home_team_name], self.logos[game_overview.away_team_name])
