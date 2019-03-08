# Introduction to computer clusters

Heavy computations are performed on a computer *cluster*. Clusters comprise different *nodes*, which are racks containing multiple CPUs. The aim of *parallel computing* is to split heavy computation across a large number of CPUs in order to reduce the computation time. The computer cluster at ASE is called *Komodo*.

A cluster is composed of a *master* node, which is what you will interact with, and *slave* nodes. The role of the master node is to dispatch the computing tasks, called *jobs*, to the slave nodes. No heavy computation takes place on the master node.


## Introduction to Komodo
### Connection to Komodo
You will work *remotely* on Komodo and will have access only to a command line environement. Connecting to Komodo is done using `ssh`. In a terminal, type:

```
ssh userName@komodo.ase.ntu.edu.sg
```

Upon entering your password, you will be connected to your `HOME` folder, which will be empty. Note that if you connect from outside NTU, you will need to install the NTU [VPN](https://ntuvpn.ntu.edu.sg/dana-na/auth/url_default/welcome.cgi).

### Jobs
*Jobs* are model runs that are *submitted* to the master node, which will dispatch it to the slave nodes for computations. Upon submission, the job joins a *queue* that manages which nodes are available. Three commands are useful:
- `qsub`: Submits the job. Each job is assigned a `job ID`, for instance `96326`
- `qstat`: Shows the jobs that are running on the cluster. To see only your own jobs, use `qstat -u userName`. Jobs can be in either of these four modes:
  - `R`: Running
  - `C`: Cancelled
  - `Q`: Queued - i.e. the job is delayed in the queue because all the nodes are busy
  - `E`: Ending
- `qdel`: Deletes a given job, use as `qdel jobID`

#### Job submission
Each model requires a slightly different submission, but the general idea is that a *bash* file (extention `.sh`) needs to be submitted using the `qsub` command. The relevant bash file is provided separately for each model, but job submissions usually follow:
```
qsub batchFile.sh
```

#### Tracking errors
Errors are recorded in a *log* file located in `~/jobId.komodo2.des.OU`. If there is a problem with the job, i.e. the job rapidly changes from `Q` to `R` to `C`, checking the log file is likely to help identifying the error.

## Accessing remote files

### Using a graphical interface
Third-party softwares can be used to browse and interact with your files on Komodo. Options include:
- [Cyberduck](https://cyberduck.io) on MacOS
- [WinSCP](https://winscp.net/eng/download.php) on Windows