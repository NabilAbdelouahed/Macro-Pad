import time
import board
import busio
import digitalio
import usb_hid
import displayio
import terminalio

from adafruit_display_text import label
from adafruit_displayio_ssd1306 import SSD1306

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from keyboard_layout_fr import KeyboardLayoutFR

displayio.release_displays()

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64

display = SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)
splash = displayio.Group()
display.root_group = splash

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutFR(keyboard)
consumer_control = ConsumerControl(usb_hid.devices)

mode_switch_pin = digitalio.DigitalInOut(board.GP2)
mode_switch_pin.direction = digitalio.Direction.INPUT
mode_switch_pin.pull = digitalio.Pull.UP

action_pins = [
    board.GP16, board.GP17, board.GP18,
    board.GP19, board.GP15, board.GP14,
    board.GP20, board.GP13, board.GP12
]
action_switches = [digitalio.DigitalInOut(pin) for pin in action_pins]
for switch in action_switches:
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.UP

current_mode = 0
mode_names = ['Sound Control', 'Open Apps', 'Open Programs', 'Custom']

def open_application(app_name):
    keyboard.press(0x08)
    keyboard.release_all()
    time.sleep(0.2)
    keyboard_layout.write('r')
    time.sleep(0.2)
    keyboard.press(0x28)
    keyboard.release_all()
    time.sleep(0.5)
    keyboard_layout.write(app_name)
    keyboard.press(0x28)
    keyboard.release_all()

def send_copy():
    keyboard.press(0x01, 0x06)
    keyboard.release_all()

def send_paste():
    keyboard.press(0x01, 0x19)
    keyboard.release_all()

def send_undo():
    keyboard.press(0x01, 0x1d)
    keyboard.release_all()

def send_redo():
    keyboard.press(0x01, 0x1c)
    keyboard.release_all()

modes = [
    [
        ('Volume Up', lambda: consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)),
        ('Volume Down', lambda: consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)),
        ('Mute', lambda: consumer_control.send(ConsumerControlCode.MUTE)),
        ('Play/Pause', lambda: consumer_control.send(ConsumerControlCode.PLAY_PAUSE)),
        ('Next Track', lambda: consumer_control.send(ConsumerControlCode.SCAN_NEXT_TRACK)),
        ('Previous Track', lambda: consumer_control.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)),
        ('Stop', lambda: consumer_control.send(ConsumerControlCode.STOP)),
        ('Fast Forward', lambda: consumer_control.send(ConsumerControlCode.FAST_FORWARD)),
        ('Rewind', lambda: consumer_control.send(ConsumerControlCode.REWIND))
    ],
    [
        ('Open Opera', lambda: open_application('opera')),
        ('Open Chrome', lambda: open_application('chrome')),
        ('Open CMD', lambda: open_application('cmd')),
        ('Open PowerShell', lambda: open_application('powershell')),
        ('Copy', send_copy),
        ('Paste', send_paste),
        ('Undo', send_undo),
        ('Redo', send_redo),
        ('Empty', lambda: None)
    ],
    [
        ('Open Krita', lambda: open_application('krita')),
        ('Open Fusion360', lambda: open_application('fusion360')),
        ('Open Inkscape', lambda: open_application('inkscape')),
        ('Open PyCharm', lambda: open_application('pycharm')),
        ('Open Android Studio', lambda: open_application('studio64')),
        ('Open VSCode', lambda: open_application('code')),
        ('Open QFlipper', lambda: open_application('qflipper')),
        ('Open DaVinci', lambda: open_application('resolve')),
        ('Empty', lambda: None)
    ],
    [('Empty', lambda: None)] * 9
]

def wrap_text(text, max_chars):
    """
    Wrap text into multiple lines so that no line exceeds max_chars characters.
    Returns a list of lines.
    """
    words = text.split()
    wrapped_lines = []
    current_line = ""

    for word in words:
        # Check if adding the next word would exceed the line length
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (word + " ")  # Add word to the current line
        else:
            wrapped_lines.append(current_line.strip())  # Add the line and reset it
            current_line = word + " "  # Start a new line with the current word

    wrapped_lines.append(current_line.strip())  # Add the last line
    return wrapped_lines

def display_text(line1, line2=''):
    # Assume each character is roughly 6 pixels wide, adjust based on your font
    max_chars_per_line = WIDTH // 6  
    line_height = 12  # Approx height of one line of text

    # Clear the previous text labels
    while len(splash) > 1:
        splash.pop(1)

    # Wrap lines
    wrapped_line1 = wrap_text(line1, max_chars_per_line)
    wrapped_line2 = wrap_text(line2, max_chars_per_line)

    # Calculate the total number of lines and the block's total height
    total_lines = len(wrapped_line1) + len(wrapped_line2)
    total_height = total_lines * line_height

    # Determine the starting y position to vertically center the text
    y_position = (HEIGHT - total_height) // 2

    # Create and position the text labels for the first set of lines
    for line in wrapped_line1:
        text_area = label.Label(terminalio.FONT, text=line, color=0xFFFFFF)
        text_area.x = (WIDTH - text_area.bounding_box[2]) // 2  # Center horizontally
        text_area.y = y_position
        splash.append(text_area)
        y_position += line_height  # Move down to the next line

    # Create and position the text labels for the second set of lines
    for line in wrapped_line2:
        text_area = label.Label(terminalio.FONT, text=line, color=0xFFFFFF)
        text_area.x = (WIDTH - text_area.bounding_box[2]) // 2  # Center horizontally
        text_area.y = y_position
        splash.append(text_area)
        y_position += line_height  # Move down to the next line

# Example usage
display_text('This is a long phrase that will be wrapped to fit the display', 'Another long phrase here.')



# Example usage
display_text('This is a long phrase that will be wrapped to fit the display', 'Another long phrase here.')


# Function call example (you can use this in the while loop or wherever necessary)
display_text('Mode:', mode_names[current_mode])


# Function call example (you can use this in the while loop or wherever necessary)
display_text('Mode:', mode_names[current_mode])


display_text('Mode:', mode_names[current_mode])

while True:
    if not mode_switch_pin.value:
        current_mode = (current_mode + 1) % 4
        display_text('Mode:', mode_names[current_mode])
        time.sleep(0.2)

    for i, switch in enumerate(action_switches):
        if not switch.value:
            action_name, action = modes[current_mode][i]
            action()
            display_text('Mode: {}'.format(mode_names[current_mode]), 'Action: {}'.format(action_name))
            while not switch.value:
                time.sleep(0.01)
            time.sleep(0.1)
    time.sleep(0.01)
