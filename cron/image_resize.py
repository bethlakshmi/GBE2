#!/usr/local/bin/python2.7

upload_dir = '/home/gbelive/webapps/gbelivemedia/uploads'
image_dir = upload_dir+'/images'
mini_dir = upload_dir+'/images/mini'

from wand.image import Image
import os

def scan_new_files(image_dir = image_dir, mini_dir = mini_dir):
    '''
    Scans a directory of images (the first arguement) for files that do not have a mini
    version in another directory of images (the second arguement).  Returns a list of images
    that do not have the mini-version.
    '''

    files = []
    for big_image in os.listdir(image_dir):
        if not os.path.isfile(mini_dir+'/'+big_image) and os.path.isfile(image_dir+'/'+big_image):
            files.append(big_image)

    return files

def minify(files, image_dir, mini_dir):
    '''
    Accepts a list of files to minify and their location directory, and saves them in 
    a second directory.  
    '''

    for f in files:
        with Image (filename=image_dir+'/'+f) as img:
            img.transform(resize='200x300>')
            img.save(filename=mini_dir+'/'+f)

files = scan_new_files(image_dir, mini_dir)
minify(files, image_dir, mini_dir)


