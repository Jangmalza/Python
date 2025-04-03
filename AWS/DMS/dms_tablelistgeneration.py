import json
import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
filename = f"{now}.json"


with open("tablelist.txt", "r") as f:
    Table_List = f.readlines()
Table_List = [ele.rstrip('\n') for ele in Table_List]

output_data = {"rules": []}

for idx, table_name in enumerate(Table_List, start=1):
    rule = {
        "rule-type": "selection",
        "rule-id": str(idx),
        "rule-name": f"rule_{idx}",
        "object-locator": {
            "schema-name": "",
            "table-name": table_name
        },
        "rule-action": "include",
        "filters": [],
        "parallel-load": None,
        "isAutoSegmentationChecked": False
    }
    output_data["rules"].append(rule)
    print(f"테이블: {table_name}")

with open(filename, "w") as outfile:
    json.dump(output_data, outfile, indent=4)

print("완료")
