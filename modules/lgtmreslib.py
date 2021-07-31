import os
import requests

# ==================
# Generic Parameters
# ==================
# My projects in LGTM currently are:
# -) https://lgtm.com/projects/g/giusepperaffa/serverless-inspector-test/
# -) https://lgtm.com/projects/g/giusepperaffa/infrastructure-inspector-test/

# This is my access token named ServerlessInspectorToken (see LGTM account)
LGTMAccessToken = "f0b46f5ea3ff6b53a0d2bb77e750fb25bc455a084b732444e0395b3f0a901ef7"

# Dictionary containing all the used API endpoints
EndPointsDict = {}
EndPointsDict['Projects'] = 'https://lgtm.com/api/v1.0/projects' # Too generic - all LGTM projects are returned!
# The following two entries include specific information about my projects
EndPointsDict['InfrastructureTestProject'] = 'https://lgtm.com/api/v1.0/projects/g/giusepperaffa/infrastructure-inspector-test'
EndPointsDict['ServerlessTestProject'] = 'https://lgtm.com/api/v1.0/projects/g/giusepperaffa/serverless-inspector-test'
# Endpoint to be used for query jobs
EndPointsDict['QueryJobs'] = 'https://lgtm.com/api/v1.0/queryjobs'

# ===============================================
# Case 1 - Obtain information about LGTM projects
# ===============================================
# Dictionary specifying headers
HeadersDict = {}
HeadersDict['Accept'] = 'application/json'
HeadersDict['Authorization'] = 'Bearer {token}'.format(token=LGTMAccessToken)
# HTTP Get request
Response = requests.get(EndPointsDict['ServerlessTestProject'], headers=HeadersDict)
# Display data
print(Response.status_code)
print(Response.json())
# You can obtain the project id (necessary for query jobs) as follows:
print(Response.json()['id'])
ProjectId = Response.json()['id']

# ==================================================
# Case 2 - Submit a query to run on one LGTM project
# ==================================================
# # Parameter dictionary to be used for this HTTP request (query string parameters)
# # Note that the ProjectId parameter was obtained with the previous HTTP request
# ParamsDict = {'language': 'python', 'project-id': ProjectId}
# # Specify additional entry within HeadersDict (suggested in the LGTM API docs)
# HeadersDict['Content-Type'] = 'text/plain'
# # Query file name
# FileName = 'query_python_subprocess_shell_true.ql'
# # As suggested in the documentation of the requests module at:
# # https://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests
# # it is possible to send data that is not form-encoded by specifying a string
# # for the named argument data of the requests.post function. In this case, such
# # string will contain the .ql file as text
# with open(os.path.join(os.path.curdir, 'codeql', 'application', FileName), mode='r') as FileObj:
#     DataStr = FileObj.read()
# # HTTP Post request
# Response = requests.post(EndPointsDict['QueryJobs'], params=ParamsDict, headers=HeadersDict, data=DataStr)
# # Display data
# print('*** Case 2: ***')
# print(Response.status_code)
# print(Response.json())
# print(Response.request.headers)
# print('This is the query id: {id}'.format(id=Response.json()['task-result']['id']))
# QueryId = Response.json()['task-result']['id']

# ======================================
# Case 3 - Get the status of a query job
# ======================================
# Modify HeadersDict for this new request
# del HeadersDict['Content-Type'] # COMMENT IN IF CASE 3 IS EXECUTED AFTER CASE 2
# Note that the QueryId parameter was obtained with the previous HTTP request
# Response = requests.get('/'.join([EndPointsDict['QueryJobs'], QueryId]), headers=HeadersDict)
Response = requests.get('/'.join([EndPointsDict['QueryJobs'], '980091792887948541']), headers=HeadersDict)
# Display data
print('*** Case 3: ***')
print(Response.status_code)
print(Response.json())
print(Response.request.headers)
print('Pending query: {pending}'.format(pending=Response.json()['stats']['pending']))

# =====================================
# Case 4 - Provide a summary of results
# =====================================
Response = requests.get('/'.join([EndPointsDict['QueryJobs'], '980091792887948541','results']), headers=HeadersDict)
# Display data
print('*** Case 4: ***')
print(Response.status_code)
print(Response.json())
print(Response.request.headers)
print('Status information: {status}'.format(status=Response.json()['data'][0]['status']))

# =========================================
# Case 5 - Fetch the results of a query job
# =========================================
ParamsDict = {'nofilter': False}
Response = requests.get('/'.join([EndPointsDict['QueryJobs'], '980091792887948541','results', str(ProjectId)]), \
    headers=HeadersDict, params=ParamsDict)
print('*** Case 5: ***')
print(Response.status_code)
print(Response.json())
print(Response.request.headers)