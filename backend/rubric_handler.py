#this file is used to handle rubric files, this rubric file contains the rubric for the assignment.

def upload_rubric_file(content):
    # For MVP, just return the content decoded as string
    return content.decode('utf-8')

def load_rubric():
    # Dummy rubric for MVP
    return "Sample Rubric: Code quality, Documentation, Plagiarism"