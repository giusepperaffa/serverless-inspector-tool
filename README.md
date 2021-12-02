# Serverless Inspector Tool
The Serverless Inspector Tool (SI) tool employs the infrastructure and application code [CodeQL](codeql) queries developed as part of this project to enable automated static analysis of serverless applications.

[Architecture](https://github.com/giusepperaffa/serverless-inspector-tool#architecture) and [implementation](https://github.com/giusepperaffa/serverless-inspector-tool#implementation) of the SI tool are explained in the following sections.

It is important to highlight that this tool was developed and tested with Ubuntu Linux 18.04 LTS and Python 3.6.9. No tests were conducted with Windows or Mac OS.

Finally, as detailed in the following table, where **ST** and **TM** stand for **Self-test Mode** and **Test Mode** respectively, the SI makes use of four additional public repositories to support its operating modes, which are further described [below](https://github.com/giusepperaffa/serverless-inspector-tool#architecture).

| GitHub Link | ST | TM |
| :---: | :---: | :---: |
| [si-tool-application-self-test](https://github.com/giusepperaffa/si-tool-application-self-test) | **Yes** | No |
| [si-tool-application-test](https://github.com/giusepperaffa/si-tool-application-test) | No | **Yes** |
| [si-tool-infrastructure-self-test](https://github.com/giusepperaffa/si-tool-infrastructure-self-test) | **Yes** | No |
| [si-tool-infrastructure-test](https://github.com/giusepperaffa/si-tool-infrastructure-test) | No | **Yes** |  

## Architecture
To facilitate its integration into an IDE, the SI tool has been developed in Python with a command-line interface, which implies that it can also be executed, as shown below, by using an independent terminal window.

![Figure 1](images/SIToolExecutionExample.png)

From an architectural point of view, as illustrated in the following diagram, the tool provides an interface towards the [LGTM public API](https://lgtm.com/help/lgtm/api/api-for-lgtm), which allows testing the code included in a given repository with user-specified CodeQL queries. To achieve this, the SI includes a main script (`servinspector.py`), which implements the test execution logic, e.g., the cycle that allows submitting multiple queries, and a Python module (`lgtmreslib.py`) developed by the author to access the above-mentioned API. Separating this functionality from the main script, in fact, facilitates code maintenance and reuse, and it allows creating a generic framework that can be used to run any CodeQL query on a target repository.

![Figure 2](images/SIToolArchitecture.png)

As [previously mentioned](https://github.com/giusepperaffa/serverless-inspector-tool#serverless-inspector-tool), the SI makes use of four additional public repositories to support the following three operating modes:

- *Conversion Mode*. This is the mode to be selected in order to convert YAML files into Python dictionaries defined as literals. The dictionaries are stored in .py files. Such conversion is necessary prior to statically analysing infrastructure code, because CodeQL cannot directly process YAML files.

- *Self-test Mode*. When the self-test mode is chosen, the CodeQL queries, which are all stored within the folder [codeql](codeql), are used to test the files included in either `si-tool-application-self-test` or `si-tool-infrastructure-self-test`. As shown in the execution example above, the self-test repository actually analysed has to be selected with the command-line option `-t`. Note that no external tool configuration file is used in self-test mode.

- *Test Mode*. If the test mode is selected, the CodeQL queries are executed to test one of the repositories included in the configuration file specified via the option `-f`. Similarly to the self-test mode, it is the option `-t` that determines the repository actually scanned. A YAML configuration file template, which currently includes the repositories tested as part of this project, can be found within the folder [config](config). Note that the target repositories are specified within the configuration file via their [LGTM URLs](https://lgtm.com/help/lgtm/adding-projects) and not their GitHub URLs.

A summary of all the command-line options, which can be displayed in the used terminal window by using the `-h` or `--help` option, is provided in the figure below. Finally, it is worth mentioning that, to improve the user interface, the main script includes a mechanism that detects when incompatible options have been specified.

![Figure 3](images/SIToolHelp.png)

## Implementation
After illustrating the [architecture](https://github.com/giusepperaffa/serverless-inspector-tool#architecture) and the configuration options of the SI tool, this section aims at succinctly describing its Python implementation. Before providing additional details, it is important to mention that the author has opted for an object-oriented approach and, consequently, used some of the language features that support this programming paradigm.

The aforementioned main script `servinspector.py` contains a set of auxiliary functions. Among them, the most important one is `ProcessProgramInputs`, which relies on the Python standard library module `argparse` to return an object encapsulating the user-specified configuration options. Such object is then passed to the instance of the class `TestLauncherCls`, which manages the logic of the test execution, e.g., by identifying the target repository, through its method `TestLauncherLogic`. The actual execution of the CodeQL queries, however, takes place thanks to the method `SubmitQueries`. The latter, after creating an instance of the interface class `LGTMAPIInterfaceCls`, included in the module `lgtmreslib`, cyclically submits all the relevant queries and checks for consistency what the LGTM interface returns, raising an exception when necessary with the Python command `assert`.

Thanks to the Python standard library module `logging`, the class `TestLauncherCls` also generates a log file containing the execution time of each query and a test report, which will be stored within the folder `reports` of the repository. Note that this folder is not visible in GitHub as it will always contain files ignored by the version control system, but it will be created in the local version of the repository, where reports files will be generated within subfolders identified via a timestamp. Both log and report files can be deleted by the user with the command-line options `-d` and `-r`.

As regards the above-mentioned `LGTMAPIInterfaceCls` class, it contains a collections of methods that have been implemented according to the [LGTM API documentation](https://lgtm.com/help/lgtm/api/api-v1#LGTM-API-specification-Query-jobs) on *query jobs*. More precisely, after initializing the relevant API endpoints within the constructor, an instance of this class allows obtaining the LGTM project ID (method `GetProjectId`), which identifies the target repository, submitting a query (method `SubmitQuery`), checking the status of its execution (method `GetQueryJobStatus`), and, finally, downloading the test results (method `GetResultsSummary` and method `GetQueryJobResults`). It is important to highlight that each method attempts to send an HTTP request multiple times up to a pre-defined maximum, in order to deal with network glitches or the temporary unavailability of the API endpoints. This mechanism is a noteworthy feature, because it greatly facilitates the use of the interface in client code, such as the script `servinspector.py` of the SI tool.

Finally, using the LGTM API is possible only if an [access token](https://lgtm.com/help/lgtm/api/managing-access-tokens) is provided. This is handled by the method `ExtractAccessTokenFromFile` of the class `TestLauncherCls`, which expects to find in the folder `config` a text file named `lgtm_access_token.txt` with this information reported in its first line.
