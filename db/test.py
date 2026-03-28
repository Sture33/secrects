import time
now = time.localtime()
hour = now.tm_hour
minute = now.tm_min
day = now.tm_yday

print(hour, minute, day)
if 0<hour<6:
    print('p1')
elif 6<hour<12:
    print('p2')
elif 12<hour<18:
    print('p3')
elif 18<hour<24:
    print('p4')