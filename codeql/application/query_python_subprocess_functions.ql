/**
* @name Identify subprocess module function calls that can cause injection flaws
* @description This query identifies calls to functions included in the subprocess module
*              (call, check_output and getoutput) without input sanitization
* @kind problem
* @problem.severity warning
* @id python/application-subprocess-function-calls
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

predicate check_module_function(API::Node myNode){
  myNode.toString().matches("%call%") or myNode.toString().matches("%check_output%") or myNode.toString().matches("%getoutput%")
}

from API::Node myFunction, DataFlow::ParameterNode p
where myFunction = API::moduleImport("subprocess").getAMember() and check_module_function(myFunction)
and TaintTracking::localTaint(p, myFunction.getACall().getArg(0))
select myFunction.getACall(), p.asExpr()

