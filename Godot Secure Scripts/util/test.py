import os
import backup

def test():
    current = os.path.dirname(os.path.abspath(__file__))


    #### BACKUP ####

    print("\n> start backup")

    test_file = os.path.join(current, "test3.txt")
    test_file_back = test_file + backup.get_suffix()

    content = "foo content"

    # FT
    with open(test_file, 'w', encoding='utf-8') as wfile:
        wfile.write(content)
    assert os.path.exists(test_file), f"Test file not found in: {test_file}"


    backup.backup(test_file)
    assert os.path.exists(test_file_back), f"Test file backup not found in: {test_file_back}"
    

    with open(test_file_back, 'r', encoding='utf-8') as rfile:
        print(f"\n[CONTENT]\nOrigin content: {content}\nBackup content: {rfile.read()}")


    print("\n> test backup overwrite")

    content = content + " overwrited!"

    with open(test_file, 'w', encoding='utf-8') as wfile:
        wfile.write(content)

    backup.backup(test_file)


    print("\n> finally result")
    with open(test_file_back, 'r', encoding='utf-8') as rfile:
        print(f"\n[CONTENT]\nOrigin content: {content}\nBackup content: {rfile.read()}")


    # TD
    os.remove(test_file)
    os.remove(test_file_back)


test()