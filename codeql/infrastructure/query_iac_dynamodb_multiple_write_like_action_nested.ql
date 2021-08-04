/**
* @name Identify multiple write-like dynamodb actions configuration with iam nested syntax
* @description This query identifies when multiple write-like dynamodb actions are specified
*              in the infrastructure code (nested iam syntax used)
* @kind problem
* @problem.severity warning
* @id python/iac-dynamodb-multiple-write-like-action-nested-syntax
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

predicate check_action_key(Dict d) {
  d.getAValue().(List).getAnElt().(Dict).getAKey().(StrConst).getText() = "Action"
  and
  count(string myElem | myElem = d.getAValue().(List).getAnElt().(Dict).getAValue().(List).getAnElt().(StrConst).getText() and myElem.matches("dynamodb:Update%") | myElem) > 1 
}

from Dict d, Dict extractedDict
where extractedDict = check_iam_key(d, "iam", "role", "statements") and check_effect_key(extractedDict) and check_action_key(extractedDict)
select d,  "Identified multiple write-like dynamodb actions configuration" 
