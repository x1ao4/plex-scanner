import os
import requests
import configparser
import xml.etree.ElementTree as ET

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the server address and token
plex_server = config.get('server', 'address')
plex_token = config.get('server', 'token')

# Get Running Mode
continuous_mode = config.getboolean('mode', 'continuous_mode')
local_mode = config.getboolean('mode', 'local_mode')

# Check if [directories] exists
if config.has_section('directories'):
    user_directories = {k: v.split(';') for k, v in config.items('directories')}
else:
    user_directories = None

# Get library directories
libraries_value = config.get('libraries', 'libraries').strip()
if libraries_value and not user_directories:
    # Get the directories of the specified libraries
    response = requests.get(f"{plex_server}/library/sections?X-Plex-Token={plex_token}")
    root = ET.fromstring(response.content)
    directories = root.findall('Directory')
    user_libraries = {directory.get('title'): [location.get('path') for location in directory.findall('Location')] for directory in directories if directory.get('title') in libraries_value.split(';')}
elif not user_directories:
    # Get the directories of all libraries
    response = requests.get(f"{plex_server}/library/sections?X-Plex-Token={plex_token}")
    root = ET.fromstring(response.content)
    directories = root.findall('Directory')
    user_libraries = {directory.get('title'): [location.get('path') for location in directory.findall('Location')] for directory in directories}
else:
    user_libraries = {}

# Get candidate directories
if not user_directories:
    candidate_directories = user_libraries
else:
    candidate_directories = user_directories

# Exclude the directories that the user needs to exclude through [exclude_directories]
if config.has_section('exclude_directories'):
    exclude_directories = {k: v.split(';') for k, v in config.items('exclude_directories')}
    final_directories = {}
    for lib, folders in candidate_directories.items():
        if lib in exclude_directories:
            final_directories[lib] = [folder for folder in folders if folder not in exclude_directories[lib]]
        else:
            final_directories[lib] = folders

# Get library IDs
response = requests.get(f"{plex_server}/library/sections?X-Plex-Token={plex_token}")
root = ET.fromstring(response.content)
directories = root.findall('Directory')
library_ids = {directory.get('title'): directory.get('key') for directory in directories if directory.get('title') in final_directories}

def refresh_plex_folder(folder_name):
    # Add two new attributes to track whether it is the first successful or failed scan
    if not hasattr(refresh_plex_folder, "first_success"):
        refresh_plex_folder.first_success = True
    if not hasattr(refresh_plex_folder, "first_failure"):
        refresh_plex_folder.first_failure = True

    # Construct the full folder path and trigger Plex scan
    for library, folder_prefixes in final_directories.items():
        for folder_prefix in folder_prefixes:
            folder_path = os.path.join(folder_prefix, folder_name)

            # When local mode is enabled, check if the folder exists
            if local_mode and not os.path.isdir(folder_path):
                continue

            # Construct the request URL
            library_id = library_ids[library]
            url = f"{plex_server}/library/sections/{library_id}/refresh?path={folder_path}&X-Plex-Token={plex_token}"

            # Send the request
            response = requests.get(url)

            # Check the response status
            if response.status_code == 200:
                # If this is the first successful scan, print a newline
                if refresh_plex_folder.first_success:
                    print()
                    refresh_plex_folder.first_success = False
                print(f"Successfully triggered Plex to scan the folder: {folder_path}")
            else:
                # If this is the first failed scan, print a newline
                if refresh_plex_folder.first_failure:
                    print()
                    refresh_plex_folder.first_failure = False
                print(f"Failed to trigger Plex to scan the folder, status code: {response.status_code}")

while True:
    # User enters the folder name
    folder_names = input("\nPlease enter the folder name(s) you want to scan, separating multiple names with semicolons: ").split(';')

    # Reset first_success and first_failure attributes
    refresh_plex_folder.first_success = True
    refresh_plex_folder.first_failure = True

    # Trigger Plex scan
    for folder_name in folder_names:
        refresh_plex_folder(folder_name.strip())

    # If the continuous mode is off, end the run after the scan is complete
    if not continuous_mode:
        break
