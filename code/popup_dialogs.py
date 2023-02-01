'''
Module to handle exception-catch pop-up dialog boxes.
'''
from PyQt5.QtWidgets import QMessageBox


class PopupDialogs():
    '''
    Class containing functions to handle exception-catch pop-up dialog boxes.
    '''

    # Design exception-catch pop-up dialog boxes
    # Purpose of each is listed within each
    @staticmethod
    def com_bad_communication(com_port):
        '''
        Receives string values in each COM Port # text field in GUI, and notifies user of communication error by means of a pop-up dialog box.

        Parameters
        ----------
        com_port (string): User input text from left COM Port text field in GUI

        Returns
        -------
        A Boolean value of True is returned when the dialog box is exited.

        '''
        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Warning)
        pop_up.setWindowTitle('Bad COM Communication!')
        pop_up.setText('<p style="font-size:11px;">' + f'Could not open "{com_port}".<br><br>Please check COM ports and try again.' + '</p>')
        pop_up.setStandardButtons(QMessageBox.Ok)

        return pop_up.exec() == QMessageBox.Ok


    @staticmethod
    def failed_confirmation(thing_to_change, value_found, value):
        '''
        Receives string values in each COM Port # text field in GUI, and notifies user of communication error by means of a pop-up dialog box.

        Parameters
        ----------
        thing_to_change (string): String based on user selected Function option from GUI, variable value set in run.py
        value_found (string): Returned string from VOLT? or CURR? command to instrument
        value (string): User input text from Set Value text field in GUI

        Returns
        -------
        A Boolean value of True is returned when the dialog box is exited.

        '''
        if thing_to_change == 'VOLT':
            thing_to_change = 'Voltage'

        else:
            thing_to_change = 'Current'

        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Warning)
        pop_up.setWindowTitle('Confirmation Test Failed!')
        pop_up.setText('<p style="font-size:11px;">' + f'Could not confirm set value!<br><br> Set {thing_to_change} value specified: {float(value)}<br>Set {thing_to_change} value detected post-command: {float(value_found)}<br><br>Please check instrument and try again.' + '</p>')
        pop_up.setStandardButtons(QMessageBox.Ok)

        return pop_up.exec() == QMessageBox.Ok
