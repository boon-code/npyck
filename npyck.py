#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import zipfile
import tempfile
import optparse

READ_SIZE = 1000

class npyck_class(object):
	
	def __init__(self, path):
		
		self.path = path
		self.version = "0.0.1"
	
	def read(self, filename, max_size = None):
		import zipfile
		z = zipfile.ZipFile(self.path, 'r')
		
		if filename in z.namelist():
			f = z.open(filename, 'r')
			buffer = f.read(max_size)
			f.close()
			z.close()
			
			return (True, buffer)
			
		z.close()
		return (False, '')

def load_pack(main_file, path, use_globals = True):
	
	import sys
	import runpy
	
	sys.argv[0] = path
	sys.path.insert(0, path)
	
	if use_globals:
		g_ = {'NPYCK_' : npyck_class(path)}
	else:
		g_ = {}
		
	result = runpy.run_module(main_file, run_name = '__main__', 
		alter_sys = True, init_globals = g_)

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

def pack(main_file, src_files, dstream = sys.stdout, use_globals = True):
	
	os_handle, zip_path = tempfile.mkstemp()
	os.close(os_handle)
	
	zf = zipfile.ZipFile(zip_path, 'w')
	
	for pyfile in src_files:
		arc = os.path.split(pyfile)
		zf.write(pyfile, arc[1])
	
	npy_file = open(sys.argv[0])
	zf.writestr("npyck.py", read2mem(npy_file))
	npy_file.close()
	
	zf.close()
	
	zf = open(zip_path, 'r')
	data = read2mem(zf)
	zf.close()
	
	os.remove(zip_path)
	
	dstream.write('#!/bin/sh\n')
	dstream.write('python -c"import npyck;')
	
	if use_globals:
		dstream.write("npyck.load_pack('%s', '$0', use_globals = True)"
		 % os.path.splitext(os.path.basename(main_file))[0])
	else:
		dstream.write("npyck.load_pack('%s', '$0', use_globals = False)"
		 % os.path.splitext(os.path.basename(main_file))[0])
	
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
	
	parser.add_option("-n", "--new_globals", action = "store_false",
		dest = "use_globals", help = "doesn't include " +
		"globals from loader, which means NPYCK_ will NOT be set")
	
	parser.set_defaults(all = False, use_globals = True)
	
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
		
		pack(mainfile, args, dstream = f, 
			use_globals = options.use_globals)
	else:
		pack(mainfile, args, use_globals = options.use_globals)


if __name__ == '__main__':
	main()
