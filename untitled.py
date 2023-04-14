import io
import PyPDF2
from Crypto.Cipher import AES


def decrypt_pdf(input_file, output_file, password):
    # Read the input PDF file
    with open(input_file, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)

        # Check if the file is encrypted
        if reader.isEncrypted:
            try:
                # Try to decrypt the file with the given password
                if reader.decrypt(password) == 1:
                    print("PDF successfully decrypted.")

                    # Create a new PDF file to save the decrypted content
                    writer = PyPDF2.PdfFileWriter()

                    # Loop through all pages and add them to the new PDF
                    for i in range(reader.getNumPages()):
                        writer.addPage(reader.getPage(i))

                    # Write the decrypted content to the output file
                    with open(output_file, 'wb') as output:
                        writer.write(output)

                    print("Decrypted PDF saved as:", output_file)
                else:
                    print("Incorrect password. Unable to decrypt the PDF.")
            except NotImplementedError:
                print("Decryption method not supported. Unable to decrypt the PDF.")
        else:
            print("The PDF is not encrypted. No decryption needed.")


if __name__ == '__main__':
    input_file = 'encrypted.pdf'
    output_file = 'decrypted.pdf'
    password = 'your_password'

    decrypt_pdf(input_file, output_file, password)
