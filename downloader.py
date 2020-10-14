import argparse
import shutil
import threading
import urllib.request
import requests
import sys, os

# Author: Josh Messitte (811976008)
# CSCI 6760 Project 3: download-accelerator
# Test downloader: python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url


def download_chunk(url, start, end, part, fname, output_dir):
    r = requests.get(url, headers={'Range':'bytes=%d-%d' % (start, end)}, stream=True)
    filename = fname + '.chunk_%d' % part
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.seek(start)
        var = f.tell()
        f.write(r.content)
    print('Downloaded %s' % filepath)

def main():

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
        try:
            content_length = int(r.headers['content-length'])
        except:
            print('Invalid URL')
            return
        # compute chunk size and remainder of last chunk downloaded
        chunk_size = content_length / num_chunks
        chunk_remainder = content_length % num_chunks
        # if there is a remainder, we have n+1 chunks total
        if chunk_remainder != 0:
            num_chunks += 1

        part = 0
        # create a parallel threads for each chunk download
        for i in range(num_chunks):
            start = chunk_size*i
            part += 1
            if i != num_chunks-1:
                end = chunk_size
            else:
                end = chunk_remainder

            t = threading.Thread(target=download_chunk, args=(url, start, end, part, file_name, output_dir))
            t.setDaemon(True)

            t.start()

        # build complete file
        filepath = os.path.join(output_dir, file_name)
        with open(filepath, 'wb') as f:
            for i in range(num_chunks):
                tmp_filename = file_name + '.chunk_%d' % i+1
                tmp_filepath = os.path.join(output_dir, tmp_filename)
                shutil.copyfileobj(open(tmp_filepath, 'rb'), f)

        print('Joining complete. File saved in %s' % filepath)


if __name__ == '__main__':
    main()


