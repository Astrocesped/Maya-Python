To use this interface, move this 'maya_scene_lights' folder to one of the 'Scripts' directories that your Maya installation reads.

Once there, you can call the window in the Script Editor with the following lines:

import maya_scene_lights.MayaSceneLights_mayaWindow as light_interface_window
reload(light_interface_window)
light_interface_window.show()

This interface makes use of Pymel and PySide, which is installed with Autodesk Maya by default, as of 2015.