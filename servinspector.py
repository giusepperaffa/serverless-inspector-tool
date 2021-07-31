# ========================================
# Import Python Modules (Standard Library)
# ========================================
import argparse
import os
import re
import sys
import yaml

# =======
# Classes
# =======
class TestLauncherCls:
    # === Class constructor ===
    def __init__(self, ConfigObj):
        self.ConfigObj = ConfigObj
        self.SetDefaultValues()
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
    def SetDefaultValues(self):
        self.ProgramFolderFullPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        # Instance variable containing the full path of the folder where the
        # configuration file for the test execution has to be stored.
        self.ConfigFolderFullPath = os.path.join(self.ProgramFolderFullPath, 'config')
        # Name of the file containing the LGTM Access Token
        self.AccessTokenFileName = 'lgtm_access_token.txt'
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
        elif (self.ConfigObj.target is not None) and (self.ConfigObj.self_test):
            print('--- A self-test on {target} code is about to be launched ---'.format(target=self.ConfigObj.target))
            print('--- No configuration file will be used ---')
            self.ExtractAccessTokenFromFile()
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
    # Create the Namespace object. It contains the parameter passed via command line
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
