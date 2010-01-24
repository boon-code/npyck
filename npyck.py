#!/usr/bin/env python

import sys
import os
import zipfile
import tempfile

READ_SIZE = 1000

def read2mem(file_obj):
	
	data = []
	rb = file_obj.read(READ_SIZE)
	while rb != '':
		data.append(rb)
		rb = file_obj.read(READ_SIZE)
	
	return "".join(data)

def main(main_file, src_files, dest = 'packout.zip'):
	
	os_handle, zip_path = tempfile.mkstemp()
	os.close(os_handle)
	
	zf = zipfile.ZipFile(zip_path, 'w')
	
	for pyfile in src_files:
		arc = os.path.split(pyfile)
		zf.write(pyfile, arc[1])
	
	zf.close()
	
	zf = open(zip_path, 'r')
	data = read2mem(zf)
	zf.close()
	
	os.remove(zip_path)
	
	df = open(dest, 'w')
	df.write("#!/bin/sh\n\n")
	df.write('python -c"import sys\n')
	df.write("import runpy\n\n")
	df.write("sys.argv[0] = '$0'\n")
	df.write("sys.path.insert(0, '$0')\n")
	df.write("result = runpy.run_module('" + 
		os.path.splitext(os.path.basename(main_file))[0] +
		"', run_name = '__main__')")
	df.write('" $*\n')
	df.write("exit\n\n")
	df.write(data)
	
	df.close()

if __name__ == '__main__':
	if len(sys.argv) > 2:
		# just add the main file to the packet, who cares...
		main(sys.argv[1], sys.argv[1:])
	else:
		print "npyck [main-filename] [other files]"

