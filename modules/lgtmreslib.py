# ========================================
# Import Python Modules (Standard Library)
# ========================================
import inspect
import os
import requests
import time

# =======
# Classes
# =======
class LGTMAPIInterfaceCls:
    # === Class constructor ===
    def __init__(self, ConfigDict):
        self.LGTMProjectURL = ConfigDict['LGTMProjectURL']
        self.AccessToken = ConfigDict['AccessToken']
        # Dictionary containing the main API endpoints
        self.EndPointsDict = {}
        self.EndPointsDict['Projects'] = 'https://lgtm.com/api/v1.0/projects'
        self.EndPointsDict['QueryJobs'] = 'https://lgtm.com/api/v1.0/queryjobs'
        # Default Headers dictionary
        self.HeadersDict = {}
        self.HeadersDict['Accept'] = 'application/json'
        self.HeadersDict['Authorization'] = 'Bearer {token}'.format(token=self.AccessToken)
        # HTTP requests are attempted multiple times in case an exception is raised
        self.MaxAttemptNum = 10
        # Methods with HTTP requests are implemented with a timeout option (seconds)
        self.TimeOut = 15
        self.WaitTimeAfterException = 180
    # === Method ===
    def GetProjectId(self):
        print('--- Method {name} - Start ---'.format(name=inspect.stack()[0][3]))
        # API endpoint corresponding to the specific LGTM project
        self.EndPointsDict['Project'] = self.EndPointsDict['Projects'] + self.LGTMProjectURL.split('/projects')[1]
        print('--- Project-specific endpoint: {endpoint} ---'.format(endpoint=self.EndPointsDict['Project']))
        for AttemptNum in range(1, self.MaxAttemptNum + 1):
            print('--- Attempt number %s ---' % AttemptNum)
            try:
                # HTTP Get request
                Response = requests.get(self.EndPointsDict['Project'], headers=self.HeadersDict, timeout=self.TimeOut)
                StatusCode = Response.status_code
                self.ProjectId = Response.json()['id']
            except Exception as Error:
                print('--- Exception raised - Details: ---')
                print('--- %s ---' % Error)
                print('--- Waiting before new attempt... ---')
                time.sleep(self.WaitTimeAfterException)
            else:
                print('--- HTTP request completed - No more attempts needed ---')
                break
        else:
            # Code in this branch gets executed when the maximum number of attempts has been reached
            print('--- Maximum number of attempts reached ---')
            print('--- The project id was not extracted ---')
            StatusCode = None
            self.ProjectId = None
        return StatusCode, self.ProjectId
    # === Method ===
    def SubmitQuery(self, QueryFileFullPath):
        print('--- Method {name} - Start ---'.format(name=inspect.stack()[0][3]))
        # Specify additional entry within HeadersDict (suggested in the LGTM API docs)
        self.HeadersDict['Content-Type'] = 'text/plain'
        # Parameter dictionary to be used for this HTTP request (query string parameters)
        ParamsDict = {'language': 'python', 'project-id': self.ProjectId}
        # As suggested in the documentation of the requests module at:
        # https://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests
        # it is possible to send data that is not form-encoded by specifying a string
        # for the named argument data of the requests.post function. In this case, such
        # string will contain the .ql file as text
        with open(QueryFileFullPath, mode='r') as FileObj:
            DataStr = FileObj.read()
        for AttemptNum in range(1, self.MaxAttemptNum + 1):
            print('--- Attempt number %s ---' % AttemptNum)
            try:
                # HTTP Post request
                Response = requests.post(self.EndPointsDict['QueryJobs'], params=ParamsDict, headers=self.HeadersDict,\
                    data=DataStr, timeout=self.TimeOut)
                StatusCode = Response.status_code
                self.QueryId = Response.json()['task-result']['id']
            except Exception as Error:
                print('--- Exception raised - Details: ---')
                print('--- %s ---' % Error)
                print('--- Waiting before new attempt... ---')
                time.sleep(self.WaitTimeAfterException)
            else:
                print('--- HTTP request completed - No more attempts needed ---')
                break
        else:
            # Code in this branch gets executed when the maximum number of attempts has been reached
            print('--- Maximum number of attempts reached ---')
            print('--- The query id was not extracted ---')
            StatusCode = None
            self.QueryId = None
        return StatusCode, self.QueryId
    # === Method ===
    def GetQueryJobStatus(self):
        print('--- Method {name} - Start ---'.format(name=inspect.stack()[0][3]))
        # Delete from header dictionary entry needed when submitting a query
        if 'Content-Type' in self.HeadersDict: del self.HeadersDict['Content-Type']
        for AttemptNum in range(1, self.MaxAttemptNum + 1):
            print('--- Attempt number %s ---' % AttemptNum)
            try:
                # HTTP Get request
                Response = requests.get('/'.join([self.EndPointsDict['QueryJobs'], self.QueryId]),\
                    headers=self.HeadersDict, timeout=self.TimeOut)
                StatusCode = Response.status_code
                NumOfPendingQueries = Response.json()['stats']['pending']
            except Exception as Error:
                print('--- Exception raised - Details: ---')
                print('--- %s ---' % Error)
                print('--- Waiting before new attempt... ---')
                time.sleep(self.WaitTimeAfterException)
            else:
                print('--- HTTP request completed - No more attempts needed ---')
                break
        else:
            # Code in this branch gets executed when the maximum number of attempts has been reached
            print('--- Maximum number of attempts reached ---')
            print('--- The number of pending queries was not extracted ---')
            StatusCode = None
            NumOfPendingQueries = None
        return StatusCode, NumOfPendingQueries
    # === Method ===
    def GetResultsSummary(self):
        print('--- Method {name} - Start ---'.format(name=inspect.stack()[0][3]))
        # Delete from header dictionary entry needed when submitting a query
        if 'Content-Type' in self.HeadersDict: del self.HeadersDict['Content-Type']
        for AttemptNum in range(1, self.MaxAttemptNum + 1):
            print('--- Attempt number %s ---' % AttemptNum)
            try:
                # HTTP Get request
                Response = requests.get('/'.join([self.EndPointsDict['QueryJobs'], self.QueryId, 'results']),\
                    headers=self.HeadersDict, timeout=self.TimeOut)
                StatusCode = Response.status_code
                ResultsSummary = Response.json()['data'][0]['status']
            except Exception as Error:
                print('--- Exception raised - Details: ---')
                print('--- %s ---' % Error)
                print('--- Waiting before new attempt... ---')
                time.sleep(self.WaitTimeAfterException)
            else:
                print('--- HTTP request completed - No more attempts needed ---')
                break
        else:
            # Code in this branch gets executed when the maximum number of attempts has been reached
            print('--- Maximum number of attempts reached ---')
            print('--- The results summary was not extracted ---')
            StatusCode = None
            ResultsSummary = None
        return StatusCode, ResultsSummary
    # === Method ===
    def GetQueryJobResults(self):
        print('--- Method {name} - Start ---'.format(name=inspect.stack()[0][3]))
        # Delete from header dictionary entry needed when submitting a query
        if 'Content-Type' in self.HeadersDict: del self.HeadersDict['Content-Type']
        # For details about the parameter dictionary to be passed to this HTTP request,
        # please refer to LGTM API documentation
        ParamsDict = {'nofilter': False}
        for AttemptNum in range(1, self.MaxAttemptNum + 1):
            print('--- Attempt number %s ---' % AttemptNum)
            try:
                # HTTP Get request
                Response = requests.get('/'.join([self.EndPointsDict['QueryJobs'], self.QueryId, 'results', str(self.ProjectId)]),\
                    headers=self.HeadersDict, timeout=self.TimeOut, params=ParamsDict)
                StatusCode = Response.status_code
                ResultsDict = Response.json()
            except Exception as Error:
                print('--- Exception raised - Details: ---')
                print('--- %s ---' % Error)
                print('--- Waiting before new attempt... ---')
                time.sleep(self.WaitTimeAfterException)
            else:
                print('--- HTTP request completed - No more attempts needed ---')
                break
        else:
            # Code in this branch gets executed when the maximum number of attempts has been reached
            print('--- Maximum number of attempts reached ---')
            print('--- The results dictionary was not extracted ---')
            StatusCode = None
            ResultsDict = None
        return StatusCode, ResultsDict
