# Functions to generate ID card and QR Code images

import io
from tempfile import NamedTemporaryFile
from shutil import copyfileobj

# Import QRCode from pyqrcode 
import qrcode 
from PIL import Image, ImageDraw, ImageFilter, ImageFont 
import os.path
from im_pass import app  #From this package. app is created in __init__

MAX_PROF_PIC_SIZE = (160,160)
# Creating copy of lab report to be sent for approval
def generate_temp_report(current_user):
    im_stream = current_user.reports[-1].lab_report.get()
    tempFileObj = NamedTemporaryFile(mode='w+b',suffix='pdf')
    tempFileObj.write(im_stream.read())
    tempFileObj.seek(0,0)
    return tempFileObj

# Using PIL as built in Mongoengine size parameter does not keep the aspect ration.
# This also  helps to do other types of image optimizations in future if original size is to be kept
def optimize_image(pf):
    if (pf):
        photo = Image.open(pf)
        photo.thumbnail(MAX_PROF_PIC_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio.; May be store small file itself in database once size is standardized

def generate_idcard(current_user,auth_url):
    rep_type = current_user.reports[-1].lab_report_type

    # Keeping separate templates for Covid Test Pass and Immunity Passport
    if rep_type == "Covid- Real Time PCR":
        card = Image.open(os.path.join(app.config['APP_STATIC'], 'Covid Pass.png'))
        title = "Covid- Real Time PCR"
    elif rep_type == "Antibody Test":
        title = "Tested for Antibody"
        card = Image.open(os.path.join(app.config['APP_STATIC'], 'Immunity Passport.png'))
    elif rep_type == "Vaccination":
        title = "Vaccination Done"
        card = Image.open(os.path.join(app.config['APP_STATIC'], 'Immunity Passport.png'))
    else:
        title="Unknown"  #should not come here
        card = Image.open(os.path.join(app.config['APP_STATIC'], 'Covid Pass.png'))
       


    cardx, cardy = card.size

    im_stream = current_user.picture.get()
    photo = Image.open(im_stream)


    photo.thumbnail(MAX_PROF_PIC_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio.; May be store small file itself in database once size is standardized
    photox, photoy = photo.size

    qrcode = generate_auth_qrcode(current_user,auth_url)
    qrx, qry = qrcode.size

    stamp = Image.open(os.path.join(app.config['APP_STATIC'], 'IssuingAuthority.png'))
    stamp.thumbnail(MAX_PROF_PIC_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio. 
    stampx, stampy = stamp.size

    card.paste(qrcode, ((cardx//2 - qrx//2), (cardy//2 - qry//2)-50))
    card.paste(photo, (cardx - photox - 30, cardy - photoy - 30))
    card.paste(stamp, (cardx - stampx - 30, 30))

    d = ImageDraw.Draw(card)
    font = ImageFont.truetype("FreeMono.ttf",20)
    d.text((30,cardy-75), current_user.name, fill=(0,0,0), font=font)  #Need to strp after certain length ?

    rep = current_user.reports[-1]
    datestr = str(rep.lab_date)
    d.text((30,cardy-50), datestr, fill=(0,0,0), font=font)

    font = ImageFont.truetype("FreeMono.ttf",25)
    d.text((30,cardy-150), title, fill=(0,0,0), font=font)

    tempFileObj = NamedTemporaryFile(mode='w+b',suffix='png')
    card.save(tempFileObj, "PNG")
    tempFileObj.seek(0,0)
    return tempFileObj



def generate_auth_qrcode(current_user,auth_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(auth_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


