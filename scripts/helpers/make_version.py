import base64, hashlib
from datetime import datetime
from cryptography.fernet import Fernet


# Grabs YYYMMDD date to use as version number, and encodes to bytes
version = datetime.today().strftime('%Y%m%d').encode('utf-8')

# Stores .exe. Path based on directory structure while compiling
exe_remote_control = 'bin\\bin\\RemoteControl\\RemoteControl.exe'

# Generates key from CONTENTS of .exe file, and not just the path itself
# Base64-encoded 32-bit byte-type key is required for Fernet.encrypt - blake2s allows 32-bit specification with byte-type digest
key = hashlib.blake2s(open(exe_remote_control, 'rb').read(), digest_size=32).digest()

# Fernet documentation says .encrypt returns "URL-safe base64-encoded" byte-type object inherently. This line was needed anyway
# Encodes byte-type objects to base64
key_64 = base64.urlsafe_b64encode(key)

# Encrypts version number - requires .exe-key from SAME compile as gui in use to decrypt
# .encrypt()takes byte-type objects - version is generic string, so .encode('utf-8') encodes to bytes
# Fernet key must be "URL-safe" base64-encoded 32-bit object
version_cipher = Fernet(key_64).encrypt(version)  

# Create .dat file containing encrypted version number
with open('version.dat', 'wb') as f:
    f.write(version_cipher)
