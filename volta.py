import os
import json
import time
from datetime import datetime
from jinja2 import Environment, PackageLoader
from markdown2 import markdown

# JSON of all blog posts
POSTS = {}

# Go through all posts and populate POSTS.
for md_post in os.listdir('content'):
	file_path = os.path.join('content', md_post)

	# Grab the date last modified.
	time = int(os.path.getmtime(file_path))
	last_modified_time = datetime.fromtimestamp(time).strftime(
		'%Y-%m-%d %H:%M:%S')

	# Open and parse the file.
	with open(file_path, 'r') as file:
		parsed_file = markdown(file.read(), extras=['metadata'])
		title = parsed_file.metadata['title']
		anchor = title.replace(' ', '-')
		
		data = {
			'content': parsed_file,
			'title': title,
			'date': last_modified_time,
			'timestamp': time,
			'anchor': anchor
		}

		POSTS[anchor] = data

# Order posts from newest to oldest
POSTS = {
	post : POSTS[post] for post in sorted(POSTS,
		key=lambda post: POSTS[post]['timestamp'],
		reverse=True)
}

# Render post in Jinja2
env = Environment(loader=PackageLoader('volta', 'templates'))
index_template = env.get_template('index.html')
index_html_content = index_template.render(posts = 
	[POSTS[post] for post in POSTS])

with open('../Muse/index.html', 'w') as file:
	file.write(index_html_content)
