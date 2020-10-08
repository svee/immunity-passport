#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @author: vee
#
# Datetime related helper functions

from datetime import datetime, timedelta
from im_pass import app  #From this package. app is created in __init__

def is_date_later_than_today(input_date):
    today = datetime.today().date()
    if (input_date > today):
        return True
    return False

# Checks if the lab report in hand has expired
def check_if_expired(rep_type, rep_date):
    today = datetime.today().date()
    expired=False
    if rep_type == "Covid- Real Time PCR":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['CovidTest']) < today):
                expired = True;
    elif rep_type == "Antibody Test":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['AntibodyTest']) < today):
                expired = True;
    elif rep_type == "Vaccination":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['Vaccination']) < today):
                expired = True;
    else:
        expired = True # Error we don't understand this type of test.
    return expired

