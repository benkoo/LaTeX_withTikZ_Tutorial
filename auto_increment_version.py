import re

TEX_FILE = "main.tex"
VERSION_PATTERN = r"(DRAFT VERSION )(\d+)\.(\d+)\.(\d+)"


def increment_version(version_str):
    major, minor, patch = map(int, version_str.split('.'))
    patch += 1  # Increment patch version by default
    return f"{major}.{minor}.{patch}"


def main():
    with open(TEX_FILE, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        match = re.search(VERSION_PATTERN, line)
        if match:
            prefix, major, minor, patch = match.groups()
            old_version = f"{major}.{minor}.{patch}"
            new_version = increment_version(old_version)
            # Use a replacement function to avoid group reference issues
            def repl(m):
                return m.group(1) + new_version
            lines[i] = re.sub(VERSION_PATTERN, repl, line)
            print(f"Version updated: {old_version} → {new_version}")
            break

    with open(TEX_FILE, 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    main()
