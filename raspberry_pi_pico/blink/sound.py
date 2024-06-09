import gc
from time import sleep
from machine import Pin, PWM, Timer

from math import radians, sin

pwm = PWM(Pin(22))
pwm.freq(1_000_000)

tim = Timer()

gc.disable()

# freq = callback interval / 20
# 8800 / 20 = 440Hz

base = 360 / 20
step = 1

def pwm_callback(_):
    global base, step
    step = (step + 1) % 20
    value = sin(radians(base * step)) * 65535
    pwm.duty_u16(int(value)) # 0-65535

tim.init(freq=8_000, mode=Timer.PERIODIC, callback=pwm_callback)
# tim.init(freq=100, mode=Timer.PERIODIC, callback=pwm_callback)

sleep(3)
tim.deinit()
