from cvzone.HandTrackingModule import HandDetector
from PSRGaming import PSR_DS_Player
from image_drawer import ImageDrawer
import cv2
import argparse
import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import threading



def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# ========================== PARSING ARGUMENTS ============================================
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-f', '--filename', type=str, metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-m', '--model', type=str, metavar='MODEL_PATH',
    help='Path to the model')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

try:
    if args.model is None:
        args.model = "model"
    if not os.path.exists(args.model):
        print ("Please download a model for your language from https://alphacephei.com/vosk/models")
        print ("and unpack as 'model' in the current folder.")
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))



# ========================== PARSING ARGUMENTS ============================================

# ========================== GLOBAL VARIABLES ==============================================
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=4)

q = queue.Queue()
model = vosk.Model(args.model)
if args.filename:
    dump_fn = open(args.filename, "wb")
else:
    dump_fn = None

ds_player = PSR_DS_Player()
im_drawer = ImageDrawer(ds_player)

final_text = None
partial_text = None
fingers1 = None
# ========================== GLOBAL VARIABLES ==============================================

# ================================ MAIN ====================================================
with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device, dtype='int16', channels=1, callback=callback):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        rec = vosk.KaldiRecognizer(model, args.samplerate)
        while True:
            # VOICE RECOGNITION
            data = q.get()
            if rec.AcceptWaveform(data):
                final_text_aux = json.loads(rec.Result())
                if final_text_aux['text'] != '':
                    final_text = final_text_aux['text']
                # print(rec.Result())
            else:
                partial_text_aux = json.loads(rec.PartialResult())
                if partial_text_aux['partial'] == '':
                    partial_text = None
                else:
                    partial_text = partial_text_aux['partial']
                # print(rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)

            # HAND RECOGNITION
            # Get image frame
            success, img = cap.read()
            img = cv2.flip(img, 1)
            # Find the hand and its landmarks
            hands, img = detector.findHands(img, flipType=False)  # with draw
            # hands = detector.findHands(img, draw=False)  # without draw

            if hands:
                # Hand 1
                hand1 = hands[0]
                lmList1 = hand1["lmList"]  # List of 21 Landmark points
                bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
                centerPoint1 = hand1['center']  # center of the hand cx,cy
                handType1 = hand1["type"]  # Handtype Left or Right

                fingers1 = detector.fingersUp(hand1)

                # print(fingers1)

            # print(threading.get_ident())
            img = ds_player.manage_inputs(img, partial_text, fingers1)

            # We write text
            if partial_text is None:
                img = im_drawer.writeText(img, final_text, is_final=True)
            else:
                img = im_drawer.writeText(img, partial_text, is_final=False)

            # Display
            cv2.imshow("Image", img)
            cv2.waitKey(1)
        cap.release()
        cv2.destroyAllWindows()
