from machine import Pin, PWM, Timer

pwm = PWM(Pin(25))
pwm.freq(10_000)
tim = Timer()

def get_pwm_callback(duty, direction):
    def pwm_callback(_):
        nonlocal duty, direction
        duty += direction
        if duty >= 255:
            direction = -1
        elif duty <= 0:
            direction = 1
        pwm.duty_u16(duty * duty)
    return pwm_callback

pwm_callback = get_pwm_callback(0, 1)

tim.init(freq=1000, mode=Timer.PERIODIC, callback=pwm_callback)
