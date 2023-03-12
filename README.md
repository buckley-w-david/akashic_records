# akashic_records

`akashic_records` is a Python package that dynamically generates functions using OpenAI code completion based on what is imported and how it is used.
Installation

To install the akashic_records package, you can use pip:

```bash
pip install akashic_records
```

## Usage

Behaviour of the `akashic_records` package is based on _what_ you import from it, and _how_ you use it.

The package generates functions on the fly based on the name you import and the way you call it.

```python
from akashic_records import quick_sort

arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
result = quick_sort(arr)
print(result)  # Output: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
```

The package will end up making requests to the OpenAI completations endpoint with the `code-davinci-002` model.

The above code will end up generating this prompt:
```
def quick_sort(arr: list):
```

Note that the parameter name matches the name of the argument that was passed in. If a constant is passed in instead of an identifier, generic names such as `p0` and `p1` will be used. To have a useful name with a constant argument, use keyword arguments.

## Return type and docstrings

This package (ab)uses type hints to give more information to the completion process.

```python
from typing import Annotated
from akashic_records import merge_sort

unsorted_list = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
result: Annotated[list, """
Sorts the input list using the mergesort algorithm.

Parameters:
-----------
unsorted_list : list
    The input list to be sorted.

Returns:
--------
list
    The sorted list.
"""] = merge_sort(unsorted_list)
print(result)  # Output: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
```

Generates the following prompt:
```
def merge_sort(unsorted_list: list) -> list:
    """
    Sorts the input list using the mergesort algorithm.

    Parameters:
    -----------
    unsorted_list : list
        The input list to be sorted.

    Returns:
    --------
    list
        The sorted list.
    """
```

If you would like to include a docstring but not a return type, only use a string for the type annotation instead of using `typing.Annotated`.

### How does the parameter name/type hint thing work?

The very neat [sorcery](https://github.com/alexmojaki/sorcery) package by [Alex Hall](https://github.com/alexmojaki).

## Options

The OpenaAI completaions endpoint has many options. Some of these are available for tweaking.

```
from akashic_records import config

config.n = 3 # https://platform.openai.com/docs/api-reference/completions/create#completions/create-n
config.max_tokens = 512 # https://platform.openai.com/docs/api-reference/completions/create#completions/create-max_tokens
config.temperature = 0.2 # https://platform.openai.com/docs/api-reference/completions/create#completions/create-temperature
```

Some additional options are available to control the prompt generation process.
```
from akashic_records import config

config.type_hint = True # Set to False to disable all type hints in prompts

# The package isn't always able to get a working completion from the API.
# In the event that something goes wrong (syntax error in the generated code, runtime error trying to run it, etc)
# The package will try to generate new completions.
# The `attempts` value controls how many times it will try.
config.attempts = 5 # Set to -1 for unlimited tries.
```

## What's with the name?

The name `akashic_records` is inspired by the spiritual belief of the [Akashic Records](https://en.wikipedia.org/wiki/Akashic_records). In this belief, the Akashic Records are a repository all universal events, thoughts, words, emotions and intent ever to have occurred in the past, present, or future in terms of all entities and life forms.

This seemed fitting for a package that in some sense contains the implementation of "every function".
