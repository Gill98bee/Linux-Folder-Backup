#!/usr/bin/python3

#############################
#                           #
#    By Gilbert A. Yeboah   #
#                           #
#############################

# WARNING! This simple script does not come with any guarantees and I will not held responsible to any damage. 
import os
import zipfile

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    # save zip file as your-file-name-choice.zip at /tmp
    zipf = zipfile.ZipFile('/tmp/your-file-name-choice.zip', 'w', zipfile.ZIP_DEFLATED)
    # enter the files/folders path to save from
    zipdir('/path/to/your/folder', zipf)
    zipf.close()