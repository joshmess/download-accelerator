# download-accelerator
Computer Networks 6760

A command line tool that, given a single URL, can download the web object pointed by the URL by using multiple parallel TCP connections and HTTP Range requests. Downloader uses threads to download chunks in parallel.


### Test the downloader:
```
$ python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url
```
