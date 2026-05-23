import csv
import heapq
import os
import tempfile
from tkinter import *

from typing import List, Dict, Any

FIELDS = ['Book_ID', 'Title', 'Author', 'Genre', 'Year', 'Pages', 'Rating', 'Is_read']

chunk_size = 120_000

TYPE_CONVERTERS = {
    'Book_ID': int,
    'Title': str,
    'Author': str,
    'Genre': str,
    'Year': int,
    'Pages': int,
    'Rating': lambda x: int(float(x)),
    'Is_read': lambda x: x.lower() in ('true', '1', 'yes', 'да')
}



class SortKeyWrapper:
    __slots__ = ('value', 'reverse')

    def __init__(self, value, reverse=False):
        self.value = value
        self.reverse = reverse

    def __lt__(self, other):

        return self.value > other.value if self.reverse else self.value < other.value


def parse_row(row: List[str]) -> Dict[str, Any]:
    if len(row) != len(FIELDS):
        raise ValueError(f"Неверное количество полей: ожидалось {len(FIELDS)}, получено {len(row)}")
    return {field: TYPE_CONVERTERS[field](val) for field, val in zip(FIELDS, row)}


def format_row(record: Dict[str, Any]) -> List[str]:
    return [str(record[field]) for field in FIELDS]


def write_chunk_to_temp(records: List[Dict[str, Any]], temp_dir: str = ".") -> str:
    os.makedirs(temp_dir, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix='.csv', prefix='extsort_run_', dir=temp_dir)
    with os.fdopen(fd, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for rec in records:
            writer.writerow(format_row(rec))
    return path


def generate_runs(input_path: str, sort_key: str, listbox, reverse: bool = False) -> List[str]:
    temp_files = []
    print(f"📖 Фаза 1: Чтение и сортировка чанков (размер: {chunk_size})...")

    with open(input_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)

        try:
            header = next(reader)
            if not (header and header[0].strip().isdigit()):
                print("Заголовок пропущен.")
        except StopIteration:
            pass

        chunk = []
        processed = 0
        index = 0
        for row in reader:
            try:
                chunk.append(parse_row(row))
            except (ValueError, IndexError, KeyError):
                continue

            if len(chunk) >= chunk_size:

                chunk.sort(key=lambda x: x[sort_key], reverse=reverse)
                temp_files.append(write_chunk_to_temp(chunk))
                chunk = []
                processed += chunk_size
                print(f" Серия {len(temp_files)}, обработано ~{processed}")
            index += 1
        listbox.insert(END, f"Кол-во строк {index}")
        listbox.update()

        if chunk:
            chunk.sort(key=lambda x: x[sort_key], reverse=reverse)
            temp_files.append(write_chunk_to_temp(chunk))
            print(f"  Серия {len(temp_files)}, обработано ~{processed + len(chunk)}")

    return temp_files


def merge_runs(temp_files: List[str], output_path: str, sort_key: str, reverse: bool = False):
    file_handles = []
    try:
        for f in temp_files:
            file_handles.append(open(f, 'r', newline='', encoding='utf-8'))

        readers = [csv.reader(fh) for fh in file_handles]
        heap = []

        for i, reader in enumerate(readers):
            try:
                row = next(reader)
                record = parse_row(row)

                heapq.heappush(heap, (SortKeyWrapper(record[sort_key], reverse), i, record, reader))
            except StopIteration:
                pass

        with open(output_path, 'w', newline='', encoding='utf-8') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(FIELDS)

            while heap:
                key_wrapper, file_idx, record, reader = heapq.heappop(heap)
                writer.writerow(format_row(record))

                try:
                    row = next(reader)
                    next_record = parse_row(row)
                    heapq.heappush(heap,
                                   (SortKeyWrapper(next_record[sort_key], reverse), file_idx, next_record, reader))
                except StopIteration:
                    pass
    finally:
        for fh in file_handles:
            fh.close()


def external_sort_multiway(input_path: str, sort_key: str, listbox, reverse: bool = False):
    output_path = f"books_sorted_by_{sort_key}"
    if sort_key not in FIELDS:
        raise ValueError(f"Недопустимый ключ сортировки. Доступные: {FIELDS}")

    direction = "по убыванию" if reverse else "по возрастанию"
    listbox.delete(0, END)
    listbox.insert(END, f"📖 Фаза 1: Чтение и сортировка чанков ({direction}, размер: {chunk_size})...")
    listbox.update()

    temp_files = generate_runs(input_path, sort_key, listbox, reverse=reverse)
    if not temp_files:
        print("⚠️ Входной файл пуст или не содержит валидных данных.")
        with open(output_path, 'w', newline='', encoding='utf-8') as out:
            out.write(','.join(FIELDS) + '\n')
        return

    listbox.delete(0, END)
    listbox.insert(END, f"🔄 Фаза 2: Многопутевое слияние ({len(temp_files)} серий)...")
    listbox.update()
    merge_runs(temp_files, output_path, sort_key, reverse=reverse)

    for f in temp_files:
        os.remove(f)
    listbox.delete(0, END)
    listbox.insert(END, "🎉 Сортировка завершена. Временные файлы удалены.")
    listbox.update()

    with open(output_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i > 5: break
            listbox.insert(END, line.strip())
            print(line.strip())