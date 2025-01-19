import os
import shutil
import re

WATCHED_DIR = "/home/garrett/Personal/Notes/0-Inbox/"
TEMPLATES_DIR = "/home/garrett/Personal/Notes/Templates/"


def parse_tags_in_file(filepath):
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            match = re.search(r'\\item \\textbf{Tags:} \\texttt{(.*?)}', content)
            if match:
                return [tag.strip() for tag in match.group(1).split(',')]
    except Exception as e:
        print(f"Error reading tags in {filepath}: {e}")
    return []


def parse_note_title(filepath):
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            match = re.search(r'\\renewcommand{\\notetitle}\{(.*?)\}', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error reading note title in {filepath}: {e}")
    return ""


def archive_file(filepath, tex_filename, file_tags):
    try:
        archive_dir = os.path.join(
            "/home/garrett/Personal/Notes", file_tags[0], file_tags[1], "1-Archive"
        )
        os.makedirs(archive_dir, exist_ok=True)
        tex_archive_path = os.path.join(archive_dir, tex_filename)
        shutil.copy(filepath, tex_archive_path)
        print(f"Archived file {filepath} to {tex_archive_path}")
    except Exception as e:
        print(f"Error archiving file {filepath}: {e}")


def update_main(tex_filename, file_tags):
    try:
        main_dir = os.path.join(
            "/home/garrett/Personal/Notes", file_tags[0], file_tags[1], "0-Main"
        )
        os.makedirs(main_dir, exist_ok=True)
        main_file = os.path.join(main_dir, "main.tex")
        main_template = os.path.join(TEMPLATES_DIR, "main.tex")

        if not os.path.exists(main_file):
            shutil.copy(main_template, main_file)

        with open(main_file, "r+") as f:
            main_content = f.read()
            input_line = f"\\input{{../1-Archive/{tex_filename}}}"
            if input_line not in main_content:
                main_content = main_content.replace(
                    "\\end{document}", f"{input_line}\n\\end{{document}}"
                )
                f.seek(0)
                f.write(main_content)
                f.truncate()
        print(f"Updated {main_file} with {input_line}.")
    except Exception as e:
        print(f"Error updating main: {e}")


def update_toc(tex_filename, file_tags, note_title):
    try:
        # Define paths
        toc_file = os.path.join(
            "/home/garrett/Personal/Notes", file_tags[0], file_tags[1], "1-Archive", "table_of_contents.tex"
        )
        toc_template = os.path.join(TEMPLATES_DIR, "table_of_contents.tex")

        # Copy template if TOC does not exist
        if not os.path.exists(toc_file):
            shutil.copy(toc_template, toc_file)

        with open(toc_file, "r+") as f:
            toc_content = f.read()

            # Ensure tag section exists
            tag_header = f"\\item {file_tags[2]}"
            if tag_header not in toc_content:
                # Insert a new tag section with an empty enumerate block at the last occurrence of \end{enumerate}
                toc_content = toc_content.rsplit(
                    "\\end{enumerate}", 1
                )
                toc_content = f"{toc_content[0]}{tag_header}\n\\begin{{enumerate}}\n\\end{{enumerate}}\n\\end{{enumerate}}{toc_content[1]}"


            # Ensure file entry is under the correct tag
            filename = os.path.splitext(tex_filename)[0]
            file_entry = f"\\item \\hyperref[{filename}]{{{note_title}}}"
            if file_entry not in toc_content:
                # Find the correct tag location to insert the file entry
                tag_position = toc_content.find(tag_header)
                end_enumerate_position = toc_content.find("\\end{enumerate}", tag_position)
                toc_content = (
                    toc_content[:end_enumerate_position]
                    + f"{file_entry}\n"
                    + toc_content[end_enumerate_position:]
                )

            # Write updated content back to file
            f.seek(0)
            f.write(toc_content)
            f.truncate()

        print(f"Updated {toc_file}.")
    except Exception as e:
        print(f"Error updating TOC: {e}")



def delete_files():
    try:
        for filename in os.listdir(WATCHED_DIR):
            file_path = os.path.join(WATCHED_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file {file_path}")
    except Exception as e:
        print(f"Error deleting files: {e}")


def compile():
    for filename in sorted(os.listdir(WATCHED_DIR)):
        filepath = os.path.join(WATCHED_DIR, filename)
        if os.path.isfile(filepath):
            tex_filename = os.path.basename(filepath)
            file_tags = parse_tags_in_file(filepath)
            if file_tags:
                note_title = parse_note_title(filepath)
                if note_title:
                    archive_file(filepath, tex_filename, file_tags)
                    update_main(tex_filename, file_tags)
                    update_toc(tex_filename, file_tags, note_title)
    delete_files()


if __name__ == "__main__":
    compile()

