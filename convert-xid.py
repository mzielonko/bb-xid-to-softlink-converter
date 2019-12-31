import requests
from webdav3.client import Client

webdav = None

def main():
    global webdav

    webdavOpts = {
        "webdav_hostname": "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08",
        "webdav_login": "markzielonko",
        "webdav_password": ""
    }
    webdav = Client(webdavOpts)
    webdav.verify = True
    # currFolder = webdav.list()
    # print(currFolder, "\n")

    searchFolder("")


    print("\n\n")

    # webpage = "https://bblearn.merlin.mb.ca/webapps/blackboard/execute/displayLearningUnit?content_id=_8456658_1&course_id=_12330_1&mode=view&framesetWrapped=true"
    webpage = "https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/course_content/module1/lesson1/intro.html"
    picture = "https://bblearn.merlin.mb.ca/bbcswebdav/xid-4317862_1"
    params = {}


    # Full page path made up of 3 parts: site location, folder location, file name
    # Full image path made up of 3 parts: site location, folder location, file name
    # Relative page path made up of 2 parts: difference between page and image folder locations, file name

    siteLocn = "bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08/" # provided
    folderLocn = "" # provided by link path (to be merged with siteLocn)
    picResp = requests.get(picture, allow_redirects=False)
    pageResp = requests.get(webpage, allow_redirects=False)


    print(pageResp.status_code, picResp.status_code)
    print(pageResp.history, picResp.history)
    print(pageResp.headers.get("location"), picResp.headers.get("location"))
    # for key, value in picResp.headers.items():
    #     print(key, ": ", value)
    for key, value in pageResp.headers.items():
        print(key, ": ", value)

def searchFolder(folderName):
    print("folderName: ", folderName)
    print(webdav.list(folderName))
    print(webdav.list("course_content"))
    print("\n\n")
    for name in webdav.list(folderName)[1:]:
        print("name: " + name)
        basePath = webdav.get_url(folderName)
        addition = "/" + name;

        # if webdav.is_dir(basePath + addition):
        #     print(fileObj)
        # else:
        #     print("(FILE) " + name)

        # NOTE: using resources does not seem to work (can't give a valid file path)


    res1 = webdav.resource("https://bblearn.merlin.mb.ca/bbcswebdav/courses/Physics40S_master_08")
    print(res1)
    print (res1.check())
    print(res1.info())



main()
