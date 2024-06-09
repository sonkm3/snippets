# Raspberry Pi pico、MicroPythonでLチカするまでのメモ

## MicroPythonを使えるように準備する
https://www.raspberrypi.org/documentation/pico/getting-started/

- 「Getting started with MicroPython」のところから「Download UF2 file」をダウンロード
- Raspberry Pi picoのボタンを押しながらUSBケーブルを接続する(PCに接続する)
- ダウンロードしたUF2ファイルをマウントされた「RPI-RP2」にコピー
- 自動でアンマウントされ、再起動したら完了

## vscodeの環境整備
- Pico-Goをインストールする
  - https://marketplace.visualstudio.com/items?itemName=ChrisWood.pico-go
  - 自動的に認識してくれる
  - Pico-Goが自動起動して鬱陶しい場合は「All commands」から「Pico-Go > Global settings」を選んで設定ファイルを開き
    - "open_on_start": false,
  - にすることで無効にできる

## REPLでLチカ
Pico-GoのターミナルがRaspberry Pi picoに接続するとREPLが使えるようになるのでREPLでLEDの点灯、消灯ができる
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

## lambdaを使って点滅させる
``` python
>>> from machine import Pin, Timer
>>> led = Pin(25, Pin.OUT)
>>> tim = Timer()
>>> tim.init(freq=2.5, mode=Timer.PERIODIC, callback=lambda _: led.toggle())
```

## 点滅のためのTimerを停止する場合はdeinit()
``` python
>>> tim.deinit()
```

## PWMで緩やかに点滅させる

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
global使いたくないけどクロージャでうまく動かせなかったのでいったんこれ

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
nonlocalすれば期待通りに動いてよかったがこれでいいのか！？

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

