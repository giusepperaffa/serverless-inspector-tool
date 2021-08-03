/**
* @name Identify subprocess module function calls that can cause code execution via shell
* @description This query identifies calls to functions included in the subprocess module
*              without input sanitization and named argument shell set to True
* @kind problem
* @problem.severity warning
* @id python/application-subprocess-function-calls-shell-true
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

from DataFlow::CallCfgNode call, DataFlow::ParameterNode p
where call = API::moduleImport("subprocess").getAMember().getACall() and call.getArgByName("shell").asExpr().toString() = "True"
and TaintTracking::localTaint(p, call.getArg(0))
select call, p.asExpr()

