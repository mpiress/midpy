import shutil

PATH = '/Users/michel/Doutorado/MidPy/'

def clear_all():
    global PATH
    loc = ['applications/', 'applications/lac/', 'applications/nscale/']
    
    for p in loc:
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['cache/', 'cache/replacement_policies/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['containers/', 'containers/wrapper/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['core/', 'core/managers/', 'core/network/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['lib/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['neural_network/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['schedulers/', 'schedulers/basedrn/', 'schedulers/batch/', 'schedulers/ondemand/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)

    loc = ['utils/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)


    loc = ['workflow/', 'workflow/lac/', 'workflow/nscale/', 'workflow/lac/scripts/', 'workflow/nscale/scripts/']
    for p in loc: 
        shutil.rmtree(PATH + p + '__pycache__', ignore_errors=True)
        shutil.rmtree(PATH + p + '.DS_Store', ignore_errors=True)


    
if __name__ == '__main__':
	clear_all()
