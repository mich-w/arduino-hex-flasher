# arduino-hex-flasher
Python CLI script that allows to flash a binary onto supported Arduino board. It contains a few functions barrowed from [PlatformIO](https://platformio.org/)  scripts as well flashing toolkits which are normally stored within .platformio folder (I'm using VS Code). Right now it supports Arduino UNO and Due boards. Contains toolkits for Linux as well as Windows. The scripts automatically detects the environment its ran on.

This kit can be very useful in scenarios where one needs to privide the binary for the project along with the upload capability without the need of sharing the source code as well having to use the whole IDE in order to compile and upload the binary on site. 

With this tool, one can simply send the binary  along with the script and viola. Python installation is still required on the other end (duh).
## Usage: 
     
     Linux example:
     $ /bin/python due_flasher.py uno /home/<USER>/firmware.hex ttyACM0

     OR

     $ /bin/python due_flasher.py due /home/<USER>/firmware_new.hex /dev/ttyACM1


