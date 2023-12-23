"""
Replaces page names in the links file with their corresponding IDs, eliminates links containing
non-existing pages, and replaces redirects with the pages to which they redirect.

Output is written to stdout.
"""

import sys
import zstandard

# Validate inputs
if len(sys.argv) < 4:
  print('[ERROR] Not enough arguments provided!')
  print('[INFO] Usage: {0} <pages_file> <redirects_file> <links_file> <unmatched_targets_file>'.format(sys.argv[0]))
  sys.exit()

PAGES_FILE = sys.argv[1]
REDIRECTS_FILE = sys.argv[2]
LINKS_FILE = sys.argv[3]
UNMATCHED_TARGETS_FILE = sys.argv[4]

if not PAGES_FILE.endswith('.zst'):
  print('[ERROR] Pages file must be zstandard compressed.')
  sys.exit()

if not REDIRECTS_FILE.endswith('.zst'):
  print('[ERROR] Redirects file must be zstandard compressed.')
  sys.exit()

if not LINKS_FILE.endswith('.zst'):
  print('[ERROR] Links file must be zstandard compressed.')
  sys.exit()

# Create a set of all page IDs and a dictionary of page titles to their corresponding IDs.
ALL_PAGE_IDS = set()
PAGE_TITLES_TO_IDS = {}
for line in zstandard.open(PAGES_FILE, 'r'):
  [page_id, page_title, _] = line.rstrip('\n').split('\t')
  ALL_PAGE_IDS.add(page_id)
  PAGE_TITLES_TO_IDS[page_title] = page_id

# Create a dictionary of page IDs to the target page ID to which they redirect.
REDIRECTS = {}
for line in zstandard.open(REDIRECTS_FILE, 'r'):
  [source_page_id, target_page_id] = line.rstrip('\n').split('\t')
  REDIRECTS[source_page_id] = target_page_id

# Loop through each line in the links file, replacing titles with IDs, applying redirects, and
# removing nonexistent pages, writing the result to stdout.
with zstandard.open(UNMATCHED_TARGETS_FILE, 'w') as unmatched_targets_file:
  unmatched_targets_file.write('source_id\ttarget_title\n')
  for line in zstandard.open(LINKS_FILE, 'r'):
    [source_page_id, target_page_title] = line.rstrip('\n').split('\t')

    source_page_exists = source_page_id in ALL_PAGE_IDS

    if source_page_exists:
      source_page_id = REDIRECTS.get(source_page_id, source_page_id)

      target_page_id = PAGE_TITLES_TO_IDS.get(target_page_title)

      if target_page_id is not None and source_page_id != target_page_id:
        target_page_id = REDIRECTS.get(target_page_id, target_page_id)
        print('\t'.join([source_page_id, target_page_id]))
      
      if target_page_id is None:
        unmatched_targets_file.write(f'{source_page_id}\t{target_page_title}\n')
