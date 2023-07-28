import shutil

def copy_file(source_file, destination_file):
    try:
        shutil.copy(source_file, destination_file)
        print(f"File '{source_file}' copied to '{destination_file}' successfully.")
    except FileNotFoundError:
        print(f"Source file '{source_file}' not found.")
    except PermissionError:
        print(f"Permission denied. Unable to copy '{source_file}' to '{destination_file}'.")
    except shutil.SameFileError:
        print("Source and destination represent the same file.")
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_image(prompt, save_path):
    destination_file = 'images/' + save_path + '.png'
    source_file = 'sample_image/red_car.png'
    copy_file(source_file, destination_file)

# Usage
# generate_image('', 'red')
    