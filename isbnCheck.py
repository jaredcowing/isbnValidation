import requests
from requests.auth import HTTPBasicAuth
import json
import urllib.parse
import csv
import collections
import itertools
with open('20240109-WEPO.csv',encoding='utf8') as csvfile:
    reader=csv.reader(csvfile)
    reader2=csv.reader(csvfile)
    fullfile=[r for r in reader]
    isbns=[r[18] for r in fullfile]
    print(isbns[0])
    print(len(isbns))
    print(len(fullfile))
client='redacted'
secret='redacted'
authBase='https://oauth.oclc.org/token?'
authParams=urllib.parse.quote('grant_type=client_credentials&scope=WorldCatMetadataAPI',safe='=&')
authURL=authBase+authParams
authHeaders={'Authorization':'Basic '+client,'Accept':'application/json'}
req=requests.Request('POST', authURL, data={}, headers=authHeaders)
#print(authURL)
#print('\r\n'.join('{}: {}'.format(k, v) for k, v in req.prepare().headers.items()))

resp=requests.post(authURL, auth=HTTPBasicAuth(client,secret),data={}).text
respJ=json.loads(resp)
token=respJ['access_token']
#isbn=['1423606736']
start=3985
end=5200
#nd=120
def fuzzySearch(auth,title,pub,yr):
    fURL="https://metadata.api.oclc.org/worldcat/search/brief-bibs?q=au%3A"+auth+"&ti%3A"+title+"&pb%3A"+pub+"&yr%3A"+yr+"&dt%3APrintBook&inCatalogLanguage=eng&itemType=&itemSubType=&content=&facets="
    resp2=requests.get(isbnURL,headers={'Authorization':'Bearer '+token})
    md=json.loads(resp2.text)
    #print(md)
    if 'briefRecords' in md:
        print([i2['isbns'] for i2 in md['briefRecords'] if 'isbns' in i2])
        isbns=list(itertools.chain.from_iterable([i2['isbns'] for i2 in md['briefRecords'] if 'isbns' in i2]))
        #isbnM=max(set(isbns),key=isbns.count)
        isbnsC=collections.Counter(isbns)
        koh=isbnsC.most_common(1)
        if len(koh)>0:
            key=koh[0][0]
            print(key)
            print(koh[0][1]/len(md['briefRecords']))
            if koh[0][1]/len(md['briefRecords'])>.6:
                return key
            else:
                return 'no ISBN found'
        else:
            return 'no isbn found'
    else:
        return 'API error'

for i,bn in enumerate(isbns[start:end]):
    if len(bn)<=5 and int(fullfile[i+start][6])>=1970:
        fuzzyResults=fuzzySearch(fullfile[i+start][1],fullfile[i+start][2],fullfile[i+start][5],fullfile[i+start][6])
        if fuzzyResults != 'no ISBN found':
            fullfile[i+start][7]=fuzzyResults
            bn=fuzzyResults
    if len(bn)>5:
        if len(bn)<10:
            bn='0'*(10-len(bn))+bn
        isbnURL="https://metadata.api.oclc.org/worldcat/search/brief-bibs?q=bn%3A"+bn+"&inCatalogLanguage=eng&itemType=&itemSubType=&content=&facets="
#print(authCodeURL)

        resp2=requests.get(isbnURL,headers={'Authorization':'Bearer '+token})
        md=json.loads(resp2.text)
        if 'numberOfRecords' in md:
            if md['numberOfRecords']>0:
                print("Matches found")
                fullfile[i+start].append('')
                fullfile[i+start][7]=bn
            elif md['numberOfRecords']<4:
                print('suspicious isbn: '+bn)
                fullfile[i+start].append('suspicious')
                fullfile[i+start][7]=bn
            else:
                print("invalid isbn: "+bn)
                fullfile[i+start].append('invalid')
            fullfile[i+start].append(md['numberOfRecords'])
            gf=[]
            ti=[]
            dt=[]
            try:
                for b in md['briefRecords']:
                    gf.append(b['generalFormat'])
                    ti.append(b['title'])
                    dt.append(b['machineReadableDate'])
                print(collections.Counter(gf))
                fullfile[i+start].append(collections.Counter(gf))
                fullfile[i+start].append(collections.Counter(ti))
                fullfile[i+start].append(collections.Counter(dt))
            except:
                fullfile[i+start].append('ERROR')
        else:
            print('invalid isbn')
            fullfile[i+start].append('invalid')

    else:
        print('invalid isbn')
        fullfile[i+start].append('invalid isbn')
    
    #print(resp2.text)
writer=csv.writer(open('wepo_isbn_check.csv','w',newline='',encoding='utf8'))
for r in fullfile:
    writer.writerow(r)