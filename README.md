# Automate Codebase Analysis

Ever had to go over all the codebase and analyze everything one-by-one? Ever wanted to "read over all of it really fast" and get "high level picture" per folder? This tool does exactly that, hope to make your codebase-analysis time shorter.

This will recursively generate...

* High-level summary of the codebase
* Highlights of the codebase
* Pythonic Pseudocode
* Import Relationships

# Installation & Use

Install sglang and run server.

```bash
pip install sglang
python -m sglang.launch_server --model-path deepseek-ai/deepseek-coder-6.7b-instruct --tp 4 --port 8080
```


Run it via

```bash
convert.py CODEBASE_DIR OUTPUT_DIR --port 8080
```


# Example Output:

The following is example output from analysis of DeepSpeed codebase:

---


### Summary

* `__init__.py`: This file is the main file that is imported when someone imports the `op Rating (out of 5):3

* `AsyncIOBuilder`: It's a class that builds asynchronous I/O operations. The importance Rating (out of 5):3

* `Major classes/methods`: AsyncIOBuilder is the main class used for building asynchronous I/O Rating (out of 5):3

* `Summary:`: This is the main package that provides classes and methods for building asynchronous I/ Rating (out of 5):3

* `AsyncIOBuilder:`: It is a class that provides methods for building asynchronous I/O operations. Rating (out of 5):3

* `Methods in AsyncIOBuilder:` These methods are used for building different types of asynchronous I/O operations. Rating (out of 5):5

* `Important methods include:` - `__init__`: Initializes the AsyncIOBuilder object. It's Rating (out of 5):2

- `build_read_from_file`: Builds an asynchronous reader from a file. Rating (out of 5):2

- `build_write_to_file`: Builds an asynchronous writer to a file. Rating (out of 5):2

- `build_concurrent_reads`: Builds multiple concurrent asynchronous read operations. Rating (out of 5):5

Overall, this codebase provides a set of tools for building asynchronous I/O operations in Python. It's a part of a larger project, likely a data-parallel computing library, that is built on top of the asyncio Python library.

### Highlights

1. **Import of AsyncIOBuilder:** This line `from ..op_builder import AsyncIOBuilder` imports the AsyncIOBuilder class from the `op_builder` module in the parent directory. This is usually used when you want to support asynchronous operations in your Python code.
2. **Class Definition:** The file doesn't contain any classes or class-like definitions. It could be a stand-alone module rather than part of a larger application, if you are familiar with Python's package structure.
3. **Module-Level Function or Variable Definitions:** Asynchronous operations in Python typically involve the use of coroutines, which are essentially asynchronous versions of ordinary functions or methods. The file appears to use the Python async IO capabilities to manage such operations.
4. **File Structure:** The file's structure makes it look like it might be a part of a larger project or solution, where other Python files also import and use AsyncIOBuilder.
5. **Identifiers:** Although, it seems as though this file could be a 'draft' or 'staging'/'development' version of a larger module or package - there are leading underscores in the file name `__init__.py`, potentially indicating that it's intended to be an 'init' file for a package, marking it as a Python package directory.

### Pythonic Pseudocode

```python
# File: ops/aio/__init__.py

# Description: 
# This Python module initializes the AsyncIOBuilder class from the op_builder module. 
# The AsyncIOBuilder class is a part of the DeepSpeed library that facilitates the creation of asynchronous operations. 
# The purpose of this file is to provide a consistent interface for asynchronous operations across various devices and systems.

# Imports: 
# Import the AsyncIOBuilder class from the op_builder module
from ..op_builder import AsyncIOBuilder

# AsyncIOBuilder Class:
# This class is initialized with the following method:

class AsyncIOBuilder:
    def __init__(self, *args, **kwargs):
        # Constructor. Initialize the AsyncIOBuilder object with the provided arguments.
        pass

    def method1(*args, **kwargs):
        # Method 1.
        # This method is responsible for ... (explanation of the method)
        pass

    def method2(*args, **kwargs):
        # Method 2.
        # This method is responsible for ... (explanation of the method)
        pass

    # Continue with other methods...
```


### import Relationships

Imports found:
from ..op_builder import AsyncIOBuilder