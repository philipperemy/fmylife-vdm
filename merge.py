import json
import os
import sys
from glob import glob

input_dir = sys.argv[1]
data = []
for input_filename in glob(input_dir + '/*.json', recursive=False):
    with open(input_filename, 'r', encoding='utf8') as r:
        data.extend(json.load(r))
output_filename = os.path.splitext(os.path.basename(input_dir))[0]
with open(output_filename + '.json', 'w', encoding='utf8') as w:
    json.dump(data, w, indent=2, ensure_ascii=False)
