import argparse
import _thread
import urllib.request
import requests


# Author: Josh Messitte (811976008)
# CSCI 6760 Project 3: download-accelerator
# Test downloader: python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url


if __name__ == '__main__':

    # Set up argument parsing automation
    prog = 'python3 downloader.py'
    descr = 'A command line tool that, given a single URL, can download the web object pointed by the URL by using multiple parallel TCP connections and HTTP Range requests.'
    parser = argparse.ArgumentParser(prog=prog, description=descr)

    parser.add_argument('-n', '--num_chunks', type=int, default=None, required=True, help='Number of chunks to break object into')
    parser.add_argument('-n', '--output_dir', type=str, default=None, required=True,help='Directory in which to store chunks')
    parser.add_argument('-f', '--file_name', type=str, default=None, required=True, help='File name for chunks')
    parser.add_argument('-u', '--object_url', type=str, default=None, required=True,help='URL of specified object')

    # Parse the given args
    args = parser.parse_args()

    num_chunks = args.num_chunks
    output_dir = args.output_dir
    file_name = args.file_name
    url = args.object_url

    # perform a head request --> check content size and check if url accepts ranges
    r = requests.head(url)
    accepts_ranges = 'accept-ranges' in r.headers and 'bytes' in r.headers['accept-ranges']

    # Ensure url provided accepts ranges
    if not accepts_ranges:
        print('The given url does not accept byte ranges for downloading.')
    else:
        # url accepts byte ranges
        content_length = int(r.headers['content-length'])
        chunk_size = content_length / num_chunks
        chunk_remainder = content_length % num_chunks

