"""Utility functions for the csdfpy module."""

from os import path
import requests
from urllib.parse import urlparse
import sys


__author__ = "Deepansh J. Srivastava"
__email__ = "srivastava.89@osu.edu"


def _download_file_from_url(url):
    res = urlparse(url)
    filename = path.split(res[2])[1]
    name, extension = path.splitext(filename)
    original_name = name
    i = 0
    while path.isfile(filename):
        filename = '{0}_{1}{2}'.format(original_name, str(i), extension)
        i += 1

    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            sys.stdout.write(
                "Downloading '{0}' from '{1}' to file '{2}'.\n".format(
                    res[2], res[1], filename
                )
            )
            for data in response.iter_content(
                chunk_size=max(int(total/1000), 1024*1024)
            ):
                downloaded += len(data)
                f.write(data)
                done = int(20*downloaded/total)
                sys.stdout.write(
                    '\r[{}{}]'.format('█' * done, '.' * (20-done))
                )
                sys.stdout.flush()

    sys.stdout.write('\n')

    return filename
