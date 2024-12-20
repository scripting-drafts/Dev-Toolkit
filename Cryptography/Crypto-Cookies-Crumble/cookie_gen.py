import compression
import random
import string
import uuid
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import Thread
from sys import exit as sysexit
from tqdm import tqdm

'''107,3741,824 chars -> 1GB TXT -> 19,173,961,.. lines, 56 characters
9,586,980.5 -> 512
4,793,490.25 -> 256
TODO: Turn to bin'''

buffer = 'buffer'
alphanum = list(string.ascii_letters) + [2, 3, 4, 5, 6, 7]

def generate_candidates():
    '''256MB Chunks'''  # 8MB for testing
    filename = uuid.uuid1()
    f = open(f'{buffer}/{filename}', 'a')

    for _ in tqdm(range(14979)):    # 4793490
        output_string = [str(random.SystemRandom().choice(alphanum)) for _ in range(56)]
        output_string = ''.join(output_string) + '\n'
        f.write(output_string)

    f.close()

'''
3 Generation Workers
1 Compression Thread
'''

max_concurrent = 3
pending = set()
executor = ThreadPoolExecutor(max_workers=max_concurrent)
cmp = compression.Compression()

while True:
    try:
        for _ in range(max_concurrent):
            pending.add(executor.submit(generate_candidates))

        while len(pending) != 0:
            _, pending = wait(pending, return_when=FIRST_COMPLETED)
        
    except Exception as e:
        executor.shutdown(cancel_futures=True)
        sysexit()

    finally:
        cmp.compress_candidates(buffer)