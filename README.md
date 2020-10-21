# download-accelerator
Computer Networks

A command line tool that, given a single URL, can download the web object pointed by the URL by using multiple parallel TCP connections and HTTP Range requests.


### Test the downloader:
```
$ python3 downloader.py -n num_chunks -o output_dir -f file_name -u object_url
```

### Outstanding Notes:
- Downlaoder seems to work correctly on : http://cobweb.cs.uga.edu/~perdisci/CSCI6760-F20/  --> but NOT on http://cobweb.cs.uga.edu/~perdisci/CSCI6760-F20/test_files/generic_arch_steps375x250.png
  - Latter yielding different(and wrong) md5sums each time depending on chunks.
- Even first link breaks at n=32 chunks

