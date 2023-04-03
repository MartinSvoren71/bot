import os
import sys
import shutil
from docx2pdf import convert
from PyPDF2 import PdfFileReader, PdfFileWriter

def compress_pdf(input_file, output_file):
    input_pdf = PdfFileReader(input_file)
    output_pdf = PdfFileWriter()

    for page_num in range(input_pdf.getNumPages()):
        output_pdf.addPage(input_pdf.getPage(page_num))

    output_pdf.setPageLayout('/TwoColumnLeft')

    with open(output_file, 'wb') as f:
        output_pdf.write(f)

def convert_and_compress(input_path, output_path):
    convert(input_path, output_path)
    compress_pdf(output_path, output_path)

def process_files(root, files):
    for file in files:
        if file.endswith(('.docx', '.txt', '.doc')):
            input_path = os.path.join(root, file)
            output_path = os.path.join(root, f'{os.path.splitext(file)[0]}.pdf')
            try:
                convert_and_compress(input_path, output_path)
                os.remove(input_path)
                print(f'Successfully converted and compressed: {input_path}')
            except Exception as e:
                print(f'Error converting {input_path}: {e}')

def main():
    start_directory = "Data/"

    for root, dirs, files in os.walk(start_directory):
        process_files(root, files)

if __name__ == "__main__":
    main()