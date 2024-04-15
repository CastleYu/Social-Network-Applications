import re
from datetime import timedelta, datetime


def convert_time_desc_to_datetime(time_string, now):
    """
    根据不同的时间字符串格式，转换为 "%Y年%m月%d日 %H:%M" 格式的字符串。
    :param time_string: 输入的时间字符串。
    :param now: 当前时间的datetime对象。
    :return: 转换后的时间字符串。
    """
    time_patterns = {
        r'(\d+)秒前.*': lambda time_match: now - timedelta(seconds=int(time_match.group(1))),
        r'(\d+)分钟前.*': lambda time_match: now - timedelta(minutes=int(time_match.group(1))),
        r'(\d+)小时前.*': lambda time_match: now - timedelta(hours=int(time_match.group(1))),
        r'(\d+)天前.*': lambda time_match: now - timedelta(days=int(time_match.group(1))),
        r'(\d+)周前.*': lambda time_match: now - timedelta(weeks=int(time_match.group(1))),
        r'(\d+)月前.*': lambda time_match: now - timedelta(days=int(time_match.group(1)) * 30),  # 简化处理
        r'(\d+)年前.*': lambda time_match: now - timedelta(days=int(time_match.group(1)) * 365),  # 简化处理
        r'(今天|昨天) ?(\d+):(\d+).*': lambda time_match: now.replace(hour=int(time_match.group(2)),
                                                                   minute=int(time_match.group(3)), second=0,
                                                                   microsecond=0) - (
                                                           timedelta(days=1) if time_match.group(
                                                               1) == '昨天' else timedelta()),
        r'(\d{1,2})月(\d{1,2})日 (\d+):(\d+).*': lambda time_match: now.replace(month=int(time_match.group(1)),
                                                                              day=int(time_match.group(2)),
                                                                              hour=int(time_match.group(3)),
                                                                              minute=int(time_match.group(4))),
        r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d+):(\d+).*': lambda time_match: datetime(year=int(time_match.group(1)),
                                                                                      month=int(time_match.group(2)),
                                                                                      day=int(time_match.group(3)),
                                                                                      hour=int(time_match.group(4)),
                                                                                      minute=int(time_match.group(5))),
        r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d+):(\d+).*': lambda time_match: datetime(year=int(time_match.group(1)),
                                                                                  month=int(time_match.group(2)),
                                                                                  day=int(time_match.group(3)),
                                                                                  hour=int(time_match.group(4)),
                                                                                  minute=int(time_match.group(5))),
    }

    for pattern, handler in time_patterns.items():
        match = re.match(pattern, time_string)
        if match:
            # 根据匹配到的模式使用相应的处理函数
            dt = handler(match)
            return dt.strftime('%Y年%m月%d日 %H:%M')

    print(f'时间字符串处理 "{time_string}" 时失败')
    return time_string
