import os
import json
import sys
import time
from enum import Enum

CONFIG_PATH = ".config.json"
CONFIG = {}
FILE_INDEX = {}



def check_config():
  try:
    with open(CONFIG_PATH, 'r') as infile:
      global CONFIG
      CONFIG = json.load(infile)
  except EnvironmentError:
    ans = input('.config.json not found. Create default .config.json? (Y/N)')
    if ans.lower() == 'y':
      init_config()
      print('Created .config.json')
    else:
      print('Exiting...')
      sys.exit(0)



def init_config():
  default_config = {
    "CONTENTS_DIR": "contents/",
    "METADATA_DIR": "metadata/",
    "FILE_INDEX": "FILE_INDEX.json",
    "OUTPUT_DIR": "output/",
    "PAGE_DIR": "page/",
    "TEMPLATE_DIR": "templates/",
    "POST_PATH": "post.html",
    "INDEX_PATH": "index.html",
    "PAGE_PATH": "page.html",
    "LAST_UPDATED": 0
  }
  with open(".config.json", 'w') as outfile:
    json.dump(default_config, outfile, indent=4)



# Clear out the output directory and rebuild the files
def rebuild_templates():
  # Rebuild posts
  if (int(os.path.getmtime(CONFIG['TEMPLATE_DIR'] + CONFIG["POST_PATH"])) > CONFIG["LAST_UPDATED"]):
    for post in os.listdir(CONFIG['OUTPUT_DIR']):
        file_path = os.path.join(CONFIG['OUTPUT_DIR'], post)
        if post != 'index.html':
          os.remove(file_path)
    # parse all posts in content
  # Rebuild index
  if (int(os.path.getmtime(CONFIG['TEMPLATE_DIR'] + CONFIG["INDEX_PATH"])) > CONFIG["LAST_UPDATED"]):
    os.remove(os.path.join(CONFIG['OUTPUT_DIR'], post), 'index.html')
    # rebuild index
  #Rebuild pages
  if (int(os.path.getmtime(CONFIG['TEMPLATE_DIR'] + CONFIG["PAGE_PATH"])) > CONFIG["LAST_UPDATED"]):
    page_dir = os.path.join(CONFIG['OUTPUT_DIR'], CONFIG['PAGE_DIR'])
    for post in os.listdir(page_dir):
        file_path = os.path.join(page_dir, post)
        os.remove(file_path)



def parse_posts(directory, parse_all=False):
  with open(CONFIG['METADATA_DIR'] + CONFIG['FILE_INDEX'], 'r') as infile:
    global FILE_INDEX
    FILE_INDEX = json.load(infile)
  for post in os.listdir(directory):
    file_path = os.path.join(directory, post)
    file_update = int(os.path.getmtime(file_path))

    # Skip subdirectories:
    if os.path.isdir(file_path):
        continue
    
    if (parse_all or file_update > CONFIG["LAST_UPDATED"]):
      with open(file_path, 'r+') as f:
        pass


def build_site():
  pass
  


if __name__ == '__main__':
  check_config()