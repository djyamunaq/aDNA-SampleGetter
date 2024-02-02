import requests 
import pandas as pd
import datetime
import random
import subprocess
import os
from argparse import ArgumentParser, Namespace
from bs4 import BeautifulSoup

def main():
    parser = ArgumentParser()

    # Set number of samples from command line
    parser.add_argument('--n', help='Number of references to download')
    parser.add_argument('--output', help='Set output destination [Default: .]', default='.')

    # Get arguments from command line
    args: Namespace = parser.parse_args()

    # Number of samples requested
    nSamples = int(args.n)

    # Get samples table from AMTDB website
    url = 'https://amtdb.org/samples'
    page = requests.get(url) 
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
            ids.append(row['sample_identifier'])
    
    # Start random generator with timestamp
    random.seed(datetime.datetime.now().timestamp())
    indexes = []
    
    # Get list of random indexes
    while len(indexes) < nSamples:
        index = random.randint(0, len(ids))
        if index not in indexes:
            indexes.append(index)
    # Filter list by generated indexes
    ids = [ids[i] for i in indexes]
    links = [links[i] for i in indexes]

    # print(ids)
    # print(links)

    # Create output dir if it doesn't exist
    output_dir = args.output
    if args.output == '.':
        output_dir = os.path.join(args.output, 'samples')
    subprocess.run(['mkdir', output_dir])

    # Download samples to output directory
    for link in links:
        subprocess.run(['wget', '-P', output_dir, link])

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