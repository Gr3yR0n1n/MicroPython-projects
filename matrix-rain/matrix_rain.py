import uasyncio as asyncio
from random import randrange, choice
import sh1106_i2c
from machine import I2C, Pin
import font_8 as font
import framebuf
import gc

class WaterDrop:
    def __init__(self,d,dropsSpeed,xPos,delay):
        #gc.collect()
        #print("gc.mem_free()", gc.mem_free() )
        
        self.d = d
        self.xPos = xPos
        self.delay = delay
        self.yPos = 1
        
        self.dropsSpeed = dropsSpeed                
                
    def aleatoriedad(self):
        self.length = randrange(2,7)                
        self.movementSpeed = choice(self.dropsSpeed)
        self.randomCharacterSpeed = choice(self.dropsSpeed)
                
    async def start(self):
        self.aleatoriedad()
        await asyncio.sleep(self.delay)
        await asyncio.gather(self.randomChar(), self.moveCharPosition())
    
    async def moveCharPosition(self):        
        while 1:            
            lengthChar = self.length * 8
            for y in range(8 + self.length):
                self.yPos = (y*8)+1
                
                # clear
                yPosClear = self.yPos - lengthChar                
                self.d.fb.fill_rect(self.xPos,yPosClear,5,7,0)
                                
                await asyncio.sleep(self.movementSpeed)
            self.aleatoriedad()
                    
    async def randomChar(self):
        while 1:
            randomNumber = randrange(48,122)
            self.displayChar(randomNumber)
            await asyncio.sleep(self.randomCharacterSpeed)
        
    def displayChar(self,number):
        glyph,char_height,char_width= font.get_int(number)
        fbc = framebuf.FrameBuffer(bytearray(glyph),char_width,char_height,framebuf.MONO_VLSB)
        self.d.fb.blit(fbc,self.xPos,self.yPos)
        #self.d.update()
        
async def refresh(d):
    while 1:
        d.update()
        await asyncio.sleep(0.001)    
        
async def rain():
    # oled setup
    i2c = I2C(-1, sda=Pin(21), scl=Pin(22), freq=400000)
    d = sh1106_i2c.Display(i2c)
    d.mirror(False)
    d.flip(False)
    
    loop = asyncio.get_event_loop()
    loop.create_task(refresh(d)) 
    
    # presets
    dropsSpeed = [0.008, 0.02,0.05,0.1,0.5,0.8]
    
    dropsDelay = [0.5,1.5,1,1.5,0.3,2,1.5,1,0.1,2,
                1,0.5,2,1.5,1,0.5,1,2,0.5,1,1.5]
    
    for x in range (21):
        xPos = (x*6)+1
        loop.create_task(WaterDrop(d,dropsSpeed,xPos,dropsDelay[x]).start() ) 
        
if __name__ == "__main__":                
    loop = asyncio.get_event_loop()
    loop.create_task(rain()) 
    loop.run_forever()