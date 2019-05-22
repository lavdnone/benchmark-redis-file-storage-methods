import timeit

item_count = 100
reads = 10000
redis_port = 6379

setup = f"""
import redis

MAX_IO = 131072
read_lo = redis.Redis(host='localhost', port={redis_port}, db=0)
read_local = redis.Redis(host='localhost', port=6379, db=0)
read_local.flushall(asynchronous=True)

item_count = {item_count}

with open('file002', 'rb') as read_file:
    contents = read_file.read()
    read_file.close()
chunks = []
for i in range(0, len(contents), 131072):
    chunks.append(contents[i:i+MAX_IO-1])

read_offset = []
for i in range(0, len(contents), 131072):
    read_offset.append(i)
read_contents = ""

"""

setup_r = f"""
import random
import redis
random.seed(0)
item_count = {item_count}
rnd_filen = random.randint(0, item_count-1)
MAX_IO = 131072
read_lo = redis.Redis(host='localhost', port={redis_port}, db=0)

with open('file002', 'rb') as read_file:
    contents = read_file.read()
    read_file.close()

read_offset = []
for i in range(0, len(contents), 131072):
    read_offset.append(i)
read_contents = ""
"""

setup_d = f"""
import redis
item_count = {item_count}
read_lo = redis.Redis(host='localhost', port={redis_port}, db=0)
"""

write_setrange = """
for i in range(item_count):
    inc = 0
    for offset in read_offset:
        read_lo.setrange(f"file_{i}", offset, chunks[inc])
        inc += 1 
"""
read_setrange = """
for offset in read_offset:
    read_contents = read_lo.getrange(f"file_{rnd_filen}", offset, MAX_IO-1)
"""


write_hset = """
for i in range(item_count):
    inc = 0
    for offset in read_offset:
        read_lo.hset(f"hfile_{i}", offset, chunks[inc])
        inc += 1
"""
read_hset = """
for offset in read_offset:
#    read_contents = read_lo.hget(f"hfile_{rnd_filen}", int(offset/MAX_IO))
    read_contents = read_lo.hget(f"hfile_{rnd_filen}", offset)

"""


write_zadd = """
for i in range(item_count):
    inc = 0
    for offset in read_offset:
        read_lo.zadd(f"zfile_{i}", {chunks[inc]: offset})
        inc += 1
"""
read_zadd = """
for offset in read_offset:
#    cursor = int(offset/MAX_IO)
    read_contents = read_lo.zrangebyscore(f"zfile_{rnd_filen}", offset, offset)
"""
read_zadd1 = """
for offset in read_offset:
#    cursor = int(offset/MAX_IO)
    read_contents = read_lo.zrangebyscore(f"zfile_{rnd_filen}", offset, offset, start=offset, num=offset+1)
"""
read_zadd2 = """
for offset in read_offset:
#    cursor = int(offset/MAX_IO)
    read_contents = read_lo.zrangebyscore(f"zfile_{rnd_filen}", "-inf", "+inf", start=offset, num=offset+1)
"""


del_setrange = """
for i in range(item_count):
    try: read_lo.delete('file_'+str(i))
    except: pass
"""

del_hset = """
for i in range(item_count):
    try: read_lo.delete(f'hfile_{i}')
    except: pass
"""

del_zadd = """
for i in range(item_count):
    try: read_lo.delete(f'zfile_{i}')
    except: pass
"""
print("")
print('write_setrange', round(timeit.Timer(write_setrange,setup).timeit(100), 5))
print('read_setrange ', round(timeit.Timer(read_setrange, setup_r).timeit(reads), 5))
print('del_setrange  ', round(timeit.Timer(del_setrange,  setup_d).timeit(1), 5))

print("")
print('write_hset    ', round(timeit.Timer(write_hset,    setup).timeit(100), 5))
print('read_hset     ', round(timeit.Timer(read_hset,     setup_r).timeit(reads), 5))
print('del_hset      ', round(timeit.Timer(del_hset,	  setup_d).timeit(1), 5))

print("")
print('write_zadd    ', round(timeit.Timer(write_zadd,    setup).timeit(100), 5))
#print('read_zadd     ', round(timeit.Timer(read_zadd,     setup_r).timeit(reads), 5))
print('rea1_zadd     ', round(timeit.Timer(read_zadd1,    setup_r).timeit(reads), 5))
#print('rea2_zadd     ', round(timeit.Timer(read_zadd2,    setup_r).timeit(reads), 5))
print('del_zadd      ', round(timeit.Timer(del_zadd,	  setup_d).timeit(1), 5))
