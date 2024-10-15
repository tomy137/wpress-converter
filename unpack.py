import os
import sys
import struct
import shutil
import json
import traceback

HEADER_SIZE = 4377  # length of the header
HEADER_CHUNK_EOF = bytes(HEADER_SIZE)  # Empty header used for check if we reached the end

def is_dir_empty(dirname):
    return len(os.listdir(dirname)) == 0

def read_from_buffer(buffer, start, end):
    _buffer = buffer[start:end]
    # Trim off the empty bytes
    return _buffer.split(b'\x00', 1)[0].decode()

def read_header(fd):
    header_chunk = fd.read(HEADER_SIZE)

    # Reached end of file
    if header_chunk == HEADER_CHUNK_EOF:
        print('Reached end of file')
        return None

    name = read_from_buffer(header_chunk, 0, 255)
    size = int(read_from_buffer(header_chunk, 255, 269))
    m_time = read_from_buffer(header_chunk, 269, 281)
    prefix = read_from_buffer(header_chunk, 281, HEADER_SIZE)

    return {
        'name': name,
        'size': size,
        'mTime': m_time,
        'prefix': prefix,
    }

def read_block_to_file(fd, header, output_path):
    output_file_path = os.path.join(output_path, header['prefix'], header['name'])
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'wb') as output_stream:
        total_bytes_to_read = header['size']
        while total_bytes_to_read > 0:
            bytes_to_read = min(512, total_bytes_to_read)
            buffer = fd.read(bytes_to_read)
            output_stream.write(buffer)
            total_bytes_to_read -= len(buffer)

def wp_extract(input_file, output_dir, override=False):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f'Input file at location "{input_file}" could not be found.')

    if override:
        shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)
    else:
        if os.path.exists(output_dir) and not is_dir_empty(output_dir):
            raise Exception(f'Output dir is not empty. Clear it first or use the --force option to override it.')

    headers = []  # List to store headers
    with open(input_file, 'rb') as input_fd:
        count_files = 0
        zero_byte_count = 0
        file_size = os.stat(input_file).st_size
        print(f'File size: {file_size}')
        last_header = {}
        while True:
            header = read_header(input_fd)
            if not header:
                break

            headers.append(header)  # Store header information
            read_block_to_file(input_fd, header, output_dir)
            count_files += 1
            last_header = header


        # Print the offset of the end of the file
        print(f'End offset for {last_header["name"]}: {input_fd.tell()}')

        if input_fd.tell() < file_size:
            zero_byte_count = file_size - input_fd.tell()

    print(f'Number of trailing zero bytes: {zero_byte_count}')

    # Write headers to a JSON file
    with open(os.path.join(output_dir, 'headers.json'), 'w') as json_file:
        json.dump(headers, json_file, indent=4)

    return count_files

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python unpack.py wpfile path_to_extract")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    try:
        count_files = wp_extract(input_file, output_dir, override=True)
        print(f'Extracted {count_files} files. Headers saved to {os.path.join(output_dir, "headers.json")}.')
    except Exception as e:
        print(f'Error: {e}')
        print(traceback.format_exc())