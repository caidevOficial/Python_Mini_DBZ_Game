import os

class ModuleInstaller:
    
    def __make_command() -> str:
        statement =\
            'py' if os.name in ['ce', 'nt', 'dos']\
            else 'python3'
        full_statement = f'{statement}  -m pip install -r requirements.txt'
        return full_statement
    
    @staticmethod
    def run_command():
        os.system(ModuleInstaller.__make_command())