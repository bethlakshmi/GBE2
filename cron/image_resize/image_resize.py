#!/usr/bin/python2.7

#upload_dir = '/home/gbelive/webapps/gbelivemedia/uploads'
upload_dir = '/vagrant/uploads'
image_dir = upload_dir+'/images'
save_dir = image_dir+'/fullsize'
mini_dirs = ['mini', 'thumb']
size = ''
ratio='>'
filename = ''
move = False
queue_length = False
help_text='''
Usage: image_resize.py [-m] [-f filename] [-u upload directory] [-i image
        directory] [-s save directory] [-q [queue length]] [-z size] [-h]

    Resizes images at the specified locations.  Can work with either a single
    specified file, or a queue of files from a directory.  Can also move the
    originals that have been resized to an image directory.

    -m - moves original file to the image directory
    -f - name of file to be resized
    -u - path to directory where original images are located
    -i - path to directory for the originals that have been resized
    -s - path to directory to save the resized images
    -q - work in queue mode, and optional length of queue.  Useful for cron
         job processing of multiple images.  Default queue length is 5, and
         0 processes all available images (max CPU usage, dangerous)
    -z - size of resized image.  May to 'mini', 'thumb' or a pixel size in the
         format of 'hhxvv>' where hh is the horizontal size, vv is the
         vertical size.
    -r - Aspect Ratio mode.
            m - Size is maximum size, aspect ratio preserved
            l - Literal height and width given, ignore original aspect ratio
            s - Shrink image.  Default.
            e - Enlarge image
            c - Resize and crop to fit listed size, preserve aspect ratio
    -h - print help text [this message]
 
'''

from wand.image import Image, Color
import os, sys


def scan_new_files(image_dir = image_dir, mini_dirs = mini_dirs):
    '''
    Scans a directory of images (the first arguement) for files that do not have mini
    versions in the directories of images (the second arguement).  Returns a list of images
    that do not have the mini-version, with the missing size appended.
    '''

    if not os.path.isdir(image_dir): os.makedirs(image_dir)
    for dir in mini_dirs:
        if not os.path.isdir(dir): os.makedirs(dir)
    
    files = []
    for big_image in os.listdir(image_dir):
        for mini_dir in mini_dirs:
            if not os.path.isfile(image_dir+'/'+mini_dir+'/'+big_image) and \
                    os.path.isfile(image_dir+'/'+big_image):
                files.append(big_image+' '+mini_dir)

    return files

def minify(files, image_dir, mini_dir, size='mini', ratio='>'):
    '''
    Accepts a list of files to minify and their location directory, and saves 
    them in a second directory.  Also accepts an optional size to resize the
    images to.  Accepts sizes of 'mini' for 200 x 300, 'thumb' for a thumbnail
    of 60 by 90 pixels, or in the format of 'hhxvv>', which is horizontal
    size by vertical size, and an aspect ratio mode.  The ratio options are:
        m - Listed sizes are maximum sizes, preserve aspect ratio
        l - Listed sizes are literal, do not preserve aspect ratio
        s - Shrink image to size, preserve aspect ratio
        e - Enlarge image to size, preserve aspect ratio
        c - Listed sizes are maximum sizes, crop to literal size, preserve
                aspect ratio
    '''

    if not os.path.isdir(mini_dir): os.makedirs(mini_dir)

    if ratio in ('m', 'l', 's', 'e'):
        if ratio == 'm': ratio = ''
        elif ratio =='l': ratio ='!'
        elif ratio =='s': ratio ='>'
        elif ratio =='e': ratio ='<'
        
    if size == 'mini':
        size='200x300'
    elif size == 'thumb':
        size='60x90'
        
    if ratio in ('m', 'l', 's', 'e'):
        if ratio == 'm': ratio = ''
        elif ratio =='l': ratio ='!'
        elif ratio =='s': ratio ='>'
        elif ratio =='e': ratio ='<'

    if not (type(files) == type(()) or type(files) == type([])):
        files = [files]
    for f in files:
        with Image (filename=image_dir+'/'+f) as img:
            if ratio == 'c':
                xx, yy = size.split('x')
                img.transform(resize=size)
                width, height = (int(xx)-img.width)/2, (int(yy)-img.height)/2
                img.frame(matte=Color('#010101'), width=width, height=height)
                if img.width != xx or img.height != yy:
                    img.transform(resize=size+'!')
                img.save(filename=mini_dir+'/'+f)
            else:
                img.transform(resize=size+ratio)
                img.save(filename=mini_dir+'/'+f)

def move_file(filename, upload_dir, save_dir):
    '''
    Moves file from upload_dir to save_dir.
    '''

    if not os.path.isdir(save_dir): os.makedirs(save_dir)
    if os.path.isfile(upload_dir+'/'+filename):
        os.rename(upload_dir+'/'+filename, save_dir+'/'+filename)

    elif not os.path.exists(upload_dir+'/'+filename):
        print "File %s does not exist at path %s." % (filename, upload_dir)
        sys.exit(5)
    else:
        print '%s is not a regular file.  Check %s.' % (filename, upload_dir)
        sys.exit(6)
        
def queue(image_dir, mini_dirs, queue_length = 5, move = False, ratio=''):
    '''
    Forms a queue of queue_length number of files to be processed, resizes only
    that many, and moves the processed full sized images into a save dir if
    move is True.
    '''

    if queue_length == '0' or queue_length == 0:
        files = scan_new_files(image_dir, mini_dirs)
    else:
        files = scan_new_files(image_dir, mini_dirs)[0: queue_length]
    for filename in files:
        if len(filename.split(" ")) == 2:
            filename, size = filename.split(" ")
            minify(filename, image_dir, image_dir+'/'+size, size, ratio)
        else:
            minify(filename, image_dir, mini_dirs[0], size, ratio)

    if move == True:
        newfiles = []
        for filename in files:
            filename = filename.split(' ')[0]
            if filename not in newfiles:
                newfiles.append(filename)
        for filename in newfiles:
            move_file(filename, image_dir, save_dir)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in range(0, len(sys.argv)):
            if sys.argv[arg] == '-m': move = True
            if sys.argv[arg] == '-f': filename = sys.argv[arg+1]; arg += 1
            if sys.argv[arg] == '-u': upload_dir = sys.argv[arg+1]; arg += 1
            if sys.argv[arg] == '-i': image_dir = sys.argv[arg+1]; arg += 1
            if sys.argv[arg] == '-s': save_dir = sys.argv[arg+1]; arg += 1
            if sys.argv[arg] == '-r':
                arg+=1
                ratio = sys.argv[arg]
                if sys.argv[arg] not in ('m', 'l', 's', 'e', 'c'):
                    print 'Incorrect aspect ratio mode incorrect.'
                    sys.exit(9)
            if sys.argv[arg] == '-q':
                if arg+1 < len(sys.argv):
                    if sys.argv[arg+1].isdigit():
                        queue_length = int(sys.argv[arg+1]); arg += 1
                else: queue_length = 5
            if sys.argv[arg] == '-z': size = sys.argv[arg+1]; arg += 1
            if sys.argv[arg] == '-h':
                # some help text
                print help_text
                sys.exit(0)
    elif len(sys.argv) == 1:
        print help_text
        sys.exit(0)
        
    if queue_length == False:
        if size == '':
            sizes = mini_dirs
        else:
            sizes = [size]
        for size in sizes:
            minify(filename, image_dir, image_dir+'/'+size, size, ratio)
        if move:
            move_file(filename, image_dir, save_dir)
    else:
        queue(image_dir, mini_dirs, queue_length, move, ratio)

