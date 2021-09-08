# https://stackoverflow.com/questions/37225035/serialize-in-json-a-base64-encoded-data

import os
import numpy as np
from base64 import b64encode,b64decode
import json

filename = 'ok.npy'
out_filename = f"{filename}.out.npy"
jsonfilename = 'ok.json'
arr = (np.random.rand(1000,128,128)*1000).astype(np.int16)

np.save(filename,arr)


ENCODING = 'utf-8'

# first: reading the binary stuff
# note the 'rb' flag
# result: bytes
with open(filename, 'rb') as open_file:
    byte_content = open_file.read()

# second: base64 encode read data
# result: bytes (again)
base64_bytes = b64encode(byte_content)

# third: decode these bytes to text
# result: string (in utf-8)
base64_string = base64_bytes.decode(ENCODING)

myjson = {filename:base64_string}

with open(jsonfilename,'w') as f:
    f.write(json.dumps(myjson))


with open(out_filename, 'wb') as f:
    f.write(b64decode(myjson[filename]))

out_arr = np.load(out_filename)

print(np.sum(out_arr-arr) ==0)

mb = 1024*1024  # convert byte to mb
print(os.path.getsize(filename)/mb)
print(os.path.getsize(out_filename)/mb)
print(os.path.getsize(jsonfilename)/mb)

# ! ls -lh *ok*