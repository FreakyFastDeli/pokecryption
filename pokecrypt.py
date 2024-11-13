from src.cryption import generate_keys, save_keys, get_keys, encrypt_binary, decrypt_binary
from src.poke import PokeServer

if __name__ == "__main__":
    api = PokeServer()
    
    while True:
        user_input = input("What would you like to do?\n1 : Generate Keys\n2 : Encrypt\n3 : Decrypt\nSelect option number (1 to 3) or type 'exit' to quit: ")
        if user_input == '1':
            p = input("Enter the name of the first pokemon: ")
            q = input("Enter the name of the second pokemon: ")
            name = input("Enter the name of the key: ")
            save_keys(*generate_keys(p, q), name)
        elif user_input == '2':
            file_name = input("Enter the name of the file you would like to encrypt: ")
            public_key = get_keys(input("Enter the name of the public key: "))[1]
            encrypt_binary('./unencrypted/' + file_name, './encrypted/' + file_name, public_key)
        elif user_input == '3':
            file_name = input("Enter the name of the file you would like to decrypt: ")
            private_key = get_keys(input("Enter the name of the private key: "))[0]
            decrypt_binary('./encrypted/' + file_name, './decrypted/' + file_name, private_key)
        elif user_input.lower() == 'exit' or user_input.lower() == 'quit' or user_input.lower() == 'q':
            break