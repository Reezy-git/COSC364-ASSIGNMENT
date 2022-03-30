import json

def pkt_build(dst, type, body):
    bin_dst = ''.join(format(ord(x), 'b') for x in dst)
    bin_type = ''.join(format(ord(x), 'b') for x in type)
    bin_body = ''.join(format(ord(x), 'b') for x in body)
    return bin_dst + bin_type + bin_body


def pkt_unravel(msg):

    return


print(pkt_build('1', '2', {'1': 0, '2': 5001}))

e = ''
f_table = {'1': (5000, 8), '2': (5001, 2)}
dst = '1'
t = '2'

pkt1 = pkt_build(dst, e, e)
pkt2 = pkt_build(dst, t, json.dumps(f_table).encode('utf8'))
print(pkt1)
print(pkt2)

