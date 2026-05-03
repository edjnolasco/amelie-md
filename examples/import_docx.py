importer = DocxImporter()
doc = importer.import_file(input_path)

markdown = doc.to_markdown()

exporter.export(markdown, output_path)