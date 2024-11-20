# Silhouette

Silhouette is an AI-powered Python code transformation tool that uses libcst and GPT models to enhance your code with PEP-compliant docstrings and type hints.

## Features

- Automatically generate comprehensive docstrings for functions, classes, and modules
- Add type hints to function parameters and return values
- Preserve existing code structure and comments


## Example Usage
``` python
from silhouette.cst_transformers import add_type_hints, add_docstrings
import os

api_key = os.getenv("OPENAI_API_KEY")

source_code = """
def calculate_average(numbers, weights=None):
    total = 0
    count = 0
    for i, num in enumerate(numbers):
        if weights:
            total += num * weights[i]
            count += weights[i]
        else:
            total += num
            count += 1
    return total / count if count else 0
"""

final_code = add_docstrings(source_code, api_key)

result = add_type_hints(final_code, api_key)
print(result)
```
### Output
``` python
def calculate_average(numbers: List[float], weights: Optional[List[float]]=None) -> float:
    """This function calculates the weighted or unweighted average of a list of numbers.
    
    Args:
        numbers: A list of numbers for which the average is to be calculated.
        weights: An optional list of weights for each number. If provided, the function calculates the weighted average. If not provided, the function calculates the unweighted average.
    
    Returns:
        The weighted or unweighted average of the input numbers. If the list of numbers is empty, the function returns 0.
    """
    total = 0
    count = 0
    for i, num in enumerate(numbers):
        if weights:
            total += num * weights[i]
            count += weights[i]
        else:
            total += num
            count += 1
    return total / count if count else 0
```