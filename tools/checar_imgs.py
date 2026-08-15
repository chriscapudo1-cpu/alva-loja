import json
from collections import defaultdict
from pathlib import Path

items = json.loads(Path("data/products.json").read_text(encoding="utf-8"))
by = defaultdict(list)
for item in items:
    by[item["tag"]].append(item)
for tag, group in by.items():
    print("---", tag)
    for item in group[:4]:
        print(f"  {item['name'][:36]:36} {item['image'].split('/')[-1]}")
    print(f"  ... +{len(group)-4}")
