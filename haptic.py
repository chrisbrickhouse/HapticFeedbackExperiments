from evdev import ecodes, ff, InputDevice, util
from psychopy.hardware import joystick

class HapticDevice( joystick.Joystick, InputDevice ):
    """Manage calibration and use of a haptic device.
    
    Attributes:
      _device (evdev.InputDevice) the input device in use
      strongMagnitude (hexadecimal) vibration strength for the strong motor
      weakMAgnitude (hexadecimal) vibration strength for the weak motor
    """
    _device = None
    _filename = '/dev/null'
    strongMagnitude = 0x0000
    weakMagnitude   = 0xfff0

    def __init__( self, id_ = 0, dev = None ):
        # Initiate joystick.Joystick
        joystick.Joystick.__init__( self, id_ )

        if dev:
            # Close the parent device and replace
            #  it with the specified device
            self._device.close() # From joystick.Joystick
            devices = joystick.pyglet_input.get_inputs() # Assumes we're using pyglet
            devMatch = [ d for d in devices if d.device._filename == dev ]
            if len(devMatch) > 1:
                raise ValueError( f'Multiple devices found for {dev}' )
            elif len(devMatch) == 0:
                raise ValueError( f'No device found at {dev}' )
            self.id = devices.index(devMatch[0])
            self._device = devMatch[0]
            self.name = self._device.device.name
        
        self._filename = self._device.device._filename
        InputDevice.__init__(self, self._filename)

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
        for event in self.read_loop():
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
        effect_id = self.upload_effect( self.effect )
        self.write( ecodes.EV_FF, effect_id, repeat )
        self.effect_id = effect_id

    def __setEffect( self, sMag, wMag, duration = 1000 ):
        try:
            self.erase_effect( self.effect_id )
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
