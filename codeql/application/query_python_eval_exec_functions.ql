/**
* @name Identify calls to built-in functions eval() and exec() that can cause injection flaws
* @description This query identifies calls to built-in functions eval() and exec()
*              without input sanitization
* @kind problem
* @problem.severity warning
* @id python/application-eval-exec-function-calls
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

predicate check_builtin_function(API::Node myNode){
  myNode.toString().matches("%eval%") or myNode.toString().matches("%exec%")
}

from API::Node myFunction, DataFlow::ParameterNode p
where myFunction = API::builtin(_) and check_builtin_function(myFunction)
and TaintTracking::localTaint(p, myFunction.getACall().getArg(0))
select myFunction.getACall(), p.asExpr()

