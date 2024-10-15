import os
import json
import sys

HEADER_SIZE = 4377  # longueur de l'en-tête

def write_header(output_stream, header, data_file_path):
    # Créer un en-tête à partir des informations fournies
    name = header['name'].ljust(255, '\x00').encode()
    

    real_size = os.stat(data_file_path).st_size
    if not real_size == header['size'] :
        print(f"File: {data_file_path}, not matching size: {real_size} != {header['size']}")
        size_str = str(real_size).ljust(14, '\x00').encode()
    else:
        # Vérifier que la taille est valide avant de la convertir
        size_str = str(header['size']).ljust(14, '\x00').encode() #if header['size'] else b'\x00' * 14

    m_time = header['mTime'].ljust(12, '\x00').encode()  # 12 caractères pour le temps
    prefix = header['prefix'].ljust(HEADER_SIZE - 255 - 14 - 12, '\x00').encode()  # Remplir le reste
    
    # Écrire l'en-tête dans le fichier de sortie
    output_stream.write(name + size_str + m_time + prefix)

def recreate_binary(output_dir, output_file):
    # Lire les en-têtes depuis le fichier JSON
    with open(os.path.join(output_dir, 'headers.json'), 'r') as json_file:
        headers = json.load(json_file)

    with open(output_file, 'wb') as output_stream:
        for header in headers:

            # Lire le fichier de données et l'écrire dans le fichier de sortie
            data_file_path = os.path.join(output_dir, header['prefix'], header['name'])
            with open(data_file_path, 'rb') as data_file:
                data = data_file.read()
                # Écrire l'en-tête
                write_header(output_stream, header, data_file_path)
                # Écrire les données
                output_stream.write(data)

        # Ajouter le HEADER_CHUNK_EOF à la fin du fichier
        output_stream.write(bytes(HEADER_SIZE))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python repack.py path_to_folder path_to_output_wpress_file")
        sys.exit(1)

    output_directory = sys.argv[1]
    output_binary_file = sys.argv[2]

    recreate_binary(output_directory, output_binary_file)
    print(f'New wpress file : {output_binary_file}')
