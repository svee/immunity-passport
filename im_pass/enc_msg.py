from cryptography.fernet import Fernet
from im_pass import app

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


#Now we use itsdangerous for generating email activation key.

from itsdangerous import URLSafeTimedSerializer


def gen_activation_key(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt="activate")


def confirm_activation_key(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt="activate",
            max_age=expiration
        )
    except:
        return False
    return email
