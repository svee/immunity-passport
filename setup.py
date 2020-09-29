
from setuptools import setup, find_packages

setup(
    name='impassport',
    version='1.0',
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    packages=['im_pass'],
    install_requires=[ 
        'flask',
        'flask_login',
        'wtforms',
        'flask_wtf',
        'flask_mongoengine',
        'Pillow',
        'email_validator',
        'qrcode',
        'cryptography'
    ]

)


