# From https://github.com/raydouglass/cmake_setuptools

# See https://cmake.org/cmake/help/latest/manual/cmake.1.html for cmake CLI options

import os
import subprocess
import shutil
import sys
from glob import glob
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

CMAKE_EXE = os.environ.get('CMAKE_EXE', shutil.which('cmake'))


def check_for_cmake():
    if not CMAKE_EXE:
        print('cmake executable not found. '
              'Set CMAKE_EXE environment or update your path')
        sys.exit(1)


class CMakeExtension(Extension):
    """
    setuptools.Extension for cmake
    """

    def __init__(self, name, pkg_name, sourcedir=''):
        check_for_cmake()
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.pkg_name = pkg_name


class CMakeBuildExt(build_ext):
    """
    setuptools build_exit which builds using cmake & make
    You can add cmake args with the CMAKE_COMMON_VARIABLES environment variable
    """

    def build_extension(self, ext):
        check_for_cmake()
        if isinstance(ext, CMakeExtension):
            output_dir = os.path.abspath(
                os.path.dirname(self.get_ext_fullpath(ext.pkg_name + "/" + ext.name)))

            build_type = 'Debug' if self.debug else 'Release'
            cmake_args = [CMAKE_EXE,
                          '-S', ext.sourcedir,
                          '-B', self.build_temp,
                          '-Wno-dev',
                          '--debug-output',
                          '-DPython_EXECUTABLE=' + sys.executable.replace("\\", "/"),
                          '-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON',
                          '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + output_dir.replace("\\", "/"),
                          '-DCMAKE_BUILD_TYPE=' + build_type]
            cmake_args.extend(
                [x for x in
                 os.environ.get('CMAKE_COMMON_VARIABLES', '').split(' ')
                 if x])

            env = os.environ.copy()
            print('Generating native project files:', cmake_args)
            subprocess.check_call(cmake_args,
                                  env=env)
            print('Listing files in current directory:', '\n'.join(glob('**', recursive=True)))
            build_args = [CMAKE_EXE, '--build', self.build_temp]
            print('Building:', build_args)
            subprocess.check_call(build_args,
                                  env=env)
            print()
        else:
            super().build_extension(ext)



class CMakeBuildExtFirst(build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

__all__ = ['CMakeBuildExt', 'CMakeExtension', 'CMakeBuildExtFirst']
