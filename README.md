# ESP8266-Home-Assistant-RGB-Bulb
This Micropython project is to Hack a TYWE3S board in a cheap WiFi RGB Bulb

You can follow the variuos teardown discussions here https://community.home-assistant.io/t/cheap-uk-wifi-bulbs-with-tasmota-teardown-help-tywe3s/40508?u=beantree

My user name is beantree

I managed to flash Micropython onto the TYWE3S board. I then found that each of the red, green, blue and white LEDs were controlled by independent Pins on the processor. Each of those Pins can be driven by PWM, which means the ability to control the brightness.

This code exposes that ability via an MQTT server, which, in turn, means I can use Home Assistant to control the bulb.

You can see my screenshot from HA in the discussion link.
