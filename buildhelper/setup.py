import glob
import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.dist import Distribution


"""
A short script to help package compiled mGBA Python bindings into a wheel.
"""

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False
    def has_ext_modules(foo):
        return True

class InstallPlatlib(install):
    def finalize_options(self):
        install.finalize_options(self)
        if self.distribution.has_ext_modules():
            self.install_lib = self.install_platlib


libs = glob.glob(os.path.join('build/python/lib.*'))
libs = [os.path.basename(lib) for lib in libs if os.path.isdir(lib)]
print(libs)
if len(libs) == 0:
    raise ValueError("No libraries found")
else:
    lib = libs[0]

from pathlib import Path
this_directory = Path(__file__).parent
long_description = """
This is an inofficial package providing wheels for the Python bindings of [mGBA](https://github.com/mgba-emu/mgba).

**IMPORTANT NOTE**: The mGBA Python bindings have officially been deprecated and are planned to be replaced with Python scripting support in the future. This package is not affiliated with the mGBA project and does not receive any dev-support. It simply serves as a convenience for users who want to use the Python bindings without having to compile them themselves.
""".strip()

setup(
    name='mgba',
    description="Wheels for the Python bindings of mGBA",
    version='0.10.2',
    packages=['mgba'],
    setup_requires=['cffi>=1.6', 'pytest-runner'],
    install_requires=['cffi>=1.6', 'cached-property'],
    extras_require={'pil': ['Pillow>=2.3']},
    distclass=BinaryDistribution,
    cmdclass={'install': InstallPlatlib},
    package_dir={'': f'build/python/{lib}'},
    package_data={'mgba': ['_pylib.*.so']},
    long_description=long_description,
    long_description_content_type='text/markdown'
)
