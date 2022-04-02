<h1 align="justify">
A Parallel and Distributed Framework Focused on Computing-Intensive Applications For Partial Computation Reuse Estimation and Optimization
</h1>

<div style="display: inline-block;">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/Maintained%3F-yes-green.svg"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white"/> 
<img align="center" height="20px" width="60px" src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white"/> 
<img align="center" height="20px" width="80px" src="https://img.shields.io/badge/Made%20for-VSCode-1f425f.svg"/> 
<a href="https://github.com/mpiress/midpy/issues">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat"/>
</a> 
<img align="center" height="20px" width="80px" src="https://badgen.net/badge/license/MIT/green"/>
</div>

<p> </p>
<p> </p>

<p align="justify">
In an important class of applications, while the tasks are performed, a large number of partial computations are produced. In such a context, each task's partial computations employ data input elements extensively as part of their processing, which makes them costly. For performance reasons, a typical optimization introduces a cache to supply common computations for similar tasks. Thus, partial computations with high overlap can be reused, which leads to a considerable reduction in processing during the execution.
</p>

<p align="justify">
In this framework, the applications mentioned above are performed through a workflow based on a dispatcher and a pool of workers model. Each worker employs wrappers classes that allow extending applications and a cache. We explore the wrappers using specialized routines, which users deploy to describe the application's method calls and cache behavior. Thus, while the dispatcher automated computation reuse, the worker pool manages a series of workers according to the computational environment available, executing application replicas with cache support. Figure 1 shows an overview of the framework structure.
</p>

<p> </p>
<p> </p>

![Build Status](https://github.com/mpiress/midpy/blob/main/imgs/framework_workflow.png)

<p align="justify">
As observed in Figure 1, a series of stages to manipulate the input tasks into the dispatcher are introduced. These stages are structured as a workflow in which input tasks are organized into pre-defined chunk sizes, reordered based on an affinity strategy, and submitted to execution. As support, the dispatcher creates and manages temporary queues, and workers consume such queues in an on-demand manner, according to a relationship between queues and workers.
</p>

<p align="justify">
On each worker, cache space is instantiated to coordinate common partial computations. Each cache space is designed to use typical replacement policies, such as Least Recently Used (LRU), and it is defined into the wrappers, side by side with the applications' routine calls. Predefined configurations address how tasks are read, workers are executed, and which policy and cache size is adopted.
</p>

<p align="justify">
The dispatcher and worker poll workflow make the execution flexible, which favors observing the application's behavior for different numbers of workers and cache sizes. Towards such flexibility, we address the framework through the following abstractions: (i) user descriptors, (ii) application and resources, (iii) composites descriptors, and (iv) kernel. Figure 2 reports the modularization introduced in the framework.
</p>

<p align="center">
<img src="https://github.com/mpiress/midpy/blob/main/imgs/modularization.png" width="70%" height="70%">
</p>

<p align="justify">
According to support modularization (i.e., Figure 2), four components describe the general workflow structure. In <b>user descriptors</b> flexible patterns are provided, allowing the description on how input tasks are read/written and which application routines are called. In <b>composite</b>, abstract resources are introduced to manipulate and deploy task affinity strategies and cache replacement policies without modifying the execution process. In addition, the <b>reduce</b> component describes how results are composed based on the requirements of the application. The <b>application/resources</b> and <b>kernel</b> are static and unmodified modules.
</p>

<p align="justify">
To compose executions according to the scheme presented in Figure 2, the dispatcher extends the abstraction of the mapper, which instantiates an affinity optimizer to reorder tasks in <img src="https://render.githubusercontent.com/render/math?math=T"/>. Tasks in <img src="https://render.githubusercontent.com/render/math?math=T"/> are evaluated in batches with predefined fixed sizes and distributed for workers according to the the task optimizer policy. This distribution is balanced, allowing each worker to operate on chunks of tasks with similar sizes. 
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

# Contatos

<div style="display: inline-block;">
<a href="https://t.me/michelpires369">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/> 
</a>

<a href="https://www.linkedin.com/in/michelpiressilva/">
<img align="center" height="20px" width="90px" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

</div>

<a style="color:black" href="mailto:michel@cefetmg.br?subject=[GitHub]%20Source%20Dynamic%20Lists">
✉️ <i>michel@cefetmg.br</i>
</a>