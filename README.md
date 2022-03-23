<h1 align="justify">
A Parallel and Distributed Framework Focused into Computing-Intensive Applications For Partial Computation Reuse Estimation 
</h1>

<div style="display: inline-block;">
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg"/> 

<img align="center" height="20px" width="80px" src="https://github.com/mpiress/midpy/blob/main/imgs/passing.svg"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Made%20for-VSCode-1f425f.svg"/> 
</div>

<p align="justify">
In the proposed framework, executions are performed under a modular workflow. In such a workflow, applications are executed as extensions, and a series of wrappers are used to adapt the execution contexts and automated computation reuse estimation. We explore the wrappers through specialized routines and address execution contexts, extending them in a dispatcher/worker architecture model. In such a scheme, while a dispatcher introduces an automated computation reuse estimation based on task overlap, a worker pool manages a series of workers, each performing an application replica with cache support. Figure 1 shows an overview of the framework structure.
</p>

<p> </p>
<p> </p>

![Build Status](https://github.com/mpiress/midpy/blob/main/imgs/architecture.png)

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

Free Software!