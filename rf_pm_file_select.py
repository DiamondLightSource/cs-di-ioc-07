#!/dls_sw/tools/bin/python2.4

# retrieve the file information from a selected folder, sort the files by last
# modified date/time and display in order newest file first
import os
import glob
import time, sys

def file_list(root, out_length, cavity, pm_day, pm_month, pm_year, pm_time):
    #root is the path to the files.
    date_file_list = []
    file_list = []
    # Constructing search value
    search_string = '%s/*/rf_postmortem-0%s-%s-%s-%sT%s.mat' % (
        root, cavity, pm_year, pm_month, pm_day, pm_time)

    # Naughty code: we're trying to select the last n values sorted by date.
    # We "know" that the date occupies characters [-23:-4] and the cavity is
    # [-26:-24].
    sortable_names = [
        (name[-23:-4], name[-26:-24], name)
        for name in glob.glob(search_string)]

    if not sortable_names:
        print >>sys.stderr, 'No files found'
        print >>sys.stderr, 'Searching', search_string
        sys.exit(1)
    
    sortable_names.sort()
    return [filename
        for _, _, filename in sortable_names[-int(out_length):]]


# save task
if __name__ == '__main__':
    #list_of_files, list_of_timestamps =  file_list(*sys.argv[1:])
    #print list_of_files
    #print list_of_timestamps
    list_of_files =  file_list(*sys.argv[1:])
    print list_of_files
