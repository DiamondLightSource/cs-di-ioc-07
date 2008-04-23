#!/dls_sw/tools/bin/python2.4

# retrieve the file information from a selected folder
# sort the files by last modified date/time and display in order newest file first
import os
import glob
import time


def file_list(root):
    #root is the path to the files.
    date_file_list = []
    for folder in glob.glob(root):
#        print "folder =", folder
     # select the type of file, for instance *.mat or all files *.*
        for file in glob.glob(folder + '/rf_postmortem-*.mat'):
            # get date form filename
            pm_date = file[55:-4]
            pm_date = time.strptime(pm_date,"%Y-%m-%dT%H:%M:%S")
            # create list of tuples ready for sorting by date
            date_file_tuple = (pm_date, file)
            date_file_list.append(date_file_tuple)

    date_file_list.sort()
    date_file_list.reverse()  # newest mod date now first
    # Changing from 1 list of 2D tupples to 2 tupples the length of the original list
    timestamps = zip(*date_file_list)[0]
    names = zip(*date_file_list)[1]
    # converting from tupple to list to allow searching
    names = list(names)
    # getting the index of the required timestamp
    ind = names.index("/home/ops/rf/RF-libera/RF_Postmortems/rf_postmortem-01-2008-04-17T10:17:22.mat")
    required_ts = timestamps[ind]
    # only selecting the entries which match the latest timestamp.
    #required_ts = timestamps[0]
    selected_names = [elem[1] for elem in date_file_list if elem[0]==required_ts]
    selected_timestamps = [elem[1] for elem in date_file_list if elem[0]==required_ts]
    #file_names = []
    #for n in selected_pms:
        # extract just the filename
        #file_names.append(n)    
    
    #print file_names[1]
    return selected_names,selected_timestamps

# save task
if __name__ == "__main__":
    list_of_files, list_of_timestamps =  file_list('/home/ops/rf/RF-libera/RF_Postmortems/')
    #print list_of_files

