/**
* @name Identify requests module function calls without parameter sanitization
* @description This query identifies calls to functions included in the requests module 
*              (get and post) without parameter sanitization
* @kind problem
* @problem.severity warning
* @id python/application-requests-function-calls
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

predicate check_module_function(API::Node myNode){
  myNode.toString().matches("%get%") or myNode.toString().matches("%post%")
}

predicate check_named_func_arg(API::Node myNode, DataFlow::ParameterNode myParameterNode){
  TaintTracking::localTaint(myParameterNode, DataFlow::exprNode(myNode.getACall().getArgByName("params").asExpr())) or
  TaintTracking::localTaint(myParameterNode, DataFlow::exprNode(myNode.getACall().getArgByName("data").asExpr()))
}

from API::Node myFunction, DataFlow::ParameterNode p
where myFunction = API::moduleImport("requests").getAMember() and check_module_function(myFunction)
and check_named_func_arg(myFunction, p)
select myFunction.getACall(), p.asExpr()

