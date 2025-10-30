import random
import hashlib
from typing import Any
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES

# 随机产生4个字符组成的字符串
def four_random_chart() -> str:
    return hex(int(65536 * (1 + random.random())))[2:][1:]

# PKCS#1 v1.5 填充 + RSA 加密
def parse_jsbn_bigint(n_obj:dict[Any, int]) -> int:
    DB = 28
    DV = 1 << DB
    t = n_obj['t']

    result = 0
    for i in range(t):
        result += n_obj[i] * (DV ** i)

    return result

def encrypt_data(plaintext:str) -> str:
    cipher = PKCS1_v1_5.new(public_key)
    encrypted = cipher.encrypt(plaintext.encode('utf-8'))
    # 转换为十六进制，确保偶数长度
    hex_result = encrypted.hex()
    if len(hex_result) % 2 == 1:
        hex_result = '0' + hex_result
    return hex_result

def RSA_jiami_r(str_16:str) -> str:
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

# AES加密
# 加密模式: AES-CBC
# 密钥长度: 128位
# IV: 固定为 "0000000000000000"
def parse_string_to_wordarray(text:str) -> list[int]:
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
def AES_O(plaintext:str, str_16:str) -> list[int]:
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

# 自定义base64编码
def geetest_base64_encode(data:list[int]) -> dict[str, Any]:
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


def encrypt_string(e:str, t:list[int], n:str) -> str:
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


def simple_md5(message:str) -> str:
    """
    简化版MD5实现，结构更清晰
    """

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