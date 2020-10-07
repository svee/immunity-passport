each "***"
echo  "activate virtual environment first with command like : source ~/deploy/v2/bin/activate"
each "***"
export FLASK_APP=im_pass
export FLASK_ENV=development
flask run -h0.0.0.0
