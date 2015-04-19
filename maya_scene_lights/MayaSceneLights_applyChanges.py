__author__ = 'Carlos Montes'

''' Modifies intensity, color and/or shadow color of selected lights by a certain amount. '''

import pymel.core as pmc

def change_intensity(quantity, operator, lights, keyframe):

    """
    Changes the intensity of passed array of Maya Light Transform nodes; may set animation keyframe.
    :param quantity: Amount of intensity to change
    :param operator: Modifying operator value. 0 = fixed quantity, 1 = addition, 2 = multiplication, 3 = add percentage
    :param lights: Array of Light nodeTypes
    :param keyframe: Boolean to define whether to set a keyframe or not
    :return: None
    """

    if not lights:
        pmc.warning('Please select one or more lights in the Light Interface window\'s list')
        return

    # Closure that returns a calculated value according to the selected operator
    def calculate_value(current_value):
        """
        :param current_value: Current intensity value of a specific light
        :return: Lambda operation according to the operator value selected
        """
        fixed = lambda x: quantity
        add = lambda x: x + quantity
        mult = lambda x: x * quantity
        percentage = lambda x: x + (x * quantity / 100.0)

        # Choose an operation based on the passed operator
        operation = {
            0: fixed,
            1: add,
            2: mult,
            3: percentage
        }[operator]

        return operation(current_value)

    # Retrieves current frame the user is on
    currentFrame = pmc.currentTime(query=True)

    for light in lights:

        # Get Intensity attribute of this specific light
        new_value = calculate_value(pmc.getAttr('%s.intensity' % light))

        if keyframe is True:
            # cutKey deletes animation found in a certain frame
            pmc.cutKey(light, time=(currentFrame, currentFrame), attribute="intensity")

            # Set a keyframe in the current light
            pmc.setKeyframe(light, time=currentFrame, attribute="intensity", value=new_value)

        # Set Intensity value
        pmc.setAttr('%s.intensity' % light, new_value)

def change_color(color_value, lights, keyframe, color_or_shadow):

    """
    Changes the light color or shadow color of a passed array of lights; may set animation keyframe.
    :param color_value: Array of integers that defines the RGB values to assign to the selected lights' color
    :param lights: Array of Light nodeTypes
    :param keyframe: Boolean to define whether to set a keyframe or not
    :param color_or_shadow: Integer that tells whether to set a color or a shadow color (1 = color, 2 = shadow)
    :return: None
    """

    if not lights:
        pmc.warning('Please select one or more lights in the Light Interface window\'s list')
        return

    # Attribute name of light and its corresponding prefix for RGB attributes (used in keyframe animation)
    attr = {
        1: ['color', 'color'],
        2: ['shadowColor', 'shadColor']
    }[color_or_shadow]

    # Retrieves current frame the user is on
    currentFrame = pmc.currentTime(query=True)
    rgb_array = ('R', 'G', 'B')

    # Closure that cuts and sets keyframes in their respective RGB attributes
    def set_rgb_keyframes(prefix):
        """
        Sets the R, G, B channels of the chosen color modification on an specific light
        :param prefix: 'color' to set a Light Color, 'shadColor' to set a Shadow Color
        :return: None
        """
        i = 0

        for color in rgb_array:
            # cutKey deletes animation found in a certain frame
            pmc.cutKey(light, time=(currentFrame, currentFrame), attribute=prefix+color)

            # Set a keyframe in the current light
            pmc.setKeyframe(light, time=currentFrame, attribute=prefix+color, value=color_value[i])

            i += 1

    for light in lights:

        if keyframe is True:
            set_rgb_keyframes(attr[1])

        # Set color or shadow value
        pmc.setAttr('%s.%s' % (light, attr[0]), color_value)