from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

"""
Warning! This file will only test the provided functions within the functions directory 
for the target subdirectory, in this case the calculator directory. There is no AI 
intrevention by executing this tests.py file.

However, if you want to test the AI functionality, then after configuring the .env file
with the API key of the relevant service its recommended to follow the given directions
in the ReadME.md file by directly working with the main.py file. All the best!🫡
"""


"""
print(get_files_info("calculator", "."))
print("-------------------------------------------------------------")
print(get_files_info("calculator", "pkg"))
print("-------------------------------------------------------------")
print(get_files_info("calculator", "/bin"))
print("-------------------------------------------------------------")
print(get_files_info("calculator", "../"))
print("-------------------------------------------------------------")
"""

"""
print(get_file_content("calculator", "lorem.txt"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "main.py"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "pkg/calculator.py"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "/bin/cat"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "pkg/does_not_exist.py"))
print("-------------------------------------------------------------")
"""


"""
print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
print("-------------------------------------------------------------")
print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
print("-------------------------------------------------------------")
print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
print("-------------------------------------------------------------")
"""


"""
print(run_python_file("calculator", "main.py"))
print("-------------------------------------------------------------")
print(run_python_file("calculator", "main.py", ["3 + 5"]))
print("-------------------------------------------------------------")
print(run_python_file("calculator", "tests.py"))
print("-------------------------------------------------------------")
print(run_python_file("calculator", "../main.py"))
print("-------------------------------------------------------------")
print(run_python_file("calculator", "nonexistent.py"))
print("-------------------------------------------------------------")
print(run_python_file("calculator", "lorem.txt"))
print("-------------------------------------------------------------")
"""

