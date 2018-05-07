import os
import time
import pickle
import shutil
import random
from  urllib.request import urlopen

from utils import Config

timeout_secs = 10 # after this many seconds we give up on a paper
if not os.path.exists(Config.src_dir): os.makedirs(Config.src_dir)
have = set(os.listdir(Config.src_dir)) # get list of all pdfs we already have

numok = 0
numtot = 0
db = pickle.load(open(Config.db_path, 'rb'))
for pid,j in db.items():
  print(j['links'])
  pdfs = [x['href'] for x in j['links'] if x['type'] == 'application/pdf']
  assert len(pdfs) == 1
  source_url = pdfs[0].replace("pdf", "e-print")
  basename = source_url.split('/')[-1]
  fname = os.path.join(Config.src_dir, basename) +  ".tar.gz"
  unpack_dir = os.path.join(os.path.dirname(fname), basename)
  # try retrieve the pdf
  numtot += 1
  try:
    if not basename in have:
      print('fetching %s into %s' % (source_url, fname))
      req = urlopen(source_url, None, timeout_secs)
      with open(fname, 'wb') as fp:
          shutil.copyfileobj(req, fp)


      if os.path.exists(fname):
          if not os.path.exists(unpack_dir):
              os.makedirs(unpack_dir, mode=0o777, exist_ok=False)
          shutil.unpack_archive(fname,
                                extract_dir=unpack_dir,
                                format="gztar")
          print("unpacked archive: {}".format(unpack_dir))
      time.sleep(0.05 + random.uniform(0,0.1))
    else:
      print('%s exists, skipping' % (fname, ))
    numok+=1
  except Exception as e:
    print('error downloading: ', source_url)
    print(e)

  print('%d/%d of %d downloaded ok.' % (numok, numtot, len(db)))

print('final number of papers downloaded okay: %d/%d' % (numok, len(db)))
