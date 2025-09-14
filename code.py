# code.py — Raspberry Pi Pico (RP2040) + CircuitPython
# One-button USB-MIDI controller (Note On/Off)
# Requirements:
#  - CircuitPython for RP2040 installed on your Pico
#  - "adafruit_midi" library folder copied to CIRCUITPY/lib
#
# Wiring:
#  - Push button between GP15 and GND
#  - Uses internal pull-up; pressed = LOW
#
# Behavior:
#  - Press:  Note On (C4, velocity 100) on MIDI channel 1
#  - Release: Note Off
#
# Tip: If nothing appears in your DAW, try changing usb_midi.ports[1] to ports[0].

import time
import board
import digitalio
import analogio
import usb_midi
from adafruit_midi import MIDI
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange

# === User settings ===
BUTTON_PIN = board.GP15     # GPIO pin for button
MIDI_NOTE = 60              # C4
VELOCITY = 100              # 1-127
CHANNEL = 0                 # 0=ch1, 15=ch16
DEBOUNCE_MS = 20            # debounce time
CC_NUMBER = 1               # Modulation wheel (CC1)
CC_DEADBAND = 1             # (legacy) basic change threshold
# --- Knob noise handling ---
ADC_SAMPLES = 8             # oversample count for averaging
CC_HYSTERESIS = 2           # min CC change to send
CC_SEND_MIN_MS = 25         # min interval between CC sends
EDGE_DEADZONE = 3           # clamp near 0/127 to suppress edge jitter

# === Hardware setup ===
btn = digitalio.DigitalInOut(BUTTON_PIN)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP  # internal pull-up: idle HIGH

# Onboard LED setup
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

# Knob (ADC) setup — GP26 is A0 on Pico
knob = analogio.AnalogIn(board.A0)

# Use USB MIDI OUT (try ports[0] if your system needs it)
midi = MIDI(midi_out=usb_midi.ports[1], out_channel=CHANNEL)

last_state = btn.value
last_change_ms = time.monotonic_ns() // 1_000_000
note_on_sent = False
last_cc_val = -1
last_cc_sent_ms = 0

def now_ms():
    return time.monotonic_ns() // 1_000_000

def adc_to_cc(val: int) -> int:
    # Convert 16-bit ADC (0-65535) to MIDI 7-bit (0-127)
    return int((val / 65535) * 127)

def read_knob_avg(samples: int = ADC_SAMPLES) -> int:
    total = 0
    for _ in range(samples):
        total += knob.value
    return total // samples

while True:
    current = btn.value  # True = released, False = pressed (because of pull-up)
    t = now_ms()

    if current != last_state and (t - last_change_ms) > DEBOUNCE_MS:
        last_change_ms = t
        last_state = current

        if current is False and not note_on_sent:
            # Button pressed -> send Note On
            midi.send(NoteOn(MIDI_NOTE, VELOCITY))
            note_on_sent = True
            led.value = True
        elif current is True and note_on_sent:
            # Button released -> send Note Off
            midi.send(NoteOff(MIDI_NOTE, 0))
            note_on_sent = False
            led.value = False

    # Knob handling — averaged + clamped + rate-limited to reduce jitter
    raw = read_knob_avg()
    cc_val = adc_to_cc(raw)
    # Edge clamping to hold hard 0/127 zones
    if cc_val <= EDGE_DEADZONE:
        cc_val = 0
    elif cc_val >= 127 - EDGE_DEADZONE:
        cc_val = 127

    if (abs(cc_val - last_cc_val) >= CC_HYSTERESIS) and ((t - last_cc_sent_ms) >= CC_SEND_MIN_MS):
        midi.send(ControlChange(CC_NUMBER, cc_val))
        last_cc_val = cc_val
        last_cc_sent_ms = t

    time.sleep(0.005)  # small idle to reduce CPU usage
