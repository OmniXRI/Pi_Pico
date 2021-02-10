'''
ssda327_i2c.py by OmniXRI Jack 11 Feb. 2021

OLED MicroPython Driver for Raspberry Pi Pico,
128x128 pixel, 4bit (16) Gray Level, I2C Interface.

https://github.com/OmniXRI/Pi_Pico_OLED_SSD1327_I2C
'''

from micropython import const # 從MicroPython中導入常數設定類別
import framebuf # 導入影格緩衝區類別

# SSD1327命令暫存器編號定義
SET_COL_ADDR          = const(0x15) # 設定行位址
SET_SCROLL_DEACTIVATE = const(0x2E) # 設定捲動不活動
SET_ROW_ADDR          = const(0x75) # 設定列位址
SET_CONTRAST          = const(0x81) # 設定顯示對比
SET_SEG_REMAP         = const(0xA0) # 設定顯示節段重新映射
SET_DISP_START_LINE   = const(0xA1) # 設定顯示起始列
SET_DISP_OFFSET       = const(0xA2) # 設定顯示偏移量
SET_DISP_MODE         = const(0xA4) # 設定顯示模式：一般0xA4, 全亮0xA5, 全滅0xA6, 反相0xA7
SET_MUX_RATIO         = const(0xA8) # 設定多重尋址
SET_FN_SELECT_A       = const(0xAB) # 設定功能選擇A
SET_DISP              = const(0xAE) # 設定顯示電源關閉0xAE,電源開啟0xAF
SET_PHASE_LEN         = const(0xB1) # 設定顯示節段波形長度
SET_DISP_CLK_DIV      = const(0xB3) # 設定顯示派波除數
SET_SECOND_PRECHARGE  = const(0xB6) # 設定第二段充電電壓
SET_GRAYSCALE_TABLE   = const(0xB8) # 設定灰階表
SET_GRAYSCALE_LINEAR  = const(0xB9) # 設定灰階線性度
SET_PRECHARGE         = const(0xBC) # 設定預充電電壓
SET_VCOM_DESEL        = const(0xBE) # 設定VCOM電壓
SET_FN_SELECT_B       = const(0xD5) # 設定功能選擇B
SET_COMMAND_LOCK      = const(0xFD) # 設定命令鎖定

# SSD1327指定命令/資料 (後六位為0)
REG_CMD  = const(0x80) # 指定為命令，Co=1, D/C#=0
REG_DATA = const(0x40) # 指定為資料，Co=0, D/C#=1

# SSD1327_I2C類別 
class SSD1327_I2C:
    # 初始化函式，設定基本變數
    def __init__(self, i2c, width, height, addr=0x3C, external_VCC=False):
        self.i2c = i2c       # 指定I2C元件
        self.width = width   # 指定OLED顯示寬度
        self.height = height # 指定OLED顯示高度
        self.addr = addr     # 顯示I2C位置（預設0x3C）
        self.external_VCC = external_VCC # 指定外部供電（預設為否）
        self.buffer = bytearray(self.width * self.height // 2)  # 由於顯示像素為4bit(16灰階)，所需記憶體數量為長x寬的一半
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.GS4_HMSB) # 配置所需記憶體，大小、長、寬及4bit顯示方式。
        self.temp = bytearray(2) # 配置給SSD1327命令緩衝區
        self.poweron()           # OLED電源開啟
        self.init_display()      # OLED進行初始化
    
    # 寫入命令函式
    def write_cmd(self, cmd):
        self.temp[0] = REG_CMD # Co=1, D/C#=0
        self.temp[1] = cmd     # 命令內容
        self.i2c.writeto(self.addr, self.temp) # 將命令寫到指定位址
        
    # 寫入資料函式
    # 不支援 I2C.start() + I2C.write() + I2C.stop()
    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40'+buf) # 指定寫入資料(REG_DATA 0x40)及寫入緩衝區內容
    
    # OLED初始化內容，依序執行命令完成初始化並清除OLED顯示區
    def init_display(self):
        for cmd in (
            SET_COMMAND_LOCK, 0x12, # 命令解鎖(Unlock)
            SET_DISP, # 關閉顯示(Display off)
            # 設定顯示解析度及排列(Resolution and layout)
            SET_DISP_START_LINE, 0x00, # 設定顯示啟始列(start line)
            SET_DISP_OFFSET, 0x0, # 設定顯示垂直偏移量(vertical offse)
            # 設定重新映射方式(Set re-map)
            # Enable column address re-map
            # Disable nibble re-map
            # Horizontal address increment
            # Enable COM re-map
            # Enable COM split odd even
            SET_SEG_REMAP, 0x51,
            SET_MUX_RATIO, self.height - 1, 
            # 設定時序及驅動電路(Timing and driving scheme)
            SET_FN_SELECT_A, 0x01, # 致能內部供電(Enable internal VDD regulator)
            SET_PHASE_LEN, 0x51, # Phase 1: 1 DCLK, Phase 2: 5 DCLKs
            SET_DISP_CLK_DIV, 0x01, # 設定顯示脈波除數(Divide ratio: 1, Oscillator Frequency: 0)
            SET_PRECHARGE, 0x08, # 設定預充電電壓(Set pre-charge voltage level: VCOMH)
            SET_VCOM_DESEL, 0x07, # 設定VCOM電壓(Set VCOMH COM deselect voltage level: 0.86*Vcc)
            SET_SECOND_PRECHARGE, 0x01, # 設定第二段充電電壓(Second Pre-charge period: 1 DCLK)
            SET_FN_SELECT_B, 0x62, # 設定功能選擇B(Enable enternal VSL, Enable second precharge)
            # 設定顯示(Display)
            SET_GRAYSCALE_LINEAR, # 使用線性灰階對照表(Use linear greyscale lookup table)
            SET_CONTRAST, 0x7f, # 設定對比中間亮度(Medium brightness)
            SET_DISP_MODE, # 設定顯示模式一般不反相(Normal, not inverted)
            # 設定行列起始位置，以公式自動轉換96x96, 128x128像素OLED
            # 96x96:
            # SET_ROW_ADDR, 0 95,
            # SET_COL_ADDR, 8, 55,
            # 128x128:
            # SET_ROW_ADDR, 0 127,
            # SET_COL_ADDR, 0, 63,
            SET_ROW_ADDR, 0x00, self.height - 1,
            SET_COL_ADDR, ((128 - self.width) // 4), 63 - ((128 - self.width) // 4),

            SET_SCROLL_DEACTIVATE, # 設定捲動不啟動
            SET_DISP | 0x01): # 設定顯示開啟(Display on)
            self.write_cmd(cmd) # 依序寫入命令            
        self.fill(0) # 清除畫面(clear screen)
        self.show()  # 顯示內容

    # 關閉OLED電源
    def poweroff(self):
        self.write_cmd(SET_FN_SELECT_A)
        self.write_cmd(0x00) # Disable internal VDD regulator, to save power
        self.write_cmd(SET_DISP)

    # 關閉OLED電源
    def poweron(self):
        self.write_cmd(SET_FN_SELECT_A)
        self.write_cmd(0x01) # Enable internal VDD regulator
        self.write_cmd(SET_DISP | 0x01)
    
    # 顯示緩衝區內容    
    def show(self):
        self.write_cmd(SET_COL_ADDR) # 指定行啟始位置
        self.write_cmd((128 - self.width) // 4)
        self.write_cmd(63 - ((128 - self.width) // 4))
        self.write_cmd(SET_ROW_ADDR) # 指定列啟始位置
        self.write_cmd(0x00)
        self.write_cmd(self.height - 1)
        self.write_data(self.buffer) # 寫入緩衝區內容
        
    # 調整顯示對比
    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast) # 對比值 0-255

    # 顯示反相(Ture/False)
    def invert(self, invert): # 
        self.write_cmd(SET_DISP_MODE | (invert & 1) << 1 | (invert & 1)) # 0xA4=Normal, 0xA7=Inverted

    # 將所有像素填入指定顏色，4bit灰階 (0 - 15)
    def fill(self, color): 
        self.framebuf.fill(color)
     
    # 將特定位置像素填入指定顏色，4bit灰階 (0 - 15)   
    def pixel(self, x, y, color):
        self.framebuf.pixel(x, y, color)

    # 軟體顯示捲動
    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)        

    # 在指定位置顯示文字串及對應顏色，4bit灰階 (0 - 15)，預設顏色15
    def text(self, string, x, y, color=15):
        self.framebuf.text(string, x, y, color)
