import os
from glob import glob
import numpy as np

# %% Download rst file
def download_file(url_rst, filename):
    try:
        from urllib.request import urlretrieve
        if os.path.isfile(filename):
            os.remove(filename)
            print('Download %s..' %(filename))
        urlretrieve(url_rst, filename)
    except:
        print('Downloading %s failed.' %(url_rst))

# %% Include ADD to rst files
def add_includes_to_rst_files():
    skipfiles = ['sponsor.rst']
    for file_path in glob("*.rst"):
        if not np.isin(file_path, skipfiles):
            with open(file_path, "r+") as file:
                contents = file.read()
                if ".. include:: add_top.add" not in contents:
                    file.seek(0)
                    file.write(".. include:: add_top.add\n\n" + contents)
                    print('Top Add included >%s' %(file_path))

                if ".. include:: add_bottom.add" not in contents:
                    file.seek(0, 2)
                    file.write("\n\n.. include:: add_bottom.add")
                    print('Bottom Add included >%s' %(file_path))

# %% ADD TO REST
def adds_in_rst(filehandle):
    # Write carbon adds
    filehandle.write("\n\n.. raw:: html\n")
    filehandle.write("\n   <hr>")
    filehandle.write("\n   <center>")
    filehandle.write('\n     <script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=CEADP27U&placement=erdogantgithubio" id="_carbonads_js"></script>')
    filehandle.write("\n   </center>")
    filehandle.write("\n   <hr>")

# %% SCAN DIRECTORY
def scan_directory(currpath, directory, ext):
    # Uitlezen op ext
    path_to_files = os.path.join(currpath, '_static', directory)
    files_in_dir = np.array(os.listdir(path_to_files))
    Iloc = np.array(list(map(lambda x: x[-len(ext):]==ext, files_in_dir)))
    return files_in_dir[Iloc]

# %% EMBED PDF IN RST
def embed_in_rst(currpath, directory, ext, title, file_rst):

    try:
        # Uitlezen op extensie
        files_in_dir = scan_directory(currpath, directory, ext)
        print('---------------------------------------------------------------')
        print('[%s] embedding in RST from directory: [%s]' %(ext, directory))

        # Open file
        filehandle = open(file_rst, 'w')
        filehandle.write(".. _code_directive:\n\n" + title + "\n#######################\n\n")

        # 3. simple concat op
        for fname in files_in_dir:
            print('[%s] processed in rst' %(fname))
            title = "**" + fname[:-len(ext)] + "**\n"
            if ext=='.pdf':
                newstr = ":pdfembed:`src:_static/" + directory + "/" + fname + ", height:600, width:700, align:middle`"
            elif ext=='.html':
                newstr = ".. raw:: html\n\n" + '   <iframe src="_static/' + directory + "/" + fname + '"' + ' height="900px" width="750px", frameBorder="0"></iframe>'
            write_to_rst = title + "\n" + newstr + "\n\n\n\n"
            # Write to rst
            filehandle.write(write_to_rst)

        # ADDs in RST wegschrijven
        adds_in_rst(filehandle)
        # Close file
        filehandle.close()
    except:
        print('ERROR IN EMBEDDING IT IN RST.')

# %% CONVERT NOTEBOOKS TO HTML
def convert_ipynb_to_html(currpath, directory, ext):
    try:
        # Uitlezen op extensie
        files_in_dir = scan_directory(currpath, directory, ext)
        # 3. simple concat op
        for fname in files_in_dir:
            path_to_file = os.path.join('_static/', directory, fname)
            print('[%s] converting to HTML' %(path_to_file))
            os.system('jupyter nbconvert --to html ' + path_to_file)
    except:
        print('ERROR IN CONVERTING NOTEBOOK TO HTML.')
