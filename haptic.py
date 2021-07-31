from evdev import ecodes, ff, InputDevice, util
from numpy import subtract
from psychopy.hardware import joystick
from psychopy.sound import Sound
from psychopy import core, visual


class HapticDevice(joystick.Joystick, InputDevice):
    """Manage calibration and use of a haptic device.

    Attributes:
      name (string): System-provided name for the device.
      id (int): Index of device in pyglet's list.
      effect (evdev.ff.Effect): Main evdev force effect.
      effect_id (int?): The ID of the effect uploaded to the device.
      offset (tuple): How much to offset inputs from the joysticks.
      strongMagnitude (int): Vibration strength for the strong motor
      weakMagnitude (int): Vibration strength for the weak motor
    """

    strongMagnitude = 0x0000
    weakMagnitude = 0xFFF0

    def __init__(self, id_=0, dev=None):
        """Creates a HapticDevice derived from evdev and psychopy

        Keyword arguments:
          id_ (int): ID of device in pyglet's list.
          dev (string): Path to the /dev device.

        Raises:
          ValueError: If the device specified by `dev` cannot
            be found, an error is thrown.
        """
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

    def calibrateRumble(
        self,
        sMag,
        wMag,
    ):
        """Interactive calibration of vibration strength

        The vibration strength starts at wMag and ticks
        down by 0x0f00 until the user presses the south button
        on the controller (e.g., x on dualshock). Pressing
        the east button progresses the calibration.

        Arguments:
          sMag (int): Strength of strong motor vibration.
          wMag (int): Strength of weak motor vibration.
          display (function): A callback function to handle
            display of instructional text. Gets passed the
            Experiment instance. Only called once.
          displayArgs (list): Arguments to be passed to `display`.

        Raises:
          ValueError: Both motors may not be set to zero.
        """
        if sMag <= 0 and wMag <= 0:
            raise ValueError("Rumble cannot be zero")
        self.__setEffect(sMag, wMag)
        self.rumble()

    def calibrateStick(self, win, display=None, displayArgs=[]):
        """Calibrate the stick's resting position.

        Currently, the procedure is to move the right stick around, release,
          and press the West button (square on PS, X on MS). Future
          implementations may support other sticks or specified buttons

        Arguments:
          win (psychopy.visual.Window): The window being used by the experiment.
            This is needed because the joystick's input is only updated on
            screen flip.
        """

        while True:
            stickPos = tuple(joystick.Joystick.getAllAxes(self))
            try:
                display(*displayArgs)
            except TypeError:
                pass
            if self.getAllButtons()[3] == True:
                # print(stickPos)
                self.offset = stickPos
                break
            win.flip()

    def getAllAxes(self):
        """Get input from all sticks, minus offset if possible"""
        try:
            return subtract(joystick.Joystick.getAllAxes(self), self.offset)
        except:
            return joystick.Joystick.getAllAxes(self)

    def getHat(self, n):
        "Get the d-pad input. Not currently used"
        return self.getAllHats()[n]

    def rumble(self, repeat=1):
        """Cause the device to rumble.

        Keyword arguments:
            repeat (int): How long the device should rumble for, in seconds
        """
        try:
            self.write(ecodes.EV_FF, self.effect_id, repeat)
        except AttributeError:
            self.effect_id = self.upload_effect(self.effect)
            self.rumble()

    def setMagnitudes(self, sMag, wMag):
        self.strongMagnitude = sMag
        self.weakMagnitude = wMag

    def setOffset(self, offset):
        self.offset = offset

    def __setEffect(self, sMag, wMag, duration=100):
        try:
            print(self.effect_id)
            self.erase_effect(self.effect_id)
            del self.effect_id
        except AttributeError:
            pass

        rumble = ff.Rumble(strong_magnitude=sMag, weak_magnitude=wMag)
        self.effect = ff.Effect(
            ecodes.FF_RUMBLE,
            -1,
            0,
            ff.Trigger(0, 0),
            ff.Replay(duration, 0),
            ff.EffectType(ff_rumble_effect=rumble),
        )


class Experiment:
    """Experiment objects control the flow of an experiment and
    serve as an abstraction layer above the hardware and
    graphics managment layers. It is set up to primarily use
    callback methods allowing external definition of processes
    without requiring (but still allowing) management of the
    execution chain.

    The best way to use this is by extending the class, creating
    a child experiment and overwriting methods where needed.

    Attributes:
      window (psychopy.visual.window): The psychopy window in
        use for this experiment.
      joystick (HapticDevice): The joystick in use.
      stims: Will be set to the output of the `makeStims`
        callback. See `makeStims`.
      invert_y_axis (bool): Whether the stick position's y-axis
        should be inverted by default.
    """

    def __init__(self, w, **kwargs):
        """Create an Experiment object

        Arguments:
          w (psychopy.visual.Window): the psychopy window to use
            for this experiment

        Keyword arguments:
          joystick (HapticDevice, optional): The joystick to
            send haptic events to.
          stims (function): A callback function used to make the
            stimuli on initialization. The function will be passed
            the `window` attribute as the first argument and then
            the arguments in `stimargs` and `stimkwargs`.
          stimargs (list): Arguments to pass to the `stims` callback.
          stimkwargs (dictionary): Keyword arguments to pass to the
            `stims` callback.
        """
        self.data = Data()
        self.window = w
        self.makeStims()
        self.setJoystick()
        try:
            self.invert_y_axis = kwargs["invertaxis"]
        except KeyError:
            self.invert_y_axis = False

    def makeStims(self):
        """Overwrite with own function."""
        pass

    def setJoystick(self):
        """Creates default joystick, can overwrite with own function."""
        self.joystick = HapticDevice()

    def calibrate(self, *args, **kwargs):
        """Runs the joystick calibration methods.

        Warning:
          This should be considered highly unstable.
            Its operation will be changed to accomodate changes in
            the `haptic.HapticDevice` calibration scheme providing
            a relatively seamless integration of calibration
            into main experiment files.

        Keyword arguments:
          sMag (int): Strong motor magnitude.
          wMag (int): Weak motor magnitude.
          step (int): How much to step up the magnitude.
        """

        def calibrateRumble(sMag, wMag):
            """Interactive calibration of vibration strength

            The vibration strength starts at wMag and ticks
            up by 0x0f00 until the user presses the south button
            on the controller (e.g., x on dualshock). Pressing
            the east button progresses the calibration.

            Raises:
              ValueError: Both motors may not be set to zero.
            """
            if sMag <= 0 and wMag <= 0:
                raise ValueError("Rumble cannot be zero")

            self.joystick.calibrateRumble(sMag, wMag)
            print(wMag)
            while True:
                self.calibrateRumbleDisplay()
                buttons = self.joystick.getAllButtons()
                if buttons[0]:
                    self.joystick.setMagnitudes(sMag, wMag)
                    return
                elif buttons[1]:
                    while True:
                        if not self.joystick.getAllButtons()[1]:
                            self.run(50, self.calibrateRumbleDisplay)
                            break
                        self.run(1, self.calibrateRumbleDisplay)
                    calibrateRumble(sMag, wMag + 0x0F00)
                self.window.flip()

        def calibrateStick():
            """Calibrate the stick's resting position.

            Currently, the procedure is to move the right stick around, release,
              and press the West button (square on PS, X on MS). Future
              implementations may support other sticks or specified buttons
            """

            while True:
                self.calibrateStickDisplay()
                stickPos = tuple(self.joystick.getAllAxes())
                buttons = self.joystick.getAllButtons()
                if buttons[3]:
                    self.joystick.setOffset(stickPos)
                    return
                self.window.flip()

        try:
            sMag = kwargs["sMag"]
        except KeyError:
            sMag = 0x0000
        try:
            wMag = kwargs["wMag"]
        except KeyError:
            wMag = 0x0F00
        try:
            step = kwargs["step"]
        except KeyError:
            step = 0x0400

        calibrateRumble(sMag, wMag)
        calibrateStick()

    def checkHold(self):
        while True:
            if True not in self.joystick.getAllButtons():
                break
            self.window.flip()

    def on_run_end(self):
        """Callback for end of a run loop. Replace with own method."""
        pass

    def on_run_loop(self, frame):
        """Callback at start of every run loop."""
        pass

    def run(self, n=1, func=None, funcargs=[], funckwargs={}):
        """Run the provided function in a loop.

        This method abstracts running `visual.window.flip` loops and
            the experiment. T
          drawing objects to the screen. Th provided function is run
          on each loop and is provided the `window` object and the
          frame number (starting from 0). These can be used to do
          more fine-grained editing within the callback.

        The callback function should return a list of objects to
          draw in the order they should be drawn.

        Warning:
          The callback function should not flip the window.
            Doing so will introduce errors into your experiment timing.

        Keyword arguments:
          n (int): The number of frames to run. On a monitor with a
            60Hz refresh rate, each frame corresponds to roughly 17ms.
            Defaults to 1.
          func (function): A callback function to run on each loop
            pass. The first argument to this callback will be the
            the frame number. This function should return a list of
            objects to draw.
          funcargs (list): Positional arguments for func.
          funckwargs (dictionary): Keyword arguments for func.
        """
        for frameN in range(n):
            try:
                self.on_run_loop(frameN)
            except StopIteration:
                self.checkHold()
                break
            try:
                draw = func(frameN, *funcargs, **funckwargs)
                for obj in draw:
                    obj.draw()
            except TypeError as e:
                pass
            except StopIteration:
                break
            self.window.flip()
        self.on_run_end()

    def stickPos(self, start=-3, stop=-1, tolerance=0.1, scale=0.25):
        """Provide the stick position, inverting y-axis if needed."""
        pos = self.joystick.getAllAxes()[start:stop]
        if self.invert_y_axis:
            pos[1] *= -1
        pos = [x * scale if abs(x) > tolerance else 0.0 for x in pos]
        return tuple(pos)


class Trial:
    def __init__(self, name, num, experiment):
        self.name = name
        self.number = num
        self.experiment = experiment
        self.data = {"trial_name": name, "trial_number": num, "data": {}}


class Data:
    """Custom data object. This data structure
    functions as an associative array, essentially
    acting like both a list and a dictionary.

    It can be sliced like a list, have values
    denoted by keys like a dictionary, but unlike
    dictionaries these keys are *ordered* and can
    be refered to either by name or position.

    Attribute:
        data (list): A list of tuples to implement associative array
    """

    def __init__(self):
        self.data = []

    def __getitem__(self, index):
        """
        Implements the retrieval of items given both
        keys and list syntax. If the object is called
        as a slice, ``data_object[1:4]``, the values
        of each element will be returned as a list.

        If the object is called with a string, then
        it behaves like a dictionary and returns the
        value associated with that key.

        If the object is called with an int, then it
        behaves like a list and returns the value at
        that index regardless of the key.
        """
        if isinstance(index, slice):
            ret = []
            for i in range(*index.indices(len(self.data))):
                ret.append(self.data[i][1])
            return ret
        elif isinstance(index, int):
            return self.data[index][1]
        elif isinstance(index, str):
            # This should raise a KeyError if nothing is found
            return [x[1] for x in self.data if x[0] == index][0]
        else:
            raise ValueError()

    def __setitem__(self, index, value):
        """Implements the setting of key value pairs."""
        match = [x for x in self.data if x[0] == index]
        if len(match) == 0:
            self.data.append((index, value))
        else:
            i = self.data.index(match[0])
            self.data[i] = (index, value)

    def append(self, value):
        """Implements an append method. The key will always be
        the position in the list, specifically, the length of
        the list at the time.
        """
        i = len(self.data)
        self.data.append((i, value))

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def __dict__(self):
        return dict(self.data)

    def __iter__(self):
        yield from self.data

    def items(self):
        return self.data

    def keys(self):
        return [x[0] for x in self.data]


if __name__ == "__main__":
    dev = HapticDevice()
    dev.calibrate()
