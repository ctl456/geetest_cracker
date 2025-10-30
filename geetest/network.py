import time
import requests
import json
import re
from typing import Tuple

def get_challenge_gt() -> Tuple[str, str]:
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
    data = json.loads(response.text)
    return data["gt"], data["challenge"]

def get_js_address(gt:str) -> dict:
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

def get_c_s(gt:str, challenge:str, w:str) -> Tuple[list[int],str]:
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

def req_slide(gt:str, challenge:str, w2:str) -> None:
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

def get_picture(gt:str, challenge:str) -> tuple[str, str, list[int], str, str, str]:
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

def req_end(gt:str, challenge:str, w:str) -> str:

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