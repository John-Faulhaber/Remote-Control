'''
Module to manipulate power supply function.
'''
import serial
from popup_dialogs import PopupDialogs


class RemoteControl():
    '''
    Class containing function to manipulate power supply function.
    '''

    @staticmethod
    def remote_control(update_status_callback, com_port, thing_to_change, value=''):
        '''
        Commandeers specified serial port and sends commands to the connected instrument.

        Parameters
        ----------
        update_status_callback (function object): Defined in run.py, prints fed string to GUI status box + refreshes GUI
        com_port (string): User input text from COM Port text field in GUI
        thing_to_change (string): String based on user selected Function option from GUI, variable value set in run.py
        value (string): User input text from Set Value text field in GUI

        Returns
        -------
        A Boolean value of True is returned if failure occurs at a known potential failure point.
        The Boolean value of True is generated by a simple "return", or when an associated popup error dialog is exited.
        Returns "None", otherwise.

        '''
        # Catch communication exceptions before running
        try:
            # Connect to the BK Precision 9141 power supply
            with serial.Serial(com_port, 9600, timeout=0) as ser:  # closes the port after use
                pass

        except serial.serialutil.SerialException:

            # Print the problem in the GUI status box
            update_status_callback('<p style="font-size:11px; color:#D60000;">' + '<br>&lt;!&gt; ' + '<span style="color:#DADADA">' + f'Could not open "{com_port}". Please check COM ports and try again.' + '</p>')

            # Inform the user of the problem via a popup dialog window to better grab their attention
            error_dialog = PopupDialogs.com_bad_communication(com_port)
            return error_dialog

        update_status_callback('<p style="font-size:11px; color:#DADADA;">' + '[Deploying remote control algorithms]' + '</p>')

        # Commandeer the serial port and send commands
        # General commands from BK Precision 9141 programming manual
        # timeout=3: return immediately when the requested number of bytes are available, otherwise wait three seconds and return all bytes that were received until then.
        # Cannot use timeout=0 if want to use any ser.read...(), no return
        # Do not use any ser.read...() immediately following a command that doesn't return (Ex.: 'VOLT #') - will wait until something returns (never), so waits until timeout to continue
        with serial.Serial(com_port, 9600, timeout=3) as ser:

            # Define the set command
            change_command = f'{thing_to_change} {value}\r'

            # Send the command
            ser.write(change_command.encode())  # Encode to bytes

            # Define the check command
            check_command = f'{thing_to_change}?\r'

            # Send the command and read all bytes of the returned value
            ser.write(check_command.encode())
            value_found = ser.readline().decode()  # Decode from bytes

            # Perform a failsafe check
            if float(value_found) == float(value):
                if thing_to_change == 'VOLT':
                    update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br><br>--> Voltage value changed to {value}' + '</p>')

                else:
                    update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br><br>--> Current value changed to {value}' + '</p>')

            else:  # Failsafe check failed
                update_status_callback('<p style="font-size:11px; color:#D60000;">' + '<br>&lt;!&gt; ' + '<span style="color:#DADADA">' + f'Could not confirm set value! Please check instrument and try again.' + '</p>')

                # Inform the user of the problem via a popup dialog window to better grab their attention
                error_dialog = PopupDialogs.failed_confirmation(thing_to_change, value_found, value)
                return error_dialog