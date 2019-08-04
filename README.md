# Volta

### Intro
Volta is a static site generator I wrote for my own blogging needs. If you want something much more polished, might I suggest [Pelican](https://github.com/getpelican/pelican)?

### Getting Started
Volta requires Python 3, uses [Jinja2](https://github.com/pallets/jinja) for templating, and [markdown2](https://github.com/trentm/python-markdown2) for parsing. To get started, run `pip3 install -r requirements.txt`.

Run Volta with `python volta.py`. Each time, Volta will look for a `.config.json` file to parse for information about which directories to look into for metadata, contents, templates, etc. If no config file is found, Volta will prompt you to create a default one.

### Using Volta
1. Write your markdown files in `contents/` (blog posts) or `contents/page` (standalone pages)
2. Run Volta.
3. HTML is generated in `output/` and `output/page`, along with an auto-generated `index.html` file.


### How Volta Works
Volta tracks files you've updated in its index files and tries to only rebuilds updated/new files. If you update a template (e.g. `templates/post.html`), it'll rebuild all posts that use that specific template.

Here is what the `.config.json` file uses:

```
{
    "CONTENTS_DIR": directory for blog posts,
    "METADATA_DIR": directory for storing {DATA}_INDEX.json,
    "OUTPUT_DIR": directory for the output HTML files,
    "PAGE_DIR": sub-directory for page posts,
    "TEMPLATES_DIR": directory for templates,
    "BASE_PATH": path for default base HTML template,
    "POST_PATH": path for default post HTML template,
    "INDEX_PATH": path for default index HTML template,
    "PAGE_PATH": path for default page HTML template,
    "POST_INDEX": path for metadata object indexing posts,
    "PAGE_INDEX": path for metadata object indexing pages,
    "LAST_UPDATED": timestamp of the last time Volta was run,
    "MAX_SUMMARY_LENGTH": number of characters for auto-generated summary,
    "TITLE": site title
  }
```

Each blog post object has optional metadata that you can add to the beginning of the file in the form of:

```
# blog_post.md
title: A title
anchor: The generated HTML slug
summary: Summary which is displayed on index.html
YOUR CONTENT GOES HERE
```

If you just want to start writing, Volta will use the following default values for the above metadata:

- `title`: Name of the parsed `.md` file.
- `anchor`: Escaped name of the parsed `.md` file, with spaces swapped for hyphens.
- `summary`: First `MAX_SUMMARY_LENGTH` characters of the file.

Other information, like `last_updated` and `word_count` are auto-generated.

If anything goes wrong, or if you just want to rebuild the whole site, you can tell Volta to re-parse all files with the `-r` flag:
`python -r volta.py`