from math import sin, radians

base = 360 / 20
step = 1

def pwm_callback(_):
    global base, step
    step = (step + 1) % 20
    value = sin(radians(base * step)) * 65535
    print(int(value))

for i in range(360/20):
    pwm_callback(0)
