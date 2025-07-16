import glob
import os

def extract_code(base_dir):
    code = ""
    for ext in ['py', 'js', 'jsx', 'ts', 'tsx', 'java', 'cpp', 'c']:
        for file in glob.glob(os.path.join(base_dir, '**', f'*.{ext}'), recursive=True):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    code += f.read() + '\n\n'
            except Exception:
                continue
    return code

if __name__ == "__main__":
    base_dir = "Blog-main/Blog-main"
    code = extract_code(base_dir)
    print(f"Total code length: {len(code)}")
    print("First 500 chars:")
    print(code[:500])
