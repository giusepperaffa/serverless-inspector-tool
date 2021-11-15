/**
* @name Identify potentially unprotected environment information
* @description This query identifies potentially unprotected environment information
*              in the infrastructure code. The query assumes that this information
*              is specified via entries that end with the strings key, secret and
*              token (case insensitive) and that protected information is included
*              by using ${}
* @kind problem
* @problem.severity warning
* @id python/iac-unprotected-environment-information
* @tags security
*/

import python

Dict extract_environment_dict(Dict d) {
  d.getAKey().(StrConst).getText() = "environment"
  and
  result = d.getAValue().(Dict)
}

string extract_environment_key(Dict d){
  result = d.getAKey().(StrConst).getText()
}

string extract_environment_value(Dict d){
  result = d.getAValue().(StrConst).getText()
}

predicate check_key_value_pair(KeyValuePair myKeyValuePair, string myKey, string myValue){
  myKeyValuePair.getKey().(StrConst).getText() = myKey
  and
  myKeyValuePair.getValue().(StrConst).getText() = myValue
}

from Dict d, Dict environmentDict, string environmentKey, string environmentValue
where environmentDict = extract_environment_dict(d) and
environmentKey = extract_environment_key(environmentDict) and environmentKey.regexpMatch("(?si).*(key|secret|token)$") and
environmentValue = extract_environment_value(environmentDict) and (not environmentValue.matches("${%")) and
check_key_value_pair(environmentDict.getAnItem().(KeyValuePair), environmentKey, environmentValue)
select environmentDict, "Identified potentially unprotected environment information - Check key " + environmentKey + " with value " + environmentValue
