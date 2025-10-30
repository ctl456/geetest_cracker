import requests
import cv2
import numpy as np
from PIL import Image

# 将 Image 转换为 Mat，通过 flag 可以控制颜色
def pilImgToCv2(img: Image.Image, flag=cv2.COLOR_RGB2BGR):
    return cv2.cvtColor(np.asarray(img), flag)

# 识别图片缺口返回滑块距离
def shibie(img: Image.Image, slice: Image.Image):
    # 通过 pilImgToCv2 将图片置灰
    # 背景图和滑块图都需要做相同处理
    grayImg = pilImgToCv2(img, cv2.COLOR_BGR2GRAY)
    # showImg(grayImg) # 可以通过它来看处理后的图片效果
    graySlice = pilImgToCv2(slice, cv2.COLOR_BGR2GRAY)
    # 做边缘检测进一步降低干扰，阈值可以自行调整
    grayImg = cv2.Canny(grayImg, 255, 255)
    # showImg(grayImg) # 可以通过它来看处理后的图片效果
    graySlice = cv2.Canny(graySlice, 255, 255)
    # 通过模板匹配两张图片，找出缺口的位置
    result = cv2.matchTemplate(grayImg, graySlice, cv2.TM_CCOEFF_NORMED)
    maxLoc = cv2.minMaxLoc(result)[3]
    # 匹配出来的滑动距离
    distance = maxLoc[0]
    # 下面的逻辑是在图片画出一个矩形框来标记匹配到的位置，可以直观的看到匹配结果，去掉也可以的
    sliceHeight, sliceWidth = graySlice.shape[:2]
    # 左上角
    x, y = maxLoc
    # 右下角
    x2, y2 = x + sliceWidth, y + sliceHeight
    resultBg = pilImgToCv2(img, cv2.COLOR_RGB2BGR)
    cv2.rectangle(resultBg, (x, y), (x2, y2), (0, 0, 255), 2)
    # showImg(resultBg) # 可以通过它来看处理后的图片效果
    return distance

# 还原图片
def restore_geetest_image(input_path:str, output_path:str) -> None:
    """
    还原极验打乱的验证码图像
    """
    Ut = [
        39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29,
        27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12, 13, 23, 22, 14, 15,
        21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17
    ]

    # 打开混淆图像
    img = Image.open(input_path)
    new_img = Image.new("RGB", (260,160))
    r = 160
    for _ in range(len(Ut)):
        a = r / 2
        c = Ut[_] % 26 * 12 + 1
        u = 80 if Ut[_] > 25 else 0
        l = img.crop(box=(c, u, c + 10, u + 80))
        new_img.paste(l, box=(_ % 26 * 10, 80 if _ > 25 else 0))

    new_img.save(output_path)
    print(f"图像已还原并保存到: {output_path}")

# 下载图片
def download_picture(bg:str, fullbg:str, slice:str) -> int:
    for i in range(3):
        if i == 0:
            url = "https://static.geetest.com/"+bg
            response = requests.get(url)
            if response.status_code == 200:
                with open("bg.jpg", "wb") as f:
                    f.write(response.content)
                    f.close()
                restore_geetest_image("bg.jpg", "bg.jpg")
            else:
                print('图片下载失败')
        else:
            if i == 1:
                url = "https://static.geetest.com/" + fullbg
                response = requests.get(url)
                if response.status_code == 200:
                    with open("fullbg.jpg", "wb") as f:
                        f.write(response.content)
                        f.close()
                    restore_geetest_image("fullbg.jpg", "fullbg.jpg")
                else:
                    print('图片下载失败')
            else:
                url = "https://static.geetest.com/" + slice
                response = requests.get(url)
                if response.status_code == 200:
                    with open("slice.jpg", "wb") as f:
                        f.write(response.content)
                        f.close()
                else:
                    print('图片下载失败')
    return shibie(Image.open('fullbg.jpg'), Image.open('slice.jpg'))