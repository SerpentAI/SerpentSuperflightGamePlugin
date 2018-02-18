from serpent.game import Game

from .api.api import SuperflightAPI

from serpent.utilities import Singleton

import time


class SerpentSuperflightGame(Game, metaclass=Singleton):

    def __init__(self, **kwargs):
        kwargs["platform"] = "steam"

        kwargs["window_name"] = "SUPERFLIGHT"

        kwargs["app_id"] = "732430"
        kwargs["app_args"] = None

        super().__init__(**kwargs)

        self.api_class = SuperflightAPI
        self.api_instance = None

        self.frame_transformation_pipeline_string = "RESIZE:100x100|GRAYSCALE|FLOAT"

        self.launched_at = None

    @property
    def screen_regions(self):
        regions = {
            "CRASHED": (61, 82, 127, 182),
            "SCORE": (78, 773, 132, 995),
            "MAPS": (609, 59, 653, 292)
        }

        return regions

    @property
    def ocr_presets(self):
        presets = {
            "SAMPLE_PRESET": {
                "extract": {
                    "gradient_size": 1,
                    "closing_size": 1
                },
                "perform": {
                    "scale": 10,
                    "order": 1,
                    "horizontal_closing": 1,
                    "vertical_closing": 1
                }
            }
        }

        return presets

    def before_launch(self):
        self.launched_at = time.time()

    def after_launch(self):
        self.is_launched = True

        time.sleep(8)

        self.window_id = self.window_controller.locate_window(self.window_name)

        if self.window_geometry is None:
            self.window_controller.move_window(self.window_id, 0, 0)
            self.window_controller.focus_window(self.window_id)

            self.window_geometry = self.extract_window_geometry()

            print(self.window_geometry)
