# immunity-passport
Covid19:  System to manage  entry 'PASS' based on test, Vaccination or immunity passport

Very Short Description:

A web application to generate QR code based 'PASS' for a given user. 
Once user submits Covid test report; it gets verified (manual over email from designated approves) and a pass is generated with user details, picture and QR code.

The  venue (say an event, international flight check-in, etc), can scan QR code and ensure that used is indeed carrying valid pass. Based on the report type different expiry periods are defined which are customizable.

Same system can be used to track and screen based on Vaccination whenever that is available.  
Wishful thinking - originally built for managing generation of  immunity passports (if and when such tests are available/approved by WHO). Idea is that the extra constraints like mask can be dropped if such test and clearance are possible.

User Guide:

Access Demo Here : <to be done>


Step -1:  Sign-up, 
Step-2: Activate account through link sent to registered email.  ( email activation process is disabled for demo version)
Step-3: Login 
Step-4: Update Profile 
Step-5: Apply for New Pass  Once approval is done, pass gets mailed to registered e-mail ID. Also one can come back to dashboard and download the same.

Beyond the validity of the Pass one can get the New Pass again with required test/vaccination report.

Note: Demo version is 'mailtrpped' - so your email will not be flooded with any mails from this app.
            Because of internal server and tunneling and mailtrap ; it seems much slower in demo.

Application Scenarios:

Recently, AIR India flights were banned for a week in Dubai following lapse of 'Date' and '72 hour validity period'  check on couple of passengers by check-in staff.  Passengers were carrying lab reports from prior to acceptable period before the flight.  
With this system, validation of test reports can be done offline by a qualified personnel and checkin process just involves scanning a QR code and getting response that it is VALID.

Let us say, soon WHO/Health authority comes-up with conclusive test that clears someone that person had right type /strength of antibody and is not prone to re-infection. But person will still have to wear mask, comply with stringent restrictions imposed for cvoid.
Those personnel can be cleared of restrictions (say wearing mask in public park) so they feel motivated and more free to move around. A big step towards feeling of normalcy.

Even if Vaccine is made available, unless there is big motivation percentage of population might be reluctant to go through it quickly. Even those who have taken will face same issue of walking around with masks and having to prove they have gone through vaccination.
With a system like this, restrictions can be completely lifted for people who have gone through complete course of vaccination as it becomes faster to scan and verify instead of carrying reports everywhere. Lets say large events, concerts can be given green signal to allow those who have gone through vaccination, it might be a good motivation


Technology

- Implemented as Python/Flask/Jinja2  with Mongodb (GridFS for reports and pictures)
- bootstrap is used for styling UI.
- Demo is hosted and tested on Apache2 on Ubuntu 20.04 server inside home network with ngrok web tunnel (ISP would not let incoming connections using DDNS).
- As there are many QR code reader samples for android, client APP is not developed. I am using Trend micro QR code scanner and opening link to ensure application is tested.
- This is intended to be used as a learning tool or as a reference frame-work (github). User interface needs to be polished, extensive testing is needed to make it ready for deployment.
- Currently python unittest framework is used to test it followed by flask built in debug mode server then now it is tested on apache2. 

Motivation:

More than anything it is a learning-python-application project to develop complete system using Flask/Jinja-2.  Wanted to see what it takes to build a simple application from a real life requirement. 

History

Some more information on how the idea started and few other details.
https://www.evernote.com/shard/s589/sh/9baf7a28-115d-4675-c760-b7be30da86cd/afba27a6a6ec291c0fb9135afca6e615
