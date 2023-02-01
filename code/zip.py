'''
Module to handle .zip file creation for compiling.
'''
# Create a zip file titled "RemoteControl", from the contents within the "temp_zip" directory
import shutil


shutil.make_archive('RemoteControl', 'zip', 'temp_zip')
