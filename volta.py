import os
import json
import sys
import time
import re
from urllib.parse import quote
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from markdown2 import markdown



MAX_SUMMARY_LEN = 150
CONFIG_PATH = ".config.json"
CONFIG = {}



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



def extract_text(text):
    _meta_data_newline = re.compile("^\n", re.MULTILINE)
    _meta_data_pattern = re.compile(r'^(?:---[\ \t]*\n)?(.*:\s+>\n\s+[\S\s]+?)(?=\n\w+\s*:\s*\w+\n|\Z)|([\S\w]+\s*:(?! >)[ \t]*.*\n?)(?:---[\ \t]*\n)?', re.MULTILINE)
    metadata_split = re.split(_meta_data_newline, text, maxsplit=1)
    metadata_content = metadata_split[0]
    match = re.findall(_meta_data_pattern, metadata_content)
    if not match:
        return text
    tail = metadata_split[1]
    return tail



def get_file_index():
  FILE_INDEX_PATH = CONFIG['METADATA_DIR'] + CONFIG['FILE_INDEX']
  try:
    with open(FILE_INDEX_PATH, 'r') as infile:
      FILE_INDEX = json.load(infile)
      return FILE_INDEX
  except EnvironmentError:
    ans = input(FILE_INDEX_PATH + ' not found. Create new file index? (Y/N)')
    if ans.lower() == 'y':
      new_index = {}
      with open(FILE_INDEX_PATH, 'w') as outfile:
        json.dump(new_index, outfile, indent=4)
      print('Created ' + FILE_INDEX_PATH)
    else:
      print('Exiting...')
      sys.exit(0)



def parse_posts(input_dir, output_dir, template_path, parse_all=False):
  FILE_INDEX = get_file_index()
  for post in os.listdir(input_dir):
    file_path = os.path.join(input_dir, post)
    file_update = int(os.path.getmtime(file_path))

    # Skip subdirectories:
    if os.path.isdir(file_path):
        continue

    if (parse_all or file_update > CONFIG["LAST_UPDATED"]):

      # TODO: Remove the old HTML file if it exists:

      with open(file_path, 'r+') as f:
        p = f.read()
        post_body = extract_text(p)
        parsed_file = markdown(p, extras=['metadata'])
        post_metadata = {
          'title': None,
          'anchor': None,
          'summary': None,
          'word_count': None,
          'date': datetime.fromtimestamp(
          file_update).strftime('%Y-%m-%d %H:%M'),
          'last-updated': file_update
        }

        # Add post attributes
        try:
          post_metadata['title'] = parsed_file.metadata['title']
        except KeyError:
          post_metadata['title'] = quote(post.replace(' ', '-'))

        try:
          post_metadata['anchor'] = parsed_file.metadata['anchor']
        except KeyError:
          post_metadata['anchor'] = quote(post.replace(' ', '-'))

        try:
          post_metadata['summary'] = parsed_file.metadata['summary']
        except KeyError:
          post_metadata['summary'] = post_body[0:MAX_SUMMARY_LEN] + '...'
        
        post_metadata['word_count'] = len(post_body.split(' '))
        
        post_id = str(os.stat(file_path).st_ino) + str(os.stat(file_path).st_dev)
        
        # Add to FILE_INDEX (either overwriting or adding a new entry)
        FILE_INDEX[post_id] = post_metadata
        data = post_metadata.copy()
        data['content'] = parsed_file
        html_path = output_dir + data['anchor'] + '.html'

        # Create HTML file
        render_HTML(html_path, template_path, data)
        print("Updated: ", data['title'])
  
  # Save updated FILE_INDEX
  with open(CONFIG['METADATA_DIR'] + CONFIG['FILE_INDEX'], 'w') as outfile:
    json.dump(FILE_INDEX, outfile, indent=4)



# TODO: sort by last-updated?
def parse_index(output_dir, template_path):
  FILE_INDEX = get_file_index()
  output_path = os.path.join(output_dir, 'index.html')
  render_HTML(output_path, FILE_INDEX, template_path)
  print('Updated index.html')



def render_HTML(output_path, data, template_path):
  env = Environment(loader=FileSystemLoader(CONFIG['TEMPLATE_DIR'])) 
  post_html = env.get_template(template_path).render(post = data)
  with open(output_path, 'w') as outfile:
    outfile.write(post_html)


def update_posts():
  # Check if post template has been updated
  post_template_path = os.path.join(CONFIG['TEMPLATE_DIR'], CONFIG['POST_PATH'])
  if int(os.path.getmtime(post_template_path)) > CONFIG["LAST_UPDATED"]:
    for post in os.listdir(CONFIG['OUTPUT_DIR']):
        file_path = os.path.join(CONFIG['OUTPUT_DIR'], post)
        # Skip subdirectories:
        if os.path.isdir(file_path):
          continue
        if post != 'index.html':
          os.remove(file_path)
    parse_all = True
  else:
    parse_all = False
  # Rebuild either all posts or some posts
  parse_posts(CONFIG['CONTENTS_DIR'], CONFIG['OUTPUT_DIR'], post_template_path, parse_all=parse_all)



def update_index():
  # Check if index template has been updated
  index_template_path = os.path.join(CONFIG['TEMPLATE_DIR'], CONFIG["INDEX_PATH"])
  if int(os.path.getmtime(index_template_path)) > CONFIG["LAST_UPDATED"]:
    os.remove(os.path.join(CONFIG['OUTPUT_DIR'], 'index.html'))
    parse_index(CONFIG['OUTPUT_DIR'], index_template_path)



def update_pages():
  # Check if page template has been updated
  page_template_path = os.path.join(CONFIG['TEMPLATE_DIR'], CONFIG["PAGE_PATH"])
  page_output_path = os.path.join(CONFIG['OUTPUT_DIR'], CONFIG['PAGE_DIR'])
  if int(os.path.getmtime(page_template_path)) > CONFIG["LAST_UPDATED"]:
    for post in os.listdir(page_output_path):
        file_path = os.path.join(page_output_path, post)
        # Skip subdirectories:
        if os.path.isdir(file_path):
          continue
        os.remove(file_path)
    parse_all = True
  else:
    parse_all = False
  page_contents_path = os.path.join(CONFIG['CONTENTS_DIR'], CONFIG['PAGE_DIR'])
  # Rebuild either all pages or some pages
  parse_posts(page_contents_path, page_output_path, page_template_path, parse_all=parse_all)



def update_time():
  CONFIG['LAST_UPDATED'] = time.time()
  with open(CONFIG_PATH, 'w') as infile:
      json.dump(CONFIG, infile, indent=4)



if __name__ == '__main__':
  check_config()
  update_posts()
  update_index()
  update_pages()
  update_time()