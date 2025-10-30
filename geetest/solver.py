import time
import random
import json
from .trajectory import generate_realistic_trajectory, process_mouse_trajectory, compress_trajectory, TrajectoryEncoder, \
    H
from .crypto import four_random_chart, RSA_jiami_r, AES_O, geetest_base64_encode, encrypt_string, simple_md5
from .imaging import download_picture
from .network import get_challenge_gt, get_js_address, get_c_s, req_slide, get_picture, req_end
from .performance import generate_fake_performance_timing, get_slide_track


def _generate_seed() -> str:
    return four_random_chart() + four_random_chart() + four_random_chart() + four_random_chart()

def get_w1(gt:str, challenge:str, str_16:str) -> str:
    r = RSA_jiami_r(str_16)
    plaintext = '{"gt":"' + gt + '","challenge":"' + challenge + '","offline":false,"new_captcha":true,"product":"float","width":"300px","https":true,"api_server":"apiv6.geetest.com","protocol":"https://","type":"fullpage","static_servers":["static.geetest.com/","static.geevisit.com/"],"voice":"/static/js/voice.1.2.6.js","click":"/static/js/click.3.1.2.js","beeline":"/static/js/beeline.1.0.1.js","fullpage":"/static/js/fullpage.9.2.0-guwyxh.js","slide":"/static/js/slide.7.9.3.js","geetest":"/static/js/geetest.6.0.9.js","aspect_radio":{"slide":103,"click":128,"voice":128,"beeline":50},"cc":16,"ww":true,"i":"-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1"}'
    o = AES_O(plaintext, str_16)
    i = geetest_base64_encode(o)
    return i['res'] + i['end'] + r

def get_w2(gt:str, challenge:str, c:list[int], s:str,str_16:str) -> str:
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

def get_w3(str_16:str, challenge:str, hkjl:int, c:list[int], s:str, gt:str) -> str:
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

def run_solver() -> None:
    # 16位字符串
    str_16 = _generate_seed()

    # 访问第一个链接获取gt challeneg
    gt, challenge = get_challenge_gt()

    # 访问第二个链接获取js文件地址（后续需要用到）
    get_js_address(gt)

    # 获取第一个w值
    w1 = get_w1(gt, challenge, str_16)

    # 访问第三个链接获取数组c与字符串s
    c, s = get_c_s(gt, challenge, w1)

    # 获取第二个w值
    w2 = get_w2(gt, challenge, c, s, str_16)

    # 访问第四个链接确认进入滑动
    req_slide(gt, challenge, w2)

    # 访问第五个链接获取最后一个w值所需要的加密参数
    bg, fullbg, c, s, slice, challenge = get_picture(gt, challenge)

    # 识别缺口位置得到滑块距离
    hkjl = download_picture(bg, fullbg, slice)

    # 获取第三个w值
    w3 = get_w3(str_16,challenge,hkjl,c,s,gt)

    # 最后的验证
    message = req_end(gt, challenge, w3)
