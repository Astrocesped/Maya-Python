__author__ = 'Carlos Montes'

"""
Connects the QtGui window in windowTemplate.py to the Maya Environment.
"""

import MayaSceneLights_pysideWindow as pysideWindow
import MayaSceneLights_applyChanges as applyChanges
import mayautils

from PySide import QtCore, QtGui
import pymel.core as pmc
import maya.OpenMaya as OpenMaya

def show():
    """
    Shows the interface window inside Maya, connects callback functions
    to some of its elements
    :return: None
    """

    if pmc.window('lightInterfaceUI', exists=True):
        pmc.deleteUI('lightInterfaceUI', wnd=True)
        
    # === WINDOW INSTANCE, BACKGROUND ===
    # ====== AND UTILITY FUNCTIONS ======

    # Get the main Maya window as a parent of the interface
    parentwindow = pysideWindow.get_maya_window()

    _window = pysideWindow.LightInterfaceWindow(parent=parentwindow)

    # Change the window's background color to a very dark gray
    background_palette = _window.palette()
    background_palette.setColor(_window.backgroundRole(),
                                QtGui.QColor(46, 46, 46))
    _window.setPalette(background_palette)

    def get_selected_widgetitems():
        """
        Retrieves selected items in the window's widget list into an array,
        as long as they exist in the scene.
        :return: List with light Transform nodes
        """

        selectedlights = [item.text() for item
                          in _window.widgetlist.selectedItems()
                          if pmc.objExists(item.text())]
        return selectedlights

    def fill_itemlist():
        """
        Retrieves the Transform nodes of current lights in the scene,
        fills the widget list, updates the window's fields.
        :return: None
        """
        # Get the Transform node and type of light for each existing one
        current_lights = [(light.getParent(), light.nodeType())
                          for light in pmc.ls(type='light')]

        current_lights.sort()

        current_selection = pmc.ls(selection=True)

        _window.populate_itemlist(current_lights, current_selection)

        # If there are any selected lights, update the intensity
        # and color frames with the light in the last place
        if current_selection:
            update_window_fields(current_selection[-1].getIntensity(),
                                 current_selection[-1].getColor(),
                                 current_selection[-1].getShadowColor())

    def update_window_fields(intensity, light_color, shadow_color):
        """
        Updates the Current Intensity, Light Color and Shadow Color widgets
        in the window at the same time.
        :param intensity: Intensity value
        :param light_color: RGB value of Light Color
        :param shadow_color: RGB value of Shadow Color
        :return: None
        """
        _window.update_intensity_label(intensity)
        _window.receive_mayacolor(light_color)
        _window.receive_mayashadow(shadow_color)

    # ===== WINDOW CONNECTIONS ======
    # === AND CALLBACK FUNCTIONS ====

    def add_to_render_layer():
        """
        Add the window's selected widgetlist items to the current Render Layer
        :return: None
        """
        try:
            pmc.editRenderLayerMembers(_window.current_render_layer,
                                       get_selected_widgetitems())
        except:
            raise RuntimeError("Cannot change current Render Layer's members")

    def apply_color_change():
        """
        Retrieve current RGB value in the window's light_color attribute
        and apply change on the selected lights.
        :return: None
        """
        # Retrieve the current color value in the window
        rgb_array = _window.giveme_light_color()

        try:
            applyChanges.change_color([value/255.00 for value in rgb_array],
                                      get_selected_widgetitems(),
                                      _window.keyframecolor_checkbox.isChecked(),
                                      1)

        except RuntimeError:
            pmc.warning('Not able to set color. Please check Script Editor')

    def apply_intensity():
        """
        Retrieve intensity value in the window's line edit, and
        apply Intensity change on the selected lights.
        :return: None
        """
        try:
            with mayautils.undo_chunk():
                applyChanges.change_intensity(float(_window.intensityquantity_textbox.text()),
                                              _window.intensityoperator_combo.currentIndex(),
                                              get_selected_widgetitems(),
                                              _window.keyframeintensity_checkbox.isChecked())

            # Update the current intensity label inside the window
            _window.update_intensity_label(pmc.getAttr('%s.intensity' % _window.latest_light_selected))

        except:
            pmc.warning('Not able to set intensity')
            raise ValueError('Insert a numerical value in Intensity textbox')

    def apply_shadow_change():
        """
        Retrieve Shadow Color value in the window's shadow_color attribute,
        and apply change on the selected lights.
        :return: None
        """
        rgb_array = _window.giveme_shadow_color()

        try:
            applyChanges.change_color([value/255.00 for value in rgb_array],
                                      get_selected_widgetitems(),
                                      _window.keyframecolor_checkbox.isChecked(),
                                      2)

        except RuntimeError:
            pmc.warning('Not able to set light color.')

    def remove_from_render_layer():
        """
        Removes the window's selected widgetlist items from the Render Layer
        :return: None
        """
        try:
            pmc.editRenderLayerMembers(_window.current_render_layer,
                                       get_selected_widgetitems(), remove=True)

        except RuntimeError:
            pmc.warning('Cannot change members of the current Render Layer')

    def render_layer_changed(_):
        """
        Update the window's widgets regarding the selected Render Layer
        :param _: OpenMaya's callback clientData parameter; not used
        :return: None
        """

        # Update the window's current Render Layer and disable or enable the Render Layer buttons
        update_window_render_layer()

    def render_layer_only():
        """
        The 'Show Lights in Current Render Layer' mode has been pressed.
        Hide certain widgetlist items or show them all.
        :return: None
        """
        if _window.render_layer_only:
            # Render Layer Only mode has been deactivated;
            # restore all widgetlist item's display
            _window.render_layer_off()

        else:
            # Render Layer Only mode activated; show only items
            # with the same name as the current Layer's members
            _window.render_layer_on(pmc.editRenderLayerMembers(
                                    _window.current_render_layer, query=True))

    def time_changed(_):
        """
        Timeline has changed, update the window fields with the
        latest selected light's attributes.
        :param _: OpenMaya's callback clientData parameter; not used
        :return: None
        """
        if _window.latest_light_selected is not None:
            _window.update_intensity_label(pmc.getAttr('%s.intensity' % _window.latest_light_selected))
            _window.receive_mayacolor(pmc.getAttr('%s.color' % _window.latest_light_selected))
            _window.receive_mayashadow(pmc.getAttr('%s.shadowColor' % _window.latest_light_selected))

    def timelistener_trigger():
        """
        Add or remove a Timeline Listener OpenMaya Callback
        :return: None
        """
        if _window.timeline_listener.isChecked():
            try:
                _window.idCallback.append(OpenMaya.MEventMessage.addEventCallback("timeChanged",
                                                                                  time_changed))
                print 'Maya API timeChanged Callback added'
            except:
                print 'Could not initiate Maya API timeChanged Callback'

        # Remove the Callback ID that is stored in the window's idCallback list
        else:
            try:
                OpenMaya.MEventMessage.removeCallback(_window.idCallback[2])
                print 'Stopped Maya API timeChanged Callback'

            except RuntimeError:
                print "Couldn't find Maya API timeChanged Callback to stop"

    def update_list_selection(_):
        """
        Update the current highlighted items in the list with the current selection
        :param _: OpenMaya's callback clientData parameter; not used
        :return: None
        """
        # Check if the click was made inside the window, or in Maya
        inside_click = _window.isActiveWindow()

        # Shouldn't update selection when selection comes from the GUI, or else
        # the callback and update_maya_selection() method mess with the normal
        # selection of the widgetList
        if not inside_click:

            _window.update_list_selection(pmc.selected())

            # Update the window's elements with the latest selected light properties
            if _window.latest_light_selected is not None:
                _window.update_intensity_label(pmc.getAttr('%s.intensity' % _window.latest_light_selected))
                _window.receive_mayacolor(pmc.getAttr('%s.color' % _window.latest_light_selected))
                _window.receive_mayashadow(pmc.getAttr('%s.shadowColor' % _window.latest_light_selected))

            # Update intensity label to have N/A if no light is selected
            else:
                _window.update_intensity_label(None)

    def update_maya_selection():
        """
        Updates the current Maya selection with the window's widgetlist selection
        :return: None
        """
        _window.latest_light_selected = None

        with mayautils.undo_chunk():

            # For each light name in the window's list of names...
            for item in _window.lightsArray:

                #If the light still exists...
                if pmc.objExists(item):

                    listitem = _window.widgetlist.findItems(item, QtCore.Qt.MatchExactly)

                    # If the item is currently selected and the light exists,
                    # add it to current selection
                    if listitem[0].isSelected():
                        # Update the window's last selected light
                        _window.latest_light_selected = listitem[0].text()
                        try:
                            pmc.select(item, add=True)
                        except:
                            raise TypeError('Could not find light: ' + item)

                    else:
                        try:
                            pmc.select(item, deselect=True)
                        except:
                            raise TypeError('Could not find light: ' + item)

        if _window.latest_light_selected is not None:
            _window.update_intensity_label(pmc.getAttr('%s.intensity' % _window.latest_light_selected))
            _window.receive_mayacolor(pmc.getAttr('%s.color' % _window.latest_light_selected))
            _window.receive_mayashadow(pmc.getAttr('%s.shadowColor' % _window.latest_light_selected))

        # Update intensity label to have N/A if no light is selected
        else:
            _window.update_intensity_label(None)

    def update_window_render_layer():
        """
        Updates the window's current Render Layer attribute and
        the Render Layer buttons availability.
        :return: None
        """
        # Get the Render Layer's name and assign it to
        # the window's current_render_layer
        _window.current_render_layer = pmc.editRenderLayerGlobals(query=True,
                                                                  currentRenderLayer=True)

        # Update the Render Layer buttons, to lock them in case this is the defaultRenderLayer
        _window.render_change_trigger()

    # Create an OpenMaya API callback for selection changes in the scene
    try:
        _window.idCallback.append(OpenMaya.MEventMessage.addEventCallback("SelectionChanged",
                                                                          update_list_selection))

    except RuntimeError:
        print 'Could not initiate SelectionChanged Maya API Callback'

    # Create an OpenMaya API callback for render layer selection in the scene
    try:
        _window.idCallback.append(OpenMaya.MEventMessage.addEventCallback("renderLayerManagerChange",
                                                                          render_layer_changed))

    except RuntimeError:
        print 'Could not initiate renderLayerManagerChange Maya API Callback'

    # Connect the window's widgets to different signals
    _window.connect(_window.widgetlist,
                    QtCore.SIGNAL('itemSelectionChanged()'),
                    update_maya_selection)

    _window.connect(_window.renderlayer_button,
                    QtCore.SIGNAL('clicked()'),
                    render_layer_only)

    _window.connect(_window.updatebutton,
                    QtCore.SIGNAL('clicked()'),
                    fill_itemlist)

    _window.connect(_window.timeline_listener,
                    QtCore.SIGNAL('clicked()'),
                    timelistener_trigger)

    _window.connect(_window.applyintensity_button,
                    QtCore.SIGNAL('clicked()'),
                    apply_intensity)

    _window.connect(_window.applycolor_button,
                    QtCore.SIGNAL('clicked()'),
                    apply_color_change)

    _window.connect(_window.applyshadow_button,
                    QtCore.SIGNAL('clicked()'),
                    apply_shadow_change)

    _window.connect(_window.renderlayer_add,
                    QtCore.SIGNAL('clicked()'),
                    add_to_render_layer)

    _window.connect(_window.renderlayer_remove,
                    QtCore.SIGNAL('clicked()'),
                    remove_from_render_layer)

    # Get the current Render Layer
    update_window_render_layer()

    # Fill the item list
    fill_itemlist()

    _window.show()
