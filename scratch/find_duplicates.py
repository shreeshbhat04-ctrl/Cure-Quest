import re
from collections import Counter

file_path = r'c:\Users\shree\project\Cure-Quest\src\cure_quest\api\models.py'
with open(file_path, 'r') as f:
    content = f.read()

classes = re.findall(r'^class (\w+)\(BaseModel\):', content, re.MULTILINE)
duplicates = [name for name, count in Counter(classes).items() if count > 1]

if duplicates:
    print(f"Found duplicate classes: {duplicates}")
else:
    print("No duplicate classes found.")
