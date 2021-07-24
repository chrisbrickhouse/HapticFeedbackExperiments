from psychopy import core, visual
from haptic import Experiment, HapticDevice


class ExampleExperiment(Experiment):
    def __init__(self):
        win = visual.Window([400, 400])
        super().__init__(win)

        self.invert_y_axis = True

        self.calibrate()
        self.run(2000, self.moveLoop)

    def calibrateRumbleDisplay(self):
        self.stims["calibrateRumbleText"].draw()
        self.stims["buttons"]["south"].draw()
        self.stims["buttons"]["east"].draw()

    def calibrateStickDisplay(self):
        self.stims["calibrateStickText"].draw()
        self.stims["buttons"]["west"].draw()

    def makeStims(self):
        cursor = visual.Circle(self.window, fillColor="blue", radius=0.01)
        buttonImage = {
            "north": "img/48px-PlayStation_button_T.png",
            "south": "img/48px-PlayStation_button_X.png",
            "east": "img/48px-PlayStation_button_C.png",
            "west": "img/48px-PlayStation_button_S.png",
        }
        buttonRet = {}
        for k, v in buttonImage.items():
            i = visual.ImageStim(
                self.window, v, name=k.rstrip(".png").replace("_", " ")
            )
            buttonRet[k] = i
        calibrateRumbleText = visual.TextStim(
            self.window,
            text="When you feel a vibration, please press\n\n\n\nOtherwise press",
        )
        calibrateStickText = visual.TextStim(
            self.window,
            text="Please move the right stick in a circle, then release it and press",
        )
        calibrateStickText.pos += (0, 0.2)
        buttonRet["east"].pos -= (0, 0.6)
        buttonRet["south"].pos -= (0, 0.1)
        buttonRet["west"].pos -= (0, 0.2)
        self.stims = {
            "cursor": cursor,
            "buttons": buttonRet,
            "calibrateRumbleText": calibrateRumbleText,
            "calibrateStickText": calibrateStickText,
        }

    def setJoystick(self):
        self.joystick = HapticDevice()

    def moveLoop(self, frameN, *args, **kwargs):
        self.stims["cursor"].pos += self.stickPos()
        return [self.stims["cursor"]]


try:
    ExampleExperiment()
except KeyboardInterrupt:
    pass
