#!/usr/bin/env python3
########################################################################
# Filename    : sep769Project.py
# Description : Automated Car Wash System using RaspberryPi
# Author      : Aditya Goel, Sulaiman Mohiuddin, Mohsin Mohammad
# modification: 2023/05/28
########################################################################

# Import Libraries
import time
import Sweep
import Sweep2
import requests
import SteppingMotor
import RPi.GPIO as GPIO
import UltrasonicRanging
from picamera import PiCamera
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

############# Constants ################################################
PUMP = 7
LED_RED1 = 33
LED_RED2 = 38
LED_GREEN1 = 35
LED_GREEN2 = 40
PCF8574_address = 0x27                          # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F                         # I2C address of the PCF8574A chip.
token="Fxy6WFgoe9gFyevx1rSak9tf5iVnqQWm"        # Blynk Token

# Create PCF8574 GPIO adapter.
try:
  mcp = PCF8574_GPIO(PCF8574_address)
except:
  try:
    mcp = PCF8574_GPIO(PCF8574A_address)
  except:
    print ('I2C Address Error !')
    exit(1)

# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

########################## Setup #############################
def setup():
  GPIO.setmode(GPIO.BOARD)                       # use PHYSICAL GPIO Numbering

  for equipments in [LED_RED1, LED_RED2, LED_GREEN1, LED_GREEN2, PUMP]:
    GPIO.setup(equipments, GPIO.OUT)             # set the all equipments to OUTPUT mode

  for eqHigh in [LED_RED1, LED_RED2]:
    GPIO.output(eqHigh, GPIO.HIGH)               # make RED LEDs output HIGH level

  for eqLow in [LED_GREEN1, LED_GREEN2, PUMP]:
    GPIO.output(eqLow, GPIO.LOW)                 # make lGREEN LEDs and PUMP output LOW level

  mcp.output(3,1)                                # turn on LCD backlight
  lcd.begin(16,2)                                # set number of LCD lines and columns
  lcd.setCursor(0,0)                             # set cursor position
  write(token,"v2","0")
  write(token,"v3","0")

############# Writing data to the Blynk Server  ################

def write(token,pin,value):
    api_url = "https://blynk.cloud/external/api/update?token="+token+"&"+pin+"="+value
    response = requests.get(api_url)
    print (response)
    if "200" in str(response):
        print("Value successfully updated")
    else:
        print("Could not find the device token or wrong pin format")

############# Capture Number Plate using Camera Sensor  ################

def image_capture():
  camera = PiCamera()
  camera.start_preview()
  time.sleep(5)
  camera.capture('/home/pi/Desktop/image.jpg')
  lcd.message( 'Car Detected' )
  write(token,"v1","Car Detected")
  time.sleep(2)
  camera.stop_preview()

############# Phase1 - Car enters the wash #########################################

def phase1_loop():
  GPIO.output(LED_RED1, GPIO.LOW)           # make ledRed1 output LOW
  GPIO.output(LED_RED2, GPIO.LOW)           # make ledRed2 output LOW
  GPIO.output(LED_GREEN1, GPIO.HIGH)        # make ledGreen1 output HIGH signalling the car to enter the wash area.

  writeLCD('Barricade Opened')
  write(token,"v1","Barricade Opened")

  Sweep.main()

  writeLCD('Barricade Closed')
  write(token,"v1","Barricade Closed")

  GPIO.output(LED_GREEN1, GPIO.LOW)         # make ledGreen1 output LOW
  GPIO.output(LED_RED1, GPIO.HIGH)          # make ledRed1 output HIGH

############# Phase2 - Car Alignment takes place ###################################

def phase2_loop():
  count = 0
  while True:
    distance = UltrasonicRanging.main()
    if (count == 5):
      writeLCD('Begin Washing')
      time.sleep(3)
      break

    elif (distance > 5):
      writeLCD('Move Forward')
      count = 0

    elif (distance < 4):
      GPIO.output(LED_RED2, GPIO.HIGH)
      writeLCD('Move Back')
      count = 0

    elif (distance > 4 and distance < 5):
      GPIO.output(LED_RED2, GPIO.HIGH)
      writeLCD('Stop')
      count += 1
      print("Waiting Time", 5-count)

  print ("Begin Washing")

############# Phase3 - Washing, Drying and Car exits the wash #######################

def phase3_loop():

  write(token,"v2","0")
  write(token,"v3","1")
  GPIO.output(PUMP, GPIO.HIGH)

  print("Washing")
  timeLeft = 10
  while(timeLeft >= 0):
    writeLCD('Washing. \nTime Left:' + str(timeLeft))
    write(token,"v1","Washing")
    write(token,"v4",str(timeLeft))
    time.sleep(1)
    timeLeft -= 1
  GPIO.output(PUMP, GPIO.LOW)

  print("Drying")
  timeLeft = 10
  while(timeLeft >= 0):
    writeLCD('Drying.\nTime Left:' + str(timeLeft))
    write(token,"v1","Drying")
    write(token,"v4",str(timeLeft))
    time.sleep(1)
    timeLeft -= 1

  print("Go")
  writeLCD('Process Complete. \nThank You.')
  write(token,"v1","Car is done washing")

  GPIO.output(LED_RED2, GPIO.LOW)               # make ledRed2 output LOW
  GPIO.output(LED_GREEN2, GPIO.HIGH)            # make ledGreen2 output HIGH

  write(token,"v2","1")
  write(token,"v3","0")

  Sweep2.main()

  GPIO.output(LED_GREEN2, GPIO.LOW)             # make ledGreen2 output HIGH
  GPIO.output(LED_RED2, GPIO.HIGH)              # make ledRed2 output LOW
  time.sleep(10)

############# Write On LCD ####################################################

def writeLCD(message):
  lcd.clear()
  lcd.setCursor(0,0)
  lcd.message(message)

############# Destroy ####################################################

def destroy():
  lcd.clear()
  GPIO.cleanup()                                # Release all GPIO

############# Main Function ##############################################

if __name__ == '__main__':                      # Program entrance
  print ('Program is starting ... \n')
  setup()
  try:
      image_capture()
      phase1_loop()
      phase2_loop()
      phase3_loop()
      print("Car is successfully washed")
      destroy()
  except KeyboardInterrupt:         # Press ctrl-c to end the program.
      destroy()
  destroy()