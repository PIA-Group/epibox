import os

def create_folder(initial_dir, nb, service):

    directory = os.path.join(initial_dir, nb)
    directory = os.path.join(directory, service)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        print('Created patient directory -- ' + directory)
            
    else:
        print('Directory -- {} -- already exists'.format(directory))

    return directory
