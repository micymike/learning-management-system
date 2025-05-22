#!/usr/bin/env python3

from backend.repo_analyzer import analyze_repo

def main():
    code = analyze_repo('https://github.com/Vaniah1/Blog')
    with open('repo_code.txt', 'w') as f:
        f.write(code)

if __name__ == '__main__':
    main()
