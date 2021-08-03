/**
* @name Identify event data returned not sanitized
* @description This query identifies when a handler input argument
*              is returned without being sanitized
* @kind problem
* @problem.severity warning
* @id python/application-event-data-returned-not-sanitized
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

from Return returnStmt, DataFlow::ParameterNode p
where TaintTracking::localTaint(p, DataFlow::exprNode(returnStmt.getValue()))
select returnStmt, p.asExpr()

