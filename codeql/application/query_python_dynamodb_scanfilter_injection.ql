/**
* @name Identify plausible dynamodb injection flaws
* @description This query checks if 1) a dynamodb client is initialized and
*              2) if a method with a ScanFilter named argument affected by
*              a handler input is called. A ScanFilter named argument is
*              typically used when scanning a dynamodb table. This query
*              implements only a plausibility check, as the data flow between
*              the dynamodb client initialization and the dynamodb table
*              scan is not checked.
* @kind problem
* @problem.severity warning
* @id python/application-dynamodb-plausible-injection-flaw
* @tags security
*/

import python
import semmle.python.dataflow.new.TaintTracking
import semmle.python.ApiGraphs

from DataFlow::CallCfgNode moduleFunctionCall, DataFlow::CallCfgNode methodCall, DataFlow::ParameterNode p
where
	moduleFunctionCall = API::moduleImport("boto3").getMember("client").getACall() and
	moduleFunctionCall.getArg(0).asExpr().(StrConst).getText() = "dynamodb" and
	TaintTracking::localTaint(p, methodCall.getArgByName("ScanFilter"))
select moduleFunctionCall, methodCall, p.asExpr(), "Plausible dynamodb injection flaw identified"

