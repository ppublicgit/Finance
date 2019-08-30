import time
import calendar
import datetime


def str2utc(s):
    # parse twitter time string into UTC seconds, unix-style
    # python's bizarro world of dates, times and calendars
    return calendar.timegm(time.strptime(s, "%a %b %d %H:%M:%S +0000 %Y"))

def snowflake2utc(sf):
    return ((sf >> 22) + 1288834974657) / 1000.0

def utc2snowflake(stamp):
    return (int(round(stamp * 1000)) - 1288834974657) << 22

def str2utcms(s):
    return 1000 * calendar.timegm(time.strptime(s, "%a %b %d %H:%M:%S +0000 %Y"))

def snowflake2utcms(sf):
    return ((sf >> 22) + 1288834974657)

id = 1165800835554664448
a = snowflake2utc(id)
b = datetime.datetime.utcfromtimestamp(a)
e = b.replace(tzinfo=datetime.timezone.utc).timestamp()
