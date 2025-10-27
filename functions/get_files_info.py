import os

def get_files_info(working_directory, directory="."):
    joint_directory = os.path.join(working_directory, directory)
    if working_directory not in os.path.abspath(joint_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(joint_directory):
        return f'Error: "{directory}" is not a directory'
    directories = os.listdir(joint_directory)
    res = ""
    for data in directories:
        fixed_data = os.path.join(joint_directory, data)
        if os.path.isdir(fixed_data) == False:
            res += f'\n{data}: file_size={os.path.getsize(fixed_data)} bytes, is_dir=False'
        else:
            res += f'\n{data}: file_size={None} bytes, is_dir=True'
    return res

