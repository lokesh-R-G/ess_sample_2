import pathlib, sys

def clean_file(path: pathlib.Path):
    try:
        data = path.read_bytes()
        if b'\x00' in data:
            new_data = data.replace(b'\x00', b'')
            path.write_bytes(new_data)
            print(f"Cleaned null bytes in {path}")
    except Exception as e:
        print(f"Error processing {path}: {e}", file=sys.stderr)

base = pathlib.Path('backend/tests')
for py_file in base.rglob('*.py'):
    clean_file(py_file)
print('Done cleaning null bytes.')
