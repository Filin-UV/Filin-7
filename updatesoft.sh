#!/bin/bash
echo "Updating software......"

echo "Renaming old files......"
sudo mv /home/pi/Filin7-RPi/config.ini /home/pi/Filin7-RPi/config-old.ini
sudo mv /home/pi/Filin7-RPi/localisation.py /home/pi/Filin7-RPi/localisation-old.py
sudo mv /home/pi/Filin7-RPi/maintk2.py /home/pi/Filin7-RPi/maintk2-old.py
sudo mv /home/pi/Filin7-RPi/README.md /home/pi/Filin7-RPi/README-old.md

echo "Downloading......"
sudo wget https://github.com/Filin-UV/Filin-7/raw/main/config.ini
sudo wget https://github.com/Filin-UV/Filin-7/raw/main/localisation.py
sudo wget https://github.com/Filin-UV/Filin-7/raw/main/maintk2.py
sudo wget https://github.com/Filin-UV/Filin-7/raw/main/README.md

echo "Cheking packets..."
if test -f "/home/pi/Filin7-RPi/config.ini";
then
sudo rm /home/pi/Filin7-RPi/config-old.ini
else
zenity --error --text="Error config.ini is not exist. Check Ethernet connection" --title="Warning!" --width=200 --height=100 --timeout=1
sudo mv /home/pi/Filin7-RPi/config-old.ini /home/pi/Filin7-RPi/config.ini
fi

if test -f "/home/pi/Filin7-RPi/localisation.py";
then
sudo rm /home/pi/Filin7-RPi/localisation-old.py
else
zenity --error --text="Error localisation.py is not exist. Check Ethernet connection" --title="Warning!" --width=200 --height=100 --timeout=1
sudo mv /home/pi/Filin7-RPi/localisation-old.py /home/pi/Filin7-RPi/localisation.py
fi

if test -f "/home/pi/Filin7-RPi/maintk2.py";
then
sudo rm /home/pi/Filin7-RPi/maintk2-old.py
else
zenity --error --text="Error maintk2.py is not exist. Check Ethernet connection" --title="Warning!" --width=200 --height=100 --timeout=1
sudo mv /home/pi/Filin7-RPi/maintk2-old.py /home/pi/Filin7-RPi/maintk2.py
fi

if test -f "/home/pi/Filin7-RPi/README.md";
then
sudo rm /home/pi/Filin7-RPi/README-old.md
else
zenity --error --text="Error README.md is not exist. Check Ethernet connection" --title="Warning!" --width=200 --height=100 --timeout=1
sudo mv /home/pi/Filin7-RPi/README-old.md /home/pi/Filin7-RPi/README.md
fi

echo "Rebooting......"






