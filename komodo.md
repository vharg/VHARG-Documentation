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


## Alternative softwares
You can install softwares that allow you to browse and interact with your files on Komodo. Options include:
- [Cyberduck](https://cyberduck.io) on MacOS
- [WinSCP](https://winscp.net/eng/download.php) on Windows