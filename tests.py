from functions.get_files_info import get_file_content
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

print(get_file_content("calculator", "main.py"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "pkg/calculator.py"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "/bin/cat"))
print("-------------------------------------------------------------")
print(get_file_content("calculator", "pkg/does_not_exist.py"))
print("-------------------------------------------------------------")