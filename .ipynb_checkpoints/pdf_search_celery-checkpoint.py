from celery import Celery

celery_app = Celery('tasks', broker='pyamqp://guest@localhost//')  # Update this with your broker URL

@celery_app.task
def process_pdf_file(filepath, keyword, pattern):
    matches = []
    is_encrypted = False
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            text = extract_text(filepath, password='', codec='utf-8')
            pages = text.split('\f')
        for page_num, page_text in enumerate(pages):
            for match in pattern.finditer(page_text):
                matches.append((page_num, match.group()))
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        if 'file has not been decrypted' in str(e):
            is_encrypted = True
        return filepath, matches, is_encrypted


    return filepath, matches, is_encrypted