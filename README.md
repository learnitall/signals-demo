# signals-demo

Demo of the [state-signals](https://github.com/distributed-system-analysis/state-signals) package for PerfConf 2021! 

Written by Ryan Drew, 2021

## Installing

Requires [minikube](https://minikube.sigs.k8s.io/docs/) cluster running within KVM on a RHEL-based host. Tested on Fedora 34 with minikube v1.23.0 and Python 3.9.6.

To create a minikube cluster and install dependencies for running the demo:

```
$ minikube start --driver=kvm
$ pip install --upgrade pip poetry
$ poetry install --extras demo
```

## Running

The demo is displayed using Jupyter Lab, therefore to get started run on the host run

```
$ poetry run jupyter lab
```

and open `main.ipynb`. This walks though the commands to run the demo. The second-to-last cell contains commented commands, which need to be run in separated terminals. Use the following layout:

```
| Terminal 1 | Terminal 2 |
| Terminal 3 | Terminal 4 |
```

Flow is as follows:

1. Open the terminals and run the appropriate command for each
1. When everything is ready to go, continue the metadata process (type `metadata` in Terminal 1)
1. Then continue the benchmark (type `benchmark` in Terminal 1)
1. Walk through the logs showing execution flow
1. Type `pbench` in Terminal 1 to show the files pbench agent collected
1. Run the last cell to show results in ES
