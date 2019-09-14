import json
import os
import sys
from glob import glob

input_dir = sys.argv[1]
data = []
for input_filename in glob(input_dir + '/*.json', recursive=False):
    with open(input_filename, 'r', encoding='utf8') as r:
        page_id = int(os.path.splitext(os.path.basename(input_filename))[0].split('_')[-1])
        m = json.load(r)
        for c in m:
            c['page_id'] = page_id
        data.extend(m)
output_filename = os.path.splitext(os.path.basename(input_dir))[0]
with open(output_filename + '.json', 'w', encoding='utf8') as w:
    json.dump(data, w, indent=2, ensure_ascii=False)
