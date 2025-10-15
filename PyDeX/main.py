import bs4, requests, time, os, urllib, threading
from flask import Flask, send_from_directory, abort, request

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.systen('clear')
startTime = 0
def log(text):
    global startTime
    # print(str((round(time.perf_counter()-startTime)*1000)/1000)+" | "+text)
indexedPages = 0
maxIndexes = 0
rpm = 0
fastIndex = False
running = False
indexedUrls = []
searchIndexKey = []
pageRankScores = []
searchIndex = {}
def index(url):
    global running
    global indexedPages
    global rpm
    running = True
    stime = time.perf_counter()
    page = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; SurplusBot/1.0; +http://surplussoftworks.vercel.app)"}).text
    log("Fetched "+url+" in "+str((round(time.perf_counter()-stime)*1000)/1000)+"s")
    soup = bs4.BeautifulSoup(page, 'html.parser')
    log("Extracting metadata for "+url+" and indexing...")
    metadata = soup.find_all("meta")
    metaTitle = soup.title.text
    metaDescription = url
    metaKeywords = []
    if len(metadata) > 0:
        for metatag in metadata:
            if metatag.has_attr("name") and metatag.has_attr("content"):
                log("Found metatag "+metatag["name"])
                if metatag["name"] == "description":
                    metaDescription = metatag["content"]
                if metatag["name"] == "title":
                    metaTitle = metatag["content"]
                if metatag["name"] == "keywords":
                    metaKeywords = metatag["content"].split(",")
                    for metaKey in metaKeywords:
                        metaKey = metaKey.strip()
    indexedUrls.append(url)
    for key in metaTitle.split(" "):
        if not key in metaKeywords:
            metaKeywords.append(key.lower().strip())
    for key in metaDescription.split(" "):
        if not key in metaKeywords:
            metaKeywords.append(key.lower().strip())
    generatedData = [metaTitle, metaDescription, metaKeywords, url]
    if not generatedData in searchIndexKey:
        pageRankScores.append(0)
        searchIndexKey.append(generatedData)
    for keyWord in metaKeywords:
        if not keyWord.lower() in searchIndex:
            searchIndex[keyWord.lower()] = []
        if not searchIndexKey.index(generatedData) in searchIndex[keyWord.lower()]:
            searchIndex[keyWord.lower()].append(searchIndexKey.index(generatedData))
    log("Searching for links in parsed HTML...")
    indexedPages += 1

    # Print stats
    clear()
    elapsedTime = round((time.perf_counter()-startTime)*1000)/1000
    print("#### Status ####")
    print("Web pages indexed: "+str(indexedPages))
    print("Time elapsed: "+str(elapsedTime)+"s")
    rpm = round((indexedPages/elapsedTime)*60)
    print("RPM: "+str(rpm))

    running = False
    links = soup.find_all("a", href=True)
    for link in links:
        if link.has_attr("href"):
            isValid = False
            try:
                result = urllib.parse.urlparse(link["href"])
                isValid = all([result.scheme, result.netloc])
            except ValueError:
                isValid = False
            if isValid:
                parsedLink = urllib.parse.urljoin(url, link['href'])
                log("Found link: "+parsedLink)
                if indexedPages < int(maxIndexes)+1 and not parsedLink in indexedUrls:
                    indexedPages += 1
                    try:
                        if fastIndex == True:
                            time.sleep(1)
                            workerIndexingUrl = parsedLink
                            threading.Thread(target=indexingWorker).start()
                        else:
                            index(parsedLink)
                    except:
                        log("Skipping this page because it has an issue I'm too lazy to fix ;-;")
                else:
                    if parsedLink in indexedUrls:
                        pageRankScores[indexedUrls.index(parsedLink)] += 1
                        log("Up the score of "+parsedLink+"!")
                    log("Skipped indexing for link")
def search(query):
    searchKeywords = []
    keywords = query.split(" ")
    for key in keywords:
        key = key.strip().lower()
        if not key in ["a", "an", "the", "is", "and", "but", "in", "on", "for", "my", "how" "do", "i"]:
            searchKeywords.append(key)
    resultSites = []
    for key in searchIndex:
        if key.strip().lower() in searchKeywords:
            for site in searchIndex[key]:
                if not site in resultSites:
                    resultSites.append(site)
    results = []
    servedSites = []
    for site in resultSites:
        key = searchIndexKey[site]
        if not key[3] in servedSites:
            results.append(key)
            servedSites.append(key[3])
    output = []
    for result in results:
        output.append([result[0],result[1],result[3]])
    return output
def indexingWorker():
    startTime = time.perf_counter()
    index(workerIndexingUrl)

# clear()
# print("## Welcome to PyDeX! ##")
# print("The quick setup menu will help you get PyDeX running in minutes.")
# print("")
# startUrl = input("What website shall we start indexing on? Make sure you type a full URL.\n> ")
# maxIndexes = input("How many web pages shall we index?\nYou'll be able to index ~60 web pages per minute on a standard internet connection.\n> ")
# clear()
# print("Warning: This can get you banned off of websites, as they'll think you're DDoSing them.\nMake sure you use a VPN or proxy that has given you permission.")
# input("Press Enter to continue.\n> ")

# startTime = time.perf_counter()
# index(startUrl)
# clear()
# print("Indexing has finished. The web interface will start in just a second...")

app = Flask(__name__)
FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')

@app.route("/", methods=['GET'])
def main():
    return send_from_directory(FILES_DIR, "index.html")
@app.route('/<path:filename>', methods=['GET'])
def serve_file(filename):
    global maxIndexes
    global startTime
    global workerIndexingUrl
    if filename == "search":
        searchResponse = search(request.args.get("query"))
        finalFile = open(FILES_DIR+"/search.html").read().replace('\n','').replace("%d",request.args.get("query")).replace("%f", str(indexedPages))
        searchResponseHTML = ""
        for element in searchResponse:
            searchResponseHTML = searchResponseHTML + "<div class='result'><a href='"+element[2]+"'><h3>"+element[0]+"</h3></a><i>"+element[1]+"</i></div>"
        return finalFile.replace("%s", searchResponseHTML)
    elif filename == "start-index":
        try:
            maxIndexes = int(request.args.get("maxPages"))
            startTime = time.perf_counter()
            workerIndexingUrl = request.args.get("start")
            threading.Thread(target=indexingWorker).start()
            return "Success"
        except:
            return "Failed"
    elif filename == "apistats":
        return str(running)+"\n"+str(indexedPages)+"\n"+str(rpm)+"\n"+str(round(time.perf_counter() - startTime))
    else:
        try:
            return send_from_directory(FILES_DIR, filename)
        except FileNotFoundError:
            abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=False)