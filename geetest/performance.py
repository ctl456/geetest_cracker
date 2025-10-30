import time
import random
from typing import Optional


def generate_fake_performance_timing(base_time: Optional[int] = None) -> dict[str, int]:
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