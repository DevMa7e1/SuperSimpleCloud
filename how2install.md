# How to install Super Simple Cloud
If you are on Linux:

Debian based distro:
1. Download the install.sh file. You can use `wget https://raw.githubusercontent.com/DevMa7e1/SuperSimpleCloud/refs/heads/main/install.sh`
2. Make it executable. Run `chmod +x install.sh`
3. And finally, run the script. You can run `./install.sh`

Any other distros:
1. Git clone the repository using `git clone https://github.com/DevMa7e1/SuperSimpleCloud.git`
2. Install python3, python3-pip, python3-venv (minimum tested & working version is 3.10)
3. In the Super Simple Cloud dir, run `python3 -m venv ./ssenv`
4. Run `source ./ssenv/bin/activate` to activate the venv 
5. Run `python3 -m pip install pycryptodome reedsolo flask`
6. Finally, run the main file using `python3 main.py`

If you are on Windows:
1. Download https://github.com/DevMa7e1/SuperSimpleCloud/archive/refs/heads/main.zip
2. Unzip the archive and go into the created dir
3. Run `pip install pycryptodome reedsolo flask`
4. Run `python main.py`

# How to run Super Simple Cloud
* Debian based distro:

  In the Super Simple Cloud dir, run `./start.sh`

* Any other distros:

  If you haven't, `chmod +x start.sh`. Then, run `./start.sh`

  If that does not work, then run:
1. `source ./ssenv/bin/activate`
2. `python3 main.py`

* Windows:

  Run `python main.py` from the unziped dir.

# How to start using Super Simple Cloud
In a web browser, type http://localhost:12345 and you're done.

To be able to access your cloud from outside your network, you should either port-forward port 12345 of the machine that you are using to run Super Simple Cloud or use a service like Ngrok or NoIP.
