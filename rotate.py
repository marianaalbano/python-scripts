import os
import tarfile
import shutil
from datetime import datetime
    

# encontra os arquivos
def search_file(dir):
    filenames = [dir+entry for entry in os.listdir(dir) if os.path.isfile(os.path.join(dir,entry))]
    return filenames

# faz o tar.gz, manda pro diretorio de destino e zera o arquivo original
def zip_file(files, source_dir):
    for file in files:
        if "log" in file:
            date = datetime.now()
            date = date.strftime("%y%m%d%H%M")

            log_name = file.replace(".log", date)
            with tarfile.open(log_name+".tar.gz", "w:gz") as tar_handle:
                tar_handle.add(file)
                tar_handle.close()
            shutil.move(log_name+".tar.gz", source_dir)

            with open(file, "w") as f:
                f.truncate()
                f.close()



if __name__ == "__main__":
    path_from = search_file("path/to/")
    path_to = "/path/to/"
    zip_file(path_from, path_to)