# akashic_records

`akashic_records` is a Python library that dynamically generates functions using OpenAI code completion based on what is imported and how it is used.
Installation

To install the akashic_records library, you can use pip:

```bash
pip install akashic_records
```

## Usage

To use the `akashic_records` library, you need to import the function you want to generate. The library generates the function on the fly based on the name you import. For example, to generate a quicksort function, you can import the quick_sort function like this:

Since this library depends on `[openai](https://github.com/openai/openai-python)`, you need to set your API key on start.
```python
import openai
openai.api_key = '<YOUR_KEY>'

from akashic_records import quick_sort

# Use the generated function
arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
result = quick_sort(arr)
print(result)  # Output: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
```

This library (ab)uses type hints to give more information to the completion process.
```python
import openai
openai.api_key = '<YOUR_KEY>'

from akashic_records import merge_sort

# Use the generated function
arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
result: """
Sorts the input list using the mergesort algorithm.

Parameters:
-----------
arr : list
    The input list to be sorted.

Returns:
--------
list
    The sorted list.
""" = merge_sort(arr)
print(result)  # Output: [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
```

### Wait, how did you do that?

The very neat [sorcery](https://github.com/alexmojaki/sorcery) package by [Alex Hall](https://github.com/alexmojaki).

## What's with the name?

The name `akashic_records` is inspired by the spiritual belief of the [Akashic Records](https://en.wikipedia.org/wiki/Akashic_records). In this belief, the Akashic Records are a repository all universal events, thoughts, words, emotions and intent ever to have occurred in the past, present, or future in terms of all entities and life forms.

This seemed fitting for a library that in some sense contains the implementation of "every function".
