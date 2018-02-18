from serpent.game_api import GameAPI

from serpent.sprite import Sprite

from serpent.input_controller import KeyboardKey

import serpent.cv
import serpent.ocr

import numpy as np

import skimage.util
import skimage.transform

import pytesseract
from PIL import Image

import time
import uuid


class SuperflightAPI(GameAPI):

    def __init__(self, game=None):
        super().__init__(game=game)

    def is_alive(self, game_frame, sprite_identifier):
        crashed_image = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["CRASHED"])
        crashed_sprite = Sprite("123", image_data=crashed_image[..., np.newaxis])

        sprite_name = sprite_identifier.identify(crashed_sprite, mode="CONSTELLATION_OF_PIXELS")

        return False if sprite_name == "SPRITE_CRASHED" else True

    def parse_score(self, game_frame):
        score_image = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["SCORE"])
        score_image = skimage.util.img_as_ubyte(np.all(score_image > 240, axis=-1))

        try:
            candidates, bounding_boxes = serpent.ocr.extract_ocr_candidates(
                score_image,
                closing_size=20,
                minimum_aspect_ratio=0.1
            )
        except Exception:
            return 0

        if len(candidates):
            try:
                score = self.perform_ocr(candidates[0], order=0, extra="--psm 7 -c tessedit_char_whitelist=0123456789")
                return int(score)
            except Exception as e:
                return 0
        else:
            return 0

    def change_map(self, seed=None, input_controller=None):
        input_controller.tap_key(KeyboardKey.KEY_DOWN)
        input_controller.tap_key(KeyboardKey.KEY_ENTER)

        time.sleep(0.5)

        self.delete_map(input_controller=input_controller)

        time.sleep(0.5)

        input_controller.tap_key(KeyboardKey.KEY_DOWN)
        input_controller.tap_key(KeyboardKey.KEY_ENTER)

        time.sleep(0.5)

        input_controller.tap_key(KeyboardKey.KEY_BACKSPACE)
        time.sleep(0.1)
        input_controller.type_string(seed or str(uuid.uuid4()).split("-")[0])
        time.sleep(0.1)
        input_controller.tap_key(KeyboardKey.KEY_ENTER)

        time.sleep(0.5)

    def delete_map(self, input_controller=None):
        input_controller.tap_key(KeyboardKey.KEY_D)
        time.sleep(0.5)

        input_controller.tap_key(KeyboardKey.KEY_DOWN)
        input_controller.tap_key(KeyboardKey.KEY_DOWN)
        input_controller.tap_key(KeyboardKey.KEY_ENTER)

    def perform_ocr(self, image, scale=10, order=5, extra=""):
        image = skimage.transform.resize(
            image,
            (image.shape[0] * scale, image.shape[1] * scale),
            mode="edge",
            order=order
        )

        black_pixel_count = image[image == 0].size
        white_pixel_count = image[image == 1].size

        if black_pixel_count > white_pixel_count:
            image = skimage.util.invert(image)

        image = skimage.util.img_as_ubyte(image)

        return pytesseract.image_to_string(Image.fromarray(image), config=extra)
