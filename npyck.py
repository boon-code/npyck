#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import zipfile
import tempfile
import optparse
import fnmatch

VERSION = "0.1.0"


class NpyckUtil(object):
    
    def __init__(self, zip_path):
        
        self.path = zip_path
        self.version = VERSION
    
    def ne_read(self, filename):
        """No exception read...
        
        Returns None on any error (except if there is an error while
        opening the zip archive, which would be a real bad error),
        on success it returns the opened file's content.
        """
        value = None
        zip = zipfile.ZipFile(self.path, 'r')
        try:
            value = zip.read(filename)
        except (KeyboardInterrupt, SystemExit), ex:
            raise ex
        except:
            return None
        finally:
            zip.close()
        
        return value
    
    def read(self, filename):
        """Normal read...
        
        Returns content of given file, if the file doesn't exist
        there will be an exception.
        """
        value = None
        zip = zipfile.ZipFile(self.path, 'r')
        try:
            value = zip.read(filename)
        finally:
            zip.close()
        
        return value


def load_pack(main_file, path, use_globals=True):
    
    import runpy
    
    if use_globals:
        environment = {'NPYCK_' : NpyckUtil(path)}
    else:
        environment = {}
    
    loader = runpy.get_loader(main_file)
    if loader is None:
        raise ImportError("No module named " + main_file)
    code = loader.get_code(main_file)
    if code is None:
        raise ImportError("No code object available for " + main_file)
    
    return runpy._run_module_code(code, environment, '__main__',
                            path, loader, True)

def read_pydir(dirname):
    
    return fnmatch.filter(os.listdir(dirname), '*.py')


def pack(main_file, src_files, dstream=sys.stdout, use_globals=True):
    
    os_handle, zip_path = tempfile.mkstemp()
    os.close(os_handle)
    
    zf = zipfile.ZipFile(zip_path, 'w')
    
    for pyfile in src_files:
        arc = os.path.split(pyfile)
        zf.write(pyfile, arc[1])
    
    zf.write(sys.argv[0], "npyck.py")
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
        dstream.write("npyck.load_pack('%s', '$0', use_globals=True)"
         % os.path.splitext(os.path.basename(main_file))[0])
    else:
        dstream.write("npyck.load_pack('%s', '$0', use_globals=False)"
         % os.path.splitext(os.path.basename(main_file))[0])
    
    dstream.write('" $*\n')
    dstream.write("exit\n\n")
    dstream.write(data)
    
    dstream.close()


def main():
    
    parser = optparse.OptionParser(
        usage = "usage: %prog [options] main-file [other source files]"
    )
    
    parser.add_option("-o", "--output", dest="filename",
        help="write output to file")
    
    parser.add_option("-a", "--all", action="store_true",
        dest="all", help="add all source files in directory")
    
    parser.add_option("-n", "--no_globals", action="store_false",
        dest="use_globals", help="doesn't include " +
        "globals from loader, which means NPYCK_ will NOT be set")
    
    parser.add_option("-V", "--version", action="store_true",
        dest="version", help="shows version number only...")
    
    parser.set_defaults(all=False, use_globals=True, version=False)
    
    options, args = parser.parse_args()
    
    if options.version:
        print("npyck version %s" % VERSION)
        return
    
    if len(args) < 1:
        parser.print_help(file=sys.stderr)
        return
    else:
        mainfile = args[0]
    
    args = frozenset(args)
    
    if options.all:
        args = args.union(read_pydir("."))
    
    if options.filename:
        f = open(options.filename, 'w')
        os.chmod(options.filename, 0764)
        
        pack(mainfile, args, dstream=f, 
            use_globals=options.use_globals)
    else:
        pack(mainfile, args, use_globals=options.use_globals)


if __name__ == '__main__':
    main()
