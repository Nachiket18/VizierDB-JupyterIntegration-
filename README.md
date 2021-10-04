

# VizierDB-JupyterIntegration
The repository contains code that will be used for VizierDB project as a component to convert the Jupyter Notebook in to Vizier accepted format

# Pipeline

The software process to calculate the variable dependencies is build in Python using 'ast' module. The overview of the components in pipleine is decribed below.

1. **Parse_notebook** - In this component each code cell from input notebook is scanned and calls to the _AST_ component are made in order to fetch the variable assignment and access information. Using this information the dependencies between variables both intra-cell and inter cell are captured and a dependency graph is generated. 
2. **AST** - This component takes the input source code and passes it to the class designated for generating and traversing the AST for the source code and captures the variable assignment while keeping track of the scope of the variable. Scope can be main program flow , loops , functions or control flow.   
3. **Parallelism Metric** - Once the dependency graph is generated, this component captures the maximum - depth subgraph which signifies the longest chain of inter - cell dependencies. This value when divided with total number of cells gives the general idea about whether the it is useful to perform the parallelism.
