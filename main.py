import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('data/fake_student_records.csv')

# Column datatype correction
df['StudentID'] = df['StudentID'].astype(str)
i = 1
while True:
    try:
        # Convert each column one by one
        df[f'Q{i}_Timestamp'] = df[f'Q{i}_Timestamp'].astype(str)
        df[f'Q{i}_CS_GPA'] = df[f'Q{i}_CS_GPA'].astype(np.float64)
        df[f'Q{i}_Overall_GPA'] = df[f'Q{i}_Overall_GPA'].astype(np.float64)
        df[f'Q{i}_CS_Units'] = df[f'Q{i}_CS_Units'].astype(np.int16)
        df[f'Q{i}_Total_Units'] = df[f'Q{i}_Total_Units'].astype(np.int16)
    except KeyError:
        # When no more columns are left to convert
        break
    i += 1

# Dictionary Construction
dict_data = dict()
for s_index, student in df.iterrows():
    i = 1
    while True:
        try:
            timestamp: str = student[f'Q{i}_Timestamp']     # something like 202401
            yyyy: str = timestamp[:4]    # crops 2024 out of 202401
            mm: str = timestamp[4:]      # crops 01 out of 202401
            cs_grade: tuple = (student[f'Q{i}_CS_Units'], student[f'Q{i}_CS_GPA'])
            overall_grade: tuple = (student[f'Q{i}_Total_Units'], student[f'Q{i}_Overall_GPA'])
            if not yyyy in dict_data:
                dict_data[yyyy] = {}
            if not mm in dict_data[yyyy]:
                dict_data[yyyy][mm] = {"CS": [], "OvA": []}
                
            dict_data[yyyy][mm]["CS"].append(cs_grade)
            dict_data[yyyy][mm]["OvA"].append(overall_grade)
        except KeyError:
            break
        i += 1

# preparation of matplot visualization
q_label_list = []
avg_cs_list = []
avg_ncs_list = []
avg_ov_list = []
for y in sorted(dict_data.keys()):
    for m in sorted(dict_data[y].keys()):
        # print(dict_data[y][m])

        if m == "01": q = "W"
        elif m == "03": q = "S"
        elif m == "08": q = "F"
        else: raise ValueError("Month Error")
        q_label_list.append(f"{y}{q}")

        # average CS GPA calculation
        # n x 2 dimension array | each row is (CS_Unit, CS_GPA) tuple
        cs_ndrray = np.array(dict_data[y][m]["CS"])
        # crop first column, becomes n x 1 array of CS_Unit
        cs_unit_ndarray = cs_ndrray[:, 0].reshape(-1, 1)
        # crop second column, becomes n x 1 array of CS_GPA
        cs_gpa_ndarray = cs_ndrray[:, 1].reshape(-1, 1)
        avg_cs_grade: int = np.sum(cs_unit_ndarray * cs_gpa_ndarray) / np.sum(cs_unit_ndarray)
        avg_cs_list.append(avg_cs_grade)
        
        # average overall GPA calculation
        # n x 2 dimension array | each row is (OvA_Unit, OvA_GPA) tuple
        ov_ndrray = np.array(dict_data[y][m]["OvA"])
        # crop first column, becomes n x 1 array of OvA_Unit
        ov_unit_ndarray = ov_ndrray[:, 0].reshape(-1, 1)
        # crop second column, becomes n x 1 array of OvA_GPA
        ov_gpa_ndarray = ov_ndrray[:, 1].reshape(-1, 1)
        avg_ov_grade: int = np.sum(ov_unit_ndarray * ov_gpa_ndarray) / np.sum(ov_unit_ndarray)
        avg_ov_list.append(avg_ov_grade)

        # average non-CS GPA calculation
        ncs_grade_point = np.sum(ov_unit_ndarray * ov_gpa_ndarray) - np.sum(cs_unit_ndarray * cs_gpa_ndarray)
        ncs_unit = np.sum(ov_unit_ndarray) - np.sum(cs_unit_ndarray)
        avg_ncs_grade: int = ncs_grade_point / ncs_unit
        avg_ncs_list.append(avg_ncs_grade)

# matplot visualization
x = np.arange(len(q_label_list))

bar_width = 0.25
bar_offset = 0.25
# Bar charts
plt.bar(x - bar_offset, avg_cs_list, width=bar_width, label='CS GPA', color='#00CC00', alpha=0.7)
plt.bar(x, avg_ncs_list, width=bar_width, label='Non-CS GPA', color='#999999', alpha=0.7)
plt.bar(x + bar_offset, avg_ov_list, width=bar_width, label='Overall GPA', color='#333333', alpha=0.7)

# Labels and Title
plt.xlabel('Quarters')
plt.ylabel('Average GPA of all CS Students')
plt.title('Comparison between CS and non-CS Performance')
plt.xticks(x, q_label_list)  # Set the x-tick labels

# Adding legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()