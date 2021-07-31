from psychopy import core, visual
from psychopy.sound import Sound
from haptic import Experiment, HapticDevice, Trial


class LexDecTrial(Trial):
    def __init__(self, audioObj, num, exp):
        self.stim = audioObj
        super().__init__(audioObj.name, num, exp)
        self.data["timing"] = {}
        self.response_card = self.experiment.response_card
        self.fixation_cross = self.experiment.fixation_cross
        self.left_response = "word"
        self.right_response = "nonword"

    def fire(self, dur=5, delay=1):
        def drawScenes(frameN, *args, **kwargs):
            if frameN >= fps * delay and frameN < fps * dur:
                if self.stim.status == "FINISHED" or self.stim.status == -1:
                    try:
                        assert self.data["timing"]["play_stop"]
                    except KeyError:
                        self.data["timing"]["play_stop"] = frameN
                    return self.response_card
            elif frameN >= fps * dur:
                self.data["timing"]["response"] = frameN
                self.data["data"]["response"] = "NA"
                raise StopIteration()
            return self.fixation_cross

        def playStim(frameN):
            def responseListener(frameN):
                pressed = self.experiment.joystick.getAllButtons()
                if True in pressed:
                    if pressed[3]:
                        self.data["timing"]["response"] = frameN
                        self.data["data"]["response"] = self.left_response
                        raise StopIteration()
                    elif pressed[1]:
                        self.data["timing"]["response"] = frameN
                        self.data["data"]["response"] = self.right_response
                        raise StopIteration()
                return

            if frameN == fps * delay:
                self.data["timing"]["play_start"] = frameN
                self.stim.play()
            else:
                responseListener(frameN)

        fps = 60  # Should probably be tied to experiment monitor
        self.experiment.on_run_loop = playStim
        self.experiment.run(600, drawScenes)
        self.experiment.on_run_loop = lambda: None
        print(self.data)


class LexDecExperiment(Experiment):
    def __init__(self):
        """Create an experiment."""

        def makeTrials():
            trials = []
            audioStims = self.stims["audio"]
            print(audioStims)
            i = 0
            for k, v in audioStims.items():
                t = LexDecTrial(v, i, self)
                trials.append(t)
                i += 1
            self.trials = trials

        win = visual.Window([400, 400])  # Create the window
        super().__init__(win)  # Initialize the parent class

        self.invert_y_axis = True  # Set config variable

        buttons = self.stims["buttons"]
        self.stims["calibrateStickText"].pos += (0, 0.2)
        buttons["east"].pos -= (0, 0.6)
        buttons["south"].pos -= (0, 0.1)
        buttons["west"].pos -= (0, 0.2)
        self.stims["buttons"] = buttons
        self.calibrate()  # Defined in the parent class
        # self.run(2000, self.mainLoop)
        self.makeTrialCard()
        makeTrials()
        self.checkHold()
        for trial in self.trials:
            trial.fire()
            self.data.append(trial.data)
            del trial
        print(self.data)

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

    def runBlock(self):
        for trial in self.trials:
            self.log_data(trial.fire())

    def makeStims(self):
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
            return buttonRet

        def makeAudio():
            audioRet = {}
            audioFiles = {
                "one": "audio/speaker1.ogg",
                "two": "audio/speaker2.ogg",
                "three": "audio/speaker3.ogg",
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

        response_text_word = visual.TextStim(self.window, text="Word")
        response_text_nonword = visual.TextStim(self.window, text="Non-word")
        response_text = [response_text_word, response_text_nonword]

        self.stims = {
            "cursor": cursor,
            "buttons": makeButtons(),
            "audio": makeAudio(),
            "responseText": response_text,
            "calibrateRumbleText": calibrateRumbleText,
            "calibrateStickText": calibrateStickText,
        }

        self.fixation_cross = visual.TextStim(self.window, text="+")

    def makeTrialCard(self, x_offset=0.5, y_offset=0.2):
        responseText = self.stims["responseText"]
        square = self.stims["buttons"]["west"]
        circle = self.stims["buttons"]["east"]
        square.pos = (0, 0)
        circle.pos = (0, 0)
        left_offset = (-1 * x_offset, 0)
        right_offset = (x_offset, 0)
        text_offset = (0, -1 * y_offset)
        img_offset = (0, y_offset)
        square.pos += left_offset
        square.pos += img_offset
        circle.pos += right_offset
        circle.pos += img_offset
        responseText[0].pos += left_offset
        responseText[0].pos += text_offset
        responseText[1].pos += right_offset
        responseText[1].pos += text_offset
        self.response_card = [responseText[0], responseText[1], square, circle]


if __name__ == "__main__":
    exp = LexDecExperiment()
