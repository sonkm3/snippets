# Blinking LED with MicroPython on Raspberry Pi pico

## Setup Raspberry Pi pico for MicroPython

- Visit Raspberry Pi pico landing page https://www.raspberrypi.org/documentation/pico/getting-started/
- Download `Download UF2 file` from `Getting started with MicroPython`.
- Holding down button on Raspberry Pi pico then connect to PC.
- Raspberry Pi pico will mounted as `RPI-RP2` then copy UF2 file to `RPI-RP2`.
- `RPI-RP2` will automaticaly unmounted then setup have done.

## Setup vscode
- Install `Pico-Go``
  - https://marketplace.visualstudio.com/items?itemName=ChrisWood.pico-go
  - Raspberry Pi pico will be automaticaly connected.
  - If `Pico-Go`'s auto-start annoys you, You can disable auto start from editing setting json, by `All commands` -> `Pico-Go > Global settings`
    - "open_on_start": false,


## Blinking LED on REPL
`Pico-Go`'s terminal will connect to Raspberry Pi pico, You can use REPL.
You can Blink LED with REPL as below.
``` python
Searching for boards on serial devices...
No boards found on USB
Connecting to /dev/tty.usbmodem0000000000001...

>>> from machine import Pin
>>> led = Pin(25, Pin.OUT)
>>> led.value(1)
>>> led.value(0)
>>> 
```

## Blinking LED with lambda
``` python
>>> from machine import Pin, Timer
>>> led = Pin(25, Pin.OUT)
>>> tim = Timer()
>>> tim.init(freq=2.5, mode=Timer.PERIODIC, callback=lambda _: led.toggle())
```

## Stop blinking LED with Timer.deinit()
``` python
>>> tim.deinit()
```

## Use PWM to blink LED gracefully

``` python
from machine import Pin, PWM, Timer

pwm = PWM(Pin(25))
pwm.freq(1000)
tim = Timer()

duty = 0
direction = 1
def pwm_callback(_):
    global duty, direction
    duty += direction
    if duty >= 255:
        direction = -1
    elif duty <= 0:
        direction = 1
    pwm.duty_u16(duty * duty)

tim.init(freq=100, mode=Timer.PERIODIC, callback=pwm_callback)

```


``` python
from machine import Pin, PWM, Timer

pwm = PWM(Pin(25))
pwm.freq(1000)
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

tim.init(freq=100, mode=Timer.PERIODIC, callback=pwm_callback)
```


## PWMで緩やかに点滅させる(PIO)

方針
- LEDにはPIOのpwmで出力
- PIOで階段状の波形を出力
- FIFOでつないで点滅させる

書くPIOのプログラム
- PIOでLチカする
- PIOのLチカからFIFOでpwmに接続する
- Lチカから階段状の波形を出力するよう変更

### machineのPWMをPIO実装に置き換える


### PIOでLチカ実装する


### machineのTimerとcallback部分をPIOに置き換える

