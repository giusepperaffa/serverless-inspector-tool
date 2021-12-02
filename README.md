# Serverless Inspector Tool
The Serverless Inspector Tool (SI) tool employs the infrastructure and application code [CodeQL](https://github.com/giusepperaffa/serverless-inspector-tool/tree/main/codeql) queries developed as part of this project to enable automated static analysis of serverless applications.

[Architecture](https://github.com/giusepperaffa/serverless-inspector-tool#architecture) and [implementation](https://github.com/giusepperaffa/serverless-inspector-tool#implementation) of the SI tool are explained in the following sections.

It is important to highlight that this tool was developed and tested with Ubuntu Linux 18.04 LTS and Python 3.6.9. No tests were conducted with Windows or Mac OS.

## Architecture
To facilitate its integration into an IDE, the SI tool has been developed in Python with a command-line interface, which implies that it can also be executed, as shown in [Fig. 1](Figure 1), by using an independent terminal window.

![Figure 1](images/SIToolExecutionExample.png)

From an architectural point of view, as illustrated in [Fig. 2](Figure 2), the tool provides an interface towards the [LGTM public API](https://lgtm.com/help/lgtm/api/api-for-lgtm), which allows testing the code included in a given repository with user-specified CodeQL queries. To achieve this, the SI includes a main script (`servinspector.py`), which implements the test execution logic, e.g., the cycle that allows submitting multiple queries, and a Python module (`lgtmreslib.py`) developed by the author to access the above-mentioned API. Separating this functionality from the main script, in fact, facilitates code maintenance and reuse, and it allows creating a generic framework that can be used to run any CodeQL query on a target repository.

![Figure 2](images/SIToolArchitecture.png)

## Implementation
