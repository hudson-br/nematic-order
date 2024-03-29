#!/usr/bin/env python3
# submit.py

"""
submit.py script.py outdir???? [options]

    Python script for simulation submission to a cluster. It creates submission bash files for Slurm.

    Arguments
    ---------
    script.py : python file
        The script to execute for data analysis. Must be a python script (.py).
    outdir???? : list of directories
        List of directories where the script.py has to be executed. Must contains a .conf file

    Options
    -------
    jobname : optional, string, default : chain
        Name of the job in the queue
    queue : optional, chosen partition, default : debug
        submit will run the script.py in the specified partition.
    nodelist : string, optional, default : ''
        submit to the list of nodes, for instance coste1, coste4, or coste[1-3,5]
    runtime : optional, default : 1-0:00
        maximum running time of the simulation. Syntax is day-hours:minutes:seconds
    cpu_per_task :
    
    ntasks :
    
    nodes :

    Examples
    --------
    1.
        submit.py chain.py queue=bigmem runtime=2-0:00 config????

    Functions

M. Le Verge--Serandour
Adapted from submit.py in cytosim_public
Creation : 28/09/18
"""


import os, sys
import subprocess

jobname = 'shells'

subcmd = 'sbatch'
queue = 'debug'
runtime = '1-0:00'
cpu_per_task = 1
nodes = 2
ntasks = 1
nodelist = ''

#
folder_path = '/lustre/home/hudson.borja/git/Confinement/'
script = '/lustre/home/hudson.borja/git/Confinement/main_Lagrangian.py'
confname = 'config.conf'

mail_warning = True
mail_type = 'ALL'
email_adress = 'hudson.borja-da-rocha@college-de-france.fr'

def write_gen(directories, queue=queue, runtime=runtime, cpu_per_task=cpu_per_task, nodelist='', jobname='chain', ntasks=1, nodes=1, mail_warning=False, email_adress=email_adress, mail_type='ALL') :
    nconfig=len(directories)
    filename='sim.sh'
    f = open(filename, 'w')
    f.write('#!/bin/bash\n')
    
    f.write('#SBATCH --job-name=' + jobname + '\n')
#    f.write('#SBATCH --ntasks=' + str(ntasks) +'\n')
    f.write('#SBATCH --nodes=' + str(nodes) +'\n')
#    f.write('#SBATCH --cpus-per-task=' + str(cpu_per_task) +'\n')
    if len(nodelist) > 0 :
        f.write('#SBATCH --nodelist=' + nodelist + '\n')
    else :
        f.write('#SBATCH --partition=' + queue + '\n')
    f.write('#SBATCH --time=' + runtime + '\n')
    f.write('#SBATCH --mem=2048\n')

#    f.write('#SBATCH --signal=INT@60\n')
#    f.write('#SBATCH --signal=TERM@120\n')

    
    f.write('#SBATCH --mincpus=1'+'\n')
#    f.write('#SBATCH --hint=nomultithread\n')


    f.write('#SBATCH --output=logs/out/out%a.txt\n')
    f.write('#SBATCH --error=logs/err/err%a.txt\n')
    f.write('#SBATCH --array=1-' + str(nconfig) + '\n')
    # Mailing options
    if mail_warning :
        f.write('#SBATCH --mail-type='+mail_type+'\n')
        f.write('#SBATCH --mail-user=' + email_adress + '\n')
    
    f.write('export OPENBLAS_NUM_THREADS=2\n')
    f.write('./job$SLURM_ARRAY_TASK_ID\n')
    
    # Load spack environment
    f.write('source /share/softs/spack/share/spack/setup-env.sh\n')
    
    # Load fenics and dependencies
    f.write('spack load fenics\n')
    f.write('spack load py-h5py\n')
    f.write('spack load gmsh\n')
    
    # Remeshing with mmg
    f.write('spack load mmg\n')
    f.write('export MMG="/share/softs/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.1/mmg-5.4.0-usu764dek3tve4kccjfqlkibhrrechlg/bin"\n')
    
    # For meshio that was installed locally with py-pip
    f.write('export PATH="/lustre/home/hudson.borja/.local/bin:$PATH"\n')
    f.write('python /lustre/home/hudson.borja/git/Confinement/main_Lagrangian.py\n')
    f.close()
    
    # 448 = -rwx------
    os.chmod(filename, 448)
    return filename

def write_s(confname, script, dirconfig, n) :
    #global confname, script
    filename='job' + str(n)
    f = open(filename, 'w')
    f.write('#!/bin/bash\n')
    # Load spack environment
    f.write('source /share/softs/spack/share/spack/setup-env.sh\n')
    f.write('#SBATCH --hint=nomultithread\n')
    # Load fenics and dependencies
    f.write('spack load fenics\n')
    f.write('spack load py-h5py\n')
    f.write('spack load gmsh\n')
    
    # Remeshing with mmg
    f.write('spack load mmg\n')
    f.write('export MMG="/share/softs/spack/opt/spack/linux-centos7-skylake_avx512/gcc-9.3.1/mmg-5.4.0-usu764dek3tve4kccjfqlkibhrrechlg/bin"\n')
    
    # For meshio that was installed locally with py-pip
    f.write('export PATH="/lustre/home/hudson.borja/.local/bin:$PATH"\n')
    f.write('cd ' + dirconfig + '\n')
    f.write('python3 ' + script + ' ' + confname)
    
    # 448 = -rwx------
    os.chmod(filename, 448)
    return 0

def main(args):
    global subcmd, queue, runtime, cpu_per_task, nodes, ntasks, script, confname, nodelist, jobname
    global mail_warning, email, mail_type
    list_dir = []

    for arg in args :
        if arg.endswith('.py') :
            script = os.path.abspath(arg)
        elif arg.startswith('queue=') :
            queue = arg[len('queue='):]
            
        elif arg.startswith('runtime=') :
            runtime = arg[len('runtime='):]
            
        elif arg.startswith('cpu-per-task=') :
            cpu_per_task = int(arg[len('cpu-per-task='):])
            if cpu_per_task < 1 :
                print('Error : too few cpus (0) per task assigned. Variable set to one.')
                cpu_per_task = 1
            elif cpu_per_task > 1 :
                print(str(cpu_per_task) + 'assigned for one task.')

        elif arg.startswith('nodelist=') :
            nodelist = arg[len('nodelist='):]
            
        elif arg.startswith('jobname=') :
            jobname = arg[len('jobname='):]
        
        elif arg.startswith('ntasks=') :
            ntasks = int(arg[len('ntasks='):])
            
        elif arg.startswith('nodes=') :
            ntasks = int(arg[len('nodes='):])
            
        elif arg.startswith('mail_warning=') :
            mail_warning = eval(arg[len('mail_warning='):])
            
        elif arg.startswith('email=') :
            email = arg[len('email='):]
            
        elif arg.startswith('mail_type=') :
            mail_type = arg[len('mail_type='):]
            
        else :
            list_dir += [arg]


    try :
        os.makedirs('logs')
        os.makedirs('logs/err')
        os.makedirs('logs/out')
    except : pass
    
    nconfig = len(list_dir)
    f = write_gen(list_dir, queue=queue, runtime=runtime, cpu_per_task=cpu_per_task, nodelist=nodelist, mail_warning=mail_warning, email_adress=email_adress, nodes=nodes, ntasks=ntasks, mail_type=mail_type, jobname=jobname)
    n = 1
    
    for dirconfig in list_dir :
        list_files = os.listdir(dirconfig)
        for elem in list_files :
            if elem.endswith('.conf') :
                confname = elem
        write_s(confname, script, dirconfig, n)
        n += 1
        
    submitname = 'sim.sh'
    subprocess.call([subcmd + ' ' + submitname], shell = True)


if __name__ == "__main__" :
    if len(sys.argv)<1 or sys.argv[1] == 'help' :
        print(__doc__)
    else :
        if len(sys.argv) > 1 :
            args = sys.argv[1:]
            main(args=args)
        else :
            main()
