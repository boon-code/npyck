#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import zipfile
import tempfile
import optparse

VERSION = "0.0.4"

class npyck_class(object):
    
    def __init__(self, path):
        
        self.path = path
        self.version = VERSION
        self._z = None
    
    def read(self, filename):
    	
    	if self._z is None:
    		self._z = zipfile.ZipFile(self.path, 'r')
    	
    	try:
    		data = self._z.read(filename)
    		return data
    	except:
    		return None
    	
    
    def close(self):
        
        if not self._z is None:
            self._z.close()

def load_pack(main_file, path, use_globals = True):
    
    import runpy
    
    if use_globals:
        g_ = {'NPYCK_' : npyck_class(path)}
    else:
        g_ = {}
        
    result = runpy.run_module(main_file, run_name = '__main__', 
        alter_sys = True, init_globals = g_)

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
    zf.writestr("npyck.py", npy_file.read())
    npy_file.close()
    
    zf.close()
    
    zf = open(zip_path, 'r')
    data = zf.read()
    zf.close()
    
    os.remove(zip_path)
    
    dstream.write('#!/bin/sh\n')
    dstream.write('python -c"import sys;')
    dstream.write("sys.argv[0] = '$0';")
    dstream.write("sys.path.insert(0, '$0');")
    dstream.write("import npyck;")
    
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
    
    parser.add_option("-n", "--no_globals", action = "store_false",
        dest = "use_globals", help = "doesn't include " +
        "globals from loader, which means NPYCK_ will NOT be set")
    
    parser.add_option("-V", "--version", action = "store_true",
    	dest = "version", help = "shows version number only...")
    
    parser.set_defaults(all = False, use_globals = True, version = False)
    
    options, args = parser.parse_args()
    
    if options.version:
    	sys.stderr.write("npyck version %s\n" % VERSION)
    	return
    
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