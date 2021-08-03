/**
* @name Identify functions triggered by HTTP events
* @description This query identifies functions triggered by HTTP events in the
*              infrastructure code. The rationale behind this query is to
*              encourage the user to check the API Gateway configuration
* @kind problem
* @problem.severity warning
* @id python/iac-functions-triggered-via-http
* @tags security
*/

import python

Dict extract_functions_dict(Dict d){
  d.getAKey().(StrConst).getText() = "functions"
  and
  result = d.getAValue().(Dict).getAValue().(Dict)
}

int http_events_counter(Dict d) {
  result = count (string myKeyOne, string myKeyTwo | myKeyOne = d.getAKey().(StrConst).getText() and
    myKeyTwo = d.getAValue().(List).getAnElt().(Dict).getAKey().(StrConst).getText() and myKeyOne = "events" and
    myKeyTwo = "http" | myKeyOne)
}

from Dict d, Dict extractedDict, int httpEventCounter
where extractedDict = extract_functions_dict(d) and httpEventCounter = http_events_counter(extractedDict) and httpEventCounter > 0 
select extractedDict, "Identified functions triggered by HTTP events - Check API Gateway configuration"

