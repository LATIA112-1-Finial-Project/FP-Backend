import os
import csv

base_path = "../../../assets/Top_500_University_Data"


# Combine 2021~2024 csv to one csv

# academic_reputation 2021 ~ 2024

def combine_academic_reputation():
    csv_list = []
    for year in range(2021, 2025):
        csv_list.append(f"{base_path}/{year}/top_500_academic_reputation_{year}.csv")

    with open(f"DB_Data/academic_reputation.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["university_id", "academic_reputation_rank", "academic_reputation_score", "year"]
        )
        y = 2021
        for csv_file in csv_list:
            key = 0
            with open(csv_file, "r") as f2:
                for row in csv.reader(f2):
                    if key == 0:
                        key = 1
                        continue
                    # if row[1] contain ".0", remove the .0, if not, do nothing
                    if row[1].find(".0") != -1:
                        row[1] = row[1].replace(".0", "")
                    writer.writerow([row[0], row[1], row[2], y])
            y += 1


# employer_reputation 2021 ~ 2024

def combine_employer_reputation():
    employer_csv_list = []
    for year in range(2021, 2025):
        employer_csv_list.append(f"{base_path}/{year}/top_500_employer_reputation_{year}.csv")

    with open(f"DB_Data/employer_reputation.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["university_id", "employer_reputation_rank", "employer_reputation_score", "year"]
        )
        ye = 2021
        for csv_file in employer_csv_list:
            key = 0
            with open(csv_file, "r") as f2:
                for row in csv.reader(f2):
                    if key == 0:
                        key = 1
                        continue
                    # if row[1] contain ".0", remove the .0, if not, do nothing
                    if row[1].find(".0") != -1:
                        row[1] = row[1].replace(".0", "")
                    writer.writerow([row[0], row[1], row[2], ye])
            ye += 1


# overall 2021 ~ 2024

def combine_overall():
    overall_csv_list = []
    for year in range(2021, 2025):
        overall_csv_list.append(f"{base_path}/{year}/top_500_overall_{year}.csv")

    with open(f"DB_Data/overall.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["university_id", "overall_rank", "overall_score", "year"]
        )
        yo = 2021
        for csv_file in overall_csv_list:
            key = 0
            with open(csv_file, "r") as f2:
                for row in csv.reader(f2):
                    if key == 0:
                        key = 1
                        continue
                    # if row[1] contain ".0", remove the .0, if not, do nothing
                    if row[1].find(".0") != -1:
                        row[1] = row[1].replace(".0", "")
                    writer.writerow([row[0], row[1], row[2], yo])
            yo += 1


if __name__ == '__main__':
    combine_academic_reputation()
    combine_employer_reputation()
    combine_overall()
