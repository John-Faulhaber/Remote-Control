# NOTE: this uses BK Precision 9141 programming commands
# https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/datasheets/en-us/9140_Series_datasheet.pdf
# https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/manuals/en-us/9140_Series_manual.pdf
# https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/programming_manuals/en-us/9140_Series_programming_manual.pdf
# https://bkpmedia.s3.us-west-1.amazonaws.com/downloads/comparison_guides/en-us/9140_Series_comparison_guide.pdf
'''
Module containing class to handle the application's GUI and operation.
'''
import sys
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import base64
import hashlib
from cryptography.fernet import Fernet

from remote_control import RemoteControl
from check_ports import CheckPorts


# Class to manage the GUI
class ApplicationUi(QtWidgets.QDialog):
    '''
    Class containing functions to handle the application's GUI and operation.
    '''

    def __init__(self):
        '''
        "Initialize" GUI window and run the functions that create the GUI.

        Parameters
        ----------
        QtWidgets.QDialog (class "PyQt5.QtWidgets.QDialog", "sip.wrappertype")

        Returns
        -------
        None

        '''
        QtWidgets.QDialog.__init__(self)

        self.__create_components()
        self.__configure_components()
        self.__construct_gui()


    def __create_components(self):
        '''
        Create GUI components, including group-boxes, widgets, and layout objects.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        # Primary Layout of top-level window
        self.main_layout = QtWidgets.QGridLayout()
        # go_row layout - distinct organization
        self.go_row_layout = QtWidgets.QHBoxLayout()

        # Creating group-boxes for nesting inside. Hierarchy: Top-window+layout -> group-box+layout -> widget
        # COM Port group-box + component objects
        self.com_port_group_box = QtWidgets.QGroupBox('Power Supply COM Port')
        self.com_port_group_box_layout = QtWidgets.QGridLayout()
        self.com_port = QtWidgets.QLineEdit()
        self.check_ports_button = QtWidgets.QPushButton('Check Ports')

        # Function group-box + component objects
        self.function_group_box = QtWidgets.QGroupBox('Function')
        self.function_group_box_layout = QtWidgets.QGridLayout()
        self.radio_button_voltage = QtWidgets.QRadioButton('Voltage')
        self.radio_button_current = QtWidgets.QRadioButton('Current')

        # Manual Voltage Values group-box + component objects
        self.set_value_group_box = QtWidgets.QGroupBox('Set Values')
        self.set_value_group_box_layout = QtWidgets.QGridLayout()
        self.set_value = QtWidgets.QLineEdit()

        # Status group-box + component objects
        self.status_group_box = QtWidgets.QGroupBox('Status')
        self.status_group_box_layout = QtWidgets.QGridLayout()
        self.status = QtWidgets.QPlainTextEdit()

        # go_row component objects - not using a nested group box
        self.clear = QtWidgets.QPushButton('Clear')
        self.always_clear = QtWidgets.QCheckBox('Always clear on "Go!"')
        self.go_button = QtWidgets.QPushButton('Go!')

        # Create decrypted "version value" object for display in bottom right of GUI. Version numberis YYYYMMDD format
        version_decrypted = self.__version_decryption()
        self.version = QtWidgets.QLabel(f'Version {version_decrypted}')

        # Create additional functional objects
        # COM Port text entry validator
        self.com_validator = QtGui.QRegExpValidator(QRegExp(r'^[0-9]{1,2}$'))  # REGEX

        # Voltage Value text entry validator
        # BK Precision 9141:
        # 60.600 > V > 0.000
        # 4.040 > I > 0.015
        # REGEX: 0, 1, or 2 digits, then optional single decimal, then 1, 2, or 3 digits. Restriction of lone decimal and resultant number value to within instrument limits is performed outside REGEX
        self.set_value_validator = QtGui.QRegExpValidator(QRegExp(r'^[0-9]{0,2}\.?[0-9]{1,3}$'))  # Up to 2 digits, optional decimal, at least 1 digit up to 3


    def __configure_components(self):
        '''
        Configure GUI components.
        Establish connections to functions, as well as declare what/when emit signal(s).
        Add features, such as "ToolTips" to specific components.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        # Main GUI window attributes
        self.setWindowTitle('Remote Control')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        # COM Port group-box + component objects attributes
        self.com_port_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.com_port.setFixedHeight(60)
        self.com_port.setFixedWidth(68)
        self.com_port.setFont(QtGui.QFont('Cascadia Mono', 29))
        self.com_port.setAlignment(Qt.AlignCenter)  # Text alignment - not widget alignment
        self.com_port.setReadOnly(False)
        self.com_port.setPlaceholderText('#')
        self.com_port.setValidator(self.com_validator)
        self.com_port.textChanged.connect(self.check_state)
        self.com_port.textChanged.emit(self.com_port.text())

        self.check_ports_button.clicked.connect(self.check_ports)

        # Function group-box + component attributes
        self.function_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.radio_button_voltage.setFont(QtGui.QFont('Cascadia Mono', 10))
        self.radio_button_voltage.setToolTip('Control the connected power supply voltage level.')
        self.radio_button_current.setFont(QtGui.QFont('Cascadia Mono', 10))
        self.radio_button_current.setToolTip('Control the connected power supply current level.')

        # Voltage Values group-box + component objects attributes
        self.set_value_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.set_value.setFixedHeight(30)
        self.set_value.setReadOnly(False)
        self.set_value.setPlaceholderText('Value | Hover over me for help')
        self.set_value.setValidator(self.set_value_validator)
        self.set_value.textChanged.connect(self.check_state)
        self.set_value.textChanged.emit(self.set_value.text())
        self.set_value.textChanged.emit(self.set_value.text())
        self.set_value.setToolTip('Set Value text restricted to "0, 1, or 2 digits, optional decimal, 1, 2, or 3 digits"\n\nExamples:\nAny integer up to 5 digits in length, or some value of the following form:\n\n.#     | #.#     | ##.#\n.##   | #.##   | ##.##\n.### | #.### | ##.###')

        # Status group-box + component objects attributes
        self.status_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.status.setStyleSheet('QPlainTextEdit {background-color: rgb(0, 0, 0);}')
        self.status.setReadOnly(True)
        self.status.setPlaceholderText('Remote Control status log will print in this box')

        # go_row component attributes
        # Make "Go!" the default button in focus. Enter key selects focused elements
        self.go_button.setDefault(True)
        self.go_button.clicked.connect(self.click_go)
        self.clear.clicked.connect(self.clear_status)
        self.version.setStyleSheet('QLabel { background-color : ; color : #6b6b6b; }')


    def __construct_gui(self):
        '''
        Assemble GUI components into GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        # Set primary layout of top-level GUI window
        self.setLayout(self.main_layout)

        # Add components to the layout objects
        # Nesting group-boxes into main_layout
        # (QGridLayout: row, column, rowSpan, columnSpan)
        self.main_layout.addWidget(self.com_port_group_box, 0, 0, 1, 1)
        self.main_layout.addWidget(self.function_group_box, 0, 1, 1, 1)
        self.main_layout.addWidget(self.set_value_group_box, 0, 2, 1, 1)
        self.main_layout.addWidget(self.status_group_box, 1, 0, 1, 3)

        # Set layouts of main_layout group-boxes
        # Add components to main_layout group-box layouts
        # [COM Port group-box]
        self.com_port_group_box.setLayout(self.com_port_group_box_layout)
        self.com_port_group_box_layout.addWidget(self.com_port, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        self.com_port_group_box_layout.addWidget(self.check_ports_button, 1, 0, 1, 1)

        # [Function group-box]
        self.function_group_box.setLayout(self.function_group_box_layout)
        self.function_group_box_layout.addWidget(self.radio_button_voltage)
        self.function_group_box_layout.addWidget(self.radio_button_current)

        # [Voltage Values group-box]
        self.set_value_group_box.setLayout(self.set_value_group_box_layout)
        self.set_value_group_box_layout.addWidget(self.set_value)

        # [Status group-box]
        self.status_group_box.setLayout(self.status_group_box_layout)
        self.status_group_box_layout.addWidget(self.status)

        # Nesting go_row_layout into main_layout
        self.main_layout.addLayout(self.go_row_layout, 2, 0, 1, 3)

        # Add components to go_row layout
        # (QHBoxLayout)
        # [GO! row has no group-box]
        self.go_row_layout.addWidget(self.clear)
        self.go_row_layout.addWidget(self.always_clear)

        # Wedge "Clear" and "Go!" apart, to the left and right edge. Order of code is significant, and determines the order of components
        self.go_row_layout.insertStretch(2) # Adds a blank in "spot 3"
        self.go_row_layout.addWidget(self.version)
        self.go_row_layout.addWidget(self.go_button)


    # SUPPLEMENTARY FUNCTIONS
    def update_status_callback(self, text):
        '''
        Display text in status widget in GUI.
        Updates/refreshes GUI.
        Can be passed as a function argument to get to other modules, allowing other modules to update the GUI
        without needing to import this module (offloads non-GUI work from GUI module + avoids circular imports).

        Parameters
        ----------
        self: Represents the instance of the Class
        text (string): Text to print in status text box

        Returns
        -------
        None

        '''
        self.status.appendHtml(text)
        QtWidgets.QApplication.processEvents()


    def clear_status(self):
        '''
        Clear text in status module in GUI.
        Updates/refreshes GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        self.status.clear()
        QtWidgets.QApplication.processEvents()


    def check_ports(self):
        '''
        Print a detailed list of all detected communication ports.
        Uses update_status_callback to update/refresh GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        CheckPorts.check_ports(self.update_status_callback)


    def check_state(self):
        '''
        Change color of QLineEdit border to reflect validator status.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None

        '''
        sender = self.sender()
        state = sender.validator().validate(sender.text(), 0)[0]

        if state == QtGui.QValidator.Acceptable:
            color = '#2bb359'  # A nice green
        elif state == QtGui.QValidator.Intermediate:
            color = '#87b7e3'  # A nice blue
        else:
            color = '#911e2e'  # A nice red

        # Perform the actual color change
        sender.setStyleSheet('QLineEdit { border: 1px solid' + f'{color}' + '; border-radius: 2px; margin-top: 0px;}')


    @staticmethod
    def __version_decryption():
        '''
        Performs decryption of version number.
        A version number is generated and encrypted into a data file when this app is built. Only an app from the same build as the mentioned data file can decrypt the version number.
        This is done so it is immediately apparent if the runtime files are the correct ones for the GUI being run.
        This is primarily relevant if end-users are overwriting old versions of individual files of the application on their system with files from new versions.

        Possible version values:
        00000001: The application .exe file is not located. This would be because a standalone GUI was run via direct command (expected), or post-compile directory structure was lost
        00000000: The application .exe file exists, but the encrypted version.dat file is missing, was not successfully decrypted, or there was an error reading it
        YYYYMMDD: The application is running normally

        Parameters
        ----------
        N/A

        Returns
        -------
        String object containing appropriate version number

        '''
        # If standalone GUI run via command
        if not Path('RemoteControl.exe').is_file():
            return '00000001'

        # Grab encrypted version number from version.dat (try to)
        try:
            with open ('version.dat', 'rb') as myfile:
                version_encrypted = myfile.read()

            # Decryption. See make_version.py in scripts\helpers for fuller explanation comments
            exe_remote_control = 'RemoteControl.exe'

            # Generate 32-bit byte-type from CONTENTS of .exe file
            key = hashlib.blake2s(open(exe_remote_control, 'rb').read(), digest_size=32).digest()

            # Encodes to base64
            key_64 = base64.urlsafe_b64encode(key)

            # Actual decryption, is being fed appropriately structured objects
            version_decrypted = Fernet(key_64).decrypt(version_encrypted).decode()
            return version_decrypted

        except:
            # .exe exists, version.dat missing/not successfully decrypted/error reading
            return '00000000'


    @staticmethod
    def exception_catcher(exception, description, trace):
        '''
        Prints exception output with customized formatting.
        Replaces default exception cathcher with "sys.excepthook = ApplicationUi.exception_catcher".

        Parameters
        ----------
        exception (exception class (Ags: "type")): Automatically passed in by system
        description (exception instance (Args: "value")): Automatically passed in by system
        trace (traceback object (Args: "traceback")): Automatically passed in by system. Not used

        Returns
        -------
        None

        '''
        # Design format of "custom" exception statement
        traceback_str = ''
        traceback_str += f'{description}: {type(exception).__name__} due to "{exception}"\n'
        tb_curr = description.__traceback__
        while tb_curr is not None:
            traceback_str += f'    File "{tb_curr.tb_frame.f_code.co_filename}", line {tb_curr.tb_lineno} in {tb_curr.tb_frame.f_code.co_name}\n'
            tb_curr = tb_curr.tb_next

        # Print and space traceback away for readability
        print(f'\n{traceback_str}\n\n')


    @staticmethod
    def dark_palette():
        '''
        General components and component attributes color scheme configuration.

        Parameters
        ----------
        N/A

        Returns
        -------
        PyQt5.QtGui.QPalette object

        '''
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window,          QtGui.QColor(43,   43,  48))  # Main dialog background color - deep gray-blue
        dark_palette.setColor(QtGui.QPalette.Button,          QtGui.QColor(43,   43,  48))  # Button background color  - deep gray-blue - set to match main dialog background color
        dark_palette.setColor(QtGui.QPalette.Base,            QtGui.QColor(25,   25,  25))  # Background color of radio buttons, text fields, checkbox, etc. - Dark gray
        dark_palette.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(212, 212, 212))  # Generic widget text - button text, check box text, label text - off-white
        dark_palette.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(212, 212, 212))  # Button text - off-white - match to generic widget text
        dark_palette.setColor(QtGui.QPalette.Text,            QtGui.QColor(215, 215, 215))  # Special widget text - group box titles, text field default text, user-input text - bright off-white
        dark_palette.setColor(QtGui.QPalette.Highlight,       QtGui.QColor(135, 183, 227))  # Text highlighting, and widget focus highlights
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(215, 215, 215))  # Color of text while highlighted - Same as Special widget text, or adjusted to be legible under chosen text highlighting color
        return dark_palette


    def click_go(self):
        '''
        Make clicking the 'Go!' button execute the primary functionality.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        A Boolean value of True is returned if failure occurs at a known potential failure point.
        The Boolean value of True is generated by a simple "return", or when an associated popup error dialog is exited.
        Returns "None", otherwise.

        '''
        # Check for user-defined GUI settings
        # Check for empty user input
        if self.always_clear.isChecked():
            self.clear_status()

        if self.com_port.text() == '':
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No COM Port value specified!<br>' + '</p>')
            return

        com_port = 'COM' + self.com_port.text()

        if self.radio_button_voltage.isChecked():
            thing_to_change = 'VOLT'

        elif self.radio_button_current.isChecked():
            thing_to_change = 'CURR'

        else:
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No Function selection made!<br>' + '</p>')
            return

        if self.set_value.text() == '':
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No set value specified!<br>' + '</p>')
            return

        # Handle leftovers from REGEX restrictions
        # Intentionally do nothing for lone decimal. Does not pass validator, but still enterable
        if self.set_value.text() == '.':
            return

        # Instrument limits
        if thing_to_change == 'VOLT' and  not 60.600 >= float(self.set_value.text()) >= 0:
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Set voltage value not within instrument limits: 60.600 > V > 0<br>' + '</p>')
            return

        if thing_to_change == 'CURR' and  not 4.040 >= float(self.set_value.text()) >= 0.015:
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Set current value not within instrument limits: 4.040 > I > 0.015<br>' + '</p>')
            return

        value = self.set_value.text()

        # Proceed with operations
        self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + '+++++++++++++++++++++++++++++<br>+++ JACKING INTO CENTRAL COMMAND +++<br>+++++++++++++++++++++++++++++<br><br>' + '</p>')
        start_time = datetime.now()

        # Feeds required methods/components through as parameters to avoid importing the entry module, which also avoids circular import hurdles
        remote_control = RemoteControl.remote_control(self.update_status_callback, com_port, thing_to_change, value)
        if remote_control is True:
            self.update_status_callback('<p style="font-size:11px; color:#D60000;">' + '<br>Error encountered. Resetting application.<br><br><br><br><br><br>' + '</p>')
            return

        self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br><br>+++++++++++++++++<br>+++ TASK COMPLETE +++<br>+++++++++++++++++<br><br>Time taken: {datetime.now() - start_time}<br><br><br><br><br><br>' + '</p>')


# Initialize the GUI
if __name__ == '__main__':
    # Create an instance of QApplication
    application = QtWidgets.QApplication(sys.argv)
    application.setStyle('Fusion')
    application.setPalette(ApplicationUi.dark_palette())

    # Setting icon here applies to all windows (as opposed to setting within each window's code)
    application.setWindowIcon(QtGui.QIcon('remote_control.ico'))

    # Override built-in exception handler and print function
    # Connect custom ApplicationUi.exception_catcher function to built-in exception handler
    sys.excepthook = ApplicationUi.exception_catcher

    # Show the application's GUI
    view = ApplicationUi()
    view.resize(1151, 635)
    view.show()

    # Execute the application's main loop
    sys.exit(application.exec())
