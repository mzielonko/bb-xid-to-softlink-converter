import requests
import os
import re
import getopt
import sys
import time

version = "1.3.6"
verbose = False
debug = False

localFolderStructure = rootLocalFolder = fullLocalFolder = None
webFolderStructure = rootWebFolder = None
rootDir = courseAddr = None
noWrite = False
errorLog = []

webDavPrefix = "https://bblearn.merlin.mb.ca/bbcswebdav/"


def main():
    parseArgs()
    parsePaths()
    if debug:
        print("Working directory:", os.getcwd())
    print("-"*50)

    for dirName, subDirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if fname.endswith(".html"):
                fullPath = str(os.path.join(dirName, fname))
                searchFile(fullPath)

    if len(errorLog) > 0:
        errLogToFile()


def parseArgs():
    global localFolderStructure
    global rootLocalFolder
    global fullLocalFolder
    global webFolderStructure
    global rootWebFolder
    global rootDir
    global courseAddr
    global noWrite
    global verbose
    global debug

    cmdArgs = sys.argv
    argumentList = cmdArgs[1:]
    if verbose:
        print("Arguments: ", argumentList)
    unixOptions = "f:w:hnvd"
    gnuOptions = ["fileRootPath=", "webRootPath=", "noWrite", "help", "verbose", "debug"]

    try:
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as error:
        print(str(error))
        sys.exit(-1)

    if (len(arguments) == 0):
        showHelpMsg()
        sys.exit(0)

    # Set values given by user
    for arg, val in arguments:
        if arg in ("-f", "--fileRootPath"):
            rootDir = str(val)
        elif arg in ("-w", "--webRootPath"):
            courseAddr = str(val)
        elif arg in ("-h", "--help"):
            showHelpMsg()
            sys.exit(0)
        elif arg in ("-n", "--noWrite"):
            print("NOWRITE: Not writing changes to files (test run)")
            noWrite = True
        elif arg in ("-v", "--verbose"):
            print("VERBOSE: Verbose mode activated")
            verbose = True
        elif arg in ("-d", "--debug"):
            print("DEBUG: Debug mode activated")
            debug = True

    # Dummy checks
    if debug:
        print("File Root Path:", rootDir)
    if rootDir is None or not os.path.exists(rootDir):
        print("Please specify a valid --fileRootPath (-f) and try again")
        sys.exit(-2)
    if courseAddr is None:
        print("Please specify a --webRootPath (-w) and try again")
        sys.exit(-3)


def errLogToFile():
    dateTime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))

    try:
        file = open("ErrorLog_" + dateTime + ".txt", "xt", encoding="utf-8")
        title = "Files that could not be completed due to links with redirect errors:"
        file.write(title + "\n" + "="*len(title) + "\n\n")
        for issueFile, link in errorLog:
            file.write(issueFile + "\n\t" + link + "\n\n")
        file.close()
        print("\nCAUTION: Some XID links unable to be converted probably due to broken links.\n"
              + "Output file \"ErrorLog_" + dateTime + ".txt\" has been written to the same file location of the script.\n"
              + "Manually fix or remove links and run again to make sure there are no additional errors in these files.\n")

    except:
        print("Unable to write output file. Check for permissions in script folder")



def showHelpMsg():
    print("convert-xid version " + str(version))
    print("-----------------------------------------------")
    print('Usage: python convert-xid.py -f | --fileRootPath "C:/Users/.../RootFolderName" -w | --webRootPath "http://bblearn.merlin.mb.ca/bbcswebdav/courses/COURSENAMEHERE" [-n | --noWrite] [-v | --verbose] [-d | --debug]')
    print("Where: \n\tfileRootPath: On computer system, uppermost folder that is used for storage when downloading a course")
    print("\twebRootPath: Path of course on the webserver (you can copy this directly from Blackboard, located under the heading \"Current Web Address\")\n")
    print("\tnoWrite: Files are opened and scanned, but changes are not written back to files (will not check if your file is available for writing either)")
    print("\tverbose: Changes are listed in more detail in the output window")
    print("\tdebug: More information is provided in function ")
    print()
    print("Description:\nScans the entire folder structure of a local directory (fileRootPath) for HTML files. Checks each file for links that rely on Blackboard's XID system, finds their course-based path, and inserts a relative link to the same file based on the html file's location. This outcome allows courses to be exported to most LMS platforms and not rely on Blackboard-specific notations and lookup protocols.")


def parsePaths():
    global webFolderStructure
    global rootWebFolder
    global localFolderStructure
    global rootLocalFolder
    global fullLocalFolder

    webFolderStructure, rootWebFolder = os.path.split(courseAddr)
    if rootWebFolder == "":     # if ends in a slash (as folders are often written), goes one further level
        webFolderStructure, rootWebFolder = os.path.split(webFolderStructure)
    print("Root web folder: %s" %(rootWebFolder))

    localFolderStructure, rootLocalFolder = os.path.split(rootDir)
    if (rootLocalFolder == ""):     # same as rootWebFolder
        localFolderStructure, rootLocalFolder = os.path.split(localFolderStructure)
    print("Root local folder: %s" %(rootLocalFolder))
    fullLocalFolder = os.path.join(localFolderStructure, rootLocalFolder)


def getFilePathLevel(fileName):
    # removes the first folder name
    relPath = os.path.relpath(fileName, fullLocalFolder)
    travPath, tempName = os.path.split(relPath)
    pathLevel = 0

    while (travPath != ""):
        pathLevel += 1
        travPath, tempName = os.path.split(travPath)

    return pathLevel


'''
    Removes pieces that are common to both paths (traces back to closest ancestor)
    @param fileName file on local system (full path)
    @param linkAddr identifcal file's location through the webdav address
'''
def removeCommonPath(fileName, linkAddr):
    global rootWebFolder

    if verbose:
        print("removeCommonPath: %s %s" % (fileName, linkAddr))
    # get rid of anything further than the root folders
    fileComponents = getPathComponents(fileName)
    linkComponents = getPathComponents(linkAddr)

    try:
        linkComponents.index(rootWebFolder)

    # if the web folder can't be found inside the full web path
    except ValueError:
        newRootWebFolder = linkComponents[linkComponents.index("bbcswebdav") + 2]

        print("-"*50)
        print(
            """WARNING:\n\tThe redirect given by the server doesn't seem to reference the same course name.
            Expected: %s\t\tGot: %s
        This can happen if the course's name was manually changed after its creation.
        Trying to use %s instead\n""" % (rootWebFolder, newRootWebFolder, newRootWebFolder))
        print("-"*50)
        # set the global root web folder to the presumed folder
        rootWebFolder = newRootWebFolder

    # remove anything preceding and including the root folder address
    relevantFileComps = fileComponents[fileComponents.index(rootLocalFolder) + 1 : ]
    relevantWebComps = linkComponents[linkComponents.index(rootWebFolder) + 1 : ]

    while (relevantFileComps[0] == relevantWebComps[0]):
        relevantFileComps = relevantFileComps[1:]
        relevantWebComps = relevantWebComps[1:]

    return [relevantFileComps, relevantWebComps]


def getRelativePath(basis, link):
    basisPath, linkPath = removeCommonPath(basis, link)
    relativePath = ""

    while True:
        # if we're working in the folder's level
        if (len(basisPath) == 1):
            for path in linkPath:
                relativePath = os.path.join(relativePath, path)
            break
        else:
            relativePath = os.path.join("..\\", relativePath)
            basisPath = basisPath[1:]

    return relativePath.replace("\\", "/")


def getPathComponents(folderStructure):
    tempFolderStructure = "" + folderStructure
    folders = []
    tempFolderStructure, tempFolder = os.path.split(tempFolderStructure)
    while tempFolder != "":
        folders.insert(0, tempFolder)
        tempFolderStructure, tempFolder = os.path.split(tempFolderStructure)

    return folders


def searchFile(fileName):
    global errorLog

    print("\tSEARCHING: %s" % (fileName))
    file = open(fileName, "rt", encoding="utf-8")
    try:
        contents = file.read()
    except UnicodeEncodeError as e:
        print("\tERROR WRITING FILE: " + fileName)
        print(e)
    except UnicodeDecodeError as e:
        print("\tERROR READING FILE: " + fileName)
        print(e)
    finally:
        file.close()

    regexLinkFind = "(http(s)?://bblearn.merlin.mb.ca)?/bbcswebdav/xid-[0-9_]*"
    xid = re.search(regexLinkFind, contents)
    while (xid):
        if (verbose):
            print("\tFOUND: %s (%s)" % (xid, fileName))
        replaceStartIndex = xid.span()[0]
        replaceEndIndex = xid.span()[1]

        # look up the real link
        xidLink = "xid" + xid.group(0).split("xid")[1]
        if verbose:
            print("\t\tSEARCHING FOR XID: %s" % (webDavPrefix + xidLink))
        linkResp = requests.get(webDavPrefix + xidLink, allow_redirects=False)

        if linkResp.status_code == 404:
            print("ERROR: Link %s cannot be found. Please check file %s manually and re-run once all XID links can be found, or remove manually." % (webDavPrefix + xidLink, fileName))
            errorLog.append((fileName, webDavPrefix + xidLink))
            return False
        # compare the relative file's path to the resulting link, only print necessary piece
        # print(linkResp.status_code)
        # print(linkResp.headers.get("location"))

        newLink = getRelativePath(fileName, linkResp.headers.get("location"))
        if verbose:
            print("\t\tOLD: %s\tNEW: %s" %(linkResp.headers.get("location"), newLink))

        if not verbose:
            print("\t\tFOUND: %s\t NEW: %s" %(webDavPrefix + xidLink, newLink))

        contents = contents[ :replaceStartIndex]  + newLink + contents[replaceEndIndex: ]
         # check again
        xid = re.search(regexLinkFind, contents)

    if not noWrite:
        file = open(fileName, "wt", encoding="utf-8")
        try:
            file.write(contents)
        except UnicodeEncodeError as e:
            print("\tERROR WRITING FILE: " + fileName)
            print(e)
        except UnicodeDecodeError as e:
            print("\tERROR READING FILE: " + fileName)
            print(e)
        finally:
            file.close()

main()
