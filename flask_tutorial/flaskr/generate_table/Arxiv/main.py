# .
# └── Arxiv
#     ├── Computer_Science
#     │   └── Computer_Science.csv
#     ├── Economics
#     │   └── Economics.csv
#     ├── Electrical_Engineering_and_Systems_Science
#     │   └── Electrical_Engineering_and_Systems_Science.csv
#     ├── Mathematics
#     │   └── Mathematics.csv
#     ├── Physics
#     │   ├── Physics_Astrophysics.csv
#     │   ├── Physics_Condensed_Matter.csv
#     │   ├── Physics_General_Relativity_and_Quantum_Cosmology.csv
#     │   ├── Physics_High_Energy_Physics_Experiment.csv
#     │   ├── Physics_High_Energy_Physics_Lattice.csv
#     │   ├── Physics_High_Energy_Physics_Phenomenology.csv
#     │   ├── Physics_High_Energy_Physics_Theory.csv
#     │   ├── Physics_Mathematical_Physics.csv
#     │   ├── Physics_Nonlinear_Sciences.csv
#     │   ├── Physics_Nuclear_Experiment.csv
#     │   ├── Physics_Nuclear_Theory.csv
#     │   ├── Physics_Physics.csv
#     │   └── Physics_Quantum_Physics.csv
#     ├── Quantitative_Biology
#     │   └── Quantitative_Biology.csv
#     ├── Quantitative_Finance
#     │   └── Quantitative_Finance.csv
#     └── Statistics
#         └── Statistics.csv

import csv
import os

id_field_list = [
    (1, "Computer_Science"),
    (2, "Mathematics"),
    (3, "Quantitative_Biology"),
    (4, "Quantitative_Finance"),
    (5, "Statistics"),
    (6, "Economics"),
    (7, "Electrical_Engineering_and_Systems_Science"),
    (8, "Physics_Astrophysics"),
    (9, "Physics_Condensed_Matter"),
    (10, "Physics_General_Relativity_and_Quantum_Cosmology"),
    (11, "Physics_High_Energy_Physics_Experiment"),
    (12, "Physics_High_Energy_Physics_Lattice"),
    (13, "Physics_High_Energy_Physics_Phenomenology"),
    (14, "Physics_High_Energy_Physics_Theory"),
    (15, "Physics_Mathematical_Physics"),
    (16, "Physics_Nonlinear_Sciences"),
    (17, "Physics_Nuclear_Experiment"),
    (18, "Physics_Nuclear_Theory"),
    (19, "Physics_Physics"),
    (20, "Physics_Quantum_Physics"),
]

base_path = "../../../assets/Arxiv"


def id_field_name():
    # Create a list with the id and field name pairs
    key = 0
    # Iterate through the id and field list
    for idx, field_name in id_field_list:
        save_path = os.path.join("arxiv_id_name.csv")
        with open(save_path, "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            if key == 0:
                csv_writer.writerow(["id", "name"])
                key = 1
            csv_writer.writerow([idx, field_name])

        print(f"CSV file created")


def field_table():
    # Table 2 field : ID(Table 1 Field name mathc to ID) - Year - Article Count - Cross List Count - Total Article Count
    # Create a list with the id and field name pairs

    key = 0
    # Iterate through the id and field list
    for idx, field_name in id_field_list:
        # Construct the CSV file path based on conditions
        if idx <= 7:
            file_path = os.path.join(base_path, field_name, f"{field_name}.csv")
        else:
            file_path = os.path.join(base_path, "Physics", f"{field_name}.csv")
        # open file path and read csv, then write to field.csv
        # field csv including: id, year, article_count, cross_list_count, total_article_count
        for row in csv.reader(open(file_path)):
            save_path = os.path.join("arxiv_field.csv")
            with open(save_path, "a", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                if key == 0:
                    csv_writer.writerow(
                        ["field_id", "year", "article_count", "cross_list_count", "total_article_count"])
                    key = 1
                if row[0] != "Year":
                    csv_writer.writerow([idx, row[0], row[1], row[2], row[3]])
        print(f"{field_name} done")


if __name__ == '__main__':
    id_field_name()
    field_table()
