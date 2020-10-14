import math
import hashlib
import argparse
import shutil
import threading
import urllib.request
import requests
import sys, os
import time


# Author: Josh Messitte (811976008)
# CSCI 6760 Project 3: download-accelerator
# Test downloader: python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url


def download_chunk(url, start, end, part, fname, output_dir):
    r = requests.get(url, headers={'Range': 'bytes=%d-%d' % (start, end)}, stream=True)
    filename = fname + '.chunk_%d' % part
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(r.content)
    print('Downloaded %s' % filepath)


def main():
    # Set up argument parsing automation
    prog = 'python3 downloader.py'
    descr = 'A command line tool that, given a single URL, can download the web object pointed by the URL by using multiple parallel TCP connections and HTTP Range requests.'
    parser = argparse.ArgumentParser(prog=prog, description=descr)
    parser.add_argument('-n', '--num_chunks', type=int, default=None, required=True,
                        help='Number of chunks to break object into')
    parser.add_argument('-o', '--output_dir', type=str, default=None, required=True,
                        help='Directory in which to store chunks')
    parser.add_argument('-f', '--file_name', type=str, default=None, required=True, help='File name for chunks')
    parser.add_argument('-u', '--object_url', type=str, default=None, required=True, help='URL of specified object')

    # Parse the given args
    args = parser.parse_args()

    num_chunks = args.num_chunks
    output_dir = args.output_dir
    file_name = args.file_name
    url = args.object_url

    # create output directory
    os.mkdir(output_dir)

    # perform a head request --> check content size and check if url accepts ranges
    r = requests.head(url)
    accepts_ranges = 'accept-ranges' in r.headers and 'bytes' in r.headers['accept-ranges']

    # Ensure url provided accepts ranges
    if not accepts_ranges:
        print('The given url does not accept byte ranges for downloading.')
    else:
        # url accepts byte ranges
        try:
            content_length = int(r.headers['content-length'])
        except:
            print('Invalid URL')
            return

        print('content-length: ', content_length)
        # compute chunk size and remainder of last chunk downloaded
        chunk_size = math.floor(content_length / num_chunks)
        chunk_remainder = content_length % num_chunks
        # if there is a remainder, we have n+1 chunks total

        part = 0
        # create a parallel threads for each chunk download
        for i in range(num_chunks):
            start = chunk_size * i
            part += 1
            if i != num_chunks - 1:
                end = start + chunk_size
            else:
                end = start + chunk_size + chunk_remainder

            print('Part ', part, ' Start is: ', start, ' end is ', end)
            t = threading.Thread(target=download_chunk, args=(url, start, end, part, file_name, output_dir))
            t.setDaemon(True)
            t.start()

        while threading.active_count() > 1:
            time.sleep(.1)

        # build complete file
        filepath = os.path.join(output_dir, file_name)
        with open(filepath, 'wb') as f:

            for i in range(num_chunks):
                tmp_filename = file_name + '.chunk_%s' % str(i + 1)
                tmp_path = os.path.join(output_dir, tmp_filename)
                shutil.copyfileobj(open(tmp_path, 'rb'), f)
                print('Copied ', tmp_path)

        print('Joining complete. File saved in %s' % filepath)
        newfile = open(filepath, 'rb')
        dat = newfile.read()
        print('SHA256 Hash: ', hashlib.sha256(dat).hexdigest())


if __name__ == '__main__':
    main()