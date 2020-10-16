import math
import hashlib
import argparse
import shutil
import threading
import urllib.parse
import sys, os
import time
import socket


# Author: Josh Messitte (811976008)
# CSCI 6760 Project 3: download-accelerator
# Test downloader: python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url

port = 80

def download_chunk(url, host, start, end, part, fname, output_dir):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    range = 'Range{'+str(start) + ':' + str(end) + '}'
    request = 'GET ' + url + ' ' + range
    socket.send(request.encode())
    response = sock.recv(4096)

    filename = fname + '.chunk_%d' % part
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(response)
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

    parse_resp = urllib.parse.urlparse(url)
    host = parse_resp[1]
    path = parse_resp[2]

    # create output directory
    os.mkdir(output_dir)

    # TCP Connection for HEAD request --> Determine size
    csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    csock.connect((host, port))
    request = 'HEAD '+url
    socket.send(request.encode())
    response = csock.recv(4096)

    print(response)

    accepts_ranges = True;

    # Ensure url provided accepts ranges
    if not accepts_ranges:
        print('The given url does not accept byte ranges for downloading.')
    else:

        content_length = int(response.headers['content-length'])

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
            t = threading.Thread(target=download_chunk, args=(url, host, start, end, part, file_name, output_dir))
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