import Tkinter as tk
from logging import root
import ttk
from Tkinter import HORIZONTAL
import RPi.GPIO as GPIO
import time
from time import sleep

waterOutIO = 12
cleanerOutIO = 13
sanitizerOutIO = 16
co2OutIO = 17
drainIO = 18
waterInIO = 19
cleanerInIO = 20
sanitizerInIO = 21
lineDrainIO = 22
pumpRunIO = 24
pumpLowIO = 26
pumpHighIO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(waterOutIO, GPIO.OUT) #04
GPIO.setup(cleanerOutIO, GPIO.OUT)
GPIO.setup(sanitizerOutIO, GPIO.OUT)
GPIO.setup(co2OutIO, GPIO.OUT)
GPIO.setup(drainIO, GPIO.OUT)
GPIO.setup(waterInIO, GPIO.OUT)
GPIO.setup(cleanerInIO, GPIO.OUT)
GPIO.setup(sanitizerInIO, GPIO.OUT)
GPIO.setup(lineDrainIO, GPIO.OUT)
GPIO.setup(pumpRunIO, GPIO.OUT)
GPIO.setup(pumpLowIO, GPIO.OUT)
GPIO.setup(pumpHighIO, GPIO.OUT)

master = tk.Tk()
master.title("GPIO Control")
master.geometry("800x1000")

Process_State = False
Timer = 5

kegCleanerTime=5
kegRinseTime1=6
kegRinseLoop1=3
kegRinseLoop2=3
kegRinseTime2=3
kegSanitzeTime=4
kegDrainTime=3
kegCO2FillTime=3
CO2PurgeTime=2


global kegRinse1
kegRinse1 = tk.StringVar()
kegRinse1.set("Keg Rinse (" + str((kegRinseTime1+kegDrainTime) * kegRinseLoop1) + " sec)")
#kegRinse1.set("Keg Rinse")
global kegRinse2
kegRinse2 = tk.StringVar()
kegRinse2.set("Keg Rinse (" + str((kegRinseTime2+CO2PurgeTime+kegDrainTime) * kegRinseLoop2) + " sec)")
#kegRinse2.set("Keg Rinse")
global kegCleaner
kegCleaner = tk.StringVar()
kegCleaner.set("Keg Cleaner")
global processStart
processStart = tk.StringVar()
processStart.set("Process Started")
global processFinish
processFinish = tk.StringVar()
processFinish.set("Process Finished")
global process
process = tk.StringVar()
process.set("Process")
global kegSanitizer
kegSanitizer = tk.StringVar()
kegSanitizer.set("Keg Sanitize")
global kegCO2Fill
kegCO2Fill = tk.StringVar()
kegCO2Fill.set("Keg CO2 Fill")
global timerLabel
timerLabel = "Timer: " + str(0)
global kegDrain
kegDrain = tk.StringVar()
kegDrain.set("Keg Drain")
global pumpHigh
pumpHigh = tk.StringVar()
pumpHigh.set("Pump High")
global pumpLow
pumpLow = tk.StringVar()
pumpLow.set("Pump Low")
global CO2Purge
CO2Purge = tk.StringVar()
CO2Purge.set("CO2 Purge")

labelTopW = 20
labelTopL = 2
labelBottomL = 1

def PumpOn(lowHigh):
    if lowHigh=="High":
        LabelSet(pumpHigh, "green", labelTopW, labelBottomL, 8, 0)
        GPIO.output(pumpLowIO, GPIO.LOW)
        GPIO.output(pumpHighIO, GPIO.HIGH)
    if lowHigh=="Low":
        LabelSet(pumpHigh, "grey", labelTopW, labelBottomL, 9, 0)
        GPIO.output(pumpHighIO, GPIO.Low)
        GPIO.output(pumpLowIO, GPIO.Low)
    GPIO.output(pumpRunIO, GPIO.HIGH)

def PumpOff():
    LabelSet(pumpHigh, "grey", labelTopW, labelBottomL, 8, 0)
    LabelSet(pumpLow, "grey", labelTopW, labelBottomL, 9, 0)
    GPIO.output(pumpRunIO, GPIO.LOW)
    GPIO.output(pumpLowIO, GPIO.HIGH) #Set to Low
    GPIO.output(pumpHighIO, GPIO.LOW)

def RinseKeg(rinseTime, loop):
    if Process_State==True:
        LabelSet(kegRinse1, "green", labelTopW, labelTopL, 1, 0)
        while loop > -1:
            GPIO.output(waterOutIO, GPIO.HIGH)
            GPIO.output(drainIO, GPIO.HIGH)
            PumpOn("High")
            x = rinseTime
            while x > -1 and Process_State == True:
                timerLabel = "Timer: " +str(x)
                LabelSetText(timerLabel, "black", labelTopW, labelTopL, 1, 1)
                LabelSetText(timerLabel, "black", labelTopW, labelBottomL, 8, 1)
                time.sleep(1.00)
                x -= 1
            PumpOff()
            GPIO.output(waterOutIO, GPIO.LOW)
            Drain(0, kegDrainTime, 1)
            loop -= 1
        Drain(3, kegDrainTime, 1)
        LabelSet(kegRinse1, "grey", labelTopW, labelTopL, 1, 0)
        time.sleep(1.00)

def WashKeg(washTime):
    if Process_State==True:
        LabelSet(kegCleaner, "green", labelTopW, labelTopL, 2, 0)
        GPIO.output(21, GPIO.HIGH)
        x = washTime
        while x > -1 and Process_State == True:
            timerLabel = "Timer: " + str(x)
            LabelSetText(timerLabel, "black", labelTopW, labelTopL, 2, 1)
            time.sleep(1.00)
            x -= 1
        GPIO.output(21, GPIO.LOW)
        LabelSet(kegCleaner, "grey", labelTopW, labelTopL, 2, 0)
        time.sleep(1.00)


def SanitizeKeg(sanitizeTime):
    LabelSet(kegSanitizer, "green", labelTopW, labelTopL, 3, 0)
    GPIO.output(20, GPIO.HIGH)
    x = sanitizeTime
    while x > -1 and Process_State == True:
        timerLabel = "Timer: " + str(x)
        LabelSetText(timerLabel, "black", labelTopW, labelTopL, 3, 1)
        time.sleep(1.00)
        x -= 1
    GPIO.output(20, GPIO.LOW)
    LabelSet(kegSanitizer, "grey", labelTopW, labelTopL, 3, 0)
    time.sleep(1.00)

def Drain(CO2Time, drainTime, drainLoop):
    y = drainLoop
    while y > 0 and Process_State == True:
        if CO2Time > 0:
            GPIO.output(drainIO, GPIO.LOW)
            GPIO.output(co2OutIO, GPIO.HIGH)
            LabelSet(CO2Purge, "green", labelTopW, labelBottomL, 11, 0)
            x = CO2Time
            while x > -1 and Process_State == True:
                timerLabel = "Timer: " + str(x)
                LabelSetText(timerLabel, "black", labelTopW, labelBottomL, 11, 1)
                time.sleep(1.00)
                x -= 1
            GPIO.output(co2OutIO, GPIO.LOW)
            LabelSet(CO2Purge, "Grey", labelTopW, labelBottomL, 11, 0)
        LabelSet(kegDrain, "green", labelTopW, labelBottomL, 10, 0)
        GPIO.output(drainIO, GPIO.HIGH)
        x = drainTime
        while x > -1 and Process_State == True:
            timerLabel = "Timer: " + str(x)
            LabelSetText(timerLabel, "black", labelTopW, labelBottomL, 10, 1)
            time.sleep(1.00)
            x -= 1
        LabelSet(kegDrain, "grey", labelTopW, labelBottomL, 10, 0)
        y -= 1
    GPIO.output(drainIO, GPIO.LOW)
    time.sleep(1.00)

def CO2Fill(CO2Time):
    LabelSet(kegCO2Fill, "green", labelTopW, labelTopL, 5, 0)
    GPIO.output(20, GPIO.HIGH)
    x = CO2Time
    while x > -1 and Process_State == True:
        timerLabel = "Timer: " + str(x)
        LabelSetText(timerLabel, "black", labelTopW, labelTopL, 5, 1)
        time.sleep(1.00)
        x -= 1
    GPIO.output(20, GPIO.LOW)
    LabelSet(kegCO2Fill, "grey", labelTopW, labelTopL, 5, 0)
    time.sleep(1.00)

def LabelSet(text1, color1, w1, h1, r1, c1 ):
    label = tk.Label(master, textvariable=text1, fg=color1, width=w1, height=h1, font=("Helvetica",30))
    label.grid(row=r1, column=c1)
    label.update()

def LabelSetText(text1, color1, w1, h1, r1, c1 ):
    label = tk.Label(master, text=text1, fg=color1, width=w1, height=h1, font=("Helvetica",30))
    label.grid(row=r1, column=c1)
    label.update()


def Process():
    global Process_State
    Process_State = True
    #setIOLow()
    LabelSet(processStart, "green", labelTopW, labelTopL, 0, 0)
    RinseKeg(kegRinseTime1, kegRinseLoop1)
    WashKeg(kegCleanerTime)
    RinseKeg(kegRinseTime2, kegRinseLoop2)
    SanitizeKeg(kegSanitzeTime)
    CO2Fill(kegCO2FillTime)
    LabelSet(processFinish, "green", labelTopW, labelTopL, 0, 0)

def Quit():
    setIOLow()
    master.destroy()

def setIOLow():
    GPIO.output(waterOutIO, GPIO.LOW)  # 04
    GPIO.output(cleanerOutIO, GPIO.LOW)
    GPIO.output(sanitizerOutIO, GPIO.LOW)
    GPIO.output(co2OutIO, GPIO.LOW)
    GPIO.output(drainIO, GPIO.LOW)
    GPIO.output(waterInIO, GPIO.LOW)
    GPIO.output(cleanerInIO, GPIO.LOW)
    GPIO.output(sanitizerInIO, GPIO.LOW)
    GPIO.output(lineDrainIO, GPIO.LOW)
    GPIO.output(pumpRunIO, GPIO.LOW)
    GPIO.output(pumpLowIO, GPIO.LOW)
    GPIO.output(pumpHighIO, GPIO.LOW)


#fontStyle = tkFont.Font(family="Lucida Grande", size=20)


LabelSet(process, "grey", labelTopW, labelTopL, 0, 0)

LabelSet(kegRinse1, "grey", labelTopW, labelTopL, 1, 0)
LabelSetText("Timer: " + str(kegRinseTime1), "black", labelTopW, labelTopL, 1, 1)

LabelSet(kegCleaner, "grey", labelTopW, labelTopL, 2, 0)
LabelSetText("Timer: " + str(kegCleanerTime), "black", labelTopW, labelTopL, 2, 1)

LabelSet(kegRinse2, "grey", labelTopW, labelTopL, 3, 0)
LabelSetText("Timer: " + str(kegRinseTime2), "black", labelTopW, labelTopL, 3, 1)

LabelSet(kegSanitizer, "grey", labelTopW, labelTopL, 4, 0)
LabelSetText("Timer: " + str(kegSanitzeTime), "black", labelTopW, labelTopL, 4, 1)

LabelSet(kegCO2Fill, "grey", labelTopW, labelTopL, 5, 0)
LabelSetText("Timer: " + str(kegCO2FillTime), "black", labelTopW, labelTopL, 5, 1)

ttk.Separator(master, orient=HORIZONTAL).grid(column=0, row=6, columnspan=2, sticky='ew')

Blanklabel = tk.Label(master, text="", fg="grey", width=labelTopW, height=1, font=("Helvetica",30))
Blanklabel.grid(row=7, column=0)

LabelSet(pumpHigh, "grey", labelTopW, labelBottomL, 8, 0)
LabelSetText("Timer: " + str(0), "black", labelTopW, labelBottomL, 8, 1)

LabelSet(pumpLow, "grey", labelTopW, labelBottomL, 9, 0)
LabelSetText("Timer: " + str(0), "black", labelTopW, labelBottomL, 9, 1)

LabelSet(kegDrain, "grey", labelTopW, labelBottomL, 10, 0)
LabelSetText("Timer: " + str(kegDrainTime), "black", labelTopW, labelBottomL, 10, 1)

LabelSet(CO2Purge, "grey", labelTopW, labelBottomL, 11, 0)
LabelSetText("Timer: " + str(CO2PurgeTime), "black", labelTopW, labelBottomL, 11, 1)

Blanklabel = tk.Label(master, text="", fg="grey", width=labelTopW, height=1, font=("Helvetica",30))
Blanklabel.grid(row=12, column=0)

Exitbutton = tk.Button(master, text="Exit", bg="red", width=labelTopW, height=4, command=Quit)
Exitbutton.grid(row=13,column=0)

Startbutton = tk.Button(master, text="Start", bg="Green", command=Process, width=labelTopW, height=4 )
Startbutton.grid(row=13, column=1)




master.mainloop()

