import os
import zipfile
import glob
import uuid

class Compression:
    def compress_candidates(self, buffer):
        '''Get last 3 generated files and compress them'''
        files_path = os.path.join(buffer, '*')

        compressed_filename = os.path.join(buffer, f'{str(uuid.uuid1())}.zip')
        # compression = zipfile.ZIP_DEFLATED
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
        file_names = [file for file in files if not file.endswith('.zip')]
        file_names = file_names[:3]

        with zipfile.ZipFile(compressed_filename, 'w') as zipf: 
            for file in file_names: 
                zipf.write(os.path.join(file), os.path.relpath(os.path.join(file), buffer))

        for file in file_names: 
            os.remove(file)

        self.cleanup(buffer)


    def decompress_candidates(self, buffer, storage):
        files_path = os.path.join(buffer, '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
        file_names = [file for file in files if file.endswith('.zip')]
        file_name = file_names[0]

        with zipfile.ZipFile(file_name, 'r') as zip: 
            zip.printdir() 
            zip.extractall(os.path.join(storage))


    def cleanup(self, buffer):
        ''' Delete first files created if there's more than 15'''
        files_amount_limit = 15
        files_path = os.path.join(buffer, '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime)
        file_names = [file for file in files if file.endswith('.zip')]
        if len(file_names) > files_amount_limit:
            files_excess = len(file_names) - files_amount_limit
            for file in file_names[:files_excess]:
                os.remove(file)