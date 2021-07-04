# monster-wizard
MonsterWizard is a python tool to help you get the most out of your D&D homebrew and purchased PDFs, by allowing you to directly convert statblocks into a structured data format of your choice.

It currently supports
- PNG
- JPG
- PDF

MW makes use of AWS Textract to turn images of statblocks into text, this means you need to setup an AWS user in order to run it
The PDF import makes use of functionality from poppler, so this must be installed

Once setup, MW can be used from either the command line, or from within a jupyter notebook

## Command Line Use
python app.py [file] 