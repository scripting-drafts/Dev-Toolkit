# Port-Bot

This is an abandoned prototype I kept developing after winning a contest along with a workgroup on a bigger project*. It could build a good source of data for a supervised training of a convolutional neural network in order to classify pictures depending on the current labels. It was tested on OS X 10.10.5. 

Run it from its folder by typing "python3.7 start.py" and scan the QR code with a phone. Message him from other phones to initialize it. I added a queue in order to handle multiple users.

The frontend is at 127.0.0.1:8000/items/ and 127.0.0.1:8000/invalid_items/ . Items can be labeled as 'active' or 'solved'. They can also be marked as invalid in order to move them to the invalid_items database, in which all information but the ID is grouped together under a single label 'data'. 

Classes of Whatsapp Web change with time, so the code has to be updated with the proper new classes. More info in the CSS SELECTORS section of port-bot.py

Requirements:
 - Python 3.7
 - Golang 1.12** (OS X 10.10.5)
 - Firefox
 - Geckodriver
 - Drive***
 - Curl
 
Libraries:
 - FastAPI
 - pydantic
 - uvicorn
 - sqlalchemy
 - selenium
 - requests
 - jinja2
 - starlette
  
  
*https://blogs.amb.cat/innoamb/ca/2019/06/05/guanyadors-innobus-2019/  
**https://golang.org/doc/install?download=go1.12.darwin-amd64.pkg  
***https://github.com/odeke-em/drive  
  
  
# TO DO

* Port-bot cleanup
* Embedded Google Maps on the Frontend
* Better HTML/Javascript for a more responsive Active/Resolved functionality
