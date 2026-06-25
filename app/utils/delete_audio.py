import os

def remove_audio_files() -> None:
    folder = r"C:\AI EVO (Journey)\EVO - rebirth\audio"
    files = os.listdir(folder)
    if len(files)!=0:
        for file_ in files:
            os.remove(os.path.join(folder,file_))
    else:
        pass
    return None