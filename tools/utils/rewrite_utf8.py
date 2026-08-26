import pathlib
files = [
    "backend/tests/integration/test_api.py",
    "backend/tests/integration/test_diff.py",
    "backend/tests/integration/test_diff2.py",
    "backend/tests/integration/test_logs.py",
    "backend/tests/integration/test_policy.py",
]
for f in files:
    p = pathlib.Path(f)
    data = p.read_bytes()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode('utf-8', errors='ignore')
    p.write_text(text, encoding='utf-8')
print('UTF-8 conversion done')
