import requests
import urllib.parse
import lxml.html as lh
from requests.exceptions import ConnectionError
pastTargets=[]
targetname=input("Input initial target (where will I stop?): ")
stop=int(input("How many times should the initial target be found before we move on to the next most frequent target? "))
stop2=int(input("How many targets should I find +"str(stop)+" times before I stop the program? "))
print("Enjoy :)")
print()


class LinkNotFoundError(Exception):
    pass

class InvalidPageNameError(Exception):
    pass

class LoopException(Exception):
    pass

class MediaWikiError(Exception):
    def __init__(self, message, errors):
        super(MediaWikiError, self).__init__(message)
        self.errors = errors

        
def valid_page_name(page):
    NON_MAINSPACE = ['File:','File talk:','Wikipedia:','Wikipedia talk:','Project:','Project talk:','Portal:','Portal talk:','Special:','Help:','Help talk:','Template:','Template talk:','Talk:','Category:','Category talk:']
    return all(not page.startswith(non_main) for non_main in NON_MAINSPACE)

def strip_parentheses(string):
    nested_parentheses = nesting_level = 0
    result = ''
    for c in string:
        # When outside of parentheses within <tags>
        if nested_parentheses < 1:
            if c == '<':
                nesting_level += 1
            if c == '>':
                nesting_level -= 1

        # When outside of <tags>
        if nesting_level < 1:
            if c == '(':
                nested_parentheses += 1
            if nested_parentheses > 0:
                result += ' '
            else:
                result += c
            if c == ')':
                nested_parentheses -= 1

        # When inside of <tags>
        else:
            result += c

    return result

# Used to store pages that have been visited in order to detect loops
# Deleted every time trace() exits (regardless of how)
visited = []

def calculateAvgHops(validPaths):
    total=0
    for path in validPaths:
        total+=len(path)
    return total/len(validPaths)

def findMostFrequentWord(paths,countedWordsIncludedYN):
    wordSoup=[]
    for path in paths:
        wordSoup+=path
    wordSoup.sort()
    maxWordValue=-1
    bestWord=""
    countedWords=[]
    if countedWordsIncludedYN=="Y":
        countedWords.append(targetname)
    for word in wordSoup:
        if word not in countedWords:
            countedWords.append(word)
            if wordSoup.count(word)>maxWordValue:
                bestWord=word
                maxWordValue=wordSoup.count(word)
    return bestWord
        

def trace(page=None, end=targetname, whole_page=False, infinite=False):
    BASE_URL = 'https://en.wikipedia.org/w/api.php'
    HEADERS = { 'User-Agent': 'The Philosophy Game/1.0.0',
                'Accept-Encoding': 'gzip' }
    if page is None:
        params = {
            'action': 'query',
            'list': 'random',
            'rnlimit': 1,
            'rnnamespace': 0,
            'format': 'json'
        }
        result = requests.get(BASE_URL, params=params, headers=HEADERS).json()
        if 'error' in result:
            del visited[:]
            raise MediaWikiError('MediaWiki error', result['error'])

        page = result['query']['random'][0]['title']

    if not valid_page_name(page):
        del visited[:]
        raise InvalidPageNameError("Invalid page name '{0}'".format(page))

    params = {
        'action': 'parse',
        'page': page,
        'prop': 'text',
        'format': 'json',
        'redirects': 1
    }

    if not whole_page:
        params['section'] = 0

    result = requests.get(BASE_URL, params=params, headers=HEADERS).json()

    if 'error' in result:
        del visited[:]
        raise MediaWikiError('MediaWiki error', result['error'])

    page = result['parse']['title']

    # Detect loop
    if page in visited:
        del visited[:]
        raise LoopException('Loop detected')

    if not whole_page:
        yield page

    if not infinite and page == end:
        del visited[:]
        return

    raw_html = result['parse']['text']['*']
    html = lh.fromstring(raw_html)

    for elm in html.cssselect('.reference,span,div,.thumb,'
                            'table,a.new,i,#coordinates'):
        elm.drop_tree()

    html = lh.fromstring(strip_parentheses(lh.tostring(html).decode('utf-8')))
    link_found = False
    for elm, attr, link, pos in html.iterlinks():
        if attr != 'href':
            continue
        next_page = link

        if not next_page.startswith('/wiki/'):
            continue

        next_page = next_page[len('/wiki/'):]
        next_page = urllib.parse.unquote(next_page)

        if not valid_page_name(next_page):
            continue

        next_page = next_page.replace('_',' ')

        pos = next_page.find('#')
        if pos != -1:
            next_page = next_page[:pos]

        link_found = True
        visited.append(page)

        for m in trace(page=next_page, end=end, whole_page=whole_page,
            infinite=infinite):
            yield m

        break

    if not link_found:
        if whole_page:
            del visited[:]
            raise LinkNotFoundError(
                'No valid link found in page "{0}"'.format(page)
            )
        else:
            for m in trace(page=page, whole_page=True, end=end,
                infinite=infinite):
                yield m



hopPagesDict={}
pathArchive=[]
validPathsArchive=[]
while True:
    visited=[]
    pastTargets.append(targetname)
    paths=[]
    index=0
    loopCounter=0
    validPaths=[]
    totalTrialsCounter=0
    while True:
        totalTrialsCounter+=1
        if loopCounter>=10:
            print("Too much, I'll break")
            break
        if len(validPaths)==stop:
            break
        someFlag=False
        paths.append([])
        try:
            for page in trace(end=targetname):
                paths[index].append(page)
                if page==targetname:
                    loopCounter=0
                    validPaths.append(paths[index])
                    print(page)
                    break
                for x in range(len(paths)):
                    if page in paths[x] and page!=paths[x][-1]: #if its in a previous path, and the path was valid, and the page is not the targetnaem
                        someFlag=True
                        i=paths[x].index(page)+1
                        while True:
                            try:
                                paths[index].append(paths[x][i])
                                print(paths[x][i])
                                page=paths[x][i]
                                if paths[x][i]==targetname:
                                    validPaths.append(paths[index])
                                    break
                                i+=1
                            except:
                                loopCounter+=1
                                print("Oops! I'm in a loop. This sucks. Oh well, moving right along!")
                                break
                            
                if someFlag==True:
                    break
                else:
                    print(page)
        except LoopException:
            loopCounter+=1
            print("Oops! I'm in a loop. This sucks. Oh well, moving right along!")
        except InvalidPageNameError as e:
            print("Damnit! Invalid page name.")
        except LinkNotFoundError as e:
            print("This page is dead - no real links to be found.")   
        print()
        index+=1
    avgHops=calculateAvgHops(validPaths)
    hopPagesDict[avgHops]=(targetname,totalTrialsCounter)
    if len(hopPagesDict)>=stop2:
        break
    targetname=findMostFrequentWord(paths,"Y")
    pathArchive.append(paths)
    validPathsArchive.append(paths)

print("Data: "+str(hopPagesDict))

    
    
