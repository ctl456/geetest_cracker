import random
import time
from typing import Dict, Optional


def generate_fake_performance_timing(base_time: Optional[int] = None) -> Dict[str, int]:
    if base_time is None:
        base_time = int(time.time() * 1000)

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

    timing: Dict[str, int] = {}

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

    timing['redirectStart'] = 0
    timing['redirectEnd'] = 0

    return timing
