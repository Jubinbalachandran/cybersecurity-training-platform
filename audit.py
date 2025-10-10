import os
import re

# Define your project root
project_root = r"D:\Jubin\Projects\Cybersecurity Awareness"

# Define expected files or folders (customize this!)
expected_files = [
    "backend/server.js",
    "models/UserResponse.js",
    "frontend/PhishingScenario.js",
    "logs/",
    "data/",
    "README.md"
]

# Track issues
missing = []
broken_links = []
empty_files = []
duplicates = {}

# Check for expected files
for path in expected_files:
    full_path = os.path.join(project_root, path)
    if not os.path.exists(full_path):
        missing.append(path)

# Walk through all files
for root, _, files in os.walk(project_root):
    for file in files:
        full_path = os.path.join(root, file)

        # Check for empty files
        if os.path.getsize(full_path) == 0:
            empty_files.append(full_path)

        # Track duplicates
        if file in duplicates:
            duplicates[file].append(full_path)
        else:
            duplicates[file] = [full_path]

        # Check for broken links in .md, .html, .js
        if file.endswith((".md", ".html", ".js")):
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                links = re.findall(r'href=["\'](.*?)["\']', content) + re.findall(r'import .*? from ["\'](.*?)["\']', content)
                for link in links:
                    if not link.startswith(("http", "https")):
                        link_path = os.path.normpath(os.path.join(root, link))
                        if not os.path.exists(link_path):
                            broken_links.append((full_path, link))

# Print results
print("\n🔍 Missing Expected Files:")
for m in missing:
    print(f" - {m}")

print("\n⚠️ Empty Files:")
for e in empty_files:
    print(f" - {e}")

print("\n🔗 Broken Internal Links:")
for f, l in broken_links:
    print(f" - {f} → {l}")

print("\n📁 Duplicate Filenames:")
for name, paths in duplicates.items():
    if len(paths) > 1:
        print(f" - {name}:")
        for p in paths:
            print(f"    • {p}")
