import requests
import os, re
import getopt, sys

rootDir, courseAddr = None

cmdArgs = sys.argv
argumentList = cmdArgs[1:]
print(argumentList)
unixOptions = "f:w:h"
gnuOptions = ["fileRootPath=", "webRootPath=", "help"]

try:
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as error:
    print(str(error))
    sys.exit(-1);

# Set values given by user
for arg, val in arguments:
    if arg in ("-f", "--fileRootPath"):
        rootDir = str(val)
    elif arg in ("-w", "--webRootPath"):
        courseAddr = str(val)
    elif arg in ("-h", "--help"):
        showHelpMsg()
        sys.exit(0)

# Dummy checks
if rootDir == None:
    error("Please specify a --fileRootPath (-f) and try again")
    sys.exit(-2)
if (courseAddr == None):
    error("Please specify a --webRootPath (-w) and try again")
    sys.exit(-3)

webDavPrefix = "https://bblearn.merlin.mb.ca/bbcswebdav/"
rootDir = "C:\\Users\\MZielonko\\Documents\\Github\\Physics 40S D2L"

courseAddr = "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08"
webFolderStructure, rootWebFolder = os.path.split(courseAddr)
if rootWebFolder == "": # if ends in a slash (as folders are often written), goes one further level
    webFolderStructure, rootWebFolder = os.path.split(webFolderStructure)
print("Root web folder: %s" %(rootWebFolder))

localFolderStructure, rootLocalFolder = os.path.split(rootDir)
if (rootLocalFolder == ""): # same as rootWebFolder
    localFolderStructure, rootLocalFolder = os.path.split(localFolderStructure)
print("Root local folder: %s" %(rootLocalFolder))
fullLocalFolder = os.path.join(localFolderStructure, rootLocalFolder)

def main():

    # webpage = "https://bblearn.merlin.mb.ca/webapps/blackboard/execute/displayLearningUnit?content_id=_8456658_1&course_id=_12330_1&mode=view&framesetWrapped=true"
    webpage = "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/course_content/module1/lesson1/intro.html"
    picture = "https://bblearn.merlin.mb.ca/bbcswebdav/xid-4317862_1"

    sampleFile = "\\exampleFile.html"
    # searchFile(rootDir + sampleFile)
    # removeCommonPath(rootDir + sampleFile, "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/course_content/images/m1_icon.gif")
    # sampleRelativePath = getRelativePath(rootDir + sampleFile, "/bbcswebdav/courses/Physics40S_master_08/course_content/images/m1_icon.gif")
    # print(sampleRelativePath)

    for dirName, subDirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if fname.endswith(".html"):
                fullPath = str(os.path.join(dirName, fname))
                searchFile(fullPath)

def getFilePathLevel(fileName):
     # removes the first folder name
    relPath = os.path.relpath(fileName, fullLocalFolder)
    travPath, tempName = os.path.split(relPath)
    pathLevel = 0

    while (travPath != ""):
        pathLevel += 1
        travPath, tempName = os.path.split(travPath)

    return pathLevel

def removeCommonPath(fileName, linkAddr):
    # get rid of anything further than the root folders
    fileComponents = getPathComponents(fileName)
    linkComponents = getPathComponents(linkAddr)
    # print(fileComponents)
    # print(linkComponents)

    # remove anything preceding and including the root folder address
    relevantFileComps = fileComponents[fileComponents.index(rootLocalFolder) + 1 : ]
    relevantWebComps = linkComponents[linkComponents.index(rootWebFolder) + 1 : ]

    while (relevantFileComps[0] == relevantWebComps[0]):
        relevantFileComps = relevantFileComps[1:]
        relevantWebComps = relevantWebComps[1:]

    #TODO put back into url form

    return [relevantFileComps, relevantWebComps]

def getRelativePath(basis, link):
    basisPath, linkPath = removeCommonPath(basis, link)
    relativePath = ""

    # print(basisPath)
    # print(linkPath)

    while True:
        # if we're working in the folder's level
        if (len(basisPath) == 1):
            for path in linkPath:
                relativePath = os.path.join(relativePath, path)
            break
        else:
            relativePath = os.path.join("..\\", relativePath)
            basisPath = basisPath[1:]

    return relativePath

def getPathComponents(folderStructure):
    tempFolderStructure = "" + folderStructure
    folders = []
    tempFolderStructure, tempFolder = os.path.split(tempFolderStructure)
    while tempFolder != "":
        folders.insert(0, tempFolder)
        tempFolderStructure, tempFolder = os.path.split(tempFolderStructure)

    return folders

def searchFile(fileName):

    file = open(fileName, "rt", encoding="utf-8")
    try:
        contents = file.read()
        # print(contents)
    except UnicodeEncodeError as e:
        print("\tERROR WRITING FILE: " + fileName)
        print(e)
    except UnicodeDecodeError as e:
        print("\tERROR READING FILE: " + fileName)
        print(e)
    finally:
        file.close()

    xid = re.search("/bbcswebdav/xid-[0-9_]*", contents)
    while (xid):
        print("\tFOUND: %s (%s)" % (xid, fileName))
        replaceStartIndex = xid.span()[0]
        replaceEndIndex = xid.span()[1]

        # look up the real link
        xidLink = "xid" + xid.group(0).split("xid")[1]
        print("\t\tSEARCHING FOR XID: %s" % (xidLink))
        linkResp = requests.get(webDavPrefix + xidLink, allow_redirects=False)

        # compare the relative file's path to the resulting link, only print necessary piece
        # print(linkResp.status_code)
        # print(linkResp.headers.get("location"))

        newLink = getRelativePath(fileName, linkResp.headers.get("location"))
        print("\t\tOLD: %s\tNEW: %s" %(linkResp.headers.get("location"), newLink))

        contents = contents[ :replaceStartIndex]  + newLink + contents[replaceEndIndex: ]
         # check again
        xid = re.search("/bbcswebdav/xid-[0-9_]*", contents)

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
