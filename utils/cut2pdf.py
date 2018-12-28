from PyPDF2 import PdfFileWriter, PdfFileReader
from tempfile import NamedTemporaryFile

def cut2pdf(src1, src2, skip_pages):
        infile = PdfFileReader(src1, 'rb')
        cutfile = PdfFileReader(src2, 'rb')
        output = PdfFileWriter()

        for i in range(infile.getNumPages()):
            if i not in skip_pages:
             p = infile.getPage(i)
             output.addPage(p)

        print(cutfile.getNumPages())
        for i in range(min(cutfile.getNumPages(),len(skip_pages))):
            output.insertPage(cutfile.getPage(i),skip_pages[i])

        outfile = NamedTemporaryFile(suffix='.pdf')
        outputStream = open(outfile.name, "wb")
        output.write(outputStream)
        outputStream.close()
        return outfile


def copy2tmpfile(src):
    filein_tmp = NamedTemporaryFile(suffix='.pdf')
    with open(filein_tmp.name, 'wb') as dest:
        for chunk in src.chunks():
            dest.write(chunk)
    return filein_tmp