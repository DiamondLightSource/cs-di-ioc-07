#!/dls_sw/tools/bin/python2.4

# retrieve the file information from a selected folder
# sort the files by last modified date/time and display in order newest file first
# tested with Python24    vegaseat    21jan2006
import os
import glob
import time


def file_list(root):
    #root is the path to the files.
    #root = '/home/ops/rf/RF-libera/RF_Postmortems/' # one specific folder
    date_file_list = []
    for folder in glob.glob(root):
#        print "folder =", folder
     # select the type of file, for instance *.mat or all files *.*
        for file in glob.glob(folder + '/rf_postmortem-*.mat'):
            # retrieves the stats for the current file as a tuple
            # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
            # the tuple element mtime at index 8 is the last-modified-  date
            stats = os.stat(file)
            # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
            # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
            # note:  this tuple can be sorted properly by date and time
            lastmod_date = time.localtime(stats[8])
            # create list of tuples ready for sorting by date
            date_file_tuple = lastmod_date, file
            date_file_list.append(date_file_tuple)

    date_file_list.sort()
    date_file_list.reverse()  # newest mod date now first

    # only selecting the entries which match the latest timestamp.
    selected_pms = [elem for elem in date_file_list if elem==date_file_list[1]]

    file_name = []
  #  file_date = []

    #print "%-40s %s" % ("filename:", "last modified:")
    for file in selected_pms:
        # extract just the filename
        file_name.append(file[1])    
        # convert date tuple to DD/MM/YYYY HH:MM:SS format
  #      file_date_temp =(time.strftime("%d/%m/%y %H:%M:%S", file[0]))
  #      file_date.append(file_date_temp)
    
    return file_name

#print "%-40s %s" % (file_name, file_date)

# save task
if __name__ == "__main__":
    list_of_files =  file_list('/home/ops/rf/RF-libera/RF_Postmortems/')
    print list_of_files[:len(list_of_files)-4]

