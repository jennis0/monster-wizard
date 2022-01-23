# PDF2VTT
PDF2VTT is a python tool to help you get the most out of D&D 5e homebrew and purchased PDFs. It allows you to directly convert statblocks into a structured data format of your choice that can then be imported into virtual tabletops (or any other storage/visualisation solution of your choice).

The tool is focused on importing PDFs but it also provides support for png and jpg files via AWS Textract - other OCR tools could feasibly be used but I found the performance wasn't good enough to be reliable.
To use this feature you need to setup an AWS user account. [TODO: Instructions].

Once setup, PDF2VTT can be used from either the command line, or from within a jupyter notebook

## VTT Support
Currently PDF2VTT only supports exports to FoundryVTT and to its own native intermediary format. I'd like to add a future capability to export to the standard WotC statblock format as well.
Because the hard work is done when generating the internal intermediary format, it should be relatively simple to write exporters for any other format of your choice, even something like GMBinder monster statblocks or HTML display.

## Foundry Import & Spell/Image Linking Functionality
Technically the output generated is not a foundry compendium, but the import/export format expected by Mana's Compendium Importer module(https://foundryvtt.com/packages/mkah-compendium-importer).
Additionally, monster/feature/spell images, and spell descriptions cannot be added as they are not included within the texts.

As a work-around, we support using existing foundry compendia to provide spells and feature images. To do this, export any spell, item, or feature compendiums you want to use from Foundry (using Mana's importer) and put them in a folder called './foundry' in the directory you are running in. These will be picked up and used to correctly link spells and add images to imported features.

## Python Setup
[Optionally, create a virtual environment]
pip install -f requirements.txt

## Command Line Use
`python pdf2vtt.py [input_file] --output [output_file] --output-format [fvtt|default]`

If you want to add proper metadata to the output file you can use
`--author [authors,] --source [proper name of document]`

Any additional metadata required by the output format will be requested in the command line.

By default, the program will append additional monsters to an existing file if one exists. Use the `--overwrite` argument to create a new file from scratch.

## Quality
I've tried to pick a variety of PDF formats when testing PDF2VTT to ensure it has at least passable performance on basically anything. The current test set includes (along with rough guides for accuracy)
 - 5e SRD (95%)
 - Outclassed: The NPC Statblock Compendium (99.9%)
 - Kobold Press: Tome of Beasts (90%)
 - Kobold Press: Warlock 15: Boss Monsters (100%)
 - Heliana's Guide to Monster Hunting: Shadow of the Broodmother (90%)
Along with several small pieces of homebrew I've downloaded from Reddit. 

In general, for sensibly formatted PDFs, expect between 90-100% accuracy, at this point the most common errors are simply merging flavour text into statblocks, along with occasionally missing features.

If you are using this and find a PDF where the performance is particularly poor let me know and I'll see if it can be used to improve the system as a whole.

## PDFType Warning
Not all PDFs can be imported, some have the text baked into the image which means we don't have access to the text without running OCR. To check if this is the case, try to highlight text within the document, if it can't be selected, it can't be parsed.
Hypothetically this could be detected and we could use the image processing backend to extract text, but this hasn't been implement yet

## TODO
- Finish FVTT import
- Better use of Foundry compendia by using defined items
- Improve handling of metadata entry from the command line.
- Handle 'image-only' PDFs which don't contain native text.
- Improve AWS Textract setup or even allow local OCR.