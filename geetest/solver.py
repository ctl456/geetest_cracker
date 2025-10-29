import json
import random
import time
from typing import List

from .crypto import (
    aes_encrypt,
    encrypt_string,
    four_random_chart,
    geetest_base64_encode,
    rsa_encrypt,
    simple_md5,
)
from .imaging import download_captcha_images
from .network import (
    get_c,
    get_challenge_gt,
    get_js_address,
    get_picture,
    get_w,
    req_end,
    req_slide,
)
from .performance import generate_fake_performance_timing
from .trajectory import (
    TrajectoryEncoder,
    compress_trajectory,
    generate_realistic_trajectory,
    get_slide_track,
    process_mouse_trajectory,
)


def _generate_seed() -> str:
    return four_random_chart() + four_random_chart() + four_random_chart() + four_random_chart()


def get_w2(gt: str, challenge: str, c: List[int], s: str, seed: str) -> str:
    fake_timing = generate_fake_performance_timing()
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
        "u": fake_timing["loadEventEnd"],
    }

    first_time = int(round(time.time() * 1000))

    original_trajectory = generate_realistic_trajectory(
        start_x=random.randint(400, 600),
        start_y=random.randint(400, 500),
        end_x=853,
        end_y=288,
        start_time=first_time
    )

    processed = process_mouse_trajectory(original_trajectory)["data"]
    compressed = compress_trajectory(processed)
    tt_value = encrypt_string(compressed, c, s)

    passtime = str(int(round(time.time() * 1000)) - first_time)
    rp_value = simple_md5(gt + challenge + passtime)

    plaintext = (
        '{"lang":"zh-cn","type":"fullpage","tt":"' + tt_value + '",' \
        '"light":"DIV_0","s":"c7c3e21112fe4f741921cb3e4ff9f7cb","h":"321f9af1e098233dbd03f250fd2b5e21","hh":"39bd9cad9e425c3a8f51610fd506e3b3","hi":"09eb21b3ae9542a9bc1e8b63b3d9a467","vip_order":-1,"ct":-1,"ep":{"v":"9.2.0-guwyxh","te":false,"$_BBn":true,"ven":"Google Inc. (AMD)","ren":"ANGLE (AMD, AMD Radeon RX 6750 GRE 12GB (0x000073DF) Direct3D11 vs_5_0 ps_5_0, D3D11)","fp":' \
        + json.dumps(original_trajectory[0], separators=(',', ':')) + ',"lp":' + json.dumps(original_trajectory[-1], separators=(',', ':')) + ',"em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0},"tm":' \
        + json.dumps(web_load_time, separators=(',', ':')) + ',"dnf":"dnf","by":0},"passtime":' + passtime + ',"rp":"' + rp_value + '","captcha_token":"112439067","tsfq":"xovrayel"}'
    )

    base64_result = geetest_base64_encode(aes_encrypt(plaintext, seed))
    return base64_result['res'] + base64_result['end'] + base64_result['end']


def _userresponse(value: float, challenge: str) -> str:
    suffix = challenge[-2:]
    numbers = []
    for char in suffix:
        o = ord(char)
        numbers.append(o - 87 if o > 57 else o - 48)
    n = 36 * numbers[0] + numbers[1]
    target = round(value) + n

    pools: List[List[str]] = [[], [], [], [], []]
    seen = {}
    index = 0
    for char in challenge[:-2]:
        if char not in seen:
            seen[char] = True
            pools[index].append(char)
            index = (index + 1) % 5

    remaining = target
    pool_index = 4
    result = ""
    weights = [1, 2, 5, 10, 50]

    while remaining > 0:
        if remaining >= weights[pool_index]:
            choice = int(random.random() * len(pools[pool_index]))
            result += pools[pool_index][choice]
            remaining -= weights[pool_index]
        else:
            pools.pop(pool_index)
            weights.pop(pool_index)
            pool_index -= 1

    return result


def get_w3(seed: str, challenge: str, distance: int, c: List[int], s: str, gt: str) -> str:
    encoder = TrajectoryEncoder()
    rsa_value = rsa_encrypt(seed)
    fake_timing = generate_fake_performance_timing()
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
        "u": fake_timing["loadEventEnd"],
    }

    trajectory, _ = get_slide_track(distance)
    print(trajectory)

    userresponse = _userresponse(trajectory[-1][0], challenge)

    encoded = encoder.encode(trajectory)
    aa_value = encoder.encrypt_string(encoded, c, s)

    passtime = str(trajectory[-1][2])
    rp_value = simple_md5(gt + challenge[:32] + passtime)

    plaintext = (
        '{"lang":"zh-cn","userresponse":"' + userresponse + '","passtime":' + passtime + ',"imgload":50,"aa":"' + aa_value + '","ep":{"v":"7.9.3","$_BIT":false,"me":true,"tm":' \
        + json.dumps(web_load_time, separators=(',', ':')) + ',"td":-1},"h9s9":"1816378497","rp":"' + rp_value + '"}'
    )

    encrypted = geetest_base64_encode(aes_encrypt(plaintext, seed))['res']
    return encrypted + rsa_value


def run_solver() -> None:
    seed = _generate_seed()
    gt, challenge = get_challenge_gt()
    get_js_address(gt)
    w = get_w(gt, challenge, seed)
    c, s = get_c(gt, challenge, w)
    w2 = get_w2(gt, challenge, c, s, seed)
    req_slide(gt, challenge, w2)
    bg, fullbg, c_value, s_value, slice_value, new_challenge = get_picture(gt, challenge)
    distance = download_captcha_images(bg, fullbg, slice_value)
    w3 = get_w3(seed, new_challenge, distance, c_value, s_value, gt)
    message = req_end(gt, new_challenge, w3)
    print(message)
