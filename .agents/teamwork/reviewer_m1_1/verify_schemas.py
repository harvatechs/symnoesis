import glob
import json

schemas = sorted(glob.glob("E:/Symnoesis/spec/schemas/*.schema.json"))
print(f"Found {len(schemas)} schema files:")
assert len(schemas) == 16, f"Expected 16 schemas, found {len(schemas)}"

for s_path in schemas:
    with open(s_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "$schema" in data, f"Missing $schema in {s_path}"
    assert data["$schema"] == "https://json-schema.org/draft/2020-12/schema", (
        f"Invalid $schema url in {s_path}: {data['$schema']}"
    )
    assert "" not in data, f"Empty key detected in {s_path}"
    filename = s_path.replace("\\", "/").split("/")[-1]
    print(f"  [PASS] {filename}: $schema={data['$schema']}, title={data.get('title')}")

print("\nAll 16 schemas verified valid with correct $schema header and 0 empty keys!")
