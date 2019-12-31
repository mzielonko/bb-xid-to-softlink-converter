import requests
import os
import re
from bs4 import BeautifulSoup

webfolder = "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/"
webDavPrefix = "https://bblearn.merlin.mb.ca/bbcswebdav/"

def main():

    # webpage = "https://bblearn.merlin.mb.ca/webapps/blackboard/execute/displayLearningUnit?content_id=_8456658_1&course_id=_12330_1&mode=view&framesetWrapped=true"
    webpage = "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/course_content/module1/lesson1/intro.html"
    picture = "https://bblearn.merlin.mb.ca/bbcswebdav/xid-4317862_1"

    rootDir = "R:\\Physics40S"

    sampleFile = "\\exampleFile.html"
    searchFile(rootDir + sampleFile)

    # for dirName, subDirList, fileList in os.walk(rootDir):
    #     print("Found directory: %s" % dirName)
    #     for fname in fileList:
    #         if fname.endswith(".html"):
    #             fullPath = str(os.path.join(dirName, fname))
    #             searchFile(fullPath)


def searchFile(fileName):
    print(fileName)
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
    if xid:
        print("FOUND: %s (%s)" % (xid, fileName))
        # look up the real link
        xidLink = "xid" + xid.group(0).split("xid")[1]
        print("SEARCHING FOR XID: %s" % (xidLink))
        linkResp = requests.get(webDavPrefix + xidLink, allow_redirects=False)

        # compare the relative file's path to the resulting link, only print necessary piece
        

    # parsed = BeautifulSoup(contents)
    # fileContents = BeautifulSoup(os.open(fileName, os.O_RDWR))
    # links = fileContents.findAll("img")
    # print(links)




main()
