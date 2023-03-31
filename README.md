# DirectorySizeCalculator

This is a Python class that calculates the size of a directory by iterating through all of its files and directories recursively. It provides several options to customize the calculation, such as specifying the file types to include or exclude, setting a maximum size for the directory, and sorting the files by size or name.

## Requirements
- `Python 3.x`
- `tqdm`
- `enum`
- `pathlib`

## Installation
Clone the repository, and ensure that all required packages `(tqdm, enum, and pathlib)` are installed in your Python environment.

## Usage
Instantiate a `DirectorySizeCalculator` object by providing the path to the directory to be processed. Optionally, you can customize the calculation by providing additional arguments to the constructor, such as the file types to include or exclude, the maximum size of the directory to calculate, whether to include hidden files, and how to sort the files.

Then, call the get_size method to calculate the size of the directory. This method returns the size in bytes by default, but you can specify a different unit of measurement using the unit argument. The method also supports multithreading, which can improve performance on large directories by processing files in parallel.

Finally, you can generate a report of the calculation by calling the `generate_report` method, which returns a string containing information such as the number of files processed, the total size of the directory, and the time taken to calculate the size.

## Example
```python
from DirectorySizeCalculator import DirectorySizeCalculator, Unit

# Instantiate a DirectorySizeCalculator object
calculator = DirectorySizeCalculator(path='/path/to/directory', file_types=['.jpg', '.png'], exclude=['.pdf'], sort_by='size')

# Calculate the size of the directory in megabytes
size = calculator.get_size(unit=Unit.MEGABYTE)

# Generate a report of the calculation
report = calculator.generate_report(num_files_processed=calculator.num_files_processed, total_size=size, time_taken=calculator.time_taken)

# Print the report
print(report)
```
## API
`DirectorySizeCalculator(path='.', file_types=None, exclude=None, max_size=None, include_hidden_files=False, sort_by=None)`
Initializes a `DirectorySizeCalculator` object.

### Arguments
`path (str)`: The path to the directory to calculate the size of. Default is `'.'`.
`file_types (list of str)`: A list of file extensions to include in the size calculation. Default is `None`.
`exclude (list of str)`: A list of file extensions to exclude from the size calculation. Default is `None`.
`max_size (int)`: The maximum size of the directory to calculate, in bytes. Default is `None`.
`include_hidden_files (bool)`: Whether or not to include hidden files in the size calculation. Default is `False`.
`sort_by (str)`: The sorting method to use when processing files. Valid values are `'size'` and `'name'`. Default is `None`.
`get_size(num_threads=1, unit=Unit.BYTE, max_size=None, top_level_only=False) -> float`: Calculates the size of the directory.

### Arguments
`num_threads (int)`: The number of threads to use for processing files. Default is `1`.
`unit (Unit)`: The unit to display the size in. Default is `Unit.BYTE`.
`max_size (int)`: The maximum size of the directory to calculate, in bytes. Default is `None`.
`top_level_only (bool)`: Whether or not to calculate the size of only the top-level directory. Default is `False`.
Returns
float: The size of the directory, in the specified unit.
`generate_report(num_files_processed, total_size, time_taken) -> str`
Generates a report of the directory size calculation.

### Arguments
`num_files_processed (int)`: The number of files processed.
`total_size (int)`: The total size of the directory.
`time_taken (float)`: The time taken to calculate the directory size, in seconds.
Returns
`str`: A report of the directory size calculation.


