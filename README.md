A small script for automatic entering of login data and some other settings after the sector update :)

**What can this script do?**
* Enter VATSIM login data (Real Name, CID, Password, Rating)
* Enter Hoppie code into every `TopSkyCPDLChoppieCode.txt`
* Enter CID for VCCS, as well as VCCS Playback/Capture Devices and G2G PTT (For the time being all the configuration values for VCCS must be copied from already configured Euroscope Profile)
* Change the size of fonts in symbology and list settings


**How to run:**

Please backup your Sectorfile folder before runnung the script. You'll need Python 3.12 or newer. In `config.ini` file you have to enter your login data. If you don't want to enter a particular data (for example Password), you can leave the field empty.

After you configured `config.ini` run `run.bat`. You can set Default Path to your EuroScope Profiles by opening the `run.bat` in text editor.

Alternatively you can run script manually in PowerShell:

```
cd "<Path where the config.ini is located>"
py "<Path where the config.ini is located>\es-update\__main__.py" "<Path to Euroscope Profiles>"
```
