import math
import random
from typing import Dict, List, Optional, Tuple


def process_mouse_trajectory(events: List[List], max_records: Optional[int] = None) -> Dict[str, object]:
    if not events or len(events) == 0:
        return {
            "data": [],
            "first_event": None,
            "last_event": None,
            "total_events": 0
        }

    prev_x = 0
    prev_y = 0
    prev_time = 0
    result = []
    first_event = None
    last_event = None

    move_events = {"move", "mousemove", "touchmove", "pointermove"}
    click_events = {
        "down", "up", "click", "mousedown", "mouseup",
        "touchstart", "touchend", "pointerdown", "pointerup"
    }
    time_only_events = {"focus", "blur", "keydown", "keyup"}

    start_index = 0
    if max_records and len(events) > max_records:
        start_index = len(events) - max_records

    for i in range(start_index, len(events)):
        event = events[i]
        event_type = event[0]

        if event_type in move_events:
            x = event[1]
            y = event[2]
            timestamp = event[3]

            if first_event is None:
                first_event = event
            last_event = event

            delta_x = x - prev_x
            delta_y = y - prev_y

            if prev_time == 0:
                time_diff = 0
            else:
                time_diff = timestamp - prev_time

            result.append([
                event_type,
                [delta_x, delta_y],
                time_diff
            ])

            prev_x = x
            prev_y = y
            prev_time = timestamp

        elif event_type in click_events:
            timestamp = event[3] if len(event) > 3 else event[1]
            time_diff = 0 if prev_time == 0 else timestamp - prev_time

            result.append([
                event_type,
                [0, 0],
                time_diff
            ])

            prev_time = timestamp

        elif event_type in time_only_events:
            timestamp = event[1]
            time_diff = 0 if prev_time == 0 else timestamp - prev_time

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


def compress_trajectory(events: List[List]) -> str:
    mapping = {
        "move": 0,
        "down": 1,
        "up": 2,
        "scroll": 3,
        "focus": 4,
        "blur": 5,
        "unload": 6,
        "unknown": 7
    }

    def pad_bits(value: int, length: int) -> str:
        bits = bin(value)[2:]
        padding = "0" * max(0, length - len(bits))
        return padding + bits

    def encode_event_types(event_types: List[str]) -> str:
        encoded = []
        n = len(event_types)
        index = 0

        while index < n:
            current = event_types[index]
            repeat = 0

            while True:
                if repeat >= 16:
                    break
                next_index = index + repeat + 1
                if next_index >= n or event_types[next_index] != current:
                    break
                repeat += 1

            index += 1 + repeat
            mapped = mapping[current]
            if repeat != 0:
                encoded.append(8 | mapped)
                encoded.append(repeat - 1)
            else:
                encoded.append(mapped)

        header = pad_bits(32768 | n, 16)
        body = "".join(pad_bits(value, 4) for value in encoded)
        return header + body

    def apply(values: List[int], fn):
        return [fn(value) for value in values]

    def encode_numbers(values: List[int], is_coordinate: bool) -> str:
        def limit_value(val: int) -> int:
            limit = 32767
            return max(-limit, min(limit, val))

        limited = apply(values, limit_value)

        n = len(limited)
        index = 0
        encoded = []

        while index < n:
            repeat_count = 1
            current = limited[index]
            absolute = abs(current)

            while (
                index + repeat_count < n
                and limited[index + repeat_count] == current
                and absolute < 127
                and repeat_count < 127
            ):
                repeat_count += 1

            if repeat_count > 1:
                encoded.append(
                    (49152 if current < 0 else 32768) | (repeat_count << 7) | absolute
                )
            else:
                encoded.append(current)

            index += repeat_count

        lengths = []
        values_bits = []

        for value in encoded:
            if value == 0:
                bits = 1
            else:
                bits = math.ceil(math.log(abs(value) + 1) / math.log(16))
                bits = max(1, bits)

            lengths.append(pad_bits(bits - 1, 2))
            values_bits.append(pad_bits(abs(value), 4 * bits))

        metadata = "".join(lengths)
        payload = "".join(values_bits)

        if is_coordinate:
            filtered = [x for x in encoded if x != 0 and (x >> 15) != 1]
            signs = "".join("1" if x < 0 else "0" for x in filtered)
        else:
            signs = ""

        return pad_bits(32768 | len(encoded), 16) + metadata + payload + signs

    event_types: List[str] = []
    time_diffs: List[int] = []
    deltas_x: List[int] = []
    deltas_y: List[int] = []

    for entry in events:
        length = len(entry)
        event_types.append(entry[0])
        time_diffs.append(entry[1] if length == 2 else entry[2])
        if length == 3:
            deltas_x.append(entry[1][0])
            deltas_y.append(entry[1][1])

    encoded = (
        encode_event_types(event_types)
        + encode_numbers(time_diffs, False)
        + encode_numbers(deltas_x, True)
        + encode_numbers(deltas_y, True)
    )

    total_length = len(encoded)
    if total_length % 6 != 0:
        encoded += pad_bits(0, 6 - total_length % 6)

    base64_chars = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"
    groups = len(encoded) // 6
    output = []

    for index in range(groups):
        segment = encoded[6 * index: 6 * (index + 1)]
        output.append(base64_chars[int(segment, 2)])

    return "".join(output)


def generate_realistic_trajectory(start_x: int, start_y: int, end_x: int, end_y: int, start_time: int) -> List[List[int]]:
    trajectory: List[List[int]] = []
    distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
    steps = int(distance / 2) + random.randint(5, 15)

    current_time = start_time
    current_x, current_y = start_x, start_y

    for i in range(steps):
        progress = i / steps

        if progress < 0.3:
            eased = progress / 0.3 * 0.2
        elif progress < 0.7:
            eased = 0.2 + (progress - 0.3) / 0.4 * 0.5
        else:
            eased = 0.7 + (progress - 0.7) / 0.3 * 0.3

        target_x = start_x + (end_x - start_x) * eased
        target_y = start_y + (end_y - start_y) * eased

        jitter_x = random.uniform(-0.5, 0.5)
        jitter_y = random.uniform(-0.5, 0.5)

        current_x = int(target_x + jitter_x)
        current_y = int(target_y + jitter_y)

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

        if random.random() < 0.15:
            trajectory.append([
                "move",
                current_x,
                current_y,
                current_time + random.randint(5, 15),
                "pointermove"
            ])
            current_time += random.randint(5, 15)

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


class TrajectoryEncoder:
    def __init__(self) -> None:
        self.charset = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
        self.base = len(self.charset)
        self.direction_chars = "stuvwxyz~"
        self.direction_patterns = [
            [1, 0],
            [2, 0],
            [1, -1],
            [1, 1],
            [0, 1],
            [0, -1],
            [3, 0],
            [2, -1],
            [2, 1]
        ]

    def encode_number(self, num: int) -> str:
        abs_num = abs(num)
        high_index = abs_num // self.base
        low_index = abs_num % self.base

        result = ""
        if num < 0:
            result += "!"

        if 0 < high_index < self.base:
            result += "$"
            result += self.charset[high_index]

        result += self.charset[low_index]
        return result

    def compress_trajectory(self, points: List[List[int]]) -> List[List[int]]:
        compressed = []
        time_accumulator = 0

        for i in range(len(points) - 1):
            dx = points[i + 1][0] - points[i][0]
            dy = points[i + 1][1] - points[i][1]
            dt = abs(points[i + 1][2] - points[i][2])

            if dx == 0 and dy == 0 and dt == 0:
                continue

            if dx == 0 and dy == 0:
                time_accumulator += dt
            else:
                compressed.append([dx, dy, dt + time_accumulator])
                time_accumulator = 0

        if time_accumulator != 0:
            compressed.append([0, 0, time_accumulator])

        return compressed

    def get_direction_code(self, dx: int, dy: int) -> Optional[str]:
        for index, pattern in enumerate(self.direction_patterns):
            if dx == pattern[0] and dy == pattern[1]:
                return self.direction_chars[index]
        return None

    def encode(self, trajectory: List[List[int]]) -> str:
        compressed = self.compress_trajectory(trajectory)

        x_encoded: List[str] = []
        y_encoded: List[str] = []
        t_encoded: List[str] = []

        for dx, dy, dt in compressed:
            direction_code = self.get_direction_code(dx, dy)

            if direction_code:
                y_encoded.append(direction_code)
            else:
                x_encoded.append(self.encode_number(dx))
                y_encoded.append(self.encode_number(dy))

            t_encoded.append(self.encode_number(dt))

        return "".join(x_encoded) + "!!" + "".join(y_encoded) + "!!" + "".join(t_encoded)

    def encrypt_string(self, value: str, params: List[int], hex_string: str) -> str:
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


def _ease_out_expo(sep: float) -> float:
    if sep == 1:
        return 1
    return 1 - pow(2, -10 * sep)


def get_slide_track(distance: int) -> Tuple[List[List[int]], int]:
    if not isinstance(distance, int) or distance < 0:
        raise ValueError(
            f"distance类型必须是大于等于0的整数: distance: {distance}, type: {type(distance)}"
        )

    slide_track: List[List[int]] = [
        [random.randint(-50, -10), random.randint(-50, -10), 0],
        [0, 0, 0],
    ]
    count = 10 + int(distance / 2)
    current_time = random.randint(50, 100)
    last_x = 0
    last_y = 0

    for i in range(count):
        x = round(_ease_out_expo(i / count) * distance)
        current_time += random.randint(10, 50)
        if x == last_x:
            continue
        slide_track.append([x, last_y, current_time])
        last_x = x

    slide_track.append(slide_track[-1])
    return slide_track, slide_track[-1][2]
