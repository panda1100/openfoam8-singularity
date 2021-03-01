"""
HPCCM recipe for OpenFOAM 8 Singularity image (MPI)
Contents:
  Ubuntu 20.04
  GNU compilers (upstream)
  OpenMPI
  OFED/MOFED
  PMI2 (SLURM)
Generating recipe (stdout):
  $ hpccm --recipe openfoam8.py --format singularity --singularity-version=3.7 > openfoam8.def
"""
from hpccm.templates.git import git


os_version = '20.04'
openfoam_version = '8'
openmpi_version = '2.1.1'
ofed_version = '4.9-2.2.4.0'

# Ubuntu base image
Stage0 += baseimage(image='ubuntu:{}'.format(os_version), _as='build')

# OpenFOAM Dependencies
ospackages = [  'software-properties-common', 'gpg-agent', 'ca-certificates', 'time', 'wget', 'git', 'build-essential', 'cmake',
                'libfl-dev', 'flex', 'bison', 'zlib1g-dev',
                'libqt5x11extras5-dev', 'qtbase5-dev', 'qttools5-dev',
                'gnuplot', 'libreadline-dev', 'libncurses5-dev',
                'libxt-dev', 'libboost-system-dev', 'libboost-thread-dev', 'libgmp-dev',
                'libmpfr-dev', 'python', 'python-dev', 'libcgal-dev', 'curl']
Stage0 += apt_get(ospackages=ospackages)

# (M)OFED
Stage0 += mlnx_ofed(version=ofed_version)

# UCX
#Stage0 += ucx(cuda=False, ofed=True)

# PMI2
Stage0 += slurm_pmi2()

# OpenMPI
Stage0 += openmpi(
                cuda=False,
                infiniband=True,
                pmi='/usr/local/slurm-pmi2',
                ucx=False,
                version=openmpi_version)

# OpenFOAM
Stage0 += shell(commands=[
	'mkdir -p /opt/OpenFOAM',
	'cd /opt/OpenFOAM',
	git().clone_step(repository='https://github.com/OpenFOAM/OpenFOAM-8.git',
			branch='master', path='/opt/OpenFOAM'),
	git().clone_step(repository='https://github.com/OpenFOAM/ThirdParty-8.git',
			branch='master', path='/opt/OpenFOAM'),
        r"sed -i '45,46s/^/# /g' /opt/OpenFOAM/OpenFOAM-8/etc/bashrc",
        r"sed -i 's@^export FOAM_INST_DIR=$HOME/$WM_PROJECT@# export FOAM_INST_DIR=$HOME/$WM_PROJECT@' /opt/OpenFOAM/OpenFOAM-8/etc/bashrc",
	r"sed -i 's@^# export FOAM_INST_DIR=/opt/$WM_PROJECT@export FOAM_INST_DIR=/opt/$WM_PROJECT@' /opt/OpenFOAM/OpenFOAM-8/etc/bashrc",
        r"sed -i '229s/^/# /g' /opt/OpenFOAM/OpenFOAM-8/etc/bashrc",
	])

Stage0 += shell(commands=[
        'alias wmRefresh="echo blah"',  #https://github.com/willgpaik/openfoam5_aci/blob/master/Singularity.of5x, https://github.com/hpcng/singularity/issues/4445
        '. /opt/OpenFOAM/OpenFOAM-8/etc/bashrc FOAMY_HEX_MESH=yes',
	'cd $WM_PROJECT_DIR',
	'export QT_SELECT=qt5',
	'./Allwmake -j 6 2>&1 | tee log.make',
	'./Allwmake -j 6 2>&1 | tee log.make'
	])

Stage0 += shell(commands=['echo ". /opt/OpenFOAM/OpenFOAM-8/etc/bashrc FOAMY_HEX_MESH=yes" >> $SINGULARITY_ENVIRONMENT'])

