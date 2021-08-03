/**
* @name Identify multiple resources configuration with iam nested syntax
* @description This query identifies when multiple resources are specified
*              in the infrastructure code (nested iam syntax used)
* @kind problem
* @problem.severity warning
* @id python/iac-multiple-resources-nested-syntax
* @tags security
*/

import python

Dict check_iam_key(Dict d, string keyValueLevelOne, string keyValueLevelTwo, string keyValueLevelThree) {
  d.getAValue().(Dict).getAKey().(StrConst).getText() = keyValueLevelOne
  and
  d.getAValue().(Dict).getAValue().(Dict).getAKey().(StrConst).getText() = keyValueLevelTwo
  and
  d.getAValue().(Dict).getAValue().(Dict).getAValue().(Dict).getAKey().(StrConst).getText() = keyValueLevelThree
  and
  result = d.getAValue().(Dict).getAValue().(Dict).getAValue().(Dict)
}

predicate check_effect_key(Dict d) { 
  d.getAValue().(List).getAnElt().(Dict).getAKey().(StrConst).getText() = "Effect"
  and
  d.getAValue().(List).getAnElt().(Dict).getAValue().(StrConst).getText() = "Allow"
}

predicate check_resource_key(Dict d) {
  d.getAValue().(List).getAnElt().(Dict).getAKey().(StrConst).getText() = "Resource"
  and  
  count(string myString | myString = d.getAValue().(List).getAnElt().(Dict).getAValue().(List).getAnElt().(StrConst).getText() and myString.matches("arn:%*") | myString) >= 1 
}

from Dict d, Dict extractedDict
where extractedDict = check_iam_key(d, "iam", "role", "statements") and check_effect_key(extractedDict) and check_resource_key(extractedDict)
select d,  "Identified multiple resources configuration"

