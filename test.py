import sys

fn = sys.argv[1]

dims = set()

cnt = 0 
with open(fn) as f:
    for line in f:
        cnt += 1
        line = line.split(' ')
        d = len(line) - 1
        dims.add(d)
        if cnt % 10000 == 0:
            print(cnt)
print('Number of diff dims = %d' % len(dims))
