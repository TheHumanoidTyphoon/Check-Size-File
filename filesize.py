import csv
import datetime
import os
from pathlib import Path

from humanize import naturalsize
from openpyxl import Workbook
from tqdm import tqdm


def get_directory_size(path: str) -> int:
    total_size = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total_size += entry.stat().st_size
        elif entry.is_dir():
            total_size += get_directory_size(entry.path)
    return total_size


def get_size(path='.', file_types=None, unit='B', exclude=None, include_subdirs=True, sort_by_size=False,
             max_size=None, output_file=None, start_date=None, end_date=None):
    if file_types:
        files = [f for f in Path(path).glob('**/*') if f.is_file() and any(f.suffix.lower() == ext.lower() for ext in file_types)]
    else:
        files = [f for f in Path(path).glob('**/*') if f.is_file()]

    if exclude:
        files = [f for f in files if not any(d in f.parts for d in exclude)]
    if not include_subdirs:
        files = [f for f in files if f.parent == Path(path)]
    if max_size:
        files = [f for f in files if f.stat().st_size <= max_size]
    if start_date:
        files = [f for f in files if os.stat(str(f)).st_mtime >= start_date]
    if end_date:
        files = [f for f in files if os.stat(str(f)).st_mtime <= end_date]

    size = 0
    results = []
    for f in tqdm(files):
        file_size = min(f.stat().st_size, max_size) if max_size else f.stat().st_size
        size += file_size
        file_metadata = os.stat(str(f))
        creation_time = datetime.datetime.fromtimestamp(file_metadata.st_ctime)
        modified_time = datetime.datetime.fromtimestamp(file_metadata.st_mtime)
        owner_id = file_metadata.st_uid
        permissions = oct(file_metadata.st_mode)[-3:]
        if f.is_file():
            results.append((str(f), naturalsize(file_size, format='%.1f', binary=True, gnu=True, suffix=True, units=unit), creation_time, modified_time, owner_id, permissions))
        elif f.is_dir():
            dir_size = get_directory_size(f)
            size += dir_size
            results.append((str(f), naturalsize(dir_size, format='%.1f', binary=True, gnu=True, suffix=True, units=unit), "", "", "", ""))

    if sort_by_size:
        results = sorted(results, key=lambda x: x[1], reverse=True)

    if output_file:
        extension = Path(output_file).suffix
        if extension == '.csv':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['File path', 'Size', 'Creation time', 'Modified time', 'Owner ID', 'Permissions'])
                writer.writerows(results)
        elif extension == '.xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(['File path', 'Size', 'Creation time', 'Modified time', 'Owner ID', 'Permissions'])
            for row in results:
                ws.append(row)
            wb.save(output_file)

    return naturalsize(size, format='%.1f', binary=True, gnu=True, suffix=True, units=unit), results










