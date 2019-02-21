# r'''Convert LaTeX or TeX source to PDF or DVI, and escape strings for LaTeX.
#
# **The python-tex project is obsolete!** Please have a look at Texcaller_.
#
# .. _Texcaller: http://www.profv.de/texcaller/
#
# Python-tex is a convenient interface
# to the TeX command line tools
# that handles all kinds of errors without much fuzz.
#
# Temporary files are always cleaned up.
# The TeX interpreter is automatically re-run as often as necessary,
# and an exception is thrown
# in case the output fails to stabilize soon enough.
# The TeX interpreter is always run in batch mode,
# so it won't ever get in your way by stopping your application
# when there are issues with your TeX source.
# Instead, an exception is thrown
# that contains all information of the TeX log.
#
# This enables you to debug TeX related issues
# directly within your application
# or within an interactive Python interpreter session.
#
# Example:
#
# >>> from tex import latex2pdf
# >>> document = ur"""
# ... \documentclass{article}
# ... \begin{document}
# ... Hello, World!
# ... \end{document}
# ... """
# >>> pdf = latex2pdf(document)
#
# >>> type(pdf)
# <type 'str'>
# >>> print "PDF size: %.1f KB" % (len(pdf) / 1024.0)
# PDF size: 5.6 KB
# >>> pdf[:5]
# '%PDF-'
# >>> pdf[-6:]
# '%%EOF\n'
# '''
#Адаптировано к Python3

import os
import os.path
import shutil
import subprocess
import tempfile

class TexLiveCaller(object):
    __version__ = '1.8.1'
    __author__ = 'Volker Grabsch & Yuriy Shtanov'
    __author_email__ = 'vog@notjusthosting.com'
    __url__ = 'http://www.profv.de/python-tex/'

    def __init__(self, fnameout):
        self.fname_out = fnameout

    def _file_read(self,filename):
        '''Read the content of a file and close it properly.'''
        f = open(filename, 'rb')
        content = f.read()
        f.close()
        return content

    def _file_write(self,filename, content):
        '''Write into a file and close it properly.'''
        f = open(filename, 'wb')
        f.write(content)
        f.close()

    def convert(self,tex_source, input_format, output_format, max_runs=5):
        '''Convert LaTeX or TeX source to PDF or DVI.'''
        # check arguments
        assert isinstance(tex_source, str)
        try:
            (tex_cmd, output_suffix) = {
                ('tex',   'dvi'): ('tex',      '.dvi'),
                ('latex', 'dvi'): ('latex',    '.dvi'),
                ('tex',   'pdf'): ('pdftex',   '.pdf'),
                ('latex', 'pdf'): ('pdflatex', '.pdf'),
                }[(input_format, output_format)]
        except KeyError:
            raise ValueError('Unable to handle conversion: %s -> %s'
                             % (input_format, output_format))
        if max_runs < 2:
            raise ValueError('max_runs must be at least 2.')
        # create temporary directory
        tex_dir = tempfile.mkdtemp(suffix='', prefix='tex-temp-')
        try:
            # create LaTeX source file
            tex_filename = os.path.join(tex_dir, 'texput.tex')
            self._file_write(tex_filename, tex_source.encode('UTF-8'))
            # run LaTeX processor as often as necessary
            aux_old = None
            for i in range(max_runs):
                tex_process = subprocess.Popen(
                    [tex_cmd,
                     '-interaction=batchmode',
                     '-halt-on-error',
                     '-no-shell-escape',
                     tex_filename,
                     ],
                    stdin=open(os.devnull, 'r'),
                    stdout=open(os.devnull, 'w'),
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    shell=False,
                    cwd=tex_dir,
                    #env={'PATH': os.getenv('PATH')},
                )
                tex_process.wait()
                if tex_process.returncode != 0:
                    log = self._file_read(os.path.join(tex_dir, 'texput.log'))
                    raise ValueError(log)
                aux = self._file_read(os.path.join(tex_dir, 'texput.aux'))
                if aux == aux_old:
                    # aux file stabilized
                    try:
                        if os.path.exists(self.fname_out):
                            self._file_write(self.fname_out, self._file_read(os.path.join(tex_dir, 'texput' + output_suffix)))
                        return self.fname_out
                    except:
                        raise ValueError('No output file was produced.')
                aux_old = aux
                # TODO:
                # Also handle makeindex and bibtex,
                # possibly in a similar manner as described in:
                # http://vim-latex.sourceforge.net/documentation/latex-suite/compiling-multiple.html
            raise ValueError("%s didn't stabilize after %i runs"
                             % ('texput.aux', max_runs))
        finally:
            # remove temporary directory
            shutil.rmtree(tex_dir)

    def tex2dvi(self,tex_source, **kwargs):
        '''Convert TeX source to DVI.'''
        return self.convert(tex_source, 'tex', 'dvi', **kwargs)

    def latex2dvi(self,tex_source, **kwargs):
        '''Convert LaTeX source to DVI.'''
        return self.convert(tex_source, 'latex', 'dvi', **kwargs)

    def tex2pdf(self,tex_source, **kwargs):
        '''Convert TeX source to PDF.'''
        return self.convert(tex_source, 'tex', 'pdf', **kwargs)

    def latex2pdf(self,tex_source, **kwargs):
        '''Convert LaTeX source to PDF.'''
        return self.convert(tex_source, 'latex', 'pdf', **kwargs)

    def test(self):
        document = u"""\\documentclass{article}\
            \\begin{document}\
                Hello, World!\
            \\end{document}\
            """
        #pdf = self.latex2pdf(document)
        return True #os.path.exists(pdf)