import ctypes
import ctypes.wintypes
import win32con
import logging
from PySide2.QtCore import Qt, QTimer


class Hotkey(object):
    """ Class for register hot key. """

    def __init__(self):
        object.__init__(self)

        self.hotkey_dict = {}

    def __del__(self):
        self.unregister_all()

    def register(self, hotkey_id, modifiers, key_code, callback):
        """ Register hot key.

        :param hotkey_id: [int] The unique id of the hot key.
        :param modifiers: [int] The modifiers of the hot key. (win32con.MOD_ALT | win32con.MOD_CONTROL | win32con.MOD_SHIFT | win32con.MOD_WIN)
        :param key_code: [int] The code of the hot key. (win32con.VK_*)
        :param callback: [function] The function called when the hot key is pressed.
        :return: [bool] Whether the hot key is successfully registered.
        """

        if hotkey_id in self.hotkey_dict.keys():
            self.unregister(hotkey_id)

        ok = ctypes.windll.user32.RegisterHotKey(None, hotkey_id, modifiers, key_code)
        if not ok:
            logging.error("Failed to register hot key: hotkey_id={hotkey_id}, modifiers={modifiers}, key_code={key_code}.".format(hotkey_id=hotkey_id, modifiers=modifiers, key_code=key_code))
            return False

        def check_message():
            msg = ctypes.wintypes.MSG()
            if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0):
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == hotkey_id:
                        callback()

                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))

        timer = QTimer()
        timer.setInterval(100)
        timer.timeout.connect(check_message, type=Qt.QueuedConnection)
        timer.start()
        self.hotkey_dict[hotkey_id] = {"modifiers": modifiers, "key_code": key_code, "callback": callback, "timer": timer}
        logging.debug("Registered hot key: hotkey_id={hotkey_id}, modifiers={modifiers}, key_code={key_code}.".format(hotkey_id=hotkey_id, modifiers=modifiers, key_code=key_code))

        return True

    def unregister(self, hotkey_id):
        """ Unregister hot key.

        :param hotkey_id: [int] The unique id of the hot key.
        :return: [bool] Whether the hot key is successfully unregistered.
        """

        if hotkey_id not in self.hotkey_dict.keys():
            logging.error("Failed to unregister hot key: hotkey_id={hotkey_id}, because it is not in the hot key dictionary.".format(hotkey_id=hotkey_id))
            return False

        hotkey = self.hotkey_dict[hotkey_id]
        modifiers = hotkey["modifiers"]
        key_code = hotkey["key_code"]
        timer = hotkey["timer"]

        timer.cancel()

        ok = ctypes.windll.user32.UnregisterHotKey(None, hotkey_id)
        if not ok:
            logging.error("Failed to unregister hot key: hotkey_id={hotkey_id}, modifiers={modifiers}, key_code={key_code}.".format(hotkey_id=hotkey_id, modifiers=modifiers, key_code=key_code))
            return False

        self.hotkey_dict.pop(hotkey_id)
        logging.debug("Unregistered hot key: hotkey_id={hotkey_id}, modifiers={modifiers}, key_code={key_code}.".format(hotkey_id=hotkey_id, modifiers=modifiers, key_code=key_code))

        return True

    def unregister_all(self):
        """ Unregister all of the hot keys registered by this 'Hotkey' instance.

        :return: [bool] Whether all of the hot keys is successfully unregistered.
        """

        ok = True
        for hotkey_id in self.hotkey_dict.keys():
            ok_ = self.unregister(hotkey_id)
            ok = ok and ok_

        return ok
