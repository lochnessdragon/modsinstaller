import requests
import json
import time
import wget
import argparse
import re
import os.path
from datetime import datetime

from colorama import init, Fore, Back, Style

api_base="https://api.cfwidget.com/"
curse_cdn_base="https://media.forgecdn.net/files/" #3706/700/create-mc1.18.1_v0.4f.jar

def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

def downloadFile(url):
	filename = url.split('/')[-1]
	print("📝 Downloading: " + filename)
	wget.download(url)

def apiRequest(url):
	for tries in range(0, 5):
		response = requests.get(url)
		if response.status_code == 202:
			print("API is indexing page. Retrying request in 3 seconds.")
			time.sleep(3)
		else:
			return response

def getProject(id, version = ""):
	extras = "" if version == "" else "?version=" + version
	response = apiRequest(api_base + str(id) + extras)
	return response.status_code, response.json()

def getUser(id):
	if isinstance(id, int):
		response = apiRequest(api_base + "author/" + str(id))
	else:
		response = apiRequest(api_base + "author/search/" + id)
	return response.status_code, response.json()

def extractAuthors(mod):
	authorList = []
	for member in mod['members']:
		authorList.append(member['username'])
	
	authors = ', '.join(authorList)
	
	if len(authorList) > 2:
		return rreplace(authors, ',', ', and', 1)
	else:
		return rreplace(authors, ',', ' and', 1)

def getDownloadsMatchingVersions(downloads, versions):
	matchingDownloads = []
	for download in downloads:
		#print(download['versions'])
		matching = True
		
		# see if the download versions includes all of the required versions
		for version in versions:
			if not version in download['versions']:
				matching=False
		if matching:
			matchingDownloads.append(download)
	
	return matchingDownloads

# picks the latest download out of a list of downloads based on a timestamp
def getLatestDownload(downloads):
	latestDownload = downloads[0]
	latestDownloadTime = datetime.strptime(downloads[0]['uploaded_at'], "%Y-%m-%dT%H:%M:%S.%fZ") # get iso date
	for download in downloads:
		potentialDownloadTime = datetime.strptime(download['uploaded_at'], "%Y-%m-%dT%H:%M:%S.%fZ") # get iso date
		
		if potentialDownloadTime > latestDownloadTime:
			latestDownload = download
	return latestDownload

# checks if a mod is installed before downloading it 
def installMod(downloadObj, force):
	if not os.path.exists(downloadObj['name']) or force:
		#print(mod['download'])
		file_id=downloadObj['url'].split('/')[-1]
		#print(file_id, "A:", file_id[0:4], "B:", file_id[4:])

		file_url=curse_cdn_base + str(int(file_id[0:4])) + "/" + str(int(file_id[4:])) + "/" + downloadObj['name']
		print("📂 Using url: " + Fore.MAGENTA + file_url)
		#print(mod['download']['url']+ "/" + mod['download']['name'])
		downloadFile(file_url)
	else:
		print("❗ File: " + Fore.MAGENTA + downloadObj['name'] + Fore.RESET + " already exists! " + Fore.YELLOW + "Skipping!")

if __name__ == '__main__':
	# Initializes Colorama
	init(autoreset=True)

	# parse argument
	parser = argparse.ArgumentParser(description='Downloads a list of mods from curseforge.')
	parser.add_argument('modlist', metavar='inputlist', nargs=1, type=str, help='the file to parse for mod ids. Can contain comments starting with #. Otherwise, should be a list of mod ids (ints), each on a new line')
	parser.add_argument('--mc-version', metavar="version", type=str, default='1.18.1', help='the minecraft version to force the mods to conform to')
	parser.add_argument('--force', action='store_true', help='forces the program to redownload any already detected files')
	parser.add_argument('--output-folder', metavar="folder", help='the output folder to output the mods to', default='./')

	args = parser.parse_args()
	print("Running modinstaller with arguments:")
	print("Input file: " + str(args.modlist))
	print("Force download: " + str(args.force))
	print("MC Target: " + args.mc_version)
	print("Output Folder: " + args.output_folder)

	modlist = []
	with open(args.modlist[0]) as modFileList:
		for line in modFileList.readlines():
			line = re.sub(r'#.*', '', line).strip()
			if(line.isdigit()):
				modlist.append(int(line))

	for modid in modlist:
		print("🔍 Searching for mod: " + Fore.BLUE + str(modid))
		status_code, mod = getProject(modid, version=args.mc_version)
		if status_code == 200:
			print("🟩  Found project: " + Fore.GREEN + mod['title'] + Fore.RESET + " by " + Fore.LIGHTYELLOW_EX + extractAuthors(mod))
		else:
			print("❌ Could not find mod: " + str(modid) + " Error: " + str(status_code) + " Skipping!")
			continue
                
		# now that we have the mod, we need to check the mc version and download the file
                
		# first check the minecraft version and forge version of the download key 
		if(args.mc_version in mod['download']['versions'] and "Forge" in mod['download']['versions']):
			# we can safely download the mod if it doesn't exist already
			installMod(mod['download'], args.force)
		else:
			print("The API didn't return the proper download file, so now we are searching for it!")
			# if that doesn't exist, check the mc version and forge version of all the downloads
			downloads = getDownloadsMatchingVersions(mod['files'], [args.mc_version, "Forge"])
			if len(downloads) > 0:
				latestDownload = getLatestDownload(downloads) # gets the latest download from a list of downloads
				# download files
				installMod(latestDownload, args.force)
			else:
				print("❌" + Fore.RED + mod['title'] + " does not have a version for minecraft " + args.mc_version)
				print(json.dumps(mod["files"], indent=4))
				continue
