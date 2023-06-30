from collections import defaultdict

import pandas as pd

from api.v1.staffology.api.employees import StaffologyEmployeeAPI
from crewpay.wsgi import application


def get_ununique_peeepz(data):
    codes = defaultdict(list)
    for row in data:

        payroll_code = row['metadata']['payrollCode'].replace('cp', '')
        codes[payroll_code].append((row['name'], row['id'], row['metadata']['payrollCode']))
    for code, peeeepz in dict(codes).items():
        if len(peeeepz) == 1:
            codes.pop(code)
    return dict(codes)


staffology_employees = StaffologyEmployeeAPI().staffology_employees_get("3e863ec8-a81f-45a5-96b9-0c4144c97148")
codes = get_ununique_peeepz(staffology_employees)

people_to_update = []
for i, (code, people) in enumerate(codes.items()):
    people_names = [(peep[0], peep[2]) for peep in people]
    person_to_delete = [peep for peep in people if not peep[2].startswith('cp')][0]
    people_to_update.append([peep for peep in people if peep[2].startswith('cp')][0])
    print(f"{i+1}/{len(codes)} - {code} duplicated with people {people_names}. Delete {person_to_delete}?")
    if input("Continue?") in ['yes', 'y']:
        StaffologyEmployeeAPI().delete_employees("3e863ec8-a81f-45a5-96b9-0c4144c97148", [person_to_delete[1]])

file_path = 'people_to_update.csv'
df = pd.DataFrame(people_to_update)
df.columns = ['name', 'id', 'payroll_code']
df.to_csv(file_path, index=False)
