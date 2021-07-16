from evdev import ecodes, ff, InputDevice, util

class HapticDevice():
    def __init__(self, dev=None):
        if dev:
            self.dev = dev
            return
        # Find first haptic device if none specified
        for name in util.list_devices():
            dev = InputDevice(name)
            if ecodes.EV_FF in dev.capabilities:
                self.dev = dev

    def calibrate(self):
        raise NotImplementedError()

    def rumble(self):
        raise NotImplementedError()
