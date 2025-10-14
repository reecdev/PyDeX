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
indexedUrls = []
searchIndexKey = []
pageRankScores = []
searchIndex = {}
def index(url):
    global indexedPages
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
    for key in metaDescription.split(" "):
        if not key in metaKeywords:
            metaKeywords.append(key.lower().strip())
    pageContent = soup.findAll(text=True)
    pageContent = (u" ".join(t.strip().lower() for t in pageContent))
    for key in pageContent.split(" "):
        if not key in metaKeywords:
            metaKeywords.append(key)
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

    # Print Stats
    clear()
    elapsedTime = round((time.perf_counter()-startTime)*1000)/1000
    print("#### Status ####")
    print("Web pages indexed: "+str(indexedPages))
    print("Time elapsed: "+str(elapsedTime)+"s")
    print("RPM: "+str(round((indexedPages/elapsedTime)*60)))

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
                        t = threading.Thread(target=index(parsedLink))
                        t.daemon = True
                        t.start()
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
        print(site)
        key = searchIndexKey[site]
        if not key[3] in servedSites:
            results.append(key)
            servedSites.append(key[3])
    output = []
    for result in results:
        output.append([result[0],result[1],result[3]])
    return output

clear()
print("## Welcome to PyDeX! ##")
print("The quick setup menu will help you get PyDeX running in minutes.")
print("")
startUrl = input("What website shall we start indexing on? Make sure you type a full URL.\n> ")
maxIndexes = input("How many web pages shall we index?\nYou'll be able to index ~60 web pages per minute on a standard internet connection.\n> ")
clear()
print("Warning: This can get you banned off of websites, as they'll think you're DDoSing them.\nMake sure you use a VPN or proxy that has given you permission.")
input("Press Enter to continue.\n> ")

startTime = time.perf_counter()
index(startUrl)
clear()
print("Indexing has finished. The web interface will start in just a second...")

app = Flask(__name__)
FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')

@app.route("/", methods=['GET'])
def main():
    return send_from_directory(FILES_DIR, "index.html")
@app.route('/<path:filename>', methods=['GET'])
def serve_file(filename):
    if filename == "search":
        searchResponse = search(request.args.get("query"))
        finalFile = open(FILES_DIR+"/search.html").read().replace('\n','').replace("%d",request.args.get("query"))
        searchResponseHTML = ""
        for element in searchResponse:
            searchResponseHTML = searchResponseHTML + "<div class='result'><a href='"+element[2]+"'><h2>"+element[0]+"</h2></a><i>"+element[1]+"</i></div>"
        return finalFile.replace("%s", searchResponseHTML)
    elif filename == "start-index":
        if len(indexedUrls) < 1:
            maxIndexes = int(request.args.get("maxPages"))
            index(request.args.get("start"))
        return "<html><head><title>PyDeX</title></head><body style='text-align: center;'><h1>Your request was submitted!</h1><p>The indexing has started. The server may temporarily slow down during indexing.</p><form action='index.html'><input type='submit' value='< Back' style='cursor: pointer'></form></body></html>"
    else:
        if len(indexedUrls) < 1:
            return "<html><head><title>PyDeX</title></head><body style='text-align: center'><h1>No websites have been indexed!</h1><p>Start an index using the options below:</p><form action='/start-index' style='display: flex; flex-direction: column; width: 250px; justify-self: center;'><input type='text' name='start' placeholder='Source Url (must be a full Url)' style='margin: 5px;'><input type='text' name='maxPages' placeholder='Max pages (useful for big websites)' style='margin: 5px;'><input type='submit' style='margin: 5px; cursor: pointer;'></form></body></html>"
        else:
            try:
                return send_from_directory(FILES_DIR, filename)
            except FileNotFoundError:
                abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=False)