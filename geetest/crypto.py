import random
from typing import Dict, List

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA


def four_random_chart() -> str:
    return hex(int(65536 * (1 + random.random())))[2:][1:]


def _parse_jsbn_bigint(n_obj: Dict[int, int]) -> int:
    db = 28
    dv = 1 << db
    length = n_obj['t']

    result = 0
    for i in range(length):
        result += n_obj[i] * (dv ** i)

    return result


def rsa_encrypt(plaintext: str) -> str:
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
    n = _parse_jsbn_bigint(n_data)
    public_key = RSA.construct((n, e))
    cipher = PKCS1_v1_5.new(public_key)
    encrypted = cipher.encrypt(plaintext.encode('utf-8'))
    hex_result = encrypted.hex()
    if len(hex_result) % 2 == 1:
        hex_result = '0' + hex_result
    return hex_result


def _parse_string_to_wordarray(text: str) -> List[int]:
    length = len(text)
    words: List[int] = []

    for i in range(length):
        word_index = i >> 2
        while len(words) <= word_index:
            words.append(0)

        char_code = ord(text[i]) & 0xFF
        shift = 24 - (i % 4) * 8
        words[word_index] |= char_code << shift

    return words


def aes_encrypt(plaintext: str, seed: str) -> List[int]:
    key_words = _parse_string_to_wordarray(seed)
    key = b''.join(w.to_bytes(4, 'big') for w in key_words)
    iv = b'0000' * 4

    pad_len = 16 - len(plaintext) % 16
    plaintext_padded = plaintext.encode() + bytes([pad_len] * pad_len)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(plaintext_padded)
    return list(ciphertext)


def geetest_base64_encode(data: List[int]) -> Dict[str, str]:
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()'
    pad_char = '.'
    masks = [7274496, 9483264, 19220, 235]
    mask_bits = 24

    def extract_bits(value: int, mask: int) -> int:
        result = 0
        for i in range(mask_bits - 1, -1, -1):
            if (mask >> i) & 1:
                result = (result << 1) | ((value >> i) & 1)
        return result

    encoded = ""
    padding = ""
    length = len(data)
    i = 0
    while i < length:
        if i + 2 < length:
            block = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2]
            encoded += charset[extract_bits(block, masks[0])]
            encoded += charset[extract_bits(block, masks[1])]
            encoded += charset[extract_bits(block, masks[2])]
            encoded += charset[extract_bits(block, masks[3])]
            i += 3
        else:
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


def encrypt_string(value: str, params: List[int], hex_string: str) -> str:
    if not params or not hex_string:
        return value

    offset = 0
    result = value
    s = params[0]
    a = params[2]
    underscore = params[4]

    while offset < len(hex_string):
        chunk = hex_string[offset:offset + 2]
        if len(chunk) < 2:
            break
        offset += 2
        c = int(chunk, 16)
        char = chr(c)
        index = (s * c * c + a * c + underscore) % len(result)
        result = result[:index] + char + result[index:]

    return result


def simple_md5(message: str) -> str:
    import hashlib

    return hashlib.md5(message.encode()).hexdigest()
