# modsinstaller
A little utility I made for myself to automate the installation of mods on a server.

## Installation
You can install the script simply by running this command on os's with curl installed:
```curl -L --output modsinstaller.py https://raw.githubusercontent.com/lochnessdragon/modsinstaller/main/main.py```
> The only required file is main.py. (I'll clean up the repo when I get around to it)

## Usage
This project requires python3.
You should also have the ```colorama```, ```requests``` and ```wget``` modules installed.

### Running the script:
Use: ```python3 modsinstaller.py <modslist.txt>``` to run. (or whatever you've named the py script file) (also whatever python3 is named on your system)

```<modslist.txt>``` is a required argument, this is the list of mods by forge id that you want to install. 
You can also comment out line in that file with "#"

Example:

```
# Install the Create mod and Flywheel
328085 # Create forge id
486392 # Flywheel forge id
```

Some optional args include:
- ```--force``` - The script usually only downloads mods that have not already 
  been installed (i.e. the .jar file named on forge's servers is not found in the local directory. 
- ```--mc-version [VERSION]``` - choose the minecraft version to target when installing mods (i.e. 1.17.1)
- ```--output-folder [FOLDER]``` - choose the folder to install the mods to
- ```--help``` - show the help and exit
