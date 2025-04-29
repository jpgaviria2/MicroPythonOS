import binascii
import os
import sys

try:
    input_file = sys.argv[1]
except IndexError:
    print('No file or directory given using current working directory')
    input_file = os.getcwd()
    

def run(in_file):
    output_file = os.path.splitext(in_file)[0] + '.py'

    ext = os.path.splitext(in_file)[1][1:]

    with open(in_file, 'rb') as f:
        data = f.read()

    data = binascii.hexlify(data)
    data = ['    ' + str(data[i: min(i + 74, len(data))])[1:] for i in range(0, len(data), 74)]
    data = '\n'.join(data)

    output = f'''\
import binascii

_{ext} = bytearray(binascii.unhexlify(
{data}
))
{ext} = memoryview(_{ext})
'''

    with open(output_file, 'w') as f:
        f.write(output)


if os.path.isdir(input_file):
    for file in os.listdir(input_file):
        file_ext = os.path.splitext(file)[1][1:]
        if file_ext not in ('bmp', 'jpg', 'gif', 'png', 'bin', 'MF'):
            continue
        
        thisfile = os.path.join(input_file, file)
        print('found file:', thisfile)
        run(thisfile)

else:
    file_ext = os.path.splitext(input_file)[1][1:]
    if file_ext not in ('bmp', 'jpg', 'gif', 'png', 'bin'):
        raise RuntimeError('supported image files are bmp, jpg, gif and png')
    print('found file:', input_file)
    run(input_file)

print('DONE!!')
