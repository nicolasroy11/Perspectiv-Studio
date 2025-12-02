class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_info(msg: str):
    formatted_msg = Colors.OKBLUE + msg + Colors.ENDC
    print(formatted_msg)

def print_warning(msg: str):
    formatted_msg = Colors.WARNING + msg + Colors.ENDC
    print(formatted_msg)

def print_error(msg: str):
    formatted_msg = Colors.ERROR + msg + Colors.ENDC
    print(formatted_msg)

def print_and_log_neutral(msg: str, file_path: str=''):
    print_info(msg)
    if file_path: log_message(message=msg + '\n', file_path=file_path)

def print_and_log_info(msg: str, file_path: str=''):
    formatted_msg = Colors.OKBLUE + msg + Colors.ENDC
    print_info(formatted_msg)
    if file_path: log_message(message=msg + '\n', file_path=file_path)

def print_and_log_milestone(msg: str, file_path: str=''):
    formatted_msg = Colors.OKCYAN + msg + Colors.ENDC
    print_info(formatted_msg)
    if file_path: log_message(message=msg + '\n', file_path=file_path)

def print_and_log_warning(msg: str, file_path: str=''):
    formatted_msg = Colors.WARNING + msg + Colors.ENDC
    print_warning(formatted_msg)
    if file_path: log_message(message=msg + '\n', file_path=file_path)

def print_and_log_error(msg: str, file_path: str=''):
    formatted_msg = Colors.ERROR + msg + Colors.ENDC
    print_error(formatted_msg)
    if file_path: log_message(message=msg + '\n', file_path=file_path)
    
def log_message(message: str, file_path: str):
    with open(file_path, mode='a') as file:
        file.writelines(message)