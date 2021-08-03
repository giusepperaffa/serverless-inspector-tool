/**
* @name Identify os.system calls that can cause injection flaws
* @description This query identifies os.system calls without input
*              argument sanitization
* @kind problem
* @problem.severity warning
* @id python/application-os-system-call
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

from DataFlow::CallCfgNode call, DataFlow::ParameterNode p
where
  call = API::moduleImport("os").getMember("system").getACall() and
  TaintTracking::localTaint(p, call.getArg(0))
select call, p.asExpr()

