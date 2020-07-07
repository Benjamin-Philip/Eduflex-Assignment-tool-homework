from setuptools import setup

filename = r"<enter path of the location of homework.py here>"

def readfile(filename):
    with open(filename, 'r+') as f:
        return f.read()

setup(
    name = "homework",
    version = "2020.07.07",
    description = "",
    long_description = readfile("Readme.md"),
    author = "Benjamin J. Philip",
    author_email = "benjamin.philip495@gmail.com",
    entry_points = {
        'console_scripts':[
            "hw = homework:__main__"
        ]
    }
)
