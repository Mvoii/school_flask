#!/usr/bin/bash

# Create project structure
#mkdir contact-app
#cd contact-app
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate.bat  # Windows

# Install required packages
pip install flask pymongo flask-login flask-mail python-dotemail
