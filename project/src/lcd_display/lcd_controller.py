"""
Module for managing the home and away LCD displays.

"""

import os
import os.path

import pigpio
from PIL import Image
from decouple import config
from typing import Dict, Tuple

from games.game_overview import GameOverview
from .lcd_display import LCDDisplay


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

    def _add_winner_text(self, home_logo, away_logo, game_overview):
        # type: (Image, Image, GameOverview) -> Tuple[Image, Image]
        """
        Add winner text to the winner's logo.

        Args:
            home_logo (Image): Home team's logo
            away_logo (Image): Away team's logo
            game_overview (GameOverview): Overview of game

        Returns:
            Tuple[Image, Image]: (home, away) logos, with modification

        """
        # Add win message to the team that won's logo.
        if game_overview.home_won:
            return self.home_display.add_winner_text(game_overview.home_team_name, home_logo), away_logo
        return home_logo, self.away_display.add_winner_text(game_overview.away_team_name, away_logo)

    def _get_team_logos(self, game_overview):
        # type: (GameOverview) -> Tuple[Image, Image]
        """
        Get the team logos.

        Notes:
            Gets Cubs 'W' logo when they win.

        Args:
            game_overview (GameOverview): Overview of game

        Returns:
            Tuple[Image, Image]: (home, away) logos

        """
        # Get the logos.
        home_logo = self.logos[game_overview.home_team_name]
        away_logo = self.logos[game_overview.away_team_name]
        # Get Cubs 'W' logo if they won.
        if game_overview.is_final() and game_overview.is_playing('Cubs'):
            if game_overview.home_team_name == 'Cubs':
                return self.logos['cubs_w_flag'].copy(), away_logo.copy()
            return home_logo.copy(), self.logos['cubs_w_flag'].copy()
        # Else, just return copies of the team logos.
        return home_logo.copy(), away_logo.copy()

    def display_team_logos(self, game_overview):
        # type: (GameOverview) -> None
        """
        Display logos for an overview.

        Args:
            game_overview (GameOverview): Overview of game

        """
        # Get the team logos.
        home_logo, away_logo = self._get_team_logos(game_overview)
        # Add status headers.
        home_logo = self.home_display.add_status_header(game_overview.status, home_logo)
        away_logo = self.away_display.add_status_header(game_overview.status, away_logo)
        # If final, annotate with winner message.
        if game_overview.is_final():
            home_logo, away_logo = self._add_winner_text(home_logo, away_logo, game_overview)
        # Display the logos.
        self._display_images(home_logo, away_logo)
