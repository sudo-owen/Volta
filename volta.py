import os
import json
import time
from datetime import datetime
from jinja2 import Environment, PackageLoader
from markdown2 import markdown

POSTS = {}
LAST_MODIFIED = 0

# Check the last time the script was run
# Update the metadata for time
with open('METADATA.json', 'r+') as f:
	data = json.load(f)
	LAST_MODIFIED = data['last-modified']
	data['last-modified'] = int(time.time())
	f.seek(0)
	json.dump(data, f)
	f.truncate()
	f.close()


# Go through all posts on the 'content' directory and parse those who have
# been updated since the last time the script was run
for md_post in os.listdir('content'):
	file_path = os.path.join('content', md_post)
	last_modified_time = os.path.getmtime(file_path)

	if (True): #last_modified_time > LAST_MODIFIED):
		with open(file_path, 'r') as file:
			POSTS[file_path] = markdown(file.read(), extras=['metadata'])
			
			# Automatically set the last modified time
			POSTS[file_path].metadata['date'] = last_modified_time
			POSTS[file_path].metadata['date-string'] = datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')

for k in POSTS.keys():
	print(POSTS[k].metadata)
