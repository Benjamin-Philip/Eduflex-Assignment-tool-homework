from setuptools import setup

filename = r"D:Benjamin/Documents/Code/Python/homework-project/Eduflex-Assignment-tool"

def readfile(filename):
    with open(filename, 'r+') as f:
        return f.read()

setup(
    name = "Eduflex-Assignmets-tool",
    version = "2020.07.07",
    description = "",
    long_description = readfile("Readme.md"),
    author = "Benjamin J. Philip",
    author_email = "benjamin.philip495@gmail.com"
    license = None
    entry_points{
        'console_scripts':[
            "hw = Eduflex-Assignments-tool:__main__"
        ]
    }
)