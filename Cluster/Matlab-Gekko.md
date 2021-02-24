# Matlab in parallel on Gekko

Trying to run Eduardo's Carey and Sparks model on Gekko has finally shed some light on how to use Matlab on a cluster. Here I was also using a job array, where each array ID represents a different volcano.

The critical thing is that the node requested in `.pbs` file is just a **dummy** node used to submit the Matlab job. We only need one worker and one CPU:

```shell
#PBS -l select=1:ncpus=1
``` 

The job is now calling the Matlab function/script and the success here is a balance between the **number of CPUs** and the **number of nodes**. Originally, I was assuming that all the CPUs of a given job should take place on the same node, but apparently not! So the key is to call `parcluster` and set `c.AdditionalProperties.ProcsPerNode = 4`, which means that the Matlab job will use a maximum of `4` CPUs on any given node, but **without being restricted to a single one**. So if `parpool` is called using `parpool(32)`, `parcluster` will look for `8` available nodes with `4` free CPUs.


```matlab
c = parcluster;
c.AdditionalProperties.ProcsPerNode = 4

% ... %

p = c.parpool(32);
```

## PBS File

Submit the job using `qsub -J 1-40 myJob.pbs`, where the `.pbs` file should look something like that:

```shell
## Job Name
#PBS -N VEI3

## Project Funding Code E,g. eee_userid
#PBS -P eos_susanna.jenkins
## Queue  Name
#PBS -q q32_eos

## Send email to yourself. Replace the email to your own email.
#PBS -M sbiasse@ntu.edu.sg

## Specify walltime in HH:MM:SS
#PBS -l walltime=48:00:00

## Select 1 hosts (nodes)
#PBS -l select=1:ncpus=1

## Load the Application
module load matlab/R2019b

## Run mpi program
cd $PBS_O_WORKDIR

## Retrieve job array
volcIdx=$PBS_ARRAY_INDEX

## Run matlab
matlab -nodisplay -logfile $PBS_JOBID.log -batch "runVEI3 $volcIdx"

```

## Matlab file

The Matlab file should start with this:

```matlab
% Retrieve the job ID and convert it
function runAll(iV)
iV = str2double(iV);

% ... %

c = parcluster;
c.AdditionalProperties.ProjectCode = 'eos_susanna.jenkins';
c.AdditionalProperties.QueueName = 'q32_eos';
c.AdditionalProperties.WallTime = '48:00:00';
c.saveProfile % Note 1
c.AdditionalProperties.ProcsPerNode = 4
c.Jobs.delete % Note 2

% Note 3
[~,tname] = fileparts(tempname);
tfolder = fullfile(c.JobStorageLocation,tname);
mkdir(tfolder)
c.JobStorageLocation = tfolder;
cobj = onCleanup(@()rmdir(tfolder));

% Start the parpool
p = c.parpool(32);
```

### Notes

1. It is apparently only necessary to set these `AdditionalProperties` and `saveProfile` once - unless another configuration is required.
2. Not sure if this is still required, but it is just to make sure that no jobs are running simultaneously
3. This comes from the whole debugging part I had with Raymond from Mathworks in 2020. It seems to give me error when I remove it, so I am just keeping it for now
