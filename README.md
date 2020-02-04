Blackboard XID to Softlink Converter
------------------------------------

Version: 1.3.x
Author: Mark Zielonko

Description: Python script used for replacing all of a selected course's XID
  links with relative paths based on the XID's redirect address

Purpose: Allowing existing courses to be converted into courses that are not
  coupled to Blackboard's proprietary file index system

Requirements:
  - python v3.x (can be installed without admin account)
  - python environment variable access (potentially)
  - internet connection with no proxy (or results may vary/fail altogether)

Usage instructions:
  *<C:\\path\\to\\python\\>*python *<C:\\path\\to\\script\\>*convert-xid.py --fileRootPath *<path to course stored on HDD>* --webRootPath *<webdav address for course>*

  - optional arguments after the previous line:
    --debug         Shows certain information that could be beneficial for debugging
    --verbose       Shows additional information for each replacement
    --noWrite       Leaves the course untouched but looks through all of the html pages and identifies broken paths (and writes log)
  - Note that path to python is optional if the path is part of your "path variable". The example assumes that python is in your
    path. Please see the following for more information: https://geek-university.com/python/add-python-to-the-windows-path/

Example:
  python convert-xid.py --fileRootPath "C:\\Users\\MZielonko\\Documents\\Github\\Physics-40S" --webRootPath "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_ZielonkoMark_2019"

Post-run instructions:
  - Recommended to check a few files to make sure that there were no course-specific errors (probably won't be)
  - Check the ErrorLog that was created with the date and time of the test being completed.
    This contains any XID links that gave a "page not found" status - you will need to find these links manually
    or simply delete them from the course
  - Re-run the checker to make sure the files that had errors don't have other errors (the script stops looking
    in a file after it encounters the first "bad link")

Potential issues:
  - If there is an error message about "unicode formatting", you may need to
    change a python environment variable before re-running the script. See
    screenshot of what that should look like in the file "EXAMPLE_EnvironmentVariableSet.jpg"

  - Make sure that you are able to create files where the script resides; if
    not, the script will be unable to create a log if there are broken links

  - Make sure that the project you are editing is in an editable location; the
    script will crash if it is unable to write changes to the file (unless in
    "noWrite" mode)
