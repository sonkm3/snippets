import machine
led = machine.Pin('LED', machine.Pin.OUT)
timer = machine.Timer()
timer.init(freq=2.5, mode=machine.Timer.PERIODIC, callback=lambda _: led.toggle())