# Documentation Technique Complète: DocxFilesMerger CLI

## Architecture

DocxFilesMerger est un script autonome avec architecture modulaire.

## Fonctions

- process_zip_file: Traitement complet d'une archive
- extract_doc_files: Extraction des documents
- convert_doc_to_docx: Conversion DOC→DOCX
- merge_docx_files: Fusion en un document
- convert_docx_to_pdf: Génération PDF

## Limitations

1. Sans LibreOffice, conversion DOC limitée
2. Fusion peut perdre certains styles complexes
3. PDF basique sans LibreOffice
