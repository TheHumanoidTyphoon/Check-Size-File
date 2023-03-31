import threading
from queue import Queue
from pathlib import Path
from tqdm import tqdm
from enum import Enum
import datetime


class Unit(Enum):
    BYTE = 1
    KILOBYTE = 2
    MEGABYTE = 3
    GIGABYTE = 4


class DirectorySizeCalculator:
    def __init__(self, path='.', file_types=None, exclude=None, max_size=None, include_hidden_files=False, sort_by=None):
        """
        Initializes a DirectorySizeCalculator object.

        Args:
            path (str): The path to the directory to calculate the size of.
            file_types (list of str): A list of file extensions to include in the size calculation.
            exclude (list of str): A list of file extensions to exclude from the size calculation.
            max_size (int): The maximum size of the directory to calculate, in bytes.
            include_hidden_files (bool): Whether or not to include hidden files in the size calculation.
            sort_by (str): The sorting method to use when processing files. Valid values are 'size' and 'name'.
        """
        self.path = Path(path)
        self.file_types = file_types or []
        self.exclude = exclude or []
        self.cache = {}
        self.include_hidden_files = include_hidden_files
        self.sort_by = sort_by

    def _get_files(self):
        """
        Returns a list of files to be processed.

        Returns:
            list of Path: A list of file paths.
        """
        files = []
        if self.path.is_dir():
            for file_ in self.path.rglob('*'):
                if not self.include_hidden_files and file_.name.startswith('.'):
                    continue
                file_ext = file_.suffix.lower()
                if self.file_types and file_ext not in self.file_types:
                    continue
                if self.exclude and file_ext in self.exclude:
                    continue
                files.append(file_)
        elif self.path.is_file() and self.path.exists():
            files.append(self.path)

        if self.sort_by == 'size':
            files.sort(key=lambda file_: file_.stat().st_size)
        elif self.sort_by == 'name':
            files.sort()

        return files

    def _get_compression_ratio(self, file_ext):
        """
        Returns the compression ratio for a given file extension.

        Args:
            file_ext (str): The file extension to get the compression ratio for.

        Returns:
            float: The compression ratio for the file extension.
        """
        compression_ratios = {'.txt': 0.5,
                              '.csv': 0.7, '.jpg': 0.9, '.pdf': 0.8}
        return compression_ratios.get(file_ext, 1.0)

    def generate_report(self, num_files_processed, total_size, time_taken):
        """
        Generates a report of the directory size calculation.

        Args:
            num_files_processed (int): The number of files processed.
            total_size (int): The total size of the directory.
            time_taken (float): The time taken to calculate the directory size, in seconds.

        Returns:
            str: A report of the directory size calculation.
        """
        report = f"Directory Size Calculation Report\n\n"
        report += f"Path: {str(self.path)}\n"
        report += f"Number of files processed: {num_files_processed}\n"
        report += f"Total size: {total_size} bytes\n"
        report += f"Time taken: {time_taken} seconds\n"
        report += f"File types: {self.file_types}\n"
        report += f"Excluded file types: {self.exclude}\n"
        report += f"Include hidden files: {self.include_hidden_files}\n"
        report += f"Sort by: {self.sort_by}\n"

        return report

    def get_size(self, num_threads=1, unit=Unit.BYTE, max_size=None, top_level_only=False):
        """
        Calculates the size of the directory.

        Args:
            num_threads (int): The number of threads to use for processing files.
            unit (Unit): The unit to display the size in.
            max_size (int): The maximum size of the directory to calculate, in bytes.
            top_level_only (bool): Whether or not to calculate the size of only the top-level directory.

        Returns:
            float: The size of the directory, in the specified unit.
        """
        start_time = datetime.datetime.now()
        files = self._get_files()
        # Check if the size has already been calculated and stored in the cache
        if str(self.path) in self.cache:
            size = self.cache[str(self.path)]
            return self._format_size(size, unit)

        size = 0
        compressed_size = 0
        file_queue = Queue()
        if top_level_only:
            for file_ in self.path.glob('*'):
                if file_.is_file():
                    file_ext = file_.suffix.lower()
                    if self.file_types and file_ext not in self.file_types:
                        continue
                    if self.exclude and file_ext in self.exclude:
                        continue
                    file_queue.put(file_)
        else:
            files = self._get_files()
            for file_ in files:
                file_queue.put(file_)

        # Create a tqdm progress bar object
        file_count = file_queue.qsize()
        progress_bar = tqdm(
            total=file_count, desc='Calculating directory size')

        def worker():
            nonlocal size, compressed_size
            while True:
                try:
                    file_ = file_queue.get_nowait()
                except:
                    break
                file_size = file_.stat().st_size
                compression_ratio = self._get_compression_ratio(
                    file_.suffix.lower())
                compressed_size += file_size * compression_ratio
                if max_size and compressed_size > max_size:
                    # If the size exceeds the limit, stop calculating and return the current size
                    return
                size += file_size
                progress_bar.update(1)

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Start the progress bar
        progress_bar.set_postfix_str(f'Threads: {num_threads}')

        for thread in threads:
            thread.join()

        # Close the progress bar
        progress_bar.close()

        end_time = datetime.datetime.now()
        time_taken = (end_time - start_time).total_seconds()

        # Store the calculated size in the cache
        self.cache[str(self.path)] = size

        # Generate and print the report
        report = self.generate_report(num_files_processed=len(
            files), total_size=size, time_taken=time_taken)
        print(report)

        return self._format_size(compressed_size, unit)

    def _format_size(self, size, unit):
        """
        Formats the size of the directory.

        Args:
            size (int): The size of the directory, in bytes.
            unit (Unit): The unit to display the size in.

        Returns:
            float: The size of the directory, in the specified unit.
        """
        if unit == Unit.BYTE:
            return size
        elif unit == Unit.KILOBYTE:
            return size / 1024
        elif unit == Unit.MEGABYTE:
            return size / (1024 * 1024)
        elif unit == Unit.GIGABYTE:
            return size / (1024 * 1024 * 1024)


def calculate_directory_size(path='.', file_types=None, exclude=None, num_threads=1, unit=Unit.BYTE, sort_by=None):
    """
    Calculates the total size of all files in a given directory.

    Args:
        path (str or Path): The path to the directory to be scanned. Default is the current directory.
        file_types (list of str, optional): A list of file extensions to include. Default is None, which includes all file types.
        exclude (list of str, optional): A list of file extensions to exclude. Default is None, which excludes no file types.
        num_threads (int, optional): The number of threads to use for scanning the directory. Default is 1.
        unit (Unit, optional): The unit of measurement to use for the size calculation. Default is Unit.BYTE.
        sort_by (str or SortBy, optional): The attribute by which to sort the directory contents before calculating their size.
                                           Default is None, which means no sorting is performed.

    Returns:
        The total size of all files in the directory, in the specified unit of measurement.
    """
    calculator = DirectorySizeCalculator(
        path=path, file_types=file_types, exclude=exclude, sort_by=sort_by)
    return calculator.get_size(num_threads=num_threads, unit=unit)


def main():
    """
    Runs some sample tests of the calculate_directory_size function and prints the results.
    """
    test_path = Path.home() / 'Documents/Test'

    # test_path = Path('\\\\server\\share\\directory')
    # calculator = DirectorySizeCalculator(path=test_path)

    max_size = 1024 * 1024  # 1 MB
    calculator = DirectorySizeCalculator(path=test_path, max_size=max_size)
    size = calculator.get_size(
        num_threads=4, unit=Unit.KILOBYTE, top_level_only=True)
    print(size)

    # Calculate size of all files in directory
    print(calculate_directory_size(
        path=test_path, num_threads=4, unit=Unit.KILOBYTE))

    # Calculate size of only .txt and .docx files in directory
    print(calculate_directory_size(path=test_path, file_types=[
          '.txt', '.docx'], num_threads=4, unit=Unit.KILOBYTE))

    # Calculate size of all files in directory except .jpg and .png files
    print(calculate_directory_size(path=test_path, exclude=[
          '.jpg', '.png'], num_threads=4, unit=Unit.KILOBYTE))


if __name__ == '__main__':
    main()


