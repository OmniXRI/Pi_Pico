'''
main.py by OmniXRI Jack, 11 Feb. 2021

OLED Test Sample

128x128 Pixel, 4bit (16) Gray Level, I2C Interface, SSD1327 Driver IC。

after system inital, OLED will show as blow, x.xxx is ADC input voltage.

OLE-OmnixriJack
L  Press : off
R  Press : off
ADC volt : x.xxx

When

Pb1 press, LED1 On, OLED display 'L Press : on'
Pb2 press, LED2 On, OLED display 'R Press : on'
SVR1 adjust, LED display 'ADC Volt : x.xxx'

https://github.com/OmniXRI/Pi_Pico_OLED_SSD1327_I2C
'''

from machine import I2C, Pin, ADC   # 從machine中導入I2C, Pin, ADC類別
from ssd1327_i2c import SSD1327_I2C # 從ssd1327_i2c中導入SSD1327_I2C類別

led1 = Pin(16, Pin.OUT) # 設定GP16為LED1輸出腳
led2 = Pin(17, Pin.OUT) # 設定GP17為LED2輸出腳
pb1  = Pin(18, Pin.IN, Pin.PULL_UP) # 設定GP18為PB1輸入腳，且自帶pull high電阻
pb2  = Pin(19, Pin.IN, Pin.PULL_UP) # 設定GP19為PB2輸入腳，且自帶pull high電阻

adc = ADC(0)       # 設定連接到ADC0(GP26)，亦可寫成ADC(26)
factor = 3.3 / (65535) # 電壓轉換因子

# 設定I2C ID, SDA, SCL腳位對應，預設通訊頻率freq=400000
i2c = I2C(0, sda=Pin(20), scl=Pin(21)) 
print("I2C Address : " + hex(i2c.scan()[0]).upper()) # 於命令列顯示出I2C裝置位置
print("I2C Configuration: " + str(i2c))              # 於命令列顯示出I2C裝置基本參數

# 配置一個SSD1327_I2C實例，顯示區大小128x128，預設位址addr=0x3C
oled = SSD1327_I2C(i2c,128,128)

while True: # 若真則循環
    oled.fill(0) # 清除顯示區域    
    oled.text("OLED-OmnixriJack", 0, 0, 15)    # 顯示字串於(0,0)位置，顏色15(最亮）
    
    if(pb1.value() == 0):                      # 若Pb1按下
        led1.value(1)                          # 點亮LED1
        oled.text("L  Press : On",  0, 20, 15) # 顯示字串於(0,20)位置，顏色15(最亮）
    else:
        led1.value(0)                          # 熄滅LED1
        oled.text("L  Press : Off", 0, 20, 15) # 顯示字串於(0,20)位置，顏色15(最亮）
        
    if(pb2.value() == 0):                      # 若Pb2按下
        led2.value(1)                          # 點亮LED2
        oled.text("R  Press : On",  0, 40, 15) # 顯示字串於(0,40)位置，顏色15(最亮）
    else:
        led2.value(0)                          # 熄滅LED2
        oled.text("R  Press : Off", 0, 40, 15) # 顯示字串於(0,40)位置，顏色15(最亮）
        
    reading = adc.read_u16() # 讀取類比輸入值16bit無號整數
    volt = reading * factor  # 將輸入值轉成電壓值
    adc_str = "ADC Volt : " + str('%.3f' % volt) # 組成電壓值字串
    oled.text(adc_str, 0, 60, 15) # 顯示字串於(0,60)位置，顏色15(最亮）
    
    oled.show() # 刷新OLED顯示區
