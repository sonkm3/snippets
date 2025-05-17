import machine
import time

temp_adc = machine.ADC(4) # RP2040内蔵の温度計は5つ目のADコンバーターに接続されています

def get_temperature():
    v = (3.3/65535) * temp_adc.read_u16()
    t = 27 - (v - 0.706)/0.001721
    return t

while True:
    print(get_temperature())
    time.sleep(1)