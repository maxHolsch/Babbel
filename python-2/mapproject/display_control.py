"""

Controlling the display through the connection from the Arduino

"""
import serial
import time
import logging
import sys
import os
import select
import pygame
import threading

# Add the path to the modules directory
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))
print(module_path)
if module_path not in sys.path:
    sys.path.append(module_path)
from waveshare_epd import epd7in5_V2
import os
from PIL import Image

AUDIO = True


# Try to open serial connection (optional for testing)
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()
    use_serial = True
    print('serial connected.')
except serial.SerialException:
    print("Serial connection not available. Using stdin for testing.")
    use_serial = False
REGION_DIR = os.path.join(os.path.dirname(__file__),'regions')

region_set = {101,102,103,104,105,106,107,108,109,110,111,112,
           201,202,203,204,205,206,207,208,209,210,211,212,
           301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,
           401,402,403,404,405,406,407,408,409,410,411,412,413,414,
           501,502,503}

# Timer object (initially None)
timeout_timer = None

timeout_duration = 5*60

def play_audio(region_name):
    # Stop any currently playing audio before starting the new one
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    audio_file = os.path.join(REGION_DIR,f"{region_name}.mp3")
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        print(f"Playing audio: {audio_file}")
    except pygame.error as e:
        print(f"Error loading {audio_file}: {e}")
    
        
# Initialize pygame mixer for audio playback
pygame.mixer.init()

cooldown_duration = 1   # seconds
SAMPLE_WINDOW = 0.6     # seconds to collect serial reads before deciding
MIN_SAMPLES = 2         # need at least this many reads in the window

logging.basicConfig(level=logging.DEBUG)

def get_raw_input():
    if use_serial and ser.in_waiting > 0:
        return ser.readline().decode('utf-8').strip()
    elif not use_serial:
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            return sys.stdin.readline().strip()
    return None

def get_input():
    """Collect serial reads over a time window. A real button press sends the
    same value repeatedly (pin held LOW). Noise from floating pins sends
    different values as it cycles through channels. Only accept if all
    reads in the window agree on the same value."""

    first_read = get_raw_input()
    if not first_read or not first_read.isdigit():
        return None

    # Collect reads over the sample window
    reads = [first_read]
    start = time.time()
    while (time.time() - start) < SAMPLE_WINDOW:
        val = get_raw_input()
        if val and val.isdigit():
            reads.append(val)
        time.sleep(0.02)

    # Need enough samples and they must ALL be the same value
    if len(reads) >= MIN_SAMPLES and len(set(reads)) == 1:
        if use_serial:
            ser.reset_input_buffer()
        return first_read

    # Mixed values = noise, reject everything
    if use_serial:
        ser.reset_input_buffer()
    return None

try:
    logging.info("Starting display...")
    epd = epd7in5_V2.EPD()
    
    logging.info("Initialising...")
    epd.init()
    epd.Clear()
    
    def reset_display():
        print("Timeout reached! Resetting display...")
    
        # Stop any ongoing audio
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    
        # Clear display (add actual display reset logic here)
        print("Display reset.")
        epd.init()
        epd.Clear()
        
    def start_timeout():
        global timeout_timer
        # Cancel any existing timer
        if timeout_timer:
            timeout_timer.cancel()
        # Start a new timer
        timeout_timer = threading.Timer(timeout_duration, reset_display)
        timeout_timer.start()

    while True:
        button_index = get_input()
        if button_index:
            print(f'read {button_index}')
            button_index = int(button_index)
            if button_index in region_set:
                region_name = button_index # this is the code for region
                print(f"Button {button_index} pressed: {region_name}")
        
                # Load region info on the display
                epd.init_fast()
                logging.info(f"Loading bmp file for {region_name}...")
                Himage = Image.open(os.path.join(REGION_DIR,f"{region_name}.bmp"))
                epd.display(epd.getbuffer(Himage))
                
                # Play the audio for the region (e.g., region_name.mp3)
                if AUDIO:
                    play_audio(region_name)
                    
                # Restart the timeout timer after a button press
                start_timeout()
                
                print(f"Cooldown for {cooldown_duration} seconds...")
                time.sleep(cooldown_duration)  # Sleep for cooldown period
                
                if use_serial:
                    ser.reset_input_buffer()  # Flush serial buffer after cooldown
                print("Ready for next input.")
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()
