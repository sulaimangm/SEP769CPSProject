#!/usr/bin/env python3
########################################################################
# Filename    : Sweep.py
# Description : Servo sweep
# Author      : www.freenove.com
# modification: 2019/12/27
########################################################################
import RPi.GPIO as GPIO
import time
OFFSET_DUTY = 0.5        # define pulse offset of servo
SERVO_MIN_DUTY = 2.5 + OFFSET_DUTY     # define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5 + OFFSET_DUTY    # define pulse duty cycle for maximum angle of servo
SERVO_DELAY_SEC = 0.001
servoPin = 8

def setup():
    global p
    GPIO.setmode(GPIO.BOARD)         # use PHYSICAL GPIO Numbering
    GPIO.setup(servoPin, GPIO.OUT)   # Set servoPin to OUTPUT mode
    GPIO.output(servoPin, GPIO.LOW)  # Make servoPin output LOW level

    p = GPIO.PWM(servoPin, 50)     # set Frequence to 50Hz
    p.start(0)                     # Set initial Duty Cycle to 0

def servoWrite(angle):      # make the servo rotate to specific angle, 0-180
    if(angle < 0):
        angle = 0
    elif(angle > 110):
        angle = 110
    dc = SERVO_MIN_DUTY + (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * angle / 180.0 # map the angle to duty cycle
    p.ChangeDutyCycle(dc)

def loop():
    for angle in range(20, 111, 1):   # make servo rotate from 0 to 180 deg
        servoWrite(angle)
        time.sleep(SERVO_DELAY_SEC)
    time.sleep(10)

    for angle in range(110, 19, -1): # make servo rotate from 180 to 0 deg
        servoWrite(angle)
        time.sleep(SERVO_DELAY_SEC)
    time.sleep(2)
    p.stop()
    print("Sweep Done")

def destroy():
    GPIO.cleanup()

def main():
    print ('Sweep Program is starting...')
    setup()
    loop()