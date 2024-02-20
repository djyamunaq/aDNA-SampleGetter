import requests 
import re
import pandas as pd
import datetime
import random
import subprocess
import os
from colorama import Fore, Back, Style
from argparse import ArgumentParser, Namespace
from bs4 import BeautifulSoup

def printErrorMessage(message):
    print(Fore.RED + Style.BRIGHT + '[ERROR]', end=' ')
    print(message)
    print(Style.RESET_ALL)

def downloadMetaData(id):
    url ='https://amtdb.org/download_metadata'

    payload = {
        'csrfmiddlewaretoken': '0HqHvj9FNjUmQFUbV1Tnn37PAEqWTNaBGK9na0245R2GjRivATuSiiAxa2zYrjpI',
        'sample_ids': id
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://amtdb.org/samples',
        'authority': 'amtdb.org',
        'method': 'POST',
        'path': '/download_metadata',
        'scheme': 'https',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Content-Length': '106',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'csrftoken=skvkjSVCb78sLFWnwa8Wp5rjkMp8PVKu8ne0YzO1tFgMeRkHb2JrkkU1UayanrZB; cookieconsent_status=dismiss; _gid=GA1.2.1056843561.1707838268; _ga=GA1.2.1007400171.1704845570; _ga_X26YEGG780=GS1.1.1707851898.14.0.1707851898.0.0.0',
        'Origin': 'https://amtdb.org',
        'Referer': 'https://amtdb.org/samples',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    r = requests.post(url, headers=headers, data=payload)
    raw_data = r.content.decode('utf-8')

    lines = [x.split(',') for x in raw_data.split('\n')]
    if len(lines) > 2:
        lines = lines[:2]

    df = pd.DataFrame(lines)
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)

    return df    

def processEbiURL(url):
    # Get samples table from AMTDB website
    url = 'https://amtdb.org/samples'
    page = requests.get(url) 
    
    if page.status_code != 200:
        message = 'Status code ' + str(page.status_code) + ' while trying to connect to ' + url
        printErrorMessage(message)
        exit(1)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', {'id': 'table-samples'})

def processNcbiURL(url):
    pass

def checkFastQLink(df):
    for value in df.iloc[0]:
        ebiPattern = re.compile("^\"http?://www.ebi.ac.uk/*")
        ncbiPattern = re.compile("^\"http?://www.ncbi.nlm.nih.gov/*")
        if ebiPattern.match(value):
            url = value.replace('\"', '')
            altId = url.split('/')[-1]
            processEbiURL(altId)
            return True
        elif ncbiPattern.match(value): 
            url = value.replace('\"', '')
            return False
    
def getFastQLink(df):
    url = ''
    for value in df.iloc[0]:
        ebiPattern = re.compile("^\"http?://www.ebi.ac.uk/*")
        ncbiPattern = re.compile("^\"http?://www.ncbi.nlm.nih.gov/*")
        if ebiPattern.match(value):
            url = value.replace('\"', '')
    return url        

def getFastQ(altId, output_dir):  
    url = f'https://www.ebi.ac.uk/ena/portal/api/filereport?accession={altId}&result=read_run&fields=run_accession,fastq_ftp,fastq_md5,fastq_bytes'
    page = requests.get(url) 

    if page.status_code != 200:
        message = 'Status code ' + str(page.status_code) + ' while trying to connect to ' + url
        printErrorMessage(message)
        exit(1)

    raw_data = page.content.decode('utf-8')
    lines = [x.split('\t') for x in raw_data.split('\n')]

    df = pd.DataFrame(lines)
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)

    for value in df['fastq_ftp']:
        if value != None:
            subprocess.run(['wget', '-P', output_dir, value])
            exit(0)
def main():
    parser = ArgumentParser()

    # Set number of samples from command line
    parser.add_argument('--nSamples', help='Number of references to download')
    parser.add_argument('--output', help='Set output destination [Default: .]', default='.')

    # Get arguments from command line
    args: Namespace = parser.parse_args()

    # Number of samples requested
    nSamples = int(args.nSamples)

    # Get samples table from AMTDB website
    url = 'https://amtdb.org/samples'
    page = requests.get(url) 
    
    if page.status_code != 200:
        message = 'Status code ' + str(page.status_code) + ' while trying to connect to ' + url
        printErrorMessage(message)
        exit(1)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', {'id': 'table-samples'})
    
    # Get table rows and remove header
    rows = table.findAll('tr')
    rows = rows[1:]
    
    # Sample ids and links to download lists
    ids = []
    links = []

    for row in rows:
        # Get '<a> tag' with fasta download link 
        aTag = row.find('a', {'class': 'a-control a-download_fasta text-decoration-none'})
        if aTag != None:
            # Mount link to download sample
            link = 'https://amtdb.org' + aTag['href']
            # Add id and link to lists
            links.append(link)
            ids.append(row['sample_id'])
    
    # Start random generator with timestamp
    random.seed(datetime.datetime.now().timestamp())
    indexes = []
    
    # Get list of random indexes
    while len(indexes) < nSamples:
        index = random.randint(0, len(ids))
        metadataDF = downloadMetaData(ids[index])
        validFastqLink = checkFastQLink(metadataDF)
        
        if validFastqLink and index not in indexes:
            indexes.append(index)

    # Filter list by generated indexes
    ids = [ids[i] for i in indexes]
    links = [links[i] for i in indexes]

    # Create output dir if it doesn't exist
    output_dir = args.output
    if args.output == '.':
        output_dir = os.path.join(args.output, 'samples')
    subprocess.run(['rm', '-rf', output_dir])
    subprocess.run(['mkdir', output_dir])
    

    # Download samples to output directory
    for i in range(len(links)):
        output_dir_sample = os.path.join(output_dir, ids[i])
        subprocess.run(['mkdir', output_dir_sample])
        subprocess.run(['wget', '-P', output_dir_sample, links[i]])
        
        # Save metadata to file
        metadataDF = downloadMetaData(ids[i])
        metadataFile = open(os.path.join(output_dir_sample, './metadata.txt'), 'w')
        metadataFile.write(metadataDF.to_string())
        metadataFile.close()
        
        data_link = getFastQLink(metadataDF)
        altId = data_link.split('/')[-1]
        getFastQ(altId, output_dir)
        
    # Mount pandas dataframe and filter by samples in ids list 
    df = pd.read_html(str(table))[0]
    df = df[df['Name'].isin(ids)]

    # Get current year 
    year = datetime.date.today().year
    # Function to calculate estimated average age based on range (Columns 'Year from' and 'Year to')
    fun = lambda x: year + (abs(x['Year from']) + abs(x['Year to']))/2 if x['Year from'] < 0 and x['Year to'] < 0 else year - (x['Year from'] + x['Year to'])/2

    # Apply lambda function to dataframe and create new column from results
    df['Age'] = df.apply(fun, axis=1)

    # print(df.columns)
    # print(df[['Name', 'Year from', 'Year to', 'Age']])

if __name__=='__main__':
    main()