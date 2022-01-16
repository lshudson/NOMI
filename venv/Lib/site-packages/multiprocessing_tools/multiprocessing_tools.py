from sys import getsizeof
import os
import multiprocessing

def map(func, items, ordered=False):
    pool = multiprocessing.Pool(processes=_get_core_count())
    items = list(items)
    chunk_size = _calculate_chunk_size(items)
    map_function = pool.imap if ordered else pool.imap_unordered
    return map_function(func, items, chunksize=chunk_size)

def filter(func, items):
    results = map(func, items, ordered=True)
    counter = 0
    for result in results:
        if result:
            yield items[counter]
        counter += 1

def _calculate_chunk_size(items):
    first_item = items[0]
    size_of_one = getsizeof(first_item)
    size_to_use = 1024*1024 # Megabyte
    chunk_size = int(size_to_use / size_of_one)
    chunk_size = min(len(items) / _get_core_count(), chunk_size)
    return int(max(1, chunk_size))

def _get_core_count():
    return len(os.sched_getaffinity(0))
