import cv2
import numpy as np
import requests
from PIL import Image


def restore_geetest_image(input_path: str, output_path: str) -> Image.Image:
    ut = [
        39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29,
        27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12, 13, 23, 22, 14, 15,
        21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17
    ]

    img = Image.open(input_path)
    new_img = Image.new("RGB", (260, 160))

    for index, value in enumerate(ut):
        crop_left = value % 26 * 12 + 1
        crop_top = 80 if value > 25 else 0
        tile = img.crop(box=(crop_left, crop_top, crop_left + 10, crop_top + 80))
        new_img.paste(tile, box=((index % 26) * 10, 80 if index > 25 else 0))

    new_img.save(output_path)
    return new_img


def pil_img_to_cv2(img: Image.Image, flag: int = cv2.COLOR_RGB2BGR):
    return cv2.cvtColor(np.asarray(img), flag)


def detect_gap_offset(background: Image.Image, slider: Image.Image) -> int:
    gray_background = pil_img_to_cv2(background, cv2.COLOR_BGR2GRAY)
    gray_slider = pil_img_to_cv2(slider, cv2.COLOR_BGR2GRAY)

    gray_background = cv2.Canny(gray_background, 255, 255)
    gray_slider = cv2.Canny(gray_slider, 255, 255)

    result = cv2.matchTemplate(gray_background, gray_slider, cv2.TM_CCOEFF_NORMED)
    max_loc = cv2.minMaxLoc(result)[3]
    distance = max_loc[0]

    slider_height, slider_width = gray_slider.shape[:2]
    x, y = max_loc
    x2, y2 = x + slider_width, y + slider_height
    display_img = pil_img_to_cv2(background, cv2.COLOR_RGB2BGR)
    cv2.rectangle(display_img, (x, y), (x2, y2), (0, 0, 255), 2)
    return distance


def download_captcha_images(bg_path: str, fullbg_path: str, slice_path: str) -> int:
    for index in range(3):
        if index == 0:
            url = f"https://static.geetest.com/{bg_path}"
            filename = "bg.jpg"
        elif index == 1:
            url = f"https://static.geetest.com/{fullbg_path}"
            filename = "fullbg.jpg"
        else:
            url = f"https://static.geetest.com/{slice_path}"
            filename = "slice.jpg"

        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"图片下载失败: {url}")

        with open(filename, "wb") as file:
            file.write(response.content)

        if filename != "slice.jpg":
            restore_geetest_image(filename, filename)

    fullbg = Image.open("fullbg.jpg")
    slider = Image.open("slice.jpg")
    return detect_gap_offset(fullbg, slider)
