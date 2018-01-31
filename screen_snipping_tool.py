import os
import sys
import argparse
import time
import PyQt5.Qt
import logging
import ctypes
import ctypes.wintypes
import win32con


DEFAULT_OUTPUT_FILE_NAME_PATTERN = "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png"
APP_NAME = "ScreenSnippingTool"
APP_DESCRIPTION = "Screen Snipping Tool"
APP_VERSION = "1.0.0"


def get_screen_image(bounding_box=None):
    """Get screen image.

    :param bounding_box: [tuple] The image rectangle in screen, formatted in (left, upper, width, height).
    :rtype: PyQt5.Qt.QPixmap or None
    :returns: Screen image.
    """

    screen = PyQt5.Qt.QGuiApplication.primaryScreen()
    if not screen:
        logging.error("Failed to get 'QScreen' object.")
        return None

    if bounding_box:
        return screen.grabWindow(0, x=bounding_box[0], y=bounding_box[1], width=bounding_box[2], height=bounding_box[3])
    else:
        return screen.grabWindow(0)


def save_image(image, file_name_pattern=DEFAULT_OUTPUT_FILE_NAME_PATTERN, override=False):
    """Save image.

    :param image: [PyQt5.Qt.QPixmap] The image to be saved.
    :param file_name_pattern: [string] The file name pattern (absolute path or relative path to this python script file). For example: "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png".
    :param override: [bool] Whether to override the output file if it exists before.
    :rtype: string or None
    :returns: If the image has been successfully saved, the image file name is returned, else "None" is returned.
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


def snip(bounding_box=None, file_name_pattern=DEFAULT_OUTPUT_FILE_NAME_PATTERN, override=False, show_time=1000):
    """Snip screen image and save it to file.

    :param bounding_box: [tuple] The image rectangle in screen, formatted in (left, upper, width, height).
    :param file_name_pattern: [string] The file name pattern (absolute path or relative path to this python script file). For example: "ScreenSnippingImages/ScreenSnippingImage_%Y-%m-%d_%H-%M-%S.png".
    :param override: [bool] Whether to override the output file if it exists before.
    :param show_time: [int] Milliseconds time to show the screen image (if 0, the image won't be shown).
    :rtype: None
    """

    logging.info("Started snipping screen.")

    screen_image = get_screen_image(bounding_box)
    file_name = save_image(screen_image, file_name_pattern, override)

    if file_name:
        logging.info("Screen image has been saved in file: {}".format(file_name))

        if show_time > 0:
            image_window = PyQt5.Qt.QLabel()
            image_window.setWindowTitle(APP_DESCRIPTION + " " + APP_VERSION)
            image_window.setWindowFlags(PyQt5.Qt.Qt.WindowStaysOnTopHint)
            image_window.setFixedSize(640, 360)
            image_window.setPixmap(screen_image)
            image_window.setScaledContents(True)
            image_window_close_timer = PyQt5.Qt.QTimer()
            image_window_close_timer.singleShot(show_time, image_window.close)
            image_window.show()
            image_window.activateWindow()
            process_events_timer = PyQt5.Qt.QTimer()
            process_events_timer.start(show_time)
            while process_events_timer.remainingTime() > 0:
                PyQt5.Qt.QApplication.processEvents()
    else:
        logging.error("Error occurred.")


def main():
    app = PyQt5.Qt.QApplication(sys.argv)

    arg_parser = argparse.ArgumentParser(prog=APP_NAME, description=APP_DESCRIPTION)
    arg_parser.add_argument("-v", "--version", action="version", version="%(prog)s {}".format(APP_VERSION))
    arg_parser.add_argument("-o", "--output", help="The output file name pattern (default: '%(default)s').", default=DEFAULT_OUTPUT_FILE_NAME_PATTERN)
    arg_parser.add_argument("-r", "--override", action="store_true", help="Whether to override the output file if it exists before.")
    arg_parser.add_argument("-l", "--log-file", help="The log file name (default: log not saved).", default="")
    arg_parser.add_argument("-s", "--show-time", type=int, help="Milliseconds time to show the screen image (if 0, the image won't be shown) (default: '%(default)s').", default=1000)
    args = arg_parser.parse_args()

    logging.basicConfig(filename=args.log_file, filemode="a", format="[%(asctime)s] [%(levelname)s] [%(module)s.%(funcName)s] %(message)s", level=logging.DEBUG)
    logging.info(APP_DESCRIPTION + " started.")

    snip_hot_key_id = 101
    try:
        ok = ctypes.windll.user32.RegisterHotKey(None, snip_hot_key_id, 1, win32con.VK_SNAPSHOT)
        if not ok:
            logging.error("Failed to register hot key for snipping.")
            return

        msg = ctypes.wintypes.MSG()
        while True:
            if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0):
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == snip_hot_key_id:
                        snip(None, args.output, args.override, args.show_time)

                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))

            app.processEvents()
            time.sleep(0.1)
    finally:
        ctypes.windll.user32.UnregisterHotKey(None, snip_hot_key_id)


if __name__ == "__main__":
    main()
