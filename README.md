# Program-Utilities-Linux

Description
This is a simple python script program that makes a backup of your directory. It could be your home folder, web folder etc.
The script uses the in-built python which is in the Python standard library. I tested it on python 3.11 but it should work just fine on both Python 2.7 and Python 3.7 

Requirements
- python zipfile module

Usage
run it as: 
./backup.py
or 
python backup.py

Problem While Running it;
This is due to file running on either Windows or Linux platform.
Convert the script using dos2unix.

Install it by running

sudo apt install dos2unix

After that, you can convert files in either direction using one of the commands

dos2unix /PATH/TO/YOUR/WINDOWS_FILE
unix2dos /PATH/TO/YOUR/LINUX_FILE
Example:

$ dos2unix backup.py
or 
$ unix2dos backup.py
