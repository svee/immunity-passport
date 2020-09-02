from cryptography.fernet import Fernet
from impass import app

# Encryption key is stored away in directory that is not checked-in
# Key itself is generated once by  key = Fernet.generate_key()
# Format of the key is MSG_ENCRYPTION_KEY=b'Z23ObuhP8ae3AqIaCGXLwwHkeDdP7abBBh-1nrGSvom='
# To keep the flexibility of adding new key in case of known vulnerability, can migrate to 
# Multifernet

key = app.config['MSG_ENCRYPTION_KEY']
fk = Fernet(key)

#Not implemented right now. Since tokens are different, it creates issues with find operations on mongo.
def encrypt_msg(email):
    return fk.encrypt(email.encode('utf8'))

def decrypt_msg(encrypted_message):
    return fk.decrypt(encrypted_message.encode('utf8'))

