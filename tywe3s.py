"""
configuration.yaml looks like this
light:
  - platform: mqtt
    name: "TYWE3S"
    state_topic: "home/lamp1/light/status"
    command_topic: "home/lamp1/light/switch"
    brightness_state_topic: "home/lamp1/brightness/status"
    brightness_command_topic: "home/lamp1/brightness/set"
    brightness_scale: 1023

"""
from umqtt.simple import MQTTClient
from machine import Pin, PWM
import utime, network, ujson
          
#### set these to match your requirements ####
state_topic = b"home/rgb1/status"
command_topic = b"home/rgb1/set"
server="192.168.1.xxx"                      # your MQTT server
ssid = 'your_ssid'
pwd = 'your_wifi password'

#### DO NOT CHANGE ANYTHING AFTER HERE ####

def send_status():
    """ send the on / off and brightness to home assistant """
    global state, white_value, color, brightness
    msg = {'state':state, 'white_value':white_value, 'brightness':brightness, 'color': color}
    msg = ujson.dumps(msg)
    msg = msg.encode()
    c.publish(state_topic, msg)
    print('sent', msg)
    
def set_rgb(color, brightness = 0):
    """ set the rgb color and brightness"""
    red_pwm.duty(int(color['r'] * brightness / 100) * 4)
    green_pwm.duty(int(color['g'] * brightness / 100) * 4)
    blue_pwm.duty(int(color['b'] * brightness / 100) * 4)
    
def set_white(white_value = 0):
    """ set the white value """
    white_pwm.duty(white_value)

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global white_value, state, color, brightness
    print((topic, msg))
    msg = ujson.loads(msg)
    state = msg['state']
    print ('received state', state)
    
    if 'white_value' in msg:                    # setting the brightnes
        white_value = msg['white_value']        # set the duty cycle to the value sent
        print('white_value', white_value)
        
    if 'color' in msg:                          # setting the rgb value
        color = msg['color']
        print ('color: ', color)
        
    if 'brightness' in msg:
        brightness = msg['brightness']          # set the duty cycle to the value sent
        print('brightness', brightness)
    
    if 'state' in msg:
        state = msg['state']
        if state == "ON":                       # setting the status
            set_white(white_value)              # set the brightness to the stored value
            set_rgb(color, brightness)
        elif state == "OFF":                    # 'OFF' received
            set_white()                         # set pwm duty to zero
            set_rgb({'r':0, 'g':0, 'b':0})
    send_status()

state = "ON"                                    # lamp status
white_value = 255                               # white pwm duty cycle
color = {'r':0, 'g':0, 'b':0}                   # initialise rgb to all off
brightness = 0                                  # initialise brightness to 0

pr = Pin(4)                                     # PWM Pin for red
pw = Pin(5)                                     # PWM Pin for white
pg = Pin(12)                                    # PWM Pin for green
pb = Pin(14)                                    # PWM Pin for blue

# configure PWM
red_pwm = PWM(pr)                               
white_pwm = PWM(pw)
green_pwm = PWM(pg)
blue_pwm = PWM(pb)

# set pwm frequency
pwm_f = 500
red_pwm.freq(pwm_f)
white_pwm.freq(pwm_f) 
green_pwm.freq(pwm_f)
blue_pwm.freq(pwm_f)

# initialise the rgb
set_rgb(color)
set_white(white_value)

sta_if = network.WLAN(network.STA_IF)       # make wifi station object      
if not sta_if.isconnected():                # check if connected
	print('connecting to network...')
	sta_if.active(True)                     # if not make station interface active
	sta_if.connect(ssid, pwd)               # connect to wifi
	while not sta_if.isconnected():         # loop round until connected
		pass
print('network config:', sta_if.ifconfig())

print(sta_if.config('dhcp_hostname'))       # unique name of ESP8266

# connec to mqtt
c = MQTTClient(sta_if.config('dhcp_hostname'), server)
c.set_callback(sub_cb)                      # set the callback function
c.connect()                                 # get connected
c.subscribe(command_topic)                  # subscribe to command topic    

send_status()                               # update home assistant with light on / off, rgb and brightness

while True:
    # blocking wait for message
    c.wait_msg()                            # endless loop waiting for messages
    
c.disconnect()                              # if we come out of the loop for any reason then disconnect

    