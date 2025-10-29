import random
import requests
import time
import json
import pickle
import re
import math
import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from PIL import Image


# 加密函数
def encrypt_data(plaintext):
    cipher = PKCS1_v1_5.new(public_key)
    encrypted = cipher.encrypt(plaintext.encode('utf-8'))
    # 转换为十六进制，确保偶数长度
    hex_result = encrypted.hex()
    if len(hex_result) % 2 == 1:
        hex_result = '0' + hex_result
    return hex_result


def parse_jsbn_bigint(n_obj):
    DB = 28
    DV = 1 << DB
    t = n_obj['t']

    result = 0
    for i in range(t):
        result += n_obj[i] * (DV ** i)

    return result


def four_random_chart():
    return hex(int(65536 * (1 + random.random())))[2:][1:]


def RSA_jiami_r(str_16):
    global public_key
    # 你的数据
    n_data = {
        0: 134982529, 1: 254232810, 2: 164556709, 3: 234907349,
        4: 134685994, 5: 35463984, 6: 258277946, 7: 12518857,
        8: 44638621, 9: 93783641, 10: 212253739, 11: 62792472,
        12: 186688352, 13: 109500232, 14: 182488077, 15: 261196188,
        16: 26354094, 17: 103248217, 18: 106891695, 19: 165771045,
        20: 41530993, 21: 263704736, 22: 111785174, 23: 12753611,
        24: 232116673, 25: 155524985, 26: 218291229, 27: 122452343,
        28: 248250238, 29: 118739550, 30: 251169095, 31: 129059733,
        32: 149835464, 33: 5498868, 34: 71719731, 35: 154456417,
        36: 49635,
        't': 37, 's': 0
    }

    e = 65537
    n = parse_jsbn_bigint(n_data)

    # 构造公钥
    public_key = RSA.construct((n, e))
    encrypted = encrypt_data(str_16)
    return encrypted


def parse_string_to_wordarray(text):
    """将字符串转换为 WordArray 格式"""
    length = len(text)
    words = []

    for i in range(length):
        # 计算在 words 数组中的索引
        word_index = i >> 2  # 相当于 i // 4

        # 确保 words 数组足够长
        while len(words) <= word_index:
            words.append(0)

        # 获取字符的 ASCII 码
        char_code = ord(text[i]) & 0xFF

        # 计算位移量
        shift = 24 - (i % 4) * 8

        # 将字符添加到对应的 word 中
        words[word_index] |= char_code << shift

    return words


def AES_O(plaintext, str_16):
    # 密钥
    key_words = parse_string_to_wordarray(str_16)
    key = b''.join(w.to_bytes(4, 'big') for w in key_words)

    # IV
    iv = b'0000' * 4  # "0000000000000000"

    # 填充(PKCS7)
    pad_len = 16 - len(plaintext) % 16
    plaintext_padded = plaintext.encode() + bytes([pad_len] * pad_len)

    # 加密
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(plaintext_padded)

    # 结果是字节数组
    return list(ciphertext)


def geetest_base64_encode(data):
    """极验自定义Base64编码"""

    # 配置
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()'
    pad_char = '.'

    # 位掩码 (这些是打乱的)
    masks = [7274496, 9483264, 19220, 235]
    mask_bits = 24  # 总位数

    def extract_bits(value, mask):
        """根据掩码提取位"""
        result = 0
        # 从高位到低位遍历
        for i in range(mask_bits - 1, -1, -1):
            # 如果掩码的第i位是1
            if (mask >> i) & 1:
                # 提取value的第i位,添加到结果
                result = (result << 1) | ((value >> i) & 1)
        return result

    encoded = ""
    padding = ""
    length = len(data)

    # 每3字节一组
    i = 0
    while i < length:
        if i + 2 < length:
            # 完整3字节
            block = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]

            # 使用4个掩码提取
            encoded += charset[extract_bits(block, masks[0])]
            encoded += charset[extract_bits(block, masks[1])]
            encoded += charset[extract_bits(block, masks[2])]
            encoded += charset[extract_bits(block, masks[3])]

            i += 3
        else:
            # 处理剩余
            remainder = length - i

            if remainder == 2:
                block = (data[i] << 16) | (data[i + 1] << 8)
                encoded += charset[extract_bits(block, masks[0])]
                encoded += charset[extract_bits(block, masks[1])]
                encoded += charset[extract_bits(block, masks[2])]
                padding = pad_char
            elif remainder == 1:
                block = data[i] << 16
                encoded += charset[extract_bits(block, masks[0])]
                encoded += charset[extract_bits(block, masks[1])]
                padding = pad_char + pad_char

            break

    return {
        "res": encoded,
        "end": padding
    }


def get_challenge_gt():
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://demos.geetest.com/slide-float.html',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        't': str(int(round(time.time() * 1000))),
    }

    response = requests.get('https://demos.geetest.com/gt/register-slide', params=params, headers=headers)
    return json.loads(response.text)["gt"], json.loads(response.text)["challenge"]


def get_js_address(gt):
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://demos.geetest.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    }

    params = {
        'gt': gt,
        'callback': 'geetest_' + str(int(round(time.time() * 1000))),
    }

    response = requests.get('https://apiv6.geetest.com/gettype.php', params=params, headers=headers)

    match = re.search(r'\((.*)\)$', response.text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    else:
        raise ValueError("无法解析 JSONP 响应")


def get_w(gt, challenge,str_16):
    r = RSA_jiami_r(str_16)
    plaintext = '{"gt":"' + gt + '","challenge":"' + challenge + '","offline":false,"new_captcha":true,"product":"float","width":"300px","https":true,"api_server":"apiv6.geetest.com","protocol":"https://","type":"fullpage","static_servers":["static.geetest.com/","static.geevisit.com/"],"voice":"/static/js/voice.1.2.6.js","click":"/static/js/click.3.1.2.js","beeline":"/static/js/beeline.1.0.1.js","fullpage":"/static/js/fullpage.9.2.0-guwyxh.js","slide":"/static/js/slide.7.9.3.js","geetest":"/static/js/geetest.6.0.9.js","aspect_radio":{"slide":103,"click":128,"voice":128,"beeline":50},"cc":16,"ww":true,"i":"-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1"}'
    o = AES_O(plaintext, str_16)
    i = geetest_base64_encode(o)
    return i['res'] + i['end'] + r


def get_c(gt, challenge, w):
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://demos.geetest.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    }

    response = requests.get(
        'https://apiv6.geetest.com/get.php?gt=' + gt + '&challenge=' + challenge + '&lang=zh-cn&pt=0&client_type=web&w=' + w + '&callback=geetest_' + str(
            int(round(time.time() * 1000))),
        headers=headers,
    )
    match = re.search(r'\((.*)\)$', response.text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)['data']['c'], json.loads(json_str)['data']['s']
    else:
        raise ValueError("无法解析 JSONP 响应")


# 处理原始轨迹数组
def process_mouse_trajectory(events, max_records=None):
    """
    处理鼠标/触摸轨迹数据，将绝对坐标转换为相对坐标和时间差

    参数:
        events: 原始事件数据列表
        max_records: 最大保留记录数（None表示保留全部）

    返回:
        处理后的事件列表
    """
    if not events or len(events) == 0:
        return []

    # 初始化变量
    prev_x = 0  # 上一个X坐标
    prev_y = 0  # 上一个Y坐标
    prev_time = 0  # 上一个时间戳
    result = []  # 结果数组
    first_event = None  # 第一个事件
    last_event = None  # 最后一个事件

    # 移动类事件（包含坐标信息）
    MOVE_EVENTS = ["move", "mousemove", "touchmove", "pointermove"]

    # 点击类事件（仅时间信息）
    CLICK_EVENTS = ["down", "up", "click", "mousedown", "mouseup",
                    "touchstart", "touchend", "pointerdown", "pointerup"]

    # 特殊事件（仅时间信息）
    TIME_ONLY_EVENTS = ["focus", "blur", "keydown", "keyup"]

    # 如果设置了最大记录数，只处理最后N条
    start_index = 0
    if max_records and len(events) > max_records:
        start_index = len(events) - max_records

    # 遍历事件
    for i in range(start_index, len(events)):
        event = events[i]
        event_type = event[0]

        # 处理移动类事件（包含X, Y坐标）
        if event_type in MOVE_EVENTS:
            x = event[1]
            y = event[2]
            timestamp = event[3]

            # 记录第一个和最后一个事件
            if first_event is None:
                first_event = event
            last_event = event

            # 计算相对坐标差值
            delta_x = x - prev_x
            delta_y = y - prev_y

            # 计算时间差
            if prev_time == 0:
                time_diff = 0  # 第一个事件时间差为0
            else:
                time_diff = timestamp - prev_time

            # 添加到结果数组
            result.append([
                event_type,
                [delta_x, delta_y],
                time_diff
            ])

            # 更新上一次的值
            prev_x = x
            prev_y = y
            prev_time = timestamp

        # 处理点击类事件（包含坐标但只记录时间差）
        elif event_type in CLICK_EVENTS:
            timestamp = event[3] if len(event) > 3 else event[1]

            # 计算时间差
            if prev_time == 0:
                time_diff = 0
            else:
                time_diff = timestamp - prev_time

            # 添加到结果数组（坐标差为[0,0]）
            result.append([
                event_type,
                [0, 0],
                time_diff
            ])

            prev_time = timestamp

        # 处理仅时间类事件（如focus）
        elif event_type in TIME_ONLY_EVENTS:
            timestamp = event[1]

            # 计算时间差
            if prev_time == 0:
                time_diff = 0
            else:
                time_diff = timestamp - prev_time

            # 添加到结果数组（仅包含时间差）
            result.append([
                event_type,
                time_diff
            ])

            prev_time = timestamp

    return {
        "data": result,
        "first_event": first_event,
        "last_event": last_event,
        "total_events": len(result)
    }


def compress_trajectory(e):
    """
    压缩轨迹数据的完整实现

    Args:
        e: 轨迹数据列表

    Returns:
        压缩后的 Base64 编码字符串
    """
    # 事件类型映射
    p = {
        "move": 0,
        "down": 1,
        "up": 2,
        "scroll": 3,
        "focus": 4,
        "blur": 5,
        "unload": 6,
        "unknown": 7
    }

    def h(e, t):
        """
        填充二进制字符串

        Args:
            e: 数值
            t: 目标长度

        Returns:
            填充后的二进制字符串
        """
        n = bin(e)[2:]  # 转为二进制并去掉 '0b' 前缀
        r = ""
        o = len(n) + 1
        while o <= t:
            r += "0"
            o += 1
        return r + n

    def f(e):
        """
        压缩事件类型数组

        Args:
            e: 事件类型列表

        Returns:
            压缩后的二进制字符串
        """
        t = []
        n = len(e)
        r = 0

        # 游程编码（Run-Length Encoding）
        while r < n:
            o = e[r]
            i = 0
            while True:
                if 16 <= i:
                    break
                s = r + i + 1
                if n <= s:
                    break
                if e[s] != o:
                    break
                i += 1

            r = r + 1 + i
            a = p[o]
            if i != 0:
                t.append(8 | a)  # 设置重复标志位
                t.append(i - 1)
            else:
                t.append(a)

        # 编码长度信息
        _ = h(32768 | n, 16)
        c = ""
        for l in range(len(t)):
            c += h(t[l], 4)

        return _ + c

    def c(e, t):
        """
        对数组每个元素应用函数

        Args:
            e: 输入数组
            t: 转换函数

        Returns:
            转换后的数组
        """
        n = []
        for r in range(len(e)):
            n.append(t(e[r]))
        return n

    def d(e, t):
        """
        压缩数值数组（游程编码 + 变长编码）

        Args:
            e: 数值数组
            t: 是否为坐标数据（需要过滤符号位）

        Returns:
            压缩后的二进制字符串
        """

        # 第一步：限制数值范围到 [-32767, 32767]
        def limit_value(val):
            limit = 32767
            return max(-limit, min(limit, val))

        e = c(e, limit_value)

        # 第二步：游程编码（Run-Length Encoding）
        n = len(e)
        r = 0
        o = []

        while r < n:
            i = 1
            s = e[r]
            a = abs(s)

            # 统计连续相同的值
            while r + i < n and e[r + i] == s and a < 127 and i < 127:
                i += 1

            if i > 1:
                # 重复值编码格式：
                # 位15: 符号标志 (1=负数49152, 0=正数32768)
                # 位14-7: 重复次数 (i)
                # 位6-0: 绝对值 (a)
                o.append((49152 if s < 0 else 32768) | (i << 7) | a)
            else:
                o.append(s)

            r += i

        e = o

        # 第三步：变长编码
        r = []  # 存储每个数字的十六进制位数
        o = []  # 存储实际数值

        for val in e:
            # 计算需要多少个十六进制位（每位4 bit）
            if val == 0:
                bits = 1
            else:
                # 方法1：使用对数（与原JS一致）
                bits = math.ceil(math.log(abs(val) + 1) / math.log(16))
                # 方法2：直接计算（更快）
                # bits = len(format(abs(val), 'x'))

                bits = max(1, bits)

            r.append(h(bits - 1, 2))  # 2位十六进制存储位数信息
            o.append(h(abs(val), 4 * bits))  # 实际值

        i = "".join(r)  # 元数据
        s = "".join(o)  # 数据

        # 第四步：符号位编码（仅用于坐标数据）
        if t:
            # 过滤掉：0值 和 已编码符号的压缩值（位15=1）
            filtered = [x for x in e if x != 0 and (x >> 15) != 1]
            n = "".join(["1" if x < 0 else "0" for x in filtered])
        else:
            n = ""

        # 最终格式：[头部16位][元数据][数据][符号位]
        # 头部：最高位置1 + 数组长度
        return h(32768 | len(e), 16) + i + s + n

    # 主函数：数据分离
    t = []  # 事件类型
    n = []  # 时间差
    r = []  # X坐标
    o = []  # Y坐标

    for i in range(len(e)):
        a = e[i]
        length = len(a)

        t.append(a[0])
        n.append(a[1] if length == 2 else a[2])

        if length == 3:
            r.append(a[1][0])
            o.append(a[1][1])

    # 压缩各部分
    c_str = f(t) + d(n, False) + d(r, True) + d(o, True)

    # 填充到6的倍数
    l = len(c_str)
    if l % 6 != 0:
        c_str += h(0, 6 - l % 6)

    # Base64编码
    def u(e):
        """Base64编码"""
        t = ""
        n = len(e) // 6
        base64_chars = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"

        for r in range(n):
            # 每次取6位二进制
            binary_str = e[6 * r: 6 * (r + 1)]
            index = int(binary_str, 2)
            t += base64_chars[index]

        return t

    return u(c_str)


def encrypt_string(e, t, n):
    """
    JS加密函数的Python实现

    参数:
    e: 原始字符串
    t: 加密参数数组
    n: 十六进制字符串
    """
    if not t or not n:
        return e

    o = 0  # 偏移量
    i = e  # 结果字符串
    s = t[0]  # 12
    a = t[2]  # 98
    _ = t[4]  # 43

    # 每次读取2个字符（十六进制）
    while o < len(n):
        r = n[o:o + 2]  # 取2个字符
        if len(r) < 2:
            break
        o += 2

        # 解析十六进制
        c = int(r, 16)

        # 转换为字符
        l = chr(c)

        # 计算插入位置: (s * c^2 + a * c + _) % len(e)
        u = (s * c * c + a * c + _) % len(e)

        # 在位置u插入字符
        i = i[:u] + l + i[u:]

    return i


# rp生成
def simple_md5(message):
    """
    简化版MD5实现，结构更清晰
    """
    import hashlib
    import struct

    # 使用内置hashlib验证结果
    def verify_result(msg):
        return hashlib.md5(msg.encode()).hexdigest()

    # 轮移位常量
    shifts = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
    ]

    # K常数（与JavaScript版本中的常数对应）
    K = [
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
        0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
        0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
        0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
        0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
        0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
        0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
    ]

    # 实际实现...
    return verify_result(message)


# 伪造浏览器性能数据
def generate_fake_performance_timing(base_time=None):
    """
    生成伪造的浏览器性能时间戳数据

    Args:
        base_time: 基准时间戳（毫秒），默认使用当前时间

    Returns:
        dict: 包含所有性能时间戳的字典
    """
    if base_time is None:
        base_time = int(time.time() * 1000)

    # 定义合理的时间间隔范围（毫秒）
    intervals = {
        'fetch': random.randint(1, 2),
        'domain_lookup_start': random.randint(3, 5),
        'domain_lookup': random.randint(5, 15),
        'connect': random.randint(50, 150),
        'ssl_offset': random.randint(30, 50),
        'request': random.randint(1, 5),
        'response': random.randint(20, 100),
        'response_end': random.randint(1, 3),
        'unload_start': random.randint(1, 3),
        'unload': random.randint(1, 5),
        'dom_loading': random.randint(1, 3),
        'dom_interactive': random.randint(50, 200),
        'dom_content_loaded': random.randint(1, 3),
        'load_event': random.randint(0, 5)
    }

    timing = {}

    # 按照时间顺序构建
    timing['navigationStart'] = base_time
    timing['fetchStart'] = timing['navigationStart'] + intervals['fetch']
    timing['domainLookupStart'] = timing['fetchStart'] + intervals['domain_lookup_start']
    timing['domainLookupEnd'] = timing['domainLookupStart'] + intervals['domain_lookup']

    timing['connectStart'] = timing['domainLookupEnd']
    timing['secureConnectionStart'] = timing['connectStart'] + intervals['ssl_offset']
    timing['connectEnd'] = timing['connectStart'] + intervals['connect']

    timing['requestStart'] = timing['connectEnd'] + intervals['request']
    timing['responseStart'] = timing['requestStart'] + intervals['response']
    timing['responseEnd'] = timing['responseStart'] + intervals['response_end']

    timing['unloadEventStart'] = timing['responseEnd'] + intervals['unload_start']
    timing['unloadEventEnd'] = timing['unloadEventStart'] + intervals['unload']

    timing['domLoading'] = timing['unloadEventEnd'] + intervals['dom_loading']
    timing['domInteractive'] = timing['domLoading'] + intervals['dom_interactive']
    timing['domContentLoadedEventStart'] = timing['domInteractive']
    timing['domContentLoadedEventEnd'] = timing['domInteractive'] + intervals['dom_content_loaded']
    timing['domComplete'] = timing['domContentLoadedEventEnd']
    timing['loadEventStart'] = timing['domComplete']
    timing['loadEventEnd'] = timing['loadEventStart'] + intervals['load_event']

    # 无重定向的情况
    timing['redirectStart'] = 0
    timing['redirectEnd'] = 0

    return timing


# 生成类人的鼠标轨迹
def generate_realistic_trajectory(start_x, start_y, end_x, end_y, start_time):
    """生成类人的鼠标轨迹"""
    trajectory = []

    # 计算距离和步数
    distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
    steps = int(distance / 2) + random.randint(5, 15)  # 根据距离动态调整步数

    current_time = start_time
    current_x, current_y = start_x, start_y

    for i in range(steps):
        # 使用贝塞尔曲线模拟自然移动
        progress = i / steps

        # 添加缓动函数（开始快，中间慢，结束快）
        if progress < 0.3:
            eased = progress / 0.3 * 0.2
        elif progress < 0.7:
            eased = 0.2 + (progress - 0.3) / 0.4 * 0.5
        else:
            eased = 0.7 + (progress - 0.7) / 0.3 * 0.3

        # 计算目标位置（添加随机抖动）
        target_x = start_x + (end_x - start_x) * eased
        target_y = start_y + (end_y - start_y) * eased

        # 添加微小的随机偏移（模拟手抖）
        jitter_x = random.uniform(-0.5, 0.5)
        jitter_y = random.uniform(-0.5, 0.5)

        current_x = int(target_x + jitter_x)
        current_y = int(target_y + jitter_y)

        # 随机时间间隔（3-25ms，符合人类反应）
        time_delta = random.choices(
            [3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 24],
            weights=[5, 8, 10, 12, 10, 8, 5, 3, 2, 1, 1]
        )[0]
        current_time += time_delta

        trajectory.append([
            "move",
            current_x,
            current_y,
            current_time,
            "pointermove"
        ])

        # 偶尔在同一位置停留（模拟视觉确认）
        if random.random() < 0.15:
            trajectory.append([
                "move",
                current_x,
                current_y,
                current_time + random.randint(5, 15),
                "pointermove"
            ])
            current_time += random.randint(5, 15)

    # 到达目标后的悬停
    hover_time = random.randint(50, 150)
    for _ in range(random.randint(2, 5)):
        current_time += random.randint(8, 25)
        trajectory.append([
            "move",
            end_x + random.randint(-1, 1),
            end_y + random.randint(-1, 1),
            current_time,
            "pointermove"
        ])

    current_time += hover_time

    # 点击事件
    trajectory.append([
        "down",
        end_x,
        end_y,
        current_time,
        "pointerdown"
    ])

    trajectory.append([
        "focus",
        current_time + 1
    ])

    click_duration = random.randint(80, 130)
    trajectory.append([
        "up",
        end_x,
        end_y,
        current_time + click_duration,
        "pointerup"
    ])

    return trajectory


# 获取第二个w
def get_w2(gt, challenge, c, s,str_16):
    # 伪造浏览器性能数据
    fake_timing = generate_fake_performance_timing()
    # 映射
    web_load_time = {
        "a": fake_timing["navigationStart"],
        "b": fake_timing["unloadEventStart"],
        "c": fake_timing["unloadEventEnd"],
        "d": fake_timing["redirectStart"],
        "e": fake_timing["redirectEnd"],
        "f": fake_timing["fetchStart"],
        "g": fake_timing["domainLookupStart"],
        "h": fake_timing["domainLookupEnd"],
        "i": fake_timing["connectStart"],
        "j": fake_timing["connectEnd"],
        "k": fake_timing["secureConnectionStart"],
        "l": fake_timing["requestStart"],
        "m": fake_timing["responseStart"],
        "n": fake_timing["responseEnd"],
        "o": fake_timing["domLoading"],
        "p": fake_timing["domInteractive"],
        "q": fake_timing["domContentLoadedEventStart"],
        "r": fake_timing["domContentLoadedEventEnd"],
        "s": fake_timing["domComplete"],
        "t": fake_timing["loadEventStart"],
        "u": fake_timing["loadEventEnd"]
    }

    first_time = int(round(time.time() * 1000))  # 伪造脚本开始运行时间

    guiji_yuanshu_shuzu = generate_realistic_trajectory(
        start_x=random.randint(400, 600),  # 起始位置随机
        start_y=random.randint(400, 500),
        end_x=853,
        end_y=288,
        start_time=first_time
    )


    trajectory = process_mouse_trajectory(guiji_yuanshu_shuzu)["data"]
    compressed = compress_trajectory(trajectory)
    tt = encrypt_string(compressed, c, s)

    passtime = str(int(round(time.time() * 1000)) - first_time)

    rp = simple_md5(gt + challenge + passtime)

    plaintext = '{"lang":"zh-cn","type":"fullpage","tt":"'+tt+'","light":"DIV_0","s":"c7c3e21112fe4f741921cb3e4ff9f7cb","h":"321f9af1e098233dbd03f250fd2b5e21","hh":"39bd9cad9e425c3a8f51610fd506e3b3","hi":"09eb21b3ae9542a9bc1e8b63b3d9a467","vip_order":-1,"ct":-1,"ep":{"v":"9.2.0-guwyxh","te":false,"$_BBn":true,"ven":"Google Inc. (AMD)","ren":"ANGLE (AMD, AMD Radeon RX 6750 GRE 12GB (0x000073DF) Direct3D11 vs_5_0 ps_5_0, D3D11)","fp":'+json.dumps(guiji_yuanshu_shuzu[0], separators=(',', ':'))+',"lp":'+json.dumps(guiji_yuanshu_shuzu[-1], separators=(',', ':'))+',"em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0},"tm":'+json.dumps(web_load_time, separators=(',', ':'))+',"dnf":"dnf","by":0},"passtime":'+passtime+',"rp":"'+rp+'","captcha_token":"112439067","tsfq":"xovrayel"}'


    result = geetest_base64_encode(AES_O(plaintext, str_16))

    return result['res']+result['end']+result['end']

# 访问slide
def req_slide(gt, challenge, w2):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://demos.geetest.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Storage-Access': 'active',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        'https://api.geevisit.com/ajax.php?gt=' + gt + '&challenge=' + challenge + '&lang=zh-cn&pt=0&client_type=web&w=' + w2 + '&callback=geetest_' + str(
            int(round(time.time() * 1000))),
        headers=headers,
    )
    print(response.text)

# 获取图片地址
def get_picture(gt,challenge):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://demos.geetest.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Storage-Access': 'active',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = {
        'is_next': 'true',
        'type': 'slide3',
        'gt': gt,
        'challenge': challenge,
        'lang': 'zh-cn',
        'https': 'true',
        'protocol': 'https://',
        'offline': 'false',
        'product': 'embed',
        'api_server': 'api.geevisit.com',
        'isPC': 'true',
        'autoReset': 'true',
        'width': '100%',
        'callback': 'geetest_'+str(int(round(time.time() * 1000))),
    }

    response = requests.get('https://api.geevisit.com/get.php', params=params, headers=headers)
    print(response.text)
    match = re.search(r'\((.*)\)$', response.text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)['bg'], json.loads(json_str)['fullbg'], json.loads(json_str)['c'], \
        json.loads(json_str)['s'], json.loads(json_str)['slice'], json.loads(json_str)['challenge']
    else:
        raise ValueError("无法解析 JSONP 响应")

# 还原图片
def restore_geetest_image(input_path, output_path):
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
    return new_img

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

# 下载图片
def download_picture(bg,fullbg,slice):
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

# 第三个w aa加密方法
class TrajectoryEncoder:
    def __init__(self):
        self.CHARSET = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
        self.BASE = len(self.CHARSET)  # 64
        self.DIRECTION_CHARS = "stuvwxyz~"
        self.DIRECTION_PATTERNS = [
            [1, 0],  # s
            [2, 0],  # t
            [1, -1],  # u
            [1, 1],  # v
            [0, 1],  # w
            [0, -1],  # x
            [3, 0],  # y
            [2, -1],  # z
            [2, 1]  # ~
        ]

    def encode_number(self, num):
        """编码单个数值为64进制"""
        abs_num = abs(num)
        high_index = abs_num // self.BASE
        low_index = abs_num % self.BASE

        result = ""

        # 负数标记
        if num < 0:
            result += "!"

        # 高位（当值>=64时）
        if high_index > 0 and high_index < self.BASE:
            result += "$"
            result += self.CHARSET[high_index]

        # 低位
        result += self.CHARSET[low_index]

        return result

    def compress_trajectory(self, points):
        """压缩轨迹：计算相邻点差值"""
        compressed = []
        time_accumulator = 0

        for i in range(len(points) - 1):
            dx = points[i + 1][0] - points[i][0]  # 不要用abs
            dy = points[i + 1][1] - points[i][1]  # 不要用abs
            dt = abs(points[i + 1][2] - points[i][2])  # 时间可以用abs

            # 跳过完全相同的点
            if dx == 0 and dy == 0 and dt == 0:
                continue

            # 位置不变只累积时间
            if dx == 0 and dy == 0:
                time_accumulator += dt
            else:
                compressed.append([dx, dy, dt + time_accumulator])
                time_accumulator = 0

        # 处理剩余时间
        if time_accumulator != 0:
            compressed.append([0, 0, time_accumulator])

        return compressed

    def get_direction_code(self, dx, dy):
        """识别是否匹配方向模式"""
        for i, pattern in enumerate(self.DIRECTION_PATTERNS):
            if dx == pattern[0] and dy == pattern[1]:
                return self.DIRECTION_CHARS[i]
        return None

    def encode(self, trajectory):
        """
        编码轨迹
        trajectory: [[x, y, timestamp], ...]
        返回: 编码后的字符串
        """
        compressed = self.compress_trajectory(trajectory)

        x_encoded = []
        y_encoded = []
        t_encoded = []

        for dx, dy, dt in compressed:
            direction_code = self.get_direction_code(dx, dy)

            if direction_code:
                # 匹配到方向模式，只记录y
                y_encoded.append(direction_code)
            else:
                # 不匹配，完整编码x和y
                x_encoded.append(self.encode_number(dx))
                y_encoded.append(self.encode_number(dy))

            # 时间总是编码
            t_encoded.append(self.encode_number(dt))

        # 拼接：x坐标 !! y坐标 !! 时间戳
        return "".join(x_encoded) + "!!" + "".join(y_encoded) + "!!" + "".join(t_encoded)

    def encrypt_string(self,e, t, n):
        """
        JS加密函数的Python实现

        参数:
        e: 原始字符串
        t: 加密参数数组
        n: 十六进制字符串
        """
        if not t or not n:
            return e

        o = 0  # 偏移量
        i = e  # 结果字符串
        s = t[0]  # 12
        a = t[2]  # 98
        _ = t[4]  # 43

        # 每次读取2个字符（十六进制）
        while o < len(n):
            r = n[o:o + 2]  # 取2个字符
            if len(r) < 2:
                break
            o += 2

            # 解析十六进制
            c = int(r, 16)

            # 转换为字符
            l = chr(c)

            # 计算插入位置: (s * c^2 + a * c + _) % len(e)
            u = (s * c * c + a * c + _) % len(e)

            # 在位置u插入字符
            i = i[:u] + l + i[u:]

        return i

# 第三个w userresponse的加密方法
def H(t, e):
    # 解析后缀
    n = e[-2:]
    r = []
    for char in n:
        o = ord(char)
        r.append(o - 87 if o > 57 else o - 48)
    n = 36 * r[0] + r[1]

    # 计算目标值
    a = round(t) + n

    # 构建字符池
    _ = [[], [], [], [], []]
    c = {}
    u = 0
    for char in e[:-2]:
        if char not in c:
            c[char] = 1
            _[u].append(char)
            u = (u + 1) % 5

    # 生成结果
    f = a
    d = 4
    p = ""
    g = [1, 2, 5, 10, 50]

    while f > 0:
        if f >= g[d]:
            h = int(random.random() * len(_[d]))
            p += _[d][h]
            f -= g[d]
        else:
            _.pop(d)
            g.pop(d)
            d -= 1

    return p

# 第三个w 轨迹生成
def __ease_out_expo(sep):
    '''
        轨迹相关操作
    '''
    if sep == 1:
        return 1
    else:
        return 1 - pow(2, -10 * sep)
def get_slide_track(distance):
    """
    根据滑动距离生成滑动轨迹
    :param distance: 需要滑动的距离
    :return: 滑动轨迹<type 'list'>: [[x,y,t], ...]
        x: 已滑动的横向距离
        y: 已滑动的纵向距离, 除起点外, 均为0
        t: 滑动过程消耗的时间, 单位: 毫秒
    """

    if not isinstance(distance, int) or distance < 0:
        raise ValueError(f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}")
    # 初始化轨迹列表
    slide_track = [
        [random.randint(-50, -10), random.randint(-50, -10), 0],
        [0, 0, 0],
    ]
    # 共记录count次滑块位置信息
    count = 10 + int(distance / 2)
    # 初始化滑动时间
    t = random.randint(50, 100)
    # 记录上一次滑动的距离
    _x = 0
    _y = 0
    for i in range(count):
        # 已滑动的横向距离
        x = round(__ease_out_expo(i / count) * distance)
        # y = round(__ease_out_expo(i / count) * 14)
        # 滑动过程消耗的时间
        t += random.randint(10, 50)
        if x == _x:
            continue
        slide_track.append([x, _y, t])
        _x = x
    slide_track.append(slide_track[-1])
    return slide_track, slide_track[-1][2]

# 获取第三个w
def get_w3(str_16,challenge,hkjl,c,s,gt):
    encoder = TrajectoryEncoder()
    u = RSA_jiami_r(str_16)
    # 伪造浏览器性能数据
    fake_timing = generate_fake_performance_timing()
    # 映射
    web_load_time = {
        "a": fake_timing["navigationStart"],
        "b": fake_timing["unloadEventStart"],
        "c": fake_timing["unloadEventEnd"],
        "d": fake_timing["redirectStart"],
        "e": fake_timing["redirectEnd"],
        "f": fake_timing["fetchStart"],
        "g": fake_timing["domainLookupStart"],
        "h": fake_timing["domainLookupEnd"],
        "i": fake_timing["connectStart"],
        "j": fake_timing["connectEnd"],
        "k": fake_timing["secureConnectionStart"],
        "l": fake_timing["requestStart"],
        "m": fake_timing["responseStart"],
        "n": fake_timing["responseEnd"],
        "o": fake_timing["domLoading"],
        "p": fake_timing["domInteractive"],
        "q": fake_timing["domContentLoadedEventStart"],
        "r": fake_timing["domContentLoadedEventEnd"],
        "s": fake_timing["domComplete"],
        "t": fake_timing["loadEventStart"],
        "u": fake_timing["loadEventEnd"]
    }



    trajectory = get_slide_track(hkjl)[0]
    print(trajectory)

    # trajectory = generator.generate(target_x)
    userresponse = H(trajectory[-1][0], challenge)

    result1 = encoder.encode(trajectory)
    aa = encoder.encrypt_string(result1, c, s)

    passtime = str(trajectory[-1][2])


    rp = simple_md5(gt + challenge[:32] + passtime)

    plaintext = '{"lang":"zh-cn","userresponse":"'+userresponse+'","passtime":'+passtime+',"imgload":50,"aa":"'+aa+'","ep":{"v":"7.9.3","$_BIT":false,"me":true,"tm":'+json.dumps(web_load_time, separators=(',', ':'))+',"td":-1},"h9s9":"1816378497","rp":"'+rp+'"}'

    h = geetest_base64_encode(AES_O(plaintext, str_16))['res']
    return h+u

# 最后的验证
def req_end(gt,challenge,w):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://demos.geetest.com/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Storage-Access': 'active',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        'https://api.geevisit.com/ajax.php?gt='+gt+'&challenge='+challenge+'&lang=zh-cn&%24_BCm=0&client_type=web&w='+w+'&callback=geetest_'+str(int(round(time.time() * 1000))),
        headers=headers,
    )
    print(response.text)
    match = re.search(r'\((.*)\)$', response.text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)['message']
    else:
        raise ValueError("无法解析 JSONP 响应")

if __name__ == '__main__':
    str_16 = four_random_chart() + four_random_chart() + four_random_chart() + four_random_chart()
    gt, challenge = get_challenge_gt()
    get_js_address(gt)
    w = get_w(gt, challenge,str_16)
    c, s = get_c(gt, challenge, w)
    w2 = get_w2(gt, challenge, c, s,str_16)
    req_slide(gt, challenge, w2)
    bg, fullbg, c, s, slice, challenge = get_picture(gt, challenge)
    hkjl = download_picture(bg,fullbg,slice)
    w3 = get_w3(str_16,challenge,hkjl,c,s,gt)
    message = req_end(gt, challenge, w3)

