# run without SLURM
mpirun -np 4 --mca btl openib,self /srv/singularity/bin/singularity exec /srv/openfoam8.sif rhoPimpleFoam -parallel
