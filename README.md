# MonsterWizard
MonsterWizard is a python tool to help you get the most out of D&D homebrew and purchased PDFs, by allowing you to directly convert statblocks into a structured data format of your choice. That can then be imported directly into virtual tabletops (or any other storage/visualisation solution of your choice).

It currently supports
- PNG
- JPG
- PDF

MonsterWizard handles PDFs natively and makes use of AWS Textract to turn images of statblocks into text, this means you need to setup an AWS user in order to run it over images
The PDF import makes use of functionality from poppler for debugging, so this must be installed to run in debug mode

Once setup, MonsterWizard can be used from either the command line, or from within a jupyter notebook

## Python Setup
pip install -f requirements.txt

## Command Line Use
`python app.py [input_file] --output [output_file] --output-format [5et|default]`

If you want to add proper metadata to the output file you can use
`--author [authors,] --source [proper name of document]`

Any additional metadata required by the output format will be requested in the command line.

By default, the program will append additional monsters to an existing file, use the `--overwrite` argument to create a new file from scratch.

## Output Formats
Currently we only support output in a MonsterWizard native JSON format and the 5eTools/Plutonium format, primarily as this is currently the only format which can be imported into FoundryVTT with relative ease. We intend to build native export of FoundryVTT compendiums into the app in the near future.

## TODO
- Improve handling of metadata entry from the command line.
- FoundryVTT Export.
- Monster image grabbing from PDFs.
- Handle 'image-only' PDFs which don't contain native text.
- Improve AWS Textract setup or even allow local OCR.