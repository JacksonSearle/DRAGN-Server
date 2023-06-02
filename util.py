import time

def format_time(curr_time):
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", curr_time)
    return formatted_time

def increase_time(curr_time, minutes):
    seconds = minutes * 60
    new_time = time.mktime(curr_time) + seconds
    return time.localtime(new_time)

def set_start_time(year, month, day, hour, minute, second):
    start_time = time.struct_time((year, month, day, hour, minute, second, -1, -1, -1))
    return start_time

def time_prompt(curr_time):
    formatted_time = "It is " + time.strftime("%B %d, %Y, %I:%M %p.", curr_time)
    return formatted_time

