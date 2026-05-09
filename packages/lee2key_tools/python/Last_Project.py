import hou, os
def execute():
    userdir = hou.getenv('HOUDINI_USER_PREF_DIR')
    file = os.path.join(userdir, "file.history")
    with open(file) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '}' in line:
                last_line = lines[i - 1].strip()
                break
        hou.hipFile.load(last_line)