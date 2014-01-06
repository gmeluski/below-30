from bs4 import BeautifulSoup
import json
import requests

def isRight(firstBoundary, lastBoundary, pointToCheck):
    return ((lastBoundary[0] - firstBoundary[0]) * (pointToCheck[1] - firstBoundary[1]) - (lastBoundary[1] - firstBoundary[1]) * (pointToCheck[0] - firstBoundary[0])) < 0

def contactCrunchBase(listItem):
    crunchBaseResponse = crunchBaseRequest(listItem.get('data-name'))
    return [crunchBaseResponse, listItem]

def returnContactString(listItem):
    hiringUrl = listItem.get('data-hiringurl') if listItem.get('data-hiringurl') else listItem.get('data-url')
    contactString = '<a target="_blank" href="' + hiringUrl + '">' + listItem.get('data-name').encode('ascii', 'xmlcharrefreplace') + '</a><br />'
    return contactString

def generateCrunchBaseUrl(companyName):
    crunchBaseUrl = 'http://api.crunchbase.com/v/1/company/'
    crunchBaseKey = '.js?api_key=g89j3ut6u473uq9sx46jk8t9'
    return crunchBaseUrl + companyName.replace('.', '').replace(' ', '+') + crunchBaseKey

def crunchBaseRequest(companyName):
    print companyName
    requestUrl = generateCrunchBaseUrl(companyName)
    print requestUrl
    try :
        crunchBaseResponse = requests.get(requestUrl)
        jsonData = json.loads(crunchBaseResponse.text)
    except Exception as e:
        print companyName + ' excepted'
        print str(e) 
        return '400'

    nameResult = 'name' in jsonData
    employeeResult = 'number_of_employees' in jsonData

    if nameResult and employeeResult:
        if (jsonData['number_of_employees'] >= 50):
            return '200'
        else:
            print 'not enough employees'
            return '402' 
    else: 
        print jsonData['error']
        return '401'

def writeFiles(responseGroups):
    contactFile = open('contactme.html', 'w')
    failureFile = open('failures.html', 'w')

    filesDictionary = {
        'contact': contactFile,
        'failure': failureFile
    }

    initializeFiles(filesDictionary)

    for key in responseGroups:
        if key == '200':
            for companyItem in responseGroups[key]:
                contactFile.write(returnContactString(companyItem))
        else:
            failureFile.write(key)
            failureFile.write('<br />-----------------------<br />')
            for companyItem in responseGroups[key]:
                failureFile.write(returnContactString(companyItem))
                if key == '402':
                    companyName = companyItem.get('data-name')
                    crunchBaseLink = '<a target="_blank" href="' + generateCrunchBaseUrl(companyName) + '">Crunchbase Link for ' + companyName + '</a><br /><br />'
                    failureFile.write(crunchBaseLink) 
            failureFile.write('<br /><br />')

    finalizeFiles(filesDictionary)

def initializeFiles(filesDictionary):
    headString = """
        <head>
        </head>
        <body>
        """
    for key in filesDictionary: 
        filesDictionary[key].write(headString)

def finalizeFiles(filesDictionary):
    for key in filesDictionary: 
        filesDictionary[key].write('</body>')


htmlFile = open('tryme.html', 'r+')
soup = BeautifulSoup(htmlFile, 'html5lib')
mainItems = soup.find_all('li')
print len(mainItems)

successCount = 0;
firstBoundary = [-74.00688886642456,40.75460438258571]
lastBoundary = [-73.96150588989258,40.74003879540742]

# 400: no json
# 401: no record
# 402: not enough employees

responseGroups = {'200':[], '400': [], '401': [], '402': []}

for listItem in soup.find_all('li'):
    coordinates = []
    coordinates.append(float(listItem.get('data-long')))
    coordinates.append(float(listItem.get('data-lat')))
    if isRight(firstBoundary, lastBoundary, coordinates):
        successCount += 1; 
        responseList = contactCrunchBase(listItem)
        responseGroups[responseList[0]].append(responseList[1])

writeFiles(responseGroups)

print 'Total companies written: ' + str(successCount)
