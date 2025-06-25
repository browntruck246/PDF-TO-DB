import sqlite3
import PyPDF2

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            title TEXT,
            author TEXT,
            num_pages INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            page_number INTEGER,
            text TEXT,
            FOREIGN KEY(document_id) REFERENCES pdf_documents(id)
        )
    ''')
    conn.commit()

def extract_pdf_data(filepath):
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        metadata = reader.metadata
        num_pages = len(reader.pages)
        doc_info = {
            'title': metadata.title if metadata and metadata.title else None,
            'author': metadata.author if metadata and metadata.author else None,
            'num_pages': num_pages
        }
        page_texts = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() if page else ""
            page_texts.append({'page_number': i+1, 'text': text})
        return doc_info, page_texts

def store_in_db(conn, filename, doc_info, page_texts):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pdf_documents (filename, title, author, num_pages)
        VALUES (?, ?, ?, ?)
    ''', (filename, doc_info['title'], doc_info['author'], doc_info['num_pages']))
    doc_id = cursor.lastrowid
    for page in page_texts:
        cursor.execute('''
            INSERT INTO pdf_pages (document_id, page_number, text)
            VALUES (?, ?, ?)
        ''', (doc_id, page['page_number'], page['text']))
    conn.commit()

def process_pdf_to_db(filepath, db_path='pdfs.db'):
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    doc_info, page_texts = extract_pdf_data(filepath)
    store_in_db(conn, filepath, doc_info, page_texts)
    conn.close()
    print(f"PDF '{filepath}' processed and stored in database '{db_path}'.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_db.py <pdf_file_path>")
    else:
        process_pdf_to_db(sys.argv[1])
