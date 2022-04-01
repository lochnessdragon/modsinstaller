import requests
import json
import time
import wget
import argparse
import re
import os.path

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

if __name__ == '__main__':
	# Initializes Colorama
	init(autoreset=True)
	
	mc_version = "1.18.1"
	
	modlist = []
	with open("modlist.txt", "r") as modfilelist:
		for line in modfilelist.readlines():
			line = re.sub(r'#.*', '', line).strip()
			if(line.isdigit()):
				modlist.append(int(line))

	for modid in modlist:
		print("🔍 Searching for mod: " + Fore.BLUE + str(modid))
		status_code, mod = getProject(modid, version=mc_version)
		if status_code == 200:
			print("🟩  Found project: " + Fore.GREEN + mod['title'] + Fore.RESET + " by " + Fore.LIGHTYELLOW_EX + extractAuthors(mod))
		else:
			print("❌ Could not find mod: " + str(modid) + " Error: " + str(status_code) + " Skipping!")
			continue
		# now that we have the mod, we need to check the mc version and download the file

		if(mc_version in mod['download']['versions']):
			# we can safely download the mod if it doesn't exist already
			if not os.path.exists(mod['download']['name']):
				#print(mod['download'])
				file_id=mod['download']['url'].split('/')[-1]
				#print(file_id, "A:", file_id[0:4], "B:", file_id[4:])
			
				file_url=curse_cdn_base + file_id[0:4] + "/" + file_id[4:] + "/" + mod['download']['name']
				print("📂 Using url: " + Fore.MAGENTA + file_url)
				#print(mod['download']['url']+ "/" + mod['download']['name'])
				downloadFile(file_url)
			else:
					print("❗ File: " + Fore.MAGENTA + mod['download']['name'] + Fore.RESET + " already exists! " + Fore.YELLOW + "Skipping!")
		else:
			print("❌" + Fore.RED + mod['title'] + " does not have a version for minecraft " + mc_version)
			continue
		
	
	#print(json.dumps(getProject(328085, version=mc_version), indent=4))

	#parser = argparse.ArgumentParser(description="Auto downloader for curseforge mods")