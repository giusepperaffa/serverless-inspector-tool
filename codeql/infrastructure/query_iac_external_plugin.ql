/**
* @name Identify configuration with external plugin(s)
* @description This query identifies when one or more plugins are specified
*              in the infrastructure code
* @kind problem
* @problem.severity warning
* @id python/iac-external-plugin
* @tags security
*/

import python

int check_plugins_key(Dict d) {
  result = count(string myKey, Expr myPluginName | myPluginName = d.getAValue().(List).getAnElt() and myKey = d.getAKey().(StrConst).getText() and myKey = "plugins"  | myPluginName)
}

from Dict d, int pluginNumber
where pluginNumber = check_plugins_key(d) and pluginNumber > 0
select d, "Identified configuration with " + pluginNumber + " external plugin(s) - Check for security vulnerabilities"

