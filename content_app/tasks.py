import subprocess

def convert_480p(source):
    target = source + '_480p.mp4'
    
    command = [
        'ffmpeg',          # The executable
        '-i', source,      # Input file
        '-s', 'hd480',     # Scale to 480p
        '-c:v', 'libx264', # Video codec
        '-crf', '23',      # Constant Rate Factor (quality setting)
        '-c:a', 'aac',     # Audio codec
        '-strict', '-2',   # Required for some AAC encoders
        target             # Output file
    ]
    
    try:

        subprocess.run(command, check=True)
        print(f"Successfully converted {source} to {target}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {source}: {e}")

    except FileNotFoundError:
        print("Error: ffmpeg command not found. Make sure ffmpeg is installed and in your system's PATH.")

def convert_720p(source):
    target = source + '_720p.mp4'
    
    command = [
        'ffmpeg',          # The executable
        '-i', source,      # Input file
        '-s', 'hd720',     # Scale to 480p
        '-c:v', 'libx264', # Video codec
        '-crf', '23',      # Constant Rate Factor (quality setting)
        '-c:a', 'aac',     # Audio codec
        '-strict', '-2',   # Required for some AAC encoders
        target             # Output file
    ]
    
    try:

        subprocess.run(command, check=True)
        print(f"Successfully converted {source} to {target}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {source}: {e}")

    except FileNotFoundError:
        print("Error: ffmpeg command not found. Make sure ffmpeg is installed and in your system's PATH.")

def convert_1080p(source):
    target = source + '_1080p.mp4'
    
    command = [
        'ffmpeg',          
        '-i', source,     
        '-s', 'hd1080',    
        '-c:v', 'libx264',
        '-crf', '23',      
        '-c:a', 'aac',    
        '-strict', '-2',   
        target             
    ]
    
    try:

        subprocess.run(command, check=True)
        print(f"Successfully converted {source} to {target}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {source}: {e}")

    except FileNotFoundError:
        print("Error: ffmpeg command not found. Make sure ffmpeg is installed and in your system's PATH.")