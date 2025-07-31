# create_test_file.py
with open('data/sample/ambiguous.txt', 'wb') as f:
    f.write(b'This is a test of fran\xe7ais') # 'ç' in latin-1
