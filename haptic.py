from evdev import ecodes, ff, InputDevice, util

class HapticDevice():
    """Manage calibration and use of a haptic device.
    
    Attributes:
      device (evdev.InputDevice) the input device in use
      strongMagnitude (hexadecimal) vibration strength for the strong motor
      weakMAgnitude (hexadecimal) vibration strength for the weak motor
    """
    device = None
    strongMagnitude = 0x0000
    weakMagnitude   = 0xfff0

    def __init__( self, dev = None):
        # Use specified device if available
        if dev:
            self.device = dev
            return

        # Find first haptic device if none specified
        for name in util.list_devices():
            dev = InputDevice( name )
            if ecodes.EV_FF in dev.capabilities():
                self.device = dev

    def calibrate( self, sMag = 0x0000, wMag = 0xfff0 ):
        """Interactive calibration of vibration strength

        The vibration strength starts at wMag and ticks
        down by 0x0f00 until the user presses the south button
        on the controller (e.g., x on dualshock). Pressing
        the east button progresses the calibration.
        """
        if sMag <= 0 and wMag <= 0:
            raise ValueError('Rumble cannot be zero')
        self.__setEffect( sMag, wMag )
        self.rumble()
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.code == 304 and event.value == 1:
                    self.strongMagnitude = sMag
                    self.weakMagnitude = wMag
                    break
                elif event.code == 305 and event.value == 1:
                    self.calibrate( sMag, wMag - 0x0f00 )
                    break

    def rumble( self, repeat = 1 ):
        """Cause the device to rumble.

        Keyword arguments:
            repeat (int) How long the device should rumble for, in seconds
        """
        effect_id = self.device.upload_effect( self.effect )
        self.device.write( ecodes.EV_FF, effect_id, repeat )
        self.effect_id = effect_id

    def __setEffect( self, sMag, wMag, duration = 1000 ):
        try:
            self.device.erase_effect( self.effect_id )
        except AttributeError:
            pass

        rumble = ff.Rumble( strong_magnitude = sMag, weak_magnitude = wMag )
        effect = ff.Effect(
                ecodes.FF_RUMBLE, -1, 0,
                ff.Trigger( 0, 0 ),
                ff.Replay( duration, 0 ),
                ff.EffectType( ff_rumble_effect = rumble )
            )
        self.effect = effect

if __name__ == '__main__':
    dev = HapticDevice()
    dev.calibrate()
