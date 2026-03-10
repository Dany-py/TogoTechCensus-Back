
from pathlib import Path
import openpyxl as op

BASE_DIR = Path(__file__).resolve().parent
try:
    projects = op.load_workbook(BASE_DIR / 'project.xlsx', data_only=True)
    sheet = projects.active
except FileNotFoundError:
    print("Erreur : Le fichier 'project.xlsx' est introuvable.")
    exit()

def excel_extract_data():
    project_dict = {}
    categories = []
    current_category = None

    merged_ranges = sheet.merged_cells.ranges

    for row in sheet.iter_rows(min_col=4, max_col=11, min_row=3, max_row=136):
        row_key_cell = row[0]
        row_key_value = row_key_cell.value
        
        if row_key_value is None:
            continue

        is_merged = any(row_key_cell.coordinate in r for r in merged_ranges)

        if is_merged:
            cat_name = str(row_key_value).upper()
            if cat_name not in categories:
                categories.append(cat_name)
            current_category = cat_name
            continue
        if current_category:
            row_data = []
            for cell in row:
                if cell.value is not None:
                    row_data.append(cell.value)
            
            row_data.append(current_category)
            project_dict[row_key_value] = row_data

    return {'project': project_dict, 'categories': categories}

"""
data = excel_extract_data()
new_project = data.get('project')
new_categories = data.get('categories')

print(f"{'PROJETS EXTRAITS':^60}")
for key, value in new_project.items():
    print(f"{'-'*60}")
    print(f"{key}: {value}")

print(f"\n{'='*60}")
print(f"LISTE DES CATÉGORIES ({len(new_categories)}):")
print(*new_categories, sep='\n')"""