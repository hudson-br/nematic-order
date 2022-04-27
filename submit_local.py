import os


path = '/Users/morpho/TURLIERLAB Dropbox/Hudson Rocha/Postdoc/git/viscous_shell-Paper_Complete/data/'
os.chdir(path)
os.system("../gen_config.py ../config.conf.tpl pname=contractility_strength pvalue='np.linspace(1,20,39)'")

for i in range(0, 39):
    os.chdir(path + 'run00' + str(i).zfill(2) )
    cwd = os.getcwd()
    print(cwd)
    os.system('python ../../main.py')