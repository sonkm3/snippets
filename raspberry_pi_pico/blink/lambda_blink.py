from machine import Pin, Timer
led = Pin(25, Pin.OUT)
tim = Timer()
tim.init(freq=2.5, mode=Timer.PERIODIC, callback=lambda _: led.toggle())
