<h1 align="justify">
A Parallel and Distributed Framework For Partial Computation Reuse Optimization Focused on Computing-intensive Applications
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
In an essential class of compute-intensive applications, while a series of independent tasks are executed, a large number of partial computations are performed. In such a process, each task's partial computations extensively employ data input elements as part of their processing, making them costly. To reduce computational impacts with overlapped data input elements, a typical optimization introduces a cache as support for similar tasks with common computations. Thus, costly partial computations with high overlap can be reused, which leads to a considerable reduction in processing during the application execution. Furthermore, it is common for such compute-intensive applications conducting cache optimization concurrently with parallel and distributed executions for performance reasons. 
</p>

<p align="justify">
Although the applications mentioned earlier benefit from optimizations such as cache and parallel and distributed execution models, similar tasks should perform close to each other. Otherwise, each task's expressive partial computations lead to a reduction of optimizations capability. In addition, such optimizations require adjustments in applications and their execution model, which makes caching and parallel executions challenging to employ. To solve this challenge, in the proposed framework, the applications are performed using a workflow based on a dispatcher and a pool of workers model. Each worker operates wrappers classes that allow extending applications and a cache without modifying the application execution model. We explore the wrappers using specialized routines, which users deploy to describe the application's method calls and cache behavior. Thus, while the dispatcher automated computation reuse, the worker pool manages a series of workers according to the computational environment available, executing application replicas with cache support. Figure 1 shows an overview of the framework structure.
</p>

<p> </p>
<p> </p>

![Build Status](https://github.com/mpiress/midpy/blob/main/imgs/framework_workflow.png)

<p align="justify">
As observed in Figure 1, a series of stages to manipulate the input tasks into the dispatcher is introduced. These stages are structured as a workflow in which input tasks are organized into pre-defined chunk sizes, reordered based on an affinity strategy, and submitted to execution. As support, the dispatcher creates and manages temporary queues, and workers consume such queues in an on-demand manner, according to the relationship between queues and workers, which is pre-established using unique identifiers.
</p>

<p align="justify">
On each worker, cache space is instantiated to coordinate common partial computations. Each cache space uses typical replacement policies, such as Least Recently Used (LRU), and it is defined in the wrappers, side by side with the applications' routine calls. Pre-defined configurations address how tasks are read, how workers are executed, and which policy and cache size are adopted.
</p>

<p align="justify">
The dispatcher and worker poll workflows make the execution flexible, which favors observing the application's behavior for different numbers of workers and cache sizes. Towards such flexibility, we address the framework through the following abstractions: (i) user descriptors, (ii) application and resources, (iii) composites descriptors and (iv) kernel. Figure 2 reports the modularization introduced in the framework.
</p>

<p align="center">
<img src="https://github.com/mpiress/midpy/blob/main/imgs/modularization.png" width="70%" height="70%">
</p>

<p align="justify">
According to support modularization (i.e., Figure 2), four components describe the general workflow structure. In <b>user descriptors</b>, flexible patterns are provided, allowing the description of how input tasks are read/written and which application routines are called. The <b>composite</b>, abstract resources are introduced to manipulate and deploy task affinity strategies and cache replacement policies without modifying the execution process. In addition, the <b>reduce component</b> describes how results are composed based on the application's requirements. The <b>application/resources</b> and <b>kernel</b> are static and unmodified modules.
</p>

<p align="justify">
To compose executions according to the scheme presented in Figure 2, the dispatcher extends the abstraction of the mapper, which instantiates an affinity optimizer to reorder tasks in <img src="https://render.githubusercontent.com/render/math?math=T"/>. Tasks in <img src="https://render.githubusercontent.com/render/math?math=T"/> are evaluated in batches with pre-defined fixed sizes and distributed to workers according to the task optimizer policy. This distribution is balanced, allowing each worker to operate on chunks of tasks with similar sizes.
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

## Docker

<p align="justify">
In this framework, the Python TensorFlow library is used to model a siamese neural network as an option to analyze similarities between tasks. So, in the last framework version, GPU support is needed for performance reasons. We provide a Dockerfile (i.e., folder docker into the project) to prepare a dispatcher computation environment quickly. In this Dockerfile, Python and GPU dependencies can be configured before execution. However, such an extension is not required if the computational environment is appropriately configured for that neural network model with Python. 
</p>

## Plugins
<p align="justify">
Because the framework performing in Python (version 3.x), there are some extension libraries are needed. The relationship of such libraries is reported into docker folder by the requeriments file. For updating Python to use there, is necessary executing above step:
</p>

```python
pip install -r requeriments.txt 
```

## Development

<p align="justify">
The last version of the framework makes it possible to execute applications in Python, C, and C++. The applications developed in C and C++ should be adapted, using the boost python as reported in python boost library <a href="https://www.boost.org/doc/libs/1_64_0/libs/python/doc/html/index.html">here</a>.  After adjustments made, the result of the compilation (i.e., the dot file so) should be saved in lib/x64 before execution. Furthermore, the user need to develop a wrapper, which it is saved in the applications folder.  Notice by examples available that such wrapper extends the <b>BaseWorkerInfo</b>, the core framework library that links applications and workers' executions. In addition to the method required by the applications, a function must be implemented according to the defined pattern. 
</p>

```python
def execute_task(self, task):
```

<p align="justify">
The execution function receives a task from the worker and performs the application methods. After the application method executions, the results are returned to the worker, which sends them to the dispatcher for acting in the reduce step, which can be modified as needed, rewriting them in the reduce folder. The final results are produced by the dispatcher, saving them by CSV files after each execution.
</p>

<p align="justify">
Once applications and reduction models are defined as needed, the executions are initiated through patterns described in the workflow folder. There are a master and worker.py and an internal folder for each application with necessary scripts. A config.py is defined to compose the experimental behavior in the inner folder. The test, training, and cache warm-up datasets are described in such a file. The scheduler strategy, the number of tasks by chunk, and cache behavior parameters are defined too as part of the definitions. Finally, information about server port, number of workers, and workers initialized by computational note (i.e., wpool) are described. Besides the config.py, a descriptor.py file deals with the rules used for reading and writing into datasets during the experiments.
</p>

<p align="justify">
Two examples are provided as part of the framework to report the rules that compose an execution. We describe the <i>Lazy Associative Classification (LAC)</i> and <i>Large-Scale Microscopy Image Analysis Workflow (Nscale)</i>. A Python implementation is proposed to develop the LAC implementation (i.e., lac.py). Another hand, in the NScale, a hybrid strategy is used, partly deployed in C++, which is performed by a Python wrapper.
</p>

## Contatos

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