<h1 align="justify">
A Parallel and Distributed Framework Focused into Computing-Intensive Applications For Partial Computation Reuse Estimation 
</h1>

<div style="display: inline-block;">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white"/> 
<img align="center" height="20px" width="60px" src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Made%20for-VSCode-1f425f.svg"/> 
<a href="https://github.com/mpiress/midpy/issues">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"/>

<img align="center" height="20px" width="80px" src="https://badgen.net/badge/license/MIT/green"/>
</a> 
</div>

<p> </p>
<p> </p>

<p align="justify">
In an important class of applications, while the tasks are performed, a large number of partial computations are produced. In such a context, each task's partial computations employ data input elements extensively as part of their processing, which makes them costly. For performance reasons, a typical optimization introduces a cache to supply common computations for similar tasks. Thus, partial computations with high overlap can be reused, which leads to a considerable reduction in processing during the execution.
</p>

<p align="justify">
In this framework, the applications mentioned above are performed through a workflow based on a dispatcher and a pool of workers model. Each worker employs wrappers classes that allow extending applications and a cache. We explore the wrappers through specialized routines, which users deploy to describe the application's method calls and cache behavior. Thus, while the dispatcher automated computation reuse, the worker pool manages a series of workers according to the computational environment available, executing application replicas with cache support. Figure 1 shows an overview of the framework structure.
</p>

<p> </p>
<p> </p>

![Build Status](https://github.com/mpiress/midpy/blob/main/imgs/architecture.png)

<p align="justify">
As observed in Figure 1, a series of stages to manipulate the input tasks into the dispatcher are introduced. These stages are structured as a workflow in which input tasks are organized into pre-defined chunk sizes, reordered based on an affinity strategy, and submitted to execution. As support, the dispatcher creates and manages temporary queues, and workers consume such queues in an on-demand manner, according to a relationship identification between queues and workers.
</p>

<p align="justify">
On each worker, ...
</p>


## Features

<p align="justify">
- Sequential and Parallel Executions Using Python and C/C++ For Applications Description 
</p>
<p align="justify">
- Cache space evaluation for different replacement policies without modifications into execution and application 
</p>
<p align="justify">
- An intuitive workflow to introduces and evaluates novel task orchestrations 
</p>
<p align="justify">
- Independence from computational architecture and operating system to manage and execute multiple workers 
</p>
<p align="justify">
- Flexible structure for on-demand adaptations, enabling the study of different computational scenarios without changing the application execution model
</p>

## Plugins

## Development

## Docker

## License

GPL

## Contacts