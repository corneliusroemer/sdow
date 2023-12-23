"""
Replaces page titles in the redirects file with their corresponding IDs.

Output is written to stdout.
"""


import io
import sys
import gzip
import zstandard

# Validate input arguments.
if len(sys.argv) < 3:
  print('[ERROR] Not enough arguments provided!')
  print('[INFO] Usage: {0} <pages_file> <redirects_file>'.format(sys.argv[0]))
  sys.exit()

PAGES_FILE = sys.argv[1]
REDIRECTS_FILE = sys.argv[2]

if not PAGES_FILE.endswith('.zst'):
  print('[ERROR] Pages file must be zstdandard compressed.')
  sys.exit()

if not REDIRECTS_FILE.endswith('.zst'):
  print('[ERROR] Redirects file must be zstdandard compressed.')
  sys.exit()

# Create a set of all page IDs and a dictionary of page titles to their corresponding IDs.
ALL_PAGE_IDS = set()
PAGE_TITLES_TO_IDS = {}
for line in zstandard.open(PAGES_FILE, 'r'):
  [page_id, page_title, _] = line.rstrip('\n').split('\t')
  ALL_PAGE_IDS.add(page_id)
  PAGE_TITLES_TO_IDS[page_title] = page_id

# Create a dictionary of redirects, replace page titles in the redirects file with their
# corresponding IDs and ignoring pages which do not exist.
REDIRECTS = {}
for line in zstandard.open(REDIRECTS_FILE, 'r'):
  [source_page_id, target_page_title] = line.rstrip('\n').split('\t')

  source_page_exists = source_page_id in ALL_PAGE_IDS
  target_page_id = PAGE_TITLES_TO_IDS.get(target_page_title)

  if source_page_exists and target_page_id is not None:
    REDIRECTS[source_page_id] = target_page_id

# Loop through the redirects dictionary and remove redirects which redirect to another redirect,
# writing the remaining redirects to stdout.
for source_page_id, target_page_id in REDIRECTS.items():
  start_target_page_id = target_page_id

  redirected_count = 0
  while target_page_id in REDIRECTS.keys():
    target_page_id = REDIRECTS[target_page_id]

    redirected_count += 1

    # Break out if there is a circular path, meaning the redirects only point to other redirects,
    # not an acutal page.
    if target_page_id == start_target_page_id or redirected_count > 100:
      target_page_id = None

  if target_page_id is not None:
    print('\t'.join([source_page_id, target_page_id]))
