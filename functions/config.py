import os

MAX_CHARS = 10000

def is_safe_path(working_directory, target_directory):
    """
    Ensure the resolved path is strictly a child of the working directory &
    Prevent directory tranversal attacks (ex: '../../etc/passwd')
    """
    working_dir_abs = os.path.abspath(working_directory)
    target_path_abs = os.path.abspath(os.path.join(working_directory, target_directory))

    try:
        common = os.path.commonpath([working_dir_abs, target_path_abs])
        return common == working_dir_abs
    except ValueError:
        return False
    