/**
* @name Identify multiple read-like dynamodb actions configuration
* @description This query identifies when multiple read-like dynamodb actions are specified
*              in the infrastructure code
* @kind problem
* @problem.severity warning
* @id python/iac-dynamodb-multiple-read-like-action
* @tags security
*/

import python

predicate check_iam_key(Dict d) {
  d.getAValue().(Dict).getAKey().(StrConst).getText() = "iamRoleStatements"
}

predicate check_effect_key(Dict d) {
  d.getAValue().(Dict).getAValue().(Dict).getAKey().(StrConst).getText() = "Effect"
  and
  d.getAValue().(Dict).getAValue().(Dict).getAValue().(StrConst).getText() = "Allow"
}

predicate check_action_key(Dict d) {
  d.getAValue().(Dict).getAValue().(Dict).getAKey().(StrConst).getText() = "Action"
  and
  forall(string myElem | myElem = d.getAValue().(Dict).getAValue().(Dict).getAValue().(List).getAnElt().(StrConst).getText() | myElem.matches("dynamodb:Get%"))
}
  
from Dict d
where check_iam_key(d) and check_effect_key(d) and check_action_key(d)
select d, "Identified multiple read-like dynamodb actions configuration"

