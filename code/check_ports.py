'''
Module to interface with computer COM ports.
'''
from serial.tools import list_ports


class CheckPorts():
    '''
    Class containing a function to interface with computer COM ports.
    '''

    @staticmethod
    def check_ports(update_status_callback):
        '''
        Print a detailed list of all detected communication ports.
        Uses update_status_callback to update/refresh GUI.

        Parameters
        ----------
        update_status_callback (function object): Defined in run.py, prints fed string to GUI status box + refreshes GUI

        Returns
        -------
        None

        '''
        update_status_callback('<p style="font-size:12px; color:#DADADA; font-weight: bold;">' + f'<br>Port List<br>{"-"*110}' + '</p>')

        # Returns a list containing serial.tools.list_ports.ListPortInfo objects - see which are being referenced below
        ports = list_ports.comports()
        for port in ports:
            update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br>{port.device}<br>\002\002\002\002\002Description: {port.description}<br>\002\002\002\002\002Hardware identification: {port.hwid}<br>\002\002\002\002\002Vendor ID: {port.vid}<br>\002\002\002\002\002Product ID: {port.pid}<br>\002\002\002\002\002Serial number: {port.serial_number}<br>\002\002\002\002\002Location: {port.location}<br>\002\002\002\002\002Manufacturer: {port.manufacturer}<br>\002\002\002\002\002Product: {port.product}<br>\002\002\002\002\002Interface: {port.interface}' + '</p>')
        update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br>{len(ports)} ports found' + '</p>')
        update_status_callback('<p style="font-size:12px; color:#DADADA; font-weight: bold;">' + f'<br>{"-"*110}<br><br>' + '</p>')
