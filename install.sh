#!/bin/bash
sudo apt install python3-pip unzip python3-venv
wget "https://github.com/DevMa7e1/SuperSimpleCloud/archive/refs/heads/main.zip"
unzip main.zip -d SuperSimpleCloud
cd SuperSimpleCloud/SuperSimpleCloud-main
python3 -m venv ./ssenv
source ./ssenv/bin/activate
pip install pycryptodome reedsolo flask
python main.py