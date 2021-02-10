from machine import Pin, ADC, PWM #  從machine導入Pin, ADC, PWM硬體參數設定類別
import utime       # 導入時間相關類別

pwm = PWM(Pin(17)) # 設定LED2為PWM輸出腳
pwm.freq(1000)     # 設定PWM頻率為1000 Hz
adc = ADC(0)       # 設定連接到ADC0(GP26)，亦可寫成ADC(26)
factor = 3.3 / (65535) # 電壓轉換因子

while True: # 若真則循環
    reading = adc.read_u16() # 讀取類比輸入值16bit無號整數
    pwm.duty_u16(reading)    # 將輸入值轉至PWM工作周期值
    vlot = reading * factor  # 將輸入值轉成電壓值
    print(vlot)              # 將輸入電壓值列印至Shell區
    utime.sleep(0.1)         # 延時0.1秒