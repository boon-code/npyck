#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import zipfile
import tempfile
import optparse

READ_SIZE = 1000

def read2mem(file_obj):
	
	data = []
	rb = file_obj.read(READ_SIZE)
	while rb != '':
		data.append(rb)
		rb = file_obj.read(READ_SIZE)
	
	return "".join(data)

def read_pydir(dir):
	
	dir_list = os.listdir(dir)
	for i in dir_list:
		if i.endswith(".py"):
			yield i

def pack(main_file, src_files, dstream = sys.stdout):
	
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
	
	dstream.write("#!/bin/sh\n\n")
	dstream.write('python -c"import sys\n')
	dstream.write("import runpy\n\n")
	dstream.write("sys.argv[0] = '$0'\n")
	dstream.write("sys.path.insert(0, '$0')\n")
	dstream.write("result = runpy.run_module('" + 
		os.path.splitext(os.path.basename(main_file))[0] +
		"', run_name = '__main__')")
	dstream.write('" $*\n')
	dstream.write("exit\n\n")
	dstream.write(data)
	
	dstream.close()


def main():
	
	parser = optparse.OptionParser(
		usage = "usage: %prog [options] main-file [other source files]"
	)
	
	parser.add_option("-o", "--output", dest = "filename",
		help = "write output to file")
	
	parser.add_option("-a", "--all", action = "store_true",
		dest = "all", help = "add all source files in directory")
	
	parser.set_defaults(all = False)
	
	options, args = parser.parse_args()
	
	if len(args) < 1:
		parser.print_help(file = sys.stderr)
		return
	else:
		mainfile = args[0]
	
	if options.all:
		args = read_pydir(".")
	
	if options.filename:
		f = open(options.filename, 'w')
		os.chmod(options.filename, 0764)
		pack(mainfile, args, dstream = f)
	else:
		pack(mainfile, args)


if __name__ == '__main__':
	main()
