import random
import math
from typing import Any, Optional


# 生成类人的鼠标轨迹
def generate_realistic_trajectory(start_x:int, start_y:int, end_x:int, end_y:int, start_time:int) -> list[Any]:
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

# 处理原始轨迹数组
def process_mouse_trajectory(events:list[Any], max_records: Optional[int] = None) -> dict[str,Any]:
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

def compress_trajectory(e:list[Any]) -> str:
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

class TrajectoryEncoder:
    def __init__(self) -> None:
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

def H(t:int, e:str) -> str:
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