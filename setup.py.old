import setuptools
import re

# versioning ------------
VERSIONFILE="d3blocks/__init__.py"
getversion = re.search( r"^__version__ = ['\"]([^'\"]*)['\"]", open(VERSIONFILE, "rt").read(), re.M)
if getversion:
    new_version = getversion.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# Setup ------------
with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()
setuptools.setup(
     install_requires=['numpy',
                       'colourmap>=1.1.10',
                       'datazets>=0.1.7',
                       'd3graph>=2.4.16',
                       'elasticgraph>=0.1.2',
                       'ismember>=1.0.1',
                       'pandas',
                       'tqdm',
                       'requests',
                       'scikit-learn',
                       'jinja2',
                       ],
     python_requires='>=3',
     name='d3blocks',
     version=new_version,
     author="Erdogan Taskesen, Oliver Verver",
     author_email="erdogant@gmail.com",
     description="Python package d3blocks",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/d3blocks/d3blocks",
	 download_url = 'https://github.com/d3blocks/d3blocks/archive/'+new_version+'.tar.gz',
     packages=setuptools.find_packages(), # Searches throughout all dirs for files to include
     include_package_data=True, # Must be true to include files depicted in MANIFEST.in
     license_files=["LICENSE"],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved",
         "Operating System :: OS Independent",
     ],
 )
