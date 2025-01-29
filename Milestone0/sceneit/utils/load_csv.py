import csv

def load_csv_data(csv_filepath: str):
    with open(csv_filepath, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)
