__author__ = 'Carlos Montes'

''' Creates the main window layout and widgets'''

from PySide import QtGui, QtCore
import os
import maya.OpenMaya as OpenMaya


class LightInterfaceWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        """
        Interface constructor
        :param parent: Window that will parent this QWidget instance
        :return: None
        """

        super(LightInterfaceWindow, self).__init__(parent)

        # Array that holds the names of lights in the scene
        self.lightsArray = []

        # Temporary array that holds the names of elements in the current render layer
        self.render_layer_array = []

        # Array that holds the ids of future Maya's MEventMessage callbacks
        self.idCallback = []

        # Saves the name of the latest selected light. Useful for Timeline Listener
        self.latest_light_selected = None

        # Saves the name of the current render layer
        self.current_render_layer = None

        # For file location of icons
        self.filepath = os.path.dirname(__file__)

        # Determines whether 'Render Layer Only' Mode is on or not
        self.render_layer_only = False

        # RGB color of the current color shown in the light and shadow color; starts as white and black
        self.color_light = QtGui.QColor(255, 255, 255)
        self.color_shadow = QtGui.QColor(0, 0, 0)

        # Create and set the container's central widget on the window
        main_container = QtGui.QWidget(self)
        self.setCentralWidget(main_container)

        # ===== UTILITY CLOSURES ====

        def add_space(layout, x, y):
            """
            Add a spacer in the window's layouts
            :param layout: Layout where the spacer will be added
            :param x: Width of spacer
            :param y: Height of spacer
            :return: None
            """
            spacer = QtGui.QSpacerItem(x, y)
            layout.addSpacerItem(spacer)
    
        def add_line(length):
            """
            Return a thick line to add in the layouts
            :param length: Length of the line
            :return: QFrame in the form of a line
            """
            line = QtGui.QFrame()
            line.setFixedWidth(length)
            line.setGeometry(QtCore.QRect(0, 0, length, 0))
            line.setFrameShape(QtGui.QFrame.HLine)
            return line
    
        def new_button(text, font_size=None):
            """
            Returns a new button
            :param text: Text that the button will contain
            :param font_size: Optional Font size of the button's text
            :return: QPushButton
            """
            button = QtGui.QPushButton('  ' + text + '  ')
            button.setStyleSheet("background-color:#555555; color:#CCCCCC;")
            button.setFixedHeight(25)
            if font_size is not None:
                font = QtGui.QFont()
                font.setPointSize(font_size)
                button.setFont(font)
            return button
    
        def new_checkbox(text):
            """
            Return a new Checkbox
            :param text: Text that will accompany the checkbox
            :return: QCheckbox
            """
            checkbox = QtGui.QCheckBox(text)
            checkbox.setStyleSheet('color:#333333;')
    
            cb_palette = checkbox.palette()
            cb_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.gray)
            checkbox.setPalette(cb_palette)
    
            return checkbox
    
        def new_label(text, size, color, bold=False):
            """
            Return a new QLabel
            :param text: Text that will be contained by the label
            :param size: Size of the label's text
            :param color: Color of the label's text
            :param bold: Boolean that tells whether to bold the label or not
            :return: QLabel
            """
            label = QtGui.QLabel(text)
            label.setStyleSheet('color:#%d;' % color)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setFixedHeight(20)
    
            font = QtGui.QFont()
            font.setPointSize(size)
            if bold:
                font.setBold(bold)
            label.setFont(font)
            return label
    
        def new_line_edit(size, readonly=False):
            """
            Return a new QLineEdit with standard styling
            :param size: Width of the textbox
            :param readonly: Boolean that tells whether to make it non-modifiable
            :return:
            """
            textbox = QtGui.QLineEdit()
            textbox.setFixedSize(size, 20)
            textbox.setStyleSheet('background-color:#444444; border:none; color:#FFFFFF')
            textbox.setReadOnly(readonly)
            textbox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            return textbox

        # ===== LEFT SIDE OF THE WINDOW =====

        # Search Textbox (and its Focus Policy) and its label, along with its container layout
        search_layout = QtGui.QHBoxLayout()
        search_label = new_label('Search Lights:', 7, 333333)
        self.searchlight_tbox = new_line_edit(110)
        self.searchlight_tbox.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Widget List that will hold the light names in the scene, and its container layout
        widgetlist_layout = QtGui.QHBoxLayout()
        self.widgetlist = QtGui.QListWidget()
        self.widgetlist.setMinimumHeight(400)
        self.widgetlist.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.widgetlist.setStyleSheet("""
                                    QListWidget {
                                        background-color:#444444;
                                    }
                                    QListWidget:item {
                                         height:45px;
                                         color:#444444;
                                    }
                                    QListWidget:item:selected {
                                         background-color:#1894C4;
                                         color:#1894C4;
                                    }
                                    QListWidget:item:hover {
                                    background-color:#AAAAAA;
                                    color:#AAAAAA;
                                    }
                                    """
                                    )

        # Render Layer Only and Update List buttons
        left_buttons_layout = QtGui.QHBoxLayout()

        self.renderlayer_button = new_button('Show Current Render Layer Only', 7)
        self.updatebutton = new_button('Update List', 8)

        # Bottom checkbox
        bottomleft_layout = QtGui.QHBoxLayout()
        self.timeline_listener = new_checkbox('Listen to Timeline Changes')

        # ===== RIGHT SIDE OF THE WINDOW =====

        # Intensity Top Label
        intensitylabel_leftline = add_line(50)
        intensitylabel_layout = QtGui.QHBoxLayout()
        intensitylabel = new_label('Intensity', 7, 333333, True)
        intensitylabel_rightline = add_line(50)

        # Main Intensity layout, Current Intensity label, modifying textbox and Operator combo box
        intensity_layout = QtGui.QVBoxLayout()

        currentintensity_layout = QtGui.QHBoxLayout()
        intensitycurrent_label = new_label('Current:', 8, 333333, True)
        self.currentintensity_label = new_label('N/A', 11, 222222, True)

        setintensity_layout = QtGui.QHBoxLayout()
        intensityquantity_label = new_label('Set:', 8, 333333)
        self.intensityquantity_textbox = new_line_edit(60)

        self.intensityoperator_combo = QtGui.QComboBox()
        self.intensityoperator_combo.addItem("fixed quantity")
        self.intensityoperator_combo.addItem("+/- increase")
        self.intensityoperator_combo.addItem("* multiply")
        self.intensityoperator_combo.addItem("+/- percentage")
        self.intensityoperator_combo.setStyleSheet("background-color:#555555; color:#CCCCCC;")
        self.intensityoperator_combo.setFixedHeight(25)

        # Intensity Bottom Widgets
        intensity_bottomlayout = QtGui.QHBoxLayout()

        self.keyframeintensity_checkbox = new_checkbox('Set Keyframe')
        self.applyintensity_button = new_button('Apply Intensity')

        # Light Color Top Label
        colorlabel_leftline = add_line(60)
        colorlabel_layout = QtGui.QHBoxLayout()
        colorlabel = new_label('Color', 7, 333333, True)
        colorlabel_rightline = add_line(60)

        # Light Color Dialog Prompter, RGB/HSV boxes and Frame
        color_layout = QtGui.QHBoxLayout()
        colorTextboxes_layout = QtGui.QVBoxLayout()
        rh_layout = QtGui.QHBoxLayout()
        gs_layout = QtGui.QHBoxLayout()
        bv_layout = QtGui.QHBoxLayout()

        self.color_frame = colorFrame(main_container, 1, self.color_light.red(),
                                      self.color_light.green(), self.color_light.blue())

        r_label = new_label('R:', 9, 333333)
        g_label = new_label('G:', 9, 333333)
        b_label = new_label('B:', 9, 333333)
        h_label = new_label('H:', 9, 333333)
        s_label = new_label('S:', 9, 333333)
        v_label = new_label('V:', 9, 333333)

        self.r_textbox = new_line_edit(40, True)
        self.g_textbox = new_line_edit(40, True)
        self.b_textbox = new_line_edit(40, True)
        self.h_textbox = new_line_edit(40, True)
        self.s_textbox = new_line_edit(40, True)
        self.v_textbox = new_line_edit(40, True)

        # Light Color Bottom
        lightcolor_bottomlayout = QtGui.QHBoxLayout()

        self.keyframecolor_checkbox = new_checkbox('Set Keyframe')
        self.applycolor_button = new_button('Apply Color')

        # Shadow Color Top Label
        colorshadowlabel_leftline = add_line(50)
        colorshadowlabel_layout = QtGui.QHBoxLayout()
        colorshadowlabel = new_label('Shadow Color', 7, 333333, True)
        colorshadowlabel_rightline = add_line(50)

        # Shadow Color Dialog Prompter, RGB/HSV boxes and Frame
        colorshadow_layout = QtGui.QHBoxLayout()
        colorshadowTextboxes_layout = QtGui.QVBoxLayout()
        rhshadow_layout = QtGui.QHBoxLayout()
        gsshadow_layout = QtGui.QHBoxLayout()
        bvshadow_layout = QtGui.QHBoxLayout()

        self.colorshadow_frame = colorFrame(main_container, 2, self.color_shadow.red(),
                                            self.color_shadow.green(), self.color_shadow.blue())

        rshadow_label = new_label('R:', 9, 333333)
        gshadow_label = new_label('G:', 9, 333333)
        bshadow_label = new_label('B:', 9, 333333)
        hshadow_label = new_label('H:', 9, 333333)
        sshadow_label = new_label('S:', 9, 333333)
        vshadow_label = new_label('V:', 9, 333333)

        self.rshadow_textbox = new_line_edit(40, True)
        self.gshadow_textbox = new_line_edit(40, True)
        self.bshadow_textbox = new_line_edit(40, True)
        self.hshadow_textbox = new_line_edit(40, True)
        self.sshadow_textbox = new_line_edit(40, True)
        self.vshadow_textbox = new_line_edit(40, True)

        # Shadow Color Bottom
        shadowcolor_bottomlayout = QtGui.QHBoxLayout()

        self.keyframeshadow_checkbox = new_checkbox('Set Keyframe')
        self.applyshadow_button = new_button('Apply Shadow')

        # Render Layer Buttons
        renderlayer_layout = QtGui.QHBoxLayout()

        self.renderlayer_add = new_button('Add to Render Layer', 7)
        self.renderlayer_remove = new_button('Remove from Render Layer', 7)

        # ============ CONNECTIONS, SIGNALS AND CALLBACKS ============

        self.connect(self.searchlight_tbox, QtCore.SIGNAL('keyReleaseEvent()'), self.search_light)

        # ============ LAYOUTS ============

        # ------ Vertical box layout for the left side ------
        vertical_layout_left = QtGui.QVBoxLayout()

        # ------ Vertical box layout for the right side ------
        vertical_layout_right = QtGui.QVBoxLayout()

        # ------ Modifiers QFrame and Layout ------
        modifiers_layout = QtGui.QVBoxLayout()
        modifiers_frame = QtGui.QFrame(main_container)
        modifiers_frame.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
        modifiers_frame.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        modifiers_frame.setLineWidth(1)

        # Search box Layout
        search_layout.addStretch(1)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.searchlight_tbox)

        add_space(vertical_layout_left, 0, 10)
        vertical_layout_left.addLayout(search_layout)
        add_space(vertical_layout_left, 0, 5)

        # Widget list Layout
        widgetlist_layout.addWidget(self.widgetlist)
        vertical_layout_left.addLayout(widgetlist_layout)
        add_space(vertical_layout_left, 0, 5)

        # Render Layer Only and Update buttons at the left side
        left_buttons_layout.addWidget(self.renderlayer_button)
        left_buttons_layout.addStretch(1)
        left_buttons_layout.addWidget(self.updatebutton)

        vertical_layout_left.addLayout(left_buttons_layout)
        add_space(vertical_layout_left, 0, 5)

        # Timeline Listener Checkbox
        bottomleft_layout.addWidget(self.timeline_listener)
        add_space(vertical_layout_left, 0, 15)
        vertical_layout_left.addLayout(bottomleft_layout)
        add_space(vertical_layout_left, 0, 5)

        # Intensity label
        intensitylabel_layout.addWidget(intensitylabel_leftline)
        add_space(intensitylabel_layout, 15, 0)
        intensitylabel_layout.addWidget(intensitylabel)
        add_space(intensitylabel_layout, 15, 0)
        intensitylabel_layout.addWidget(intensitylabel_rightline)
        intensitylabel_layout.setAlignment(QtCore.Qt.AlignCenter)

        modifiers_layout.addLayout(intensitylabel_layout)
        add_space(modifiers_layout, 0, 5)

        # Intensity modifiers
        currentintensity_layout.addWidget(intensitycurrent_label)
        add_space(currentintensity_layout, 30, 0)
        currentintensity_layout.addWidget(self.currentintensity_label)
        currentintensity_layout.setAlignment(QtCore.Qt.AlignCenter)

        setintensity_layout.addWidget(intensityquantity_label)
        add_space(setintensity_layout, 4, 0)
        setintensity_layout.addWidget(self.intensityquantity_textbox)
        add_space(setintensity_layout, 8, 0)
        setintensity_layout.addWidget(self.intensityoperator_combo)
        setintensity_layout.setAlignment(QtCore.Qt.AlignCenter)

        intensity_layout.addLayout(currentintensity_layout)
        add_space(intensity_layout, 0, 5)
        intensity_layout.addLayout(setintensity_layout)

        modifiers_layout.addLayout(intensity_layout)
        add_space(modifiers_layout, 0, 6)

        # Bottom elements of intensity
        add_space(intensity_bottomlayout, 20, 0)
        intensity_bottomlayout.addWidget(self.keyframeintensity_checkbox)
        intensity_bottomlayout.addStretch(1)
        intensity_bottomlayout.addWidget(self.applyintensity_button)
        add_space(intensity_bottomlayout, 20, 0)

        modifiers_layout.addLayout(intensity_bottomlayout)
        add_space(modifiers_layout, 0, 10)

        # Color label
        colorlabel_layout.addWidget(colorlabel_leftline)
        add_space(colorlabel_layout, 15, 0)
        colorlabel_layout.addWidget(colorlabel)
        add_space(colorlabel_layout, 15, 0)
        colorlabel_layout.addWidget(colorlabel_rightline)
        colorlabel_layout.setAlignment(QtCore.Qt.AlignCenter)

        modifiers_layout.addLayout(colorlabel_layout)
        add_space(modifiers_layout, 0, 5)

        # Color Canvas, Buttons and Textboxes
        add_space(color_layout, 20, 0)
        color_layout.addWidget(self.color_frame)

        rh_layout.addWidget(r_label)
        add_space(rh_layout, 2, 0)
        rh_layout.addWidget(self.r_textbox)
        rh_layout.addStretch(1)
        rh_layout.addWidget(h_label)
        add_space(rh_layout, 2, 0)
        rh_layout.addWidget(self.h_textbox)
        add_space(rh_layout, 20, 0)
        colorTextboxes_layout.addLayout(rh_layout)

        gs_layout.addWidget(g_label)
        add_space(gs_layout, 2, 0)
        gs_layout.addWidget(self.g_textbox)
        gs_layout.addStretch(1)
        gs_layout.addWidget(s_label)
        add_space(gs_layout, 2, 0)
        gs_layout.addWidget(self.s_textbox)
        add_space(gs_layout, 20, 0)
        colorTextboxes_layout.addLayout(gs_layout)

        bv_layout.addWidget(b_label)
        add_space(bv_layout, 2, 0)
        bv_layout.addWidget(self.b_textbox)
        bv_layout.addStretch(1)
        bv_layout.addWidget(v_label)
        add_space(bv_layout, 2, 0)
        bv_layout.addWidget(self.v_textbox)
        add_space(bv_layout, 20, 0)
        colorTextboxes_layout.addLayout(bv_layout)

        color_layout.addLayout(colorTextboxes_layout)

        add_space(modifiers_layout, 0, 5)
        modifiers_layout.addLayout(color_layout)
        add_space(modifiers_layout, 0, 5)

        # Bottom elements of light color
        add_space(lightcolor_bottomlayout, 20, 0)
        lightcolor_bottomlayout.addWidget(self.keyframecolor_checkbox)
        lightcolor_bottomlayout.addStretch(1)
        lightcolor_bottomlayout.addWidget(self.applycolor_button)
        add_space(lightcolor_bottomlayout, 20, 0)
        lightcolor_bottomlayout.setAlignment(QtCore.Qt.AlignLeft)

        modifiers_layout.addLayout(lightcolor_bottomlayout)
        add_space(modifiers_layout, 0, 10)

        # Shadow Color label
        colorshadowlabel_layout.addWidget(colorshadowlabel_leftline)
        add_space(colorshadowlabel_layout, 15, 0)
        colorshadowlabel_layout.addWidget(colorshadowlabel)
        add_space(colorshadowlabel_layout, 15, 0)
        colorshadowlabel_layout.addWidget(colorshadowlabel_rightline)
        colorshadowlabel_layout.setAlignment(QtCore.Qt.AlignCenter)

        modifiers_layout.addLayout(colorshadowlabel_layout)
        add_space(modifiers_layout, 0, 5)

        # Shadow Color Canvas, Buttons and Textboxes
        add_space(colorshadow_layout, 20, 0)
        colorshadow_layout.addWidget(self.colorshadow_frame)

        rhshadow_layout.addWidget(rshadow_label)
        add_space(rhshadow_layout, 2, 0)
        rhshadow_layout.addWidget(self.rshadow_textbox)
        rhshadow_layout.addStretch(1)
        rhshadow_layout.addWidget(hshadow_label)
        add_space(rhshadow_layout, 2, 0)
        rhshadow_layout.addWidget(self.hshadow_textbox)
        add_space(rhshadow_layout, 20, 0)
        colorshadowTextboxes_layout.addLayout(rhshadow_layout)

        gsshadow_layout.addWidget(gshadow_label)
        add_space(gsshadow_layout, 2, 0)
        gsshadow_layout.addWidget(self.gshadow_textbox)
        gsshadow_layout.addStretch(1)
        gsshadow_layout.addWidget(sshadow_label)
        add_space(gsshadow_layout, 2, 0)
        gsshadow_layout.addWidget(self.sshadow_textbox)
        add_space(gsshadow_layout, 20, 0)
        colorshadowTextboxes_layout.addLayout(gsshadow_layout)

        bvshadow_layout.addWidget(bshadow_label)
        add_space(bvshadow_layout, 2, 0)
        bvshadow_layout.addWidget(self.bshadow_textbox)
        bvshadow_layout.addStretch(1)
        bvshadow_layout.addWidget(vshadow_label)
        add_space(bvshadow_layout, 2, 0)
        bvshadow_layout.addWidget(self.vshadow_textbox)
        add_space(bvshadow_layout, 20, 0)
        colorshadowTextboxes_layout.addLayout(bvshadow_layout)

        colorshadow_layout.addLayout(colorshadowTextboxes_layout)
        colorshadow_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        add_space(modifiers_layout, 0, 5)
        modifiers_layout.addLayout(colorshadow_layout)

        # Bottom elements of shadow color
        add_space(shadowcolor_bottomlayout, 20, 0)
        shadowcolor_bottomlayout.addWidget(self.keyframeshadow_checkbox)
        shadowcolor_bottomlayout.addStretch(1)
        shadowcolor_bottomlayout.addWidget(self.applyshadow_button)
        add_space(shadowcolor_bottomlayout, 20, 0)
        shadowcolor_bottomlayout.setAlignment(QtCore.Qt.AlignLeft)

        add_space(modifiers_layout, 0, 5)
        modifiers_layout.addLayout(shadowcolor_bottomlayout)
        add_space(modifiers_layout, 0, 10)

        modifiers_layout.setAlignment(QtCore.Qt.AlignCenter)
        vertical_layout_right.addWidget(modifiers_frame)

        # Finish modifiers' layout by setting it to the modifier frame
        modifiers_frame.setLayout(modifiers_layout)

        # Render Layer Buttons
        renderlayer_layout.addWidget(self.renderlayer_add)
        add_space(renderlayer_layout, 20, 0)
        renderlayer_layout.addWidget(self.renderlayer_remove)
        renderlayer_layout.setAlignment(QtCore.Qt.AlignCenter)

        add_space(vertical_layout_right, 0, 15)
        vertical_layout_right.addLayout(renderlayer_layout)

        # Set Alignments for containers
        vertical_layout_right.setAlignment(QtCore.Qt.AlignTop)

        # Main layout (Horizontal) for the whole window
        main_layout = QtGui.QHBoxLayout()
        add_space(main_layout, 10, 0)
        main_layout.addLayout(vertical_layout_left)
        add_space(main_layout, 20, 0)
        main_layout.addLayout(vertical_layout_right)
        add_space(main_layout, 10, 0)

        # Fill the color textboxes with the default colors
        self.update_lightcolor_boxes(self.color_light)
        self.update_shadowcolor_boxes(self.color_shadow)

        main_container.setLayout(main_layout)
        self.setWindowTitle('Light Interface')
        self.setObjectName('lightInterfaceUI')

    def color_selected(self, color, where):
        """
        A light color or shadow color has been selected; change the content of the corresponding widgets
        :param color: Hexadecimal value of the selected color
        :param where: 1 for color light, 2 for shadow color
        :return: None
        """
        # Either a light color (1) or a shadow color has been selected
        if where is 1:
            self.color_light = color
            self.update_lightcolor_boxes(self.color_light)
        else:
            self.color_shadow = color
            self.update_shadowcolor_boxes(self.color_shadow)

    def giveme_light_color(self):
        """
        Retrieves the current light RGB color value in the window; compare to HSV value to tell if they're different
        :return: Array with RGB values of self.color_light and a comparison between RGB and HSV values
        """
        try:
            rgb_value = QtGui.QColor(int(self.r_textbox.text()), int(self.g_textbox.text()),
                                  int(self.b_textbox.text()))

            hsv_value = QtGui.QColor()
            hsv_value.setHsv(int(self.h_textbox.text()), int(self.s_textbox.text()),
                            int(self.v_textbox.text()))

            return [[rgb_value.red(), rgb_value.green(), rgb_value.blue()], rgb_value == hsv_value]

        except:
            raise ValueError('Only numerical values should be inside the Color textboxes')

    def giveme_shadow_color(self):
        """
        Retrieves the current shadow RGB color value in the window; compare to HSV value to tell if they're different
        :return: Array with RGB values of self.shadow_color and a comparison between RGB and HSV values
        """
        try:
            rgb_value = QtGui.QColor(int(self.rshadow_textbox.text()), int(self.gshadow_textbox.text()),
                                     int(self.bshadow_textbox.text()))

            hsv_value = QtGui.QColor()
            hsv_value.setHsv(int(self.hshadow_textbox.text()), int(self.sshadow_textbox.text()),
                             int(self.vshadow_textbox.text()))

            return [[rgb_value.red(), rgb_value.green(), rgb_value.blue()], rgb_value == hsv_value]

        except:
            raise ValueError('Only numerical values should be inside the Shadow Color textboxes')

    def populate_itemlist(self, lights_array, selected_array):
        """
        Fill the widgetlist with the passed array of lights
        :param lights_array: Transform node names of lights in the current scene
        :param selected_array: Array of selected items in the scene
        :return:None
        """
        for item in self.lightsArray:
            list_items = self.widgetlist.findItems(str(item), QtCore.Qt.MatchExactly)
            self.widgetlist.removeItemWidget(list_items[0])

        self.lightsArray = []
        self.widgetlist.clear()
        counter = 0

        for item, light_type in lights_array:
            self.lightsArray.append(str(item))

            # Create a ListWidgetItem with the light's name. This text will be hidden with the widgetlist's Stylesheet
            list_item = QtGui.QListWidgetItem(self.lightsArray[counter])

            # Create a Custom Widget with the light's name and an icon according to its type and render layer presence
            custom_widget = CustomListWidgetItem(self.widgetlist, self.lightsArray[counter],
                                                 os.path.join(self.filepath, 'icon_' + light_type + '.png'))

            self.widgetlist.addItem(list_item)
            self.widgetlist.setItemWidget(list_item, custom_widget)

            if item in selected_array:
                list_item.setSelected(True)
                self.latest_light_selected = item

            counter += 1

    def receive_mayacolor(self, rgb_float_array):
        """
        Receives a Float Array from a Light nodetype's getColor method to update the window's color_light
        :param rgb_float_array: RGB value of a specific light
        :return: None
        """
        self.color_light.setRedF(rgb_float_array[0])
        self.color_light.setGreenF(rgb_float_array[1])
        self.color_light.setBlueF(rgb_float_array[2])

        self.update_lightcolor_boxes(self.color_light)

    def receive_mayashadow(self, rgb_float_array):
        """
        Receives a Float Array from a Light nodetype's getShadowColor method
        :param rgb_float_array: RGB value of a specific light's shadow color
        :return:
        """
        self.color_shadow.setRedF(rgb_float_array[0])
        self.color_shadow.setGreenF(rgb_float_array[1])
        self.color_shadow.setBlueF(rgb_float_array[2])

        self.update_shadowcolor_boxes(self.color_shadow)

    def render_change_trigger(self):
        """
        A new Render Layer has been selected; check if this is the defaultRenderLayer and reset Render Layer Only mode
        :return: None
        """
        if self.current_render_layer == 'defaultRenderLayer':
            self.renderlayer_button.setEnabled(False)
            self.renderlayer_add.setEnabled(False)
            self.renderlayer_remove.setEnabled(False)
        else:
            self.renderlayer_button.setEnabled(True)
            self.renderlayer_add.setEnabled(True)
            self.renderlayer_remove.setEnabled(True)

        self.render_layer_off()

    def render_layer_off(self):
        """
        Render Layer Mode has been deactivated; show all lights and reset everything related to render layers
        :return: None
        """
        self.render_layer_array = []
        self.render_layer_only = False
        self.renderlayer_button.setText('Show Current Render Layer Only')

        # Go through each list item and unhide it
        for i in range(self.widgetlist.count()):
            self.widgetlist.item(i).setHidden(False)

    def render_layer_on(self, layer_elements):
        """
        Render Layer Mode has been activated
        :param layer_elements: Array of elements in the current Render Layer
        :return: None
        """
        self.render_layer_array = layer_elements
        self.render_layer_only = True
        self.renderlayer_button.setText('Show All Lights')

        # Go through each list item and hide or unhide it
        for i in range(self.widgetlist.count()):
            listitem = self.widgetlist.item(i)

            if listitem.text() in self.render_layer_array:
                listitem.setHidden(False)
            else:
                listitem.setHidden(True)

    def search_light(self, letters):
        """
        Look for lights through the widgetlist that match the passed string
        :param letters: String of characters that the user has typed
        :return: None
        """
        # If Render Layer Only is on... show those lights that are in the window's render_layer_array and match letters
        if self.render_layer_only:
            # Go through each list item and hide it or unhide it
            for i in range(self.widgetlist.count()):
                listitem = self.widgetlist.item(i)
                match = listitem.text().find(letters)
                if match >= 0 and listitem.text() in self.render_layer_array:
                    listitem.setHidden(False)
                else:
                    listitem.setHidden(True)

        # Else do it the easier way
        else:
            # Go through each list item and hide it or unhide it
            for i in range(self.widgetlist.count()):
                listitem = self.widgetlist.item(i)
                match = listitem.text().find(letters)
                if match < 0:
                    listitem.setHidden(True)
                else:
                    listitem.setHidden(False)

    def update_list_selection(self, selected_array):
        """
        Updates the current widgetlist selection
        :param selected_array: Array of selected lights in the scene
        :return:
        """
        self.latest_light_selected = None

        for item in self.lightsArray:
            listitem = self.widgetlist.findItems(item, QtCore.Qt.MatchExactly)

            if item in selected_array:
                listitem[0].setSelected(QtCore.Qt.Checked)
                self.latest_light_selected = listitem[0].text()
            else:
                listitem[0].setSelected(QtCore.Qt.Unchecked)

    def update_intensity_label(self, quantity=None):
        """
        Updates the current intensity label's content
        :param quantity: Intensity quantity of a specific light. If None, N/A will be displayed
        :return: None
        """
        if quantity is None:
            self.currentintensity_label.setText('N/A')
        else:
            self.currentintensity_label.setText("%.2f" % quantity)

    def update_lightcolor_boxes(self, color):
        """
        Fill the light color lineEdits with a certain string in its respective attributes, change color frame
        :param color: QColor instance
        :return:
        """
        self.r_textbox.setText(str(color.red()))
        self.g_textbox.setText(str(color.green()))
        self.b_textbox.setText(str(color.blue()))
        if color.hue() < 0:
            self.h_textbox.setText('0')
        else:
            self.h_textbox.setText(str(color.hue()))
        self.s_textbox.setText(str(color.saturation()))
        self.v_textbox.setText(str(color.value()))

        self.color_frame.update_color(self.color_light)

    def update_shadowcolor_boxes(self, color):
        """
        Fill the shadow color boxes with a certain string in its respective attributes, change shadow color frame
        :param color: QColor instance
        :return: None
        """
        self.rshadow_textbox.setText(str(color.red()))
        self.gshadow_textbox.setText(str(color.green()))
        self.bshadow_textbox.setText(str(color.blue()))
        if color.hue() < 0:
            self.hshadow_textbox.setText('0')
        else:
            self.hshadow_textbox.setText(str(color.hue()))
        self.sshadow_textbox.setText(str(color.saturation()))
        self.vshadow_textbox.setText(str(color.value()))

        self.colorshadow_frame.update_color(self.color_shadow)

    # ============ OVERRIDDEN FUNCTIONS ============

    # When the window is closed, kill the MEvent Message Callback
    def closeEvent(self, event):
        """
        Remove OpenMaya callbacks when the window is closed
        :param event: Unused event parameter
        :return: None
        """
        for id in self.idCallback:
            try:
                OpenMaya.MEventMessage.removeCallback(id)
                print 'Callback removed'

            except:
                print 'Could not locate such a thing as a Maya API Callback. Closing anyway.'

        event.accept()

    def keyReleaseEvent(self, event):
        """
        Look for a widgetlist item to find light names
        :param event: Unused event parameter
        :return: None
        """
        self.search_light(self.searchlight_tbox.text())


class colorFrame(QtGui.QFrame):
    def __init__(self, parent, number, red, green, blue):
        """
        Create a customizable QFrame that reacts to a click by opening a QColorDialog
        :param parent: Widget parent of this frame
        :param number: 1 if it's Color Light, 2 if it's Shadow Color
        :param red: Red value to set on a new QColor
        :param green: Green value to set on a new QColor
        :param blue: Blue value to set on a new QColor
        :return: None
        """
        super(colorFrame, self).__init__(parent)

        self.kind = number
        self.hexadecimal = QtGui.QLabel('', self)
        self.color = QtGui.QColor(red, green, blue)
        self.update_color(self.color)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.hexadecimal)
        vertical_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setLineWidth(1)
        self.setFixedSize(80, 80)
        self.setLayout(vertical_layout)

    def update_color(self, color):
        """
        Updates the current frame's QColor's value
        :param color: QColor
        :return: None
        """
        self.color = color
        self.setStyleSheet("background-color: %s" % self.color.name())

        if self.color.black() < 128:
            self.hexadecimal.setStyleSheet('color:#000000')
        else:
            self.hexadecimal.setStyleSheet('color:#FFFFFF')
        self.hexadecimal.setText(self.color.name())

    def mousePressEvent(self, event):
        """
        Display a QColorDialog when being clicked on
        :param event: Unused event parameter
        :return: None
        """
        color = QtGui.QColorDialog.getColor()

        self.update_color(color)
        self.parent().parent().parent().color_selected(color, self.kind)


class CustomListWidgetItem(QtGui.QWidget):
    def __init__(self, parent, name, icon_path):
        """
        Creates a new Custom Widget that displays a light's icon according to its nodeType, and its name
        """
        super(CustomListWidgetItem, self).__init__(parent)

        main_layout = QtGui.QHBoxLayout()

        self.light_icon = QtGui.QLabel()
        self.light_icon.setFixedSize(45, 45)
        pixmap = QtGui.QPixmap(30, 30)
        pixmap.load(icon_path)
        self.light_icon.setPixmap(pixmap)
        self.light_icon.setAlignment(QtCore.Qt.AlignTop)

        self.light_name = QtGui.QLabel(name)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.light_name.setFont(font)
        self.light_name.setStyleSheet('color:#FFFFFF')

        spacer = QtGui.QSpacerItem(10, 0)
        main_layout.addSpacerItem(spacer)
        main_layout.addWidget(self.light_icon)
        spacer = QtGui.QSpacerItem(20, 0)
        main_layout.addSpacerItem(spacer)
        main_layout.addWidget(self.light_name)
        main_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.setLayout(main_layout)


def main():
    """
    Test function for PySide only window template
    :return: None
    """
    import sys

    app = QtGui.QApplication(sys.argv)

    ex = LightInterfaceWindow()

    # Change the window's background color
    background_palette = ex.palette()
    background_palette.setColor(ex.backgroundRole(), QtCore.Qt.darkGray)
    ex.setPalette(background_palette)

    def fill_itemlist():
        test_array = [['item' + str(i), 'spotLight'] for i in range(10)]
        current_selection = ['item4', 'item7']

        ex.populate_itemlist(test_array, current_selection)

    fill_itemlist()

    ex.show()

    app.exec_()

if __name__ == '__main__':
    main()