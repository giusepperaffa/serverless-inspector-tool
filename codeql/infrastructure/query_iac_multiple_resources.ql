/**
* @name Identify multiple resources configuration
* @description This query identifies when multiple resources are specified
*              in the infrastructure code
* @kind problem
* @problem.severity warning
* @id python/iac-multiple-resources
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

predicate check_resource_key(Dict d) {
  d.getAValue().(Dict).getAValue().(Dict).getAKey().(StrConst).getText() = "Resource"
  and
  d.getAValue().(Dict).getAValue().(Dict).getAValue().(StrConst).getText().matches("arn%*")
}
  
from Dict d
where check_iam_key(d) and check_effect_key(d) and check_resource_key(d)
select d, "Identified multiple resources configuration"

