import re

def lfs_link(path):
    return f"https://media.githubusercontent.com/media/269652/my-classical-legacy/refs/heads/main/{path}"

def refactor_links(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace PDF links (handles spaces and special characters)
    content = re.sub(
        r"https://github\.com/269652/my-classical-legacy/raw/refs/heads/main/scores/([^\)]*?\.pdf)",
        lambda m: lfs_link(f"scores/{m.group(1)}"),
        content
    )
    # Replace WAV links (handles spaces and special characters)
    content = re.sub(
        r"https://github\.com/269652/my-classical-legacy/raw/refs/heads/main/interpretations/suno/([^\)]*?\.wav)",
        lambda m: lfs_link(f"interpretations/suno/{m.group(1)}"),
        content
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    refactor_links("README.md")