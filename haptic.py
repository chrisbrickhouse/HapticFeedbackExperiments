from evdev import ecodes, ff, InputDevice, util
from psychopy.hardware import joystick


class HapticDevice(joystick.Joystick, InputDevice):
    """Manage calibration and use of a haptic device.

    Attributes:
      _device (evdev.InputDevice) the input device in use
      strongMagnitude (hexadecimal) vibration strength for the strong motor
      weakMAgnitude (hexadecimal) vibration strength for the weak motor
    """

    strongMagnitude = 0x0000
    weakMagnitude = 0xFFF0

    def __init__(self, id_=0, dev=None):
        # Initiate joystick.Joystick
        joystick.Joystick.__init__(self, id_)

        if dev:
            # Close the parent device and replace
            #  it with the specified device
            self._device.close()  # From joystick.Joystick
            devices = joystick.pyglet_input.get_inputs()  # Assumes we're using pyglet
            devMatch = [d for d in devices if d.device._filename == dev]
            if len(devMatch) > 1:
                raise ValueError(f"Multiple devices found for {dev}")
            elif len(devMatch) == 0:
                raise ValueError(f"No device found at {dev}")
            self.id = devices.index(devMatch[0])
            self._device = devMatch[0]
            self._device.open()
            self.name = self._device.device.name

        self._filename = self._device.device._filename
        InputDevice.__init__(self, self._filename)

    def calibrateRumble(self, sMag=0x0000, wMag=0xFFF0):
        """Interactive calibration of vibration strength

        The vibration strength starts at wMag and ticks
        down by 0x0f00 until the user presses the south button
        on the controller (e.g., x on dualshock). Pressing
        the east button progresses the calibration.
        """
        if sMag <= 0 and wMag <= 0:
            raise ValueError("Rumble cannot be zero")
        self.__setEffect(sMag, wMag)
        self.rumble()
        for event in self.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.code == 304 and event.value == 1:
                    self.strongMagnitude = sMag
                    self.weakMagnitude = wMag
                    break
                elif event.code == 305 and event.value == 1:
                    self.calibrate(sMag, wMag - 0x0F00)
                    break

    def calibrateStick(self, win):
        """Move stick, release, then press West"""

        while True:
            stickPos = tuple(joystick.Joystick.getAllAxes(self))
            if self.getAllButtons()[3] == True:
                print(stickPos)
                self.offset = stickPos
                break
            win.flip()

    def getAllAxes(self):
        try:
            return subtract(joystick.Joystick.getAllAxes(self), self.offset)
        except:
            return joystick.Joystick.getAllAxes(self)

    def getHat(self, n):
        return self.getAllHats()[n]

    def rumble(self, repeat=1):
        """Cause the device to rumble.

        Keyword arguments:
            repeat (int) How long the device should rumble for, in seconds
        """
        try:
            self.write(ecodes.EV_FF, self.effect_id, repeat)
        except AttributeError:
            effect_id = self.upload_effect(self.effect)
            self.effect_id = effect_id
            self.rumble()

    def __setEffect(self, sMag, wMag, duration=100):
        try:
            self.erase_effect(self.effect_id)
        except AttributeError:
            pass

        rumble = ff.Rumble(strong_magnitude=sMag, weak_magnitude=wMag)
        effect = ff.Effect(
            ecodes.FF_RUMBLE,
            -1,
            0,
            ff.Trigger(0, 0),
            ff.Replay(duration, 0),
            ff.EffectType(ff_rumble_effect=rumble),
        )
        self.effect = effect


if __name__ == "__main__":
    dev = HapticDevice()
    dev.calibrate()
