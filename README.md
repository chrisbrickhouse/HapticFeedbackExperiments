# Haptic feedback experiments
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

This repository hosts code for running experiments using a gamepad input and haptic feedback using the gamepad's rumble motors. You can find the main framework in `haptic.py`, examples in the `examples` directory, and experiments that I've been running in the `experiments` directory.

The framework interface has [API documentation](http://christianbrickhouse.com/HapticFeedbackExperiments/_build/html/index.html), though be careful since the interface may change rapidly. 

If you need additional functionality or run into problems, let me know or submit a patch so it can be fixed.

## Object-oriented approach
The program is an object-oriented framework for writing experiments. Instead of providing a bunch of functions, `haptic.py` provides classes which have predefined behaviors that control how the experiment executes. To change how the experiment runs, you *extend* the class and change or add functions as needed. For example, the Experiment class already contains loop logic for running trials, so instead of writing your own loop, you write a function that should execute on every loop and add it to the list of functions executed during each loop step. For example:
```{python}
from psychopy import core, visual
from haptic import Experiment

# We create our own class that extends the Experiment class provided by haptic
class NewExperiment( Experiment ):
	# We can modify the init function and run our own code
	def __init__( self ):
		win = visual.Window( [400,400] )
		# Call the parent function to run the default code
		super().__init__( win )

	# If there are default functions that we want to skip, we can overwrite them
	# and not call the parent function. For example, Experiment.__init__ calls
	# Experiment.setJoystick(), but we don't want to run that in this example.
	def setJoystick( self ):
		pass

	# Experiment.run() handles the main loop, and it runs Experiment.on_run_loop() on each iteration
	# so our main experiment logic can be handled by writing our own on_run_loop function like so:
	def on_run_loop( self, iterationNumber ):
		print( f"This is iteration number {iterationNumber}" )
```

The above example demonstrates the concept of ***hooking***: the parent class handles the main timing and execution of the program, but it provides **hooks** that are run at particular times. To run a particular function at a particular time, we simply hang our function onto the proper hook. IF we look at the documentation for `Experiment.run()`, we can see that it provides two hooks. The first is `Experiment.on_run_loop()` which we use in the above example. This hook is run on every loop cycle, so if we want something to run at the start of every loop, we simply create a function using that name. The second is `Experiment.on_run_end()` which is run at the end of every loop. If there are cleanup actions or logging that needs to be done, we can write that function and name it `on_run_end` so that it is called at the right time.

While this style may take some getting-used-to, an object-oriented framework allows for better integration of the various parts of the experiment. A haptic feedback experiment requires managing the display window, the experimental logic, data logging, device registration, calibration, and rumble execution, and these all must be done at the proper time in the proper order. Instead of doing that ourselves, we can set up a standard way of doing these things (a class) so that they are always done in the proper order, and any customization can be done as needed using predefined hooks that execute at known and predictable times. IT allows you to focus on writing the experiment, rather than figuring out how to make all the different parts fit together. After the initial hurdle, it is a far more powerful solution.

If you are still confused about how this library works, you can [look at a full example](https://github.com/chrisbrickhouse/HapticFeedbackExperiments/blob/main/examples/experiment-example.py). You may also benefit from the [python documentation on classes](https://docs.python.org/3/tutorial/classes.html) especially the [section on class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance), and learning about [the bridge pattern](https://en.wikipedia.org/wiki/Bridge_pattern#Python) more generally.
