import re
import glob

files = glob.glob('templates/**/*.html', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    original = content

    # Replace: "%.2f"|format(X) => X|ind
    pattern = r'"%.2f"\|format\(([^)]+)\)'
    content = re.sub(pattern, lambda m: m.group(1) + '|ind', content)

    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f'Updated: {f}')

print('Done!')
