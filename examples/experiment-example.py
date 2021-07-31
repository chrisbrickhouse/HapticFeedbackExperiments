from psychopy import core, visual
from psychopy.sound import Sound
from haptic import Experiment, HapticDevice, Trial


class ExampleExperiment(Experiment):
    """The Experiment class is used as a parent
      class for all individual experiments. This
      allows more automization while allowing
      customization. This is generally done
      through overwriting particular functions
      defined in the Experiment class.

    For example, the member function `makeStims`
      will always be called on initialization
      without the end user needing to remember
      to add that call. Simply creating a member
      function with that name will cause it
      to be run.

    Others are optional callbacks where certain
      member functions will be called at specific
      times. If an end user does not define their
      own `calibrateRumbleDisplay` then nothing
      will be shown but the calibration will still
      fire. Rather than passing a callback function
      class inheretence allows these callbacks to
      be defined in the class.

    In the case where you simply want to extend
      the function of a base class method, you
      can override the function here and call
      `super().functionName(args)` when you
      want the parent event to fire.
    """

    def __init__(self):
        """Create an experiment.

        The `__init__` function is where any
          startup information goes. It is a
          good place to define configuration
          variables like `invert_y_axis`.

        Remember to call the parent `__init__`
        function using `super().__init__(window)`
        or else some functions will not work.
        """
        win = visual.Window([400, 400])  # Create the window
        super().__init__(win)  # Initialize the parent class

        self.invert_y_axis = True  # Set config variable

        self.calibrate()  # Defined in the parent class
        self.run(2000, self.mainLoop)
        # Callback functions used in `run` calls should
        # generally be member functions as this allows
        # them to access the internal attributes and
        # class methods.

    def calibrateRumbleDisplay(self):
        """`Experiment.calibrate` looks for this method
        and will run its contents on every window flip.
        """
        self.stims["calibrateRumbleText"].draw()
        self.stims["buttons"]["south"].draw()
        self.stims["buttons"]["east"].draw()

    def calibrateStickDisplay(self):
        """`Experiment.calibrate` looks for this method
        and will run its contents on every window flip.
        """
        self.stims["calibrateStickText"].draw()
        self.stims["buttons"]["west"].draw()

    def makeStims(self):
        """`Experiment.__init__` looks for this method
        and will run its contents on initialization.
        """
        def makeButtons():
            buttonRet = {}
            buttonImage = {
                "north": "img/48px-PlayStation_button_T.png",
                "south": "img/48px-PlayStation_button_X.png",
                "east": "img/48px-PlayStation_button_C.png",
                "west": "img/48px-PlayStation_button_S.png",
            }
            for k, v in buttonImage.items():
                i = visual.ImageStim(
                    self.window, v, name=k.rstrip(".png").replace("_", " ")
                )
                buttonRet[k] = i
            buttonRet["east"].pos -= (0, 0.6)
            buttonRet["south"].pos -= (0, 0.1)
            buttonRet["west"].pos -= (0, 0.2)
            return buttonRet

        def makeAudio():
            audioRet = {}
            audioFiles = {
                "one": "audio/speaker1.ogg",
                "two": "audio/speaker2.ogg",
                "three": "audio/speaker3.ogg"
            }
            for k, v in audioFiles.items():
                i = Sound(v, name=k)
                audioRet[k] = i
            return audioRet

        cursor = visual.Circle(self.window, fillColor="blue", radius=0.01)

        calibrateRumbleText = visual.TextStim(
            self.window,
            text="When you feel a vibration, please press\n\n\n\nOtherwise press",
        )
        calibrateStickText = visual.TextStim(
            self.window,
            text="Please move the right stick in a circle, then release it and press",
        )
        calibrateStickText.pos += (0, 0.2)
        self.stims = {
            "cursor": cursor,
            "buttons": makeButtons(),
            "audio": makeAudio(),
            "calibrateRumbleText": calibrateRumbleText,
            "calibrateStickText": calibrateStickText,
        }

    def setJoystick(self):
        """`Experiment.__init__` looks for this method
        and will run its contents on initialization.
        """
        self.joystick = HapticDevice()

    def mainLoop(self, frameN, *args, **kwargs):
        """This is a callback used in the `__init__`
        method above.

        See also:
          Experiment.run
        """
        self.stims["cursor"].pos += self.stickPos()
        return [self.stims["cursor"]]


try:
    ExampleExperiment()
except KeyboardInterrupt:
    pass
