#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:32:20 2020

@author: vee
"""
from  pymongo import MongoClient
from flask import Flask, render_template, redirect, url_for, request
from flask import jsonify

import bcrypt

app = Flask(__name__)

lab_rec = {
		"labname":"",
		"city":"",
		"country":"",
		"test_date":"" #We go on appending so latest date is at the end
		}

user_rec = {
	"_id":"",
	"hash":"",
	"name":"",
	"dob":"",
	"email":"",
	"ckey": 0, #Form a single directional key out of name, dob and email
	"photo":"",
	"lab":""
	}

def gen_qr (ckey):
	return ckey  #Later we generate QR code here

def print_rec(im_coll, uname, passwd):
	for rec in im_coll.find({"_id":uname}):
			if bcrypt.checkpw(passwd.encode('utf8'), rec['hash']):
				return (gen_qr(rec["ckey"]))
				
def add_user(im_coll, uname, passwd):
		ur = user_rec  #Store personal data encrypted; ckey has hash generated from name+dob+email
		
		salt = bcrypt.gensalt()
		ur['_id'] = uname
		ur['hash'] = bcrypt.hashpw(passwd.encode('utf8'), salt)
		str = uname+"dob"+ "email" #need to refer later to actual values
		ur['ckey'] =  bcrypt.hashpw(str.encode('utf8'), salt) 
		im_coll.insert_one(ur)
		
def is_user_present(im_coll, uname, passwd):	
	for rec in im_coll.find({"_id":uname}):
			if bcrypt.checkpw(passwd.encode('utf8'), rec['hash']):
				return True
	return False		
				
		
#cryptic key is put as data in QR Code to find the record easily		
def validate_pholder(im_coll, qr_hash):
	if im_coll.find(["ckey", qr_hash]):
		return True
	else:
		return False
def connect_to_db():
	try: 
		client = MongoClient("mongodb://localhost:27017/")
	except Exception as e:   
		return jsonify({'Could not connect to MongoDB': e.message}), 500
	
	    
	im_base = client.db_impass
	im_table =im_base['ImmunityPassport'] 
	im_coll = im_table["PassHolders"]
	return im_coll
	

@app.route('/register', methods=['POST', 'GET'])
def register_user():
	error = None
	
	if request.method == 'POST': 
		uname = request.form['username']
		passwd = request.form['password']
		
		im_coll = connect_to_db()
	
		if im_coll.find({"_id":uname}).count():
			return jsonify({'message': 'User name already exists; Try Login'}), 500

		add_user(im_coll, uname, passwd)
		return redirect(url_for('register_user'))
	return render_template('login.html', error=error)		   
		


@app.route('/getqr', methods=['GET','POST'])
def get_qr():
	error = None
	if request.method == 'POST': 
		username = request.form['username']
		password = request.form['password']
		
		im_coll = connect_to_db()
	    
		if print_rec(im_coll, username, password):   
			return jsonify({'message': 'Password is correct'})  # You'll want to return a token that verifies the user in the future
		return jsonify({'error': 'User or password are incorrect'}), 401
	return render_template('getqr.html', error=error)		   


if __name__ == '__main__':
    app.run(debug=True)