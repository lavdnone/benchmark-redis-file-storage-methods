# benchmark-redis-file-storage-methods

Test to see which way it is to push/store files through/in redis.
# keys vs hash vs sorted set
- keys way has limit of 512Mb file size without effort
- in sorted and hash items (saved file blocks) naming/score presumes rw Offset so no MAX_IO change on live system (first block named 0 second 131072 etc.)
- current rw block emulation MAX_IO = 131072 (128k)


# local
keys:
- write_setrange 21.57212
- read_setrange  10.70573
- del_setrange   0.00491

hash:
- write_hset     21.93116
- read_hset      20.5348
- del_hset       0.0058

sorted set:
- write_zadd     34.96599
- rea1_zadd      11.61833
- del_zadd       0.0065

# VM Centos 7.6
keys:
- write_setrange 38.05548
- read_setrange  21.5849
- del_setrange   0.0115

hash:
- write_hset     37.69397
- read_hset      28.85869
- del_hset       0.01855

sorted set:
- write_zadd     57.97613
- rea1_zadd      22.64661
- del_zadd       0.01304


# through dynomite cluster
- 3 node dynomite cluster: https://github.com/Netflix/dynomite
- added latency for nodes: tc qdisc add dev eth0 root netem delay 2ms 1ms
- redis port used 8397

keys:
- write_setrange 171.03115
- read_setrange  42.67535
- del_setrange   0.06957

hash:
- write_hset     159.63332
- read_hset      113.46556
- del_hset       0.03107

sorted set:
- write_zadd     184.72535
- rea1_zadd      41.27067
- del_zadd       0.03111

# startup
- docker run --name redis -p 0.0.0.0:6379:6379 -v ~/redis:/data -d redis:5-alpine
- N node number
- dynomite -c vmN.yaml -d -o dyno.log

```cat vm1.yaml 
dyn_o_mite:
  datacenter: dc-1
  rack: rack1
  dyn_listen: 192.168.1.221:7379
  dyn_seeds:
  - 192.168.1.221:7379:rack1:dc-2:0
  - 192.168.1.223:7379:rack1:dc-3:0
  listen: 0.0.0.0:8379
  servers:
  - 127.0.0.1:6379:1
  tokens: '0'
  secure_server_option: datacenter
  pem_key_file: /home/iadmin/dynomite/conf/dynomite.pem
  data_store: 0
  stats_listen: 192.168.1.221:22222
  read_consistency : DC_QUORUM
  write_consistency : DC_QUORUM

cat vm2.yaml 
dyn_o_mite:
  datacenter: dc-2
  rack: rack1
  dyn_listen: 192.168.1.222:7379
  dyn_seeds:
  - 192.168.1.221:7379:rack1:dc-1:0
  - 192.168.1.223:7379:rack1:dc-3:0
  listen: 0.0.0.0:8379
  servers:
  - 127.0.0.1:6379:1
  tokens: '0'
  secure_server_option: datacenter
  pem_key_file: /home/iadmin/dynomite/conf/dynomite.pem
  data_store: 0
  stats_listen: 192.168.1.222:22222
  read_consistency : DC_QUORUM
  write_consistency : DC_QUORUM

cat vm3.yaml 
dyn_o_mite:
  datacenter: dc-3
  rack: rack1
  dyn_listen: 192.168.1.223:7379
  dyn_seeds:
  - 192.168.1.221:7379:rack1:dc-1:0
  - 192.168.1.223:7379:rack1:dc-2:0
  listen: 0.0.0.0:8379
  servers:
  - 127.0.0.1:6379:1
  tokens: '0'
  secure_server_option: datacenter
  pem_key_file: /home/iadmin/dynomite/conf/dynomite.pem
  data_store: 0
  stats_listen: 192.168.1.223:22222
  read_consistency : DC_QUORUM
  write_consistency : DC_QUORUM

```
