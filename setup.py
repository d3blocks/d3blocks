import setuptools
import re

# versioning ------------
VERSIONFILE="pyd3/__init__.py"
getversion = re.search( r"^__version__ = ['\"]([^'\"]*)['\"]", open(VERSIONFILE, "rt").read(), re.M)
if getversion:
    new_version = getversion.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# Setup ------------
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     install_requires=['numpy','pandas'],
     python_requires='>=3',
     name='pyd3',
     version=new_version,
     author="Erdogan Taskesen, Oliver Verver",
     author_email="erdogant@gmail.com",
     description="Python package pyd3",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/erdogant/pyd3",
	 download_url = 'https://github.com/erdogant/pyd3/archive/'+new_version+'.tar.gz',
     packages=setuptools.find_packages(), # Searches throughout all dirs for files to include
     include_package_data=True, # Must be true to include files depicted in MANIFEST.in
     license_files=["LICENSE"],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved",
         "Operating System :: OS Independent",
     ],
 )
