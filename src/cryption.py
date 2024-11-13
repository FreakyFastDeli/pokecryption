import base64
import os
import sys
from src.poke import PokeServer

def generate_keys(p_poke="pidgeotto", q_poke="ekans"):
    api = PokeServer()
    p = api.get_id_from_mon(p_poke)
    q = api.get_id_from_mon(q_poke)
    if not is_prime(p) or not is_prime(q):
        print("**** ERROR p and q must be prime numbers, please choose prime pokemon ****")
        exit(1)
    n = p * q
    if n < 256:
        print("**** ERROR n must be greater than 255, please choose pokemon with bigger IDs ****")
        exit(1)
    if n > 1025:
        print("**** ERROR n must be less than 1025, please choose pokemon with smaller IDs ****")
    phi = (p - 1) * (q - 1)
    e = 17
    d = pow(e, -1, phi)
    e_poke = api.get_mon_from_id(e)
    d_poke = api.get_mon_from_id(d)
    n_poke = api.get_mon_from_id(n)
    return ((e_poke, n_poke), (d_poke, n_poke))

def save_keys(public_key, private_key, key_name='key'):
    key_path = './keys/' + key_name
    os.makedirs(os.path.dirname(key_path + '.pub'), exist_ok=True)
    with open(key_path + '.pub', 'w') as file:
        file.write(f"{public_key[0]}\n{public_key[1]}")
    with open(key_path, 'w') as file:
        file.write(f"{private_key[0]}\n{private_key[1]}")

def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def write_binary_file(file_path, data):
    with open(file_path, 'wb') as file:
        file.write(data)

def get_max_block_size(n):
    block_size = 1
    while True:
        if (256 ** (block_size + 1) - 1) < n:
            block_size += 1
        else:
            break
    return block_size

def bytes_to_blocks(data, block_size):
    blocks = []
    for i in range(0, len(data), block_size):
        block = 0
        for j in range(block_size):
            if (i + j) < len(data):
                block = (block << 8) + data[i + j]
            else:
                block = (block << 8)
        blocks.append(block)
    return blocks

def encrypt_blocks(blocks, public_key):
    e, n = public_key
    return [pow(block, e, n) for block in blocks]

def decrypt_blocks(encrypted_blocks, private_key, block_size):
    d, n = private_key
    decrypted_blocks = [pow(block, d, n) for block in encrypted_blocks]
    return decrypted_blocks

def blocks_to_bytes(blocks, block_size):
    data = bytearray()
    for block in blocks:
        for _ in range(block_size):
            byte = block & 0xFF 
            data.append(byte)   
            block = block >> 8  
    return bytes(data)

def rsa_encrypt(data, public_key):
    e, n = public_key
    block_size = get_max_block_size(n)
    blocks = bytes_to_blocks(data, block_size)
    encrypted_blocks = encrypt_blocks(blocks, public_key)
    return encrypted_blocks, block_size

def rsa_decrypt(encrypted_blocks, private_key, block_size):
    decrypted_blocks = decrypt_blocks(encrypted_blocks, private_key, block_size)
    decrypted_data = blocks_to_bytes(decrypted_blocks, block_size)
    return decrypted_data

def is_base64_encoded(data):
    try:
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False

def is_prime(n):
    for i in range(2, (n//2)+1):
        if (n % i) == 0:
            return False
    else:
        return True

def encrypt_binary(input_path, output_path, public_key_poke):
    try:
        api = PokeServer()
        public_key = api.get_id_from_mon(public_key_poke[0]), api.get_id_from_mon(public_key_poke[1])
        data = read_binary_file(input_path)
    except Exception as e:
        print(f"Error reading input file '{input_path}': {e}")
        return

    if is_text_file(input_path):
        data = encode_data_to_base64(data)
    try:
        encrypted_blocks, block_size = rsa_encrypt(data, public_key)
    except Exception as e:
        print(f"Error during encryption: {e}")
        return

    try:
        encrypted_data = ' '.join([str(block_size)] + [str(block) for block in encrypted_blocks])
    except Exception as e:
        print(f"Error preparing encrypted data: {e}")
        return

    try:
        with open(output_path, 'w') as file:
            file.write(encrypted_data)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")

def decrypt_binary(input_path, output_path, private_key_poke):
    try:
        api = PokeServer()
        private_key = api.get_id_from_mon(private_key_poke[0]), api.get_id_from_mon(private_key_poke[1])
        with open(input_path, 'r') as file:
            data = file.read().strip().split()
    except Exception as e:
        print(f"Error reading encrypted file '{input_path}': {e}")
        return

    if not data:
        print("Encrypted file is empty.")
        return

    try:
        block_size = int(data[0])
    except ValueError:
        print("Invalid block size in encrypted file.")
        return

    try:
        encrypted_blocks = list(map(int, data[1:]))
    except ValueError:
        print("Encrypted blocks contain non-integer values.")
        return

    try:
        decrypted_data = rsa_decrypt(encrypted_blocks, private_key, block_size)
    except Exception as e:
        print(f"Error during decryption: {e}")
        return

    if is_base64_encoded(decrypted_data):
        try:
            decrypted_data = decode_data_from_base64(decrypted_data)
        except Exception as e:
            print(f"Error decoding Base64 data: {e}")
            return
    try:
        write_binary_file(output_path, decrypted_data)
    except Exception as e:
        print(f"Error writing to output file '{output_path}': {e}")


def get_keys(name='key'):
    public_key_path = os.path.join('./keys', f"{name}.pub")
    private_key_path = os.path.join('./keys', name)
    try:
        with open(public_key_path, 'r') as file:
            e, n = map(str, file.read().strip().split())
        with open(private_key_path, 'r') as file:
            d, n = map(str, file.read().strip().split())
        return (e, n), (d, n)
    except Exception as e:
        print(f"Error reading keys: {e}")
        sys.exit(1)

def is_text_file(filepath, encoding='utf-8'):
    try:
        with open(filepath, 'r', encoding=encoding) as file:
            file.read()
        return True
    except UnicodeDecodeError:
        return False
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return False

def encode_data_to_base64(data_bytes):
    try:
        encoded_data = base64.b64encode(data_bytes)
        return encoded_data
    except Exception as e:
        print(f"Error during Base64 encoding: {e}")
        raise

def decode_data_from_base64(data_bytes):
    try:
        decoded_data = base64.b64decode(data_bytes)
        return decoded_data
    except Exception as e:
        print(f"Error during Base64 decoding: {e}")
        raise
