import os
import sys
import argparse
import time
import logging
import win32con
import hotkey
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QGuiApplication, QPixmap
from PySide2.QtWidgets import QApplication, QDialog, QGridLayout, QInputDialog, QLabel
from PIL import Image
import pytesseract

DEFAULT_OUTPUT_FILE_NAME_PATTERN = "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png"
APP_NAME = "ScreenSnippingTool"
APP_DESCRIPTION = "Screen Snipping Tool"
APP_VERSION = "1.1.0"

#fast solution for tesseract is not installed or it's not in your path (for Windows). You can 
#set up your path on your system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

def get_screen_image(bounding_box):
    """ Get screen image.

    :param bounding_box: [tuple] The image rectangle in screen, formatted in (left, upper, width, height).
    :returns: [QPixmap or None] Screen image.
    """

    screen = QGuiApplication.primaryScreen()
    if not screen:
        logging.error("Failed to get 'QScreen' object.")
        return None

    if bounding_box:
        return screen.grabWindow(0, x=bounding_box[0], y=bounding_box[1], width=bounding_box[2], height=bounding_box[3])
    else:
        return screen.grabWindow(0)


def save_image(image, file_name_pattern=DEFAULT_OUTPUT_FILE_NAME_PATTERN, override=False):
    """ Save image.

    :param image: [QPixmap] The image to be saved.
    :param file_name_pattern: [string] The file name pattern (absolute path or relative path to this python script file). For example: "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png".
    :param override: [bool] Whether to override the output file if it exists before.
    :returns: [string or None] If the image has been successfully saved, the image file name is returned, else "None" is returned.
    """

    file_name = time.strftime(file_name_pattern, time.localtime())

    if not os.path.isabs(file_name):
        this_file_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = os.path.join(this_file_dir, file_name)

    if (not override) and os.path.exists(file_name):
        logging.error("File already exists: {}".format(file_name))
        return None

    file_dir = os.path.dirname(file_name)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    ok = image.save(file_name)
    if not ok:
        logging.error("Failed to save image to file: {}".format(file_name))
        return None

    return file_name


def snip(bounding_box, file_name_pattern=DEFAULT_OUTPUT_FILE_NAME_PATTERN, override=False, show_time=1000, assign_description=0):
    """ Snip screen image and save it to file.

    :param bounding_box: [tuple] The image rectangle in screen, formatted in (left, upper, width, height).
    :param file_name_pattern: [string] The file name pattern (absolute path or relative path to this python script file). For example: "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png".
    :param override: [bool] Whether to override the output file if it exists before.
    :param show_time: [int] Milliseconds time to show the screen image (if 0, the image won't be shown).
    :param assign_description: [int] Whether to assign description to the screen image (1 for manually input, 2 for OCR, others for no description).
    """

    logging.info("Started snipping screen.")

    screen_image = get_screen_image(bounding_box=bounding_box)
    file_name = save_image(image=screen_image, file_name_pattern=file_name_pattern, override=override)

    if file_name:
        logging.info("Screen image has been saved in file: {}".format(file_name))

        if show_time > 0:
            image_dialog = QDialog()
            image_dialog.setWindowTitle(APP_DESCRIPTION + " " + APP_VERSION)
            image_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
            image_dialog.setFixedSize(640, 360)
            image_dialog.setContentsMargins(0, 0, 0, 0)
            image_label = QLabel()
            image_dialog_layout = QGridLayout(image_dialog)
            image_dialog_layout.setContentsMargins(0, 0, 0, 0)
            image_dialog_layout.addWidget(image_label)
            image_label.setPixmap(screen_image)
            image_label.setScaledContents(True)
            QTimer().singleShot(10, image_dialog.activateWindow)
            QTimer().singleShot(show_time, image_dialog.close)
            image_dialog.exec()

            if assign_description == 1:
                description_input_dialog = QInputDialog()
                description_input_dialog.setWindowTitle(APP_DESCRIPTION + " " + APP_VERSION)
                description_input_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
                description_input_dialog.setFixedSize(400, 200)
                description_input_dialog.setInputMode(description_input_dialog.TextInput)
                description_input_dialog.setLabelText("Please input description:")
                QTimer().singleShot(10, description_input_dialog.activateWindow)
                description_input_dialog.exec()
                description = description_input_dialog.textValue()
                if description:
                    description_file_name = file_name + ".txt"
                    with open(description_file_name, "w") as file:
                        file.write(description)
                    logging.info("Assigned a description for screen image file: {}".format(file_name))
                    logging.debug("Description: {}".format(description))
            elif assign_description == 2:
                textFromImage = pytesseract.image_to_string(Image.open(file_name))
                description_file_name = file_name + "-OCR.txt"
                with open(description_file_name, "w") as file:
                    file.write(textFromImage)
                os.startfile(description_file_name)
            else:
                pass
    else:
        logging.error("Error occurred.")


def main():
    app = QApplication(sys.argv)

    arg_parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)
    arg_parser.add_argument("-v", "--version", action="version", version="%(prog)s {}".format(APP_VERSION))
    arg_parser.add_argument("-o", "--output", help="The output file name pattern (default: '%(default)s').", default=DEFAULT_OUTPUT_FILE_NAME_PATTERN)
    arg_parser.add_argument("-r", "--override", action="store_true", help="Whether to override the output file if it exists before.")
    arg_parser.add_argument("-l", "--log-file", help="The log file name (default: log not saved).", default="")
    arg_parser.add_argument("-s", "--show-time", type=int, help="Milliseconds time to show the screen image (if 0, the image won't be shown) (default: '%(default)s').", default=1000)
    arg_parser.add_argument("-d", "--assign-description", type=int, help="Whether to assign description to the screen image (1 for manually input, 2 for OCR [NOT IMPLEMENTED], others for no description) (default: '%(default)s').", default=0)
    arg_parser.add_argument("-b", "--bounding_box", nargs='*', type=int, help = "[tuple] The image rectangle in screen, enter dimensions by entering numbers e.g -b 150 200 300 400")
    args = arg_parser.parse_args()

    logging.basicConfig(filename=args.log_file, filemode="a", format="[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s", level=logging.DEBUG)
    logging.info(APP_DESCRIPTION + " started.")

    def snip_():
        if args.bounding_box:
            bounding_box = tuple(args.bounding_box)
        else:
            bounding_box = None
        snip(bounding_box, file_name_pattern=args.output, override=args.override, show_time=args.show_time, assign_description=args.assign_description)

    hotkey_ = hotkey.Hotkey()
    hotkey_.register(101, win32con.MOD_ALT, win32con.VK_SNAPSHOT, snip_)

    while True:
        try:
            app.processEvents()
            time.sleep(0.1)
        except Exception as e:
            logging.debug("Exception occurred: {}".format(e))

if __name__ == "__main__":
    main()
