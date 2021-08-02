# ========================================
# Import Python Modules (Standard Library)
# ========================================
import argparse
import logging
import os
import re
import sys
import time
import yaml

# =======
# Classes
# =======
class TestLauncherCls:
    # === Class constructor ===
    def __init__(self, ConfigObj):
        self.ConfigObj = ConfigObj
        self.SetDefaultValues()
        self.LogFileSetUp()
        self.TestLauncherLogic()
    # === Method ===
    def ExtractAccessTokenFromFile(self):
        # A regular expression is used to remove all newline characters
        NewLineRegExp = re.compile(r'\n')
        with open(os.path.join(self.ConfigFolderFullPath, self.AccessTokenFileName), mode='r') as AccessTokenFileObj:
            self.AccessToken = NewLineRegExp.sub('', AccessTokenFileObj.read())
    # === Method ===
    def ExtractDictFromConfigFile(self):
        assert os.path.splitext(self.ConfigObj.file)[1] in ('.yml', '.yaml'), \
            '--- Inconsistency detected - The specified configuration file is not a YAML file ---'
        with open(os.path.join(self.ConfigFolderFullPath, self.ConfigObj.file), mode='r') as ConfigFileObj:
            self.ConfigDict = yaml.load(ConfigFileObj)
    # === Method ===
    def GenerateReport(self):
        # Create test execution-specific folder if it does not exist
        TestFolderFullPath = os.path.join(self.ReportsFolderFullPath, 'test_' + self.TestExecId)
        if not os.path.isdir(TestFolderFullPath): os.mkdir(TestFolderFullPath)
        # print('*** Results dictionary to be processed ***')
        # print(self.ResultsDict)
        # print()
        with open(os.path.join(TestFolderFullPath, os.path.splitext(self.QueryFileName)[0] + '.txt') , mode='w') as ReportFileObj:
            ReportFileObj.write(self.DataSep.join(['File', 'URL']) + '\n')
            for NestedList in self.ResultsDict['data']:
                for DataDict in NestedList:
                    try:
                        ReportFileObj.write(self.DataSep.join([DataDict['file'], DataDict['url']]) + '\n')
                        # print(DataDict['file'])
                        # print(DataDict['url'])
                    except KeyError as Error:
                        print('--- The dictionary being processed does not include the key: %s ---' % Error)

    # === Method ===
    def LogFileSetUp(self):
        # The log file basename will be modified by concatenating the test execution id
        LogFileBaseName = 'queries_exec_times'
        logging.basicConfig(filename=LogFileBaseName + '_' + self.TestExecId + '.log', filemode='w',\
            level=logging.INFO, format='%(message)s')
        logging.info(self.DataSep.join(['Query', 'Time(s)']))
    # === Method ===
    def SetDefaultValues(self):
        # Name of the file containing the LGTM Access Token
        self.AccessTokenFileName = 'lgtm_access_token.txt'
        # Data separator (log and report files)
        self.DataSep = '\t'
        # Test execution identifier for log and report log file
        TestExecIdRegExp = re.compile(r'(\s|:)')
        self.TestExecId = '_'.join(TestExecIdRegExp.sub('_', time.ctime().replace('  ', ' ')).split('_')[1:-1]).lower()
        # Full path of the folder where this file is stored
        self.ProgramFolderFullPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        # Full path of the folder where the configuration file is stored
        self.ConfigFolderFullPath = os.path.join(self.ProgramFolderFullPath, 'config')
        # Full path of the folder where the query files are stored
        self.QueryFolderFullPath = os.path.join(self.ProgramFolderFullPath, 'codeql')
        # Full path of the folder where the report files are stored
        self.ReportsFolderFullPath = os.path.join(self.ProgramFolderFullPath, 'reports')
        # Create generic report folder if it does not exist
        if not os.path.isdir(self.ReportsFolderFullPath): os.mkdir(self.ReportsFolderFullPath)
        # LGTM projects used in self-test mode
        self.SelfTestConfigDict = {'LGTMProjectURLs': {}}
        self.SelfTestConfigDict['LGTMProjectURLs']['ApplicationCode'] = 'https://lgtm.com/projects/g/giusepperaffa/serverless-inspector-test/'
        self.SelfTestConfigDict['LGTMProjectURLs']['InfrastructureCode'] = 'https://lgtm.com/projects/g/giusepperaffa/infrastructure-inspector-test/'
        # Timeout parameter (seconds)
        self.TimeOut = 300
        # Wait times (seconds)
        self.WaitTime = 20
        self.WaitTimeAfterException = 120

    # === Method ===
    def SubmitQueries(self, LGTMProjectURL):
        # Create instance of LGTM API interface class
        LGTMAPIConfigDict = {'LGTMProjectURL': LGTMProjectURL, 'AccessToken': self.AccessToken}
        self.LGTMAPIInterfaceObj = lgtmreslib.LGTMAPIInterfaceCls(LGTMAPIConfigDict)
        # The status coe will be returned as an integer
        StatusCode, ProjectId = self.LGTMAPIInterfaceObj.GetProjectId()
        print('--- LGTM Project Id: %s ---' % ProjectId)
        if (StatusCode == 200) and (ProjectId is not None):
            # for QueryFileName in os.listdir(os.path.join(self.QueryFolderFullPath, self.ConfigObj.target)):
            for QueryFileName in ('A',):
                try:
                    print()
                    self.QueryFileName = QueryFileName
                    print('--- Submitting query: %s ---' % self.QueryFileName)
                    QueryStartTime = time.time()
                    # Submit query via interface object
                    # StatusCode, QueryId = self.LGTMAPIInterfaceObj.SubmitQuery(os.path.join(self.QueryFolderFullPath,\
                    #     self.ConfigObj.target, self.QueryFileName))
                    StatusCode, QueryId = self.LGTMAPIInterfaceObj.SubmitQuery('/home/giuseppe/Desktop/Python_Test/codeql/infrastructure/query_iac_multiple_action.ql')
                    # StatusCode, QueryId = self.LGTMAPIInterfaceObj.SubmitQuery('/home/giuseppe/Desktop/Python_Test/codeql/application/query_python_subprocess_shell_true.ql')
                    print('--- Query Id: %s ---' % QueryId)
                    assert (StatusCode == 202), '--- Query submission unsuccessful ---'
                    # Get the number of pending queries
                    StatusCode, NumOfPendingQueries = self.LGTMAPIInterfaceObj.GetQueryJobStatus()
                    # Wait until there is no pending query or a timeout
                    QueryExecutionStartTime = time.time()
                    while (NumOfPendingQueries != 0) and (time.time() - QueryExecutionStartTime <= self.TimeOut):
                        print('--- Waiting until end of query execution... ---')
                        time.sleep(self.WaitTime)
                        StatusCode, NumOfPendingQueries = self.LGTMAPIInterfaceObj.GetQueryJobStatus()
                    print('--- Number of pending queries: %s ---' % NumOfPendingQueries)
                    assert (StatusCode == 200) and (NumOfPendingQueries == 0), '--- Problem detected during the execution of the query ---'
                    # Get query results summary
                    StatusCode, ResultsSummary = self.LGTMAPIInterfaceObj.GetResultsSummary()
                    print('--- Results summary: %s ---' % ResultsSummary)
                    assert (StatusCode == 200) and (ResultsSummary == 'success'), '--- Problem detected in the results summary ---'
                    # Get query results
                    StatusCode, self.ResultsDict = self.LGTMAPIInterfaceObj.GetQueryJobResults()
                    QueryEndTime = time.time()
                    logging.info(self.DataSep.join([QueryFileName, str(QueryEndTime - QueryStartTime)]))
                    # Generate report containing query results
                    self.GenerateReport()
                except Exception as Error:
                    print('--- Exception raised - Details: ---')
                    print('--- %s ---' % Error)
                    print('--- Waiting before submitting new query... ---')
                    time.sleep(self.WaitTimeAfterException)
        else:
            print('--- HTTP request unsuccessful - No project id retrieved ---')
            print('--- No query will be submitted ---')
    # === Method ===
    def TestLauncherLogic(self):
        if self.ConfigObj.conversion is not None:
            print('--- YAML file => Python dictionary conversion is about to start ---')
            print('--- Source Folder Full Path: {Src} ---'.format(Src=self.ConfigObj.conversion[0]))
            print('--- Source Folder Full Path: {Dst} ---'.format(Dst=self.ConfigObj.conversion[1]))
            YamlToDictConverter(self.ConfigObj.conversion[0], self.ConfigObj.conversion[1])
        elif self.ConfigObj.delete_logs:
            print('--- All log files are about to be deleted ---')
            RemoveFilesFromFolder(self.ProgramFolderFullPath, '.log')
        elif (self.ConfigObj.target is not None) and (self.ConfigObj.file is not None):
            print('--- A test on {target} code is about to be launched ---'.format(target=self.ConfigObj.target))
            print('--- Configuration file full path: {path} ---'.format(path=\
                os.path.join(self.ConfigFolderFullPath, self.ConfigObj.file)))
            self.ExtractAccessTokenFromFile()
            self.ExtractDictFromConfigFile()
            print('--- LGTM Project URL: {url} ---'.format(url=\
                self.ConfigDict['LGTMProjectURLs'][self.ConfigObj.target.capitalize() + 'Code']))
            self.SubmitQueries(self.ConfigDict['LGTMProjectURLs'][self.ConfigObj.target.capitalize() + 'Code'])
        elif (self.ConfigObj.target is not None) and (self.ConfigObj.self_test):
            print('--- A self-test on {target} code is about to be launched ---'.format(target=self.ConfigObj.target))
            print('--- No configuration file will be used ---')
            self.ExtractAccessTokenFromFile()
            self.SubmitQueries(self.SelfTestConfigDict['LGTMProjectURLs'][self.ConfigObj.target.capitalize() + 'Code'])
        else:
            print('--- The input arguments configuration is inconsistent - No test will be launched ---')

# =========
# Functions
# =========
def ProcessProgramInputs():
    ParserObj = argparse.ArgumentParser()
    # Create group of mutually exclusive options
    ModeGroupParserObj = ParserObj.add_mutually_exclusive_group(required=True)
    ModeGroupParserObj.add_argument('-c', '--conversion', action='store', type=str, nargs=2, metavar=('src', 'dst'), \
        help='Conversion - Source folder full path with YAML files and destination folder full path must be specified')
    ModeGroupParserObj.add_argument('-d', '--delete-logs', action='store_true', \
        help='Delete log files - All log files (*.log) within the program folder will be deleted')
    ModeGroupParserObj.add_argument('-t', '--target', action='store', type=str, metavar='target', \
        help="Target - Specifies whether the tool will be used to test infrastructure code ('infrastructure') or \
        application code ('application')", choices=['infrastructure', 'application'])
    # Create group of mutually exclusive options
    ConfigGroupParserObj = ParserObj.add_mutually_exclusive_group(required=False)
    ConfigGroupParserObj.add_argument('-f', '--file', action='store', type=str, metavar='file', \
        help='File - Configuration file name used when the self-test mode is disabled')
    ConfigGroupParserObj.add_argument('-s', '--self-test', action='store_true', \
        help='Self-test - The CodeQL queries will be tested against code samples provided with this tool')
    # Return the Namespace object. It contains the parameters passed via command line
    return ParserObj.parse_args()

def RemoveFilesFromFolder(FolderFullPath, FileExtension):
    for Elem in (FltFile for FltFile in os.listdir(FolderFullPath) if FltFile.endswith(FileExtension)):
        print('--- File {name} is about to be deleted ---'.format(name=Elem))
        os.remove(os.path.join(FolderFullPath, Elem))

def YamlToDictConverter(YamlFolderFullPath, PyFolderFullPath):
    """
    YamlFolderFullPath: Full path of the folder where all the .yml files to be converted are stored
    PyFolderFullPath: Full path of the folder where all the generated .py files are stored
    """
    for FileName in (FltFileName for FltFileName in os.listdir(YamlFolderFullPath) if os.path.splitext(FltFileName)[1] in ('.yml', '.yaml')):
        print('--- Processing file: %s ---' % FileName)
        # Create file object that yaml.load() will map into a nested Python dictionary
        with open(os.path.join(YamlFolderFullPath, FileName), mode='r') as YamlFileObj:
            InfrastructureDict = yaml.load(YamlFileObj)
        # Create .py file containing a comment and an assignment statement with the obtained dictionary
        with open(os.path.join(PyFolderFullPath, os.path.splitext(FileName)[0] + '.py'), mode='w') as PyFileObj:
            CommentString = 'Infrastructure Dictionary'
            PyFileObj.write('\n'.join(['# ' + ('=' * len(CommentString)), '# ' + CommentString, '# ' + ('=' * len(CommentString))]) + '\n')
            PyFileObj.write('InfrastructureDict = ' + str(InfrastructureDict))

# ====
# Main
# ====
if __name__ == '__main__':
    # Include folder where custom modules are stored in the Python search path
    ModulesFolderName = 'modules'
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ModulesFolderName))
    # Import custom modules
    try:
        import lgtmreslib
    except Exception as Error:
        print('--- Exception raised while importing custom modules - Details: ---')
        print('--- %s ---' % Error)
    # Create instance of class TestLauncherCls which implements the program logic
    TestLauncherObj = TestLauncherCls(ProcessProgramInputs())
