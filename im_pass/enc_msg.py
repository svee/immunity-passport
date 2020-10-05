from cryptography.fernet import Fernet
from im_pass import app

# We are using three different security schemes
# 1. werkzeug.security -  generate_password_hash, check_password_hash for password encryption/decryption.
# 2. Fernet to encode/decode email ID inside QR code URL on ID card.
# 3. itsdangerous - URLSafeTimedSerializer for encoding email activation, password reset and report approval links

# Encryption key is stored away in directory that is not checked-in
# Key itself is generated once by  key = Fernet.generate_key()
# Format of the key is MSG_ENCRYPTION_KEY=b'Z23ObuhP8ae3AqIaCGXLwwHkeDdP7abBBh-1nrGSvom='
# To keep the flexibility of adding new key in case of known vulnerability, can migrate to 
# Multifernet

key = app.config['MSG_ENCRYPTION_KEY']

#Not implemented right now. Since tokens are different, it creates issues with find operations on mongo.
def encrypt_msg(email):
    fk = Fernet(key)
    return fk.encrypt(email.encode('utf8'))

def decrypt_msg(encrypted_message):
    fk = Fernet(key)
    return fk.decrypt(encrypted_message.encode('utf8'))


#Now we use itsdangerous for generating  secret key used for email activation, reset and approval

from itsdangerous import URLSafeTimedSerializer


def gen_secret_key(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt="activate")


def confirm_secret_key(token, expiration=None):   #Note that email activation link never expires; can change to shorter value.
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
