# PDF to Markdown Converter

## Overview

The PDF to Markdown converter is a powerful tool within the Twinizer package that extracts content from PDF documents and converts it to well-formatted Markdown. It handles text, images, tables, and document structure, with optional OCR capabilities for scanned documents.

## Features

### Core Features

- **Text Extraction**: Extract text while preserving formatting, headings, and paragraphs
- **Image Extraction**: Extract images from PDFs and save them to a specified directory
- **Table Detection**: Automatically detect and convert tables to Markdown format
- **OCR Integration**: Use Optical Character Recognition for scanned documents
- **Table of Contents Generation**: Create a table of contents based on document structure
- **Metadata Extraction**: Extract document metadata (title, author, creation date)
- **Custom Styling**: Apply custom styling to the generated Markdown

### Advanced Features

- **Selective Page Processing**: Process specific pages or page ranges
- **Image Processing**: Apply filters and transformations to extracted images
- **Layout Analysis**: Preserve document layout with advanced analysis
- **Annotation Extraction**: Extract and convert annotations and comments
- **Form Field Extraction**: Extract form fields and their values
- **Password-Protected PDFs**: Handle password-protected documents

## Installation

```bash
# Basic installation
pip install twinizer

# With OCR dependencies
pip install twinizer[pdf]
```

Required dependencies for full functionality:
- PyPDF2 or PyMuPDF (pdf parsing)
- Pillow (image processing)
- pytesseract (OCR, optional)
- Tesseract OCR engine (for OCR functionality)

## Command Line Usage

```bash
# Basic conversion
twinizer pdf to-markdown input.pdf --output output.md

# With OCR enabled
twinizer pdf to-markdown input.pdf --output output.md --ocr

# Extract images
twinizer pdf to-markdown input.pdf --output output.md --extract-images --images-dir images

# Generate table of contents
twinizer pdf to-markdown input.pdf --output output.md --toc

# Process specific pages
twinizer pdf to-markdown input.pdf --output output.md --pages 1-5,10,15-20

# Full featured conversion
twinizer pdf to-markdown input.pdf --output output.md --ocr --extract-images --images-dir images --toc --metadata
```

## Python API

### Basic Usage

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter()

# Convert PDF to Markdown
markdown = converter.convert("input.pdf")

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)
```

### Advanced Usage

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter with all options
converter = PDFToMarkdownConverter(
    use_ocr=True,                # Enable OCR for text extraction
    extract_images=True,         # Extract images from PDF
    images_dir="images",         # Directory to save extracted images
    ocr_language="eng",          # OCR language (default: eng)
    image_format="png",          # Format for extracted images (png, jpg)
    min_image_size=100,          # Minimum size for extracted images (pixels)
    table_detection=True,        # Enable table detection
    preserve_layout=True,        # Try to preserve document layout
    heading_detection=True,      # Detect and format headings
    code_block_detection=True,   # Detect and format code blocks
    list_detection=True,         # Detect and format lists
    password=None                # Password for protected PDFs
)

# Convert PDF to Markdown with advanced options
markdown = converter.convert(
    pdf_path="input.pdf",
    generate_toc=True,           # Generate table of contents
    include_metadata=True,       # Include document metadata
    page_range="1-5,10,15-20",   # Process specific pages
    heading_level_offset=0,      # Offset for heading levels
    image_width=600,             # Width for embedded images
    image_prefix="img",          # Prefix for image filenames
    code_language_hint="python"  # Default language for code blocks
)

# Get extracted images
markdown, extracted_images = converter.convert(
    pdf_path="input.pdf",
    return_images=True           # Return list of extracted image paths
)

print(f"Extracted {len(extracted_images)} images")
```

## Detailed Feature Examples

### OCR (Optical Character Recognition)

The OCR feature uses Tesseract to extract text from scanned documents or images within PDFs.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter with OCR enabled
converter = PDFToMarkdownConverter(
    use_ocr=True,
    ocr_language="eng"  # Language code for Tesseract
)

# Convert scanned PDF to Markdown
markdown = converter.convert("scanned_document.pdf")
```

#### Multi-language OCR

```python
# For documents with multiple languages
converter = PDFToMarkdownConverter(
    use_ocr=True,
    ocr_language="eng+fra+deu"  # English, French, and German
)
```

#### OCR Configuration

```python
# Advanced OCR configuration
converter = PDFToMarkdownConverter(
    use_ocr=True,
    ocr_language="eng",
    ocr_config="--psm 1 --oem 3"  # Tesseract configuration
)
```

### Image Extraction and Processing

The converter can extract images from PDFs and save them to a specified directory.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter with image extraction enabled
converter = PDFToMarkdownConverter(
    extract_images=True,
    images_dir="images",
    image_format="png",
    min_image_size=100  # Ignore images smaller than 100x100 pixels
)

# Convert PDF to Markdown
markdown = converter.convert("document_with_images.pdf")
```

#### Image Processing

```python
# With image processing
converter = PDFToMarkdownConverter(
    extract_images=True,
    images_dir="images",
    image_processing={
        "resize": (800, None),  # Resize to 800px width, maintain aspect ratio
        "quality": 85,          # JPEG quality (if format is jpg)
        "optimize": True,       # Optimize images
        "grayscale": False      # Convert to grayscale
    }
)
```

#### Image Filtering

```python
# Filter images by size and type
converter = PDFToMarkdownConverter(
    extract_images=True,
    images_dir="images",
    min_image_size=200,         # Minimum size in pixels
    max_image_size=2000,        # Maximum size in pixels
    image_types=["jpeg", "png"] # Only extract these image types
)
```

### Table Detection and Conversion

The converter can detect tables in PDFs and convert them to Markdown tables.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter with table detection enabled
converter = PDFToMarkdownConverter(
    table_detection=True
)

# Convert PDF to Markdown
markdown = converter.convert("document_with_tables.pdf")
```

#### Example of a Converted Table

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

#### Advanced Table Options

```python
# Advanced table options
converter = PDFToMarkdownConverter(
    table_detection=True,
    table_options={
        "header_detection": True,   # Auto-detect table headers
        "min_rows": 2,              # Minimum rows to consider as table
        "min_cols": 2,              # Minimum columns to consider as table
        "max_cell_width": 30,       # Maximum width of cell content
        "cell_alignment": "left"    # Cell content alignment
    }
)
```

### Table of Contents Generation

The converter can generate a table of contents based on the headings detected in the document.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter()

# Convert PDF to Markdown with table of contents
markdown = converter.convert(
    pdf_path="document.pdf",
    generate_toc=True,
    toc_title="## Table of Contents",
    toc_depth=3  # Include headings up to level 3
)
```

#### Example of Generated Table of Contents

```markdown
## Table of Contents

- [Introduction](#introduction)
  - [Background](#background)
  - [Objectives](#objectives)
- [Methodology](#methodology)
  - [Data Collection](#data-collection)
  - [Analysis](#analysis)
- [Results](#results)
- [Conclusion](#conclusion)
```

### Metadata Extraction

The converter can extract and include document metadata in the generated Markdown.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter()

# Convert PDF to Markdown with metadata
markdown = converter.convert(
    pdf_path="document.pdf",
    include_metadata=True
)
```

#### Example of Extracted Metadata

```markdown
---
title: Document Title
author: Author Name
subject: Document Subject
keywords: keyword1, keyword2, keyword3
created: 2023-01-01
modified: 2023-02-15
---

# Document Content Starts Here
```

### Selective Page Processing

The converter can process specific pages or page ranges.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter()

# Convert specific pages to Markdown
markdown = converter.convert(
    pdf_path="document.pdf",
    page_range="1-5,10,15-20"  # Process pages 1-5, 10, and 15-20
)
```

### Password-Protected PDFs

The converter can handle password-protected PDFs.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter

# Create converter
converter = PDFToMarkdownConverter()

# Convert password-protected PDF to Markdown
markdown = converter.convert(
    pdf_path="protected_document.pdf",
    password="your_password"
)
```

## Integration with Other Twinizer Components

### Converting Extracted Images to Mermaid Diagrams

You can combine PDF extraction with image processing to convert diagrams to Mermaid format.

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter
from twinizer.converters.image.mermaid import MermaidDiagramGenerator

# Extract images from PDF
pdf_converter = PDFToMarkdownConverter(extract_images=True)
markdown, extracted_images = pdf_converter.convert("document.pdf", return_images=True)

# Convert diagrams to Mermaid
mermaid_generator = MermaidDiagramGenerator()
mermaid_diagrams = []

for image_path in extracted_images:
    # Check if image might be a diagram
    if image_path.endswith(('.png', '.jpg', '.jpeg')):
        try:
            # Try to convert to flowchart
            mermaid_diagram = mermaid_generator.image_to_flowchart(
                image_path=image_path,
                threshold=128,
                simplify=0.05,
                direction="TB"
            )
            
            # Save Mermaid diagram
            diagram_path = image_path.replace('.png', '.mmd').replace('.jpg', '.mmd').replace('.jpeg', '.mmd')
            with open(diagram_path, 'w') as f:
                f.write(mermaid_diagram)
                
            mermaid_diagrams.append(diagram_path)
            print(f"Converted {image_path} to Mermaid diagram: {diagram_path}")
        except Exception as e:
            print(f"Failed to convert {image_path} to Mermaid: {e}")

print(f"Successfully converted {len(mermaid_diagrams)} images to Mermaid diagrams")
```

### Converting Extracted Images to ASCII Art

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter
from twinizer.converters.image.ascii import AsciiArtConverter

# Extract images from PDF
pdf_converter = PDFToMarkdownConverter(extract_images=True)
markdown, extracted_images = pdf_converter.convert("document.pdf", return_images=True)

# Convert images to ASCII art
ascii_converter = AsciiArtConverter()
ascii_arts = []

for image_path in extracted_images:
    try:
        # Convert to ASCII art
        ascii_art = ascii_converter.convert(
            image_path=image_path,
            width=80,
            output_format="text"
        )
        
        # Save ASCII art
        art_path = image_path + ".txt"
        with open(art_path, 'w') as f:
            f.write(ascii_art)
            
        ascii_arts.append(art_path)
        print(f"Converted {image_path} to ASCII art: {art_path}")
    except Exception as e:
        print(f"Failed to convert {image_path} to ASCII art: {e}")

print(f"Successfully converted {len(ascii_arts)} images to ASCII art")
```

### Converting Extracted Images to 3D Models

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter
from twinizer.converters.image.image_to_3d import ImageTo3DConverter

# Extract images from PDF
pdf_converter = PDFToMarkdownConverter(extract_images=True)
markdown, extracted_images = pdf_converter.convert("document.pdf", return_images=True)

# Convert images to 3D models
model_converter = ImageTo3DConverter(output_dir="3d_models")
models = []

for image_path in extracted_images:
    try:
        # Convert to height map
        heightmap_path = model_converter.image_to_heightmap(
            image_path=image_path,
            invert=False,
            blur_sigma=1.0
        )
        
        # Convert to 3D mesh
        mesh_path = model_converter.heightmap_to_mesh(
            heightmap_path=heightmap_path,
            scale_z=0.1,
            output_format="obj"
        )
        
        models.append(mesh_path)
        print(f"Converted {image_path} to 3D model: {mesh_path}")
    except Exception as e:
        print(f"Failed to convert {image_path} to 3D model: {e}")

print(f"Successfully converted {len(models)} images to 3D models")
```

## Advanced Examples

### Complete PDF Analysis Pipeline

This example demonstrates a complete PDF analysis pipeline that:
1. Converts a PDF to Markdown
2. Extracts images
3. Converts diagrams to Mermaid
4. Generates 3D models from charts
5. Creates a summary report

```python
import os
from twinizer.converters.pdf2md import PDFToMarkdownConverter
from twinizer.converters.image.mermaid import MermaidDiagramGenerator
from twinizer.converters.image.image_to_3d import ImageTo3DConverter
from twinizer.converters.image.ascii import AsciiArtConverter

def analyze_pdf(pdf_path, output_dir="output"):
    """Complete PDF analysis pipeline."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create converters
    pdf_converter = PDFToMarkdownConverter(
        use_ocr=True,
        extract_images=True,
        images_dir=os.path.join(output_dir, "images")
    )
    
    mermaid_generator = MermaidDiagramGenerator()
    model_converter = ImageTo3DConverter(output_dir=os.path.join(output_dir, "3d_models"))
    ascii_converter = AsciiArtConverter()
    
    # Convert PDF to Markdown
    print(f"Converting {pdf_path} to Markdown...")
    markdown, extracted_images = pdf_converter.convert(
        pdf_path=pdf_path,
        generate_toc=True,
        include_metadata=True,
        return_images=True
    )
    
    # Save Markdown
    markdown_path = os.path.join(output_dir, "document.md")
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"Extracted {len(extracted_images)} images")
    
    # Process each image
    mermaid_diagrams = []
    ascii_arts = []
    models = []
    
    for image_path in extracted_images:
        image_name = os.path.basename(image_path)
        print(f"Processing image: {image_name}")
        
        # Try to convert to Mermaid diagram
        try:
            mermaid_path = os.path.join(output_dir, "mermaid", image_name + ".mmd")
            os.makedirs(os.path.dirname(mermaid_path), exist_ok=True)
            
            mermaid_diagram = mermaid_generator.image_to_flowchart(image_path)
            with open(mermaid_path, "w") as f:
                f.write(mermaid_diagram)
            
            mermaid_diagrams.append(mermaid_path)
            print(f"  Created Mermaid diagram: {mermaid_path}")
        except Exception as e:
            print(f"  Failed to create Mermaid diagram: {e}")
        
        # Try to convert to ASCII art
        try:
            ascii_path = os.path.join(output_dir, "ascii", image_name + ".txt")
            os.makedirs(os.path.dirname(ascii_path), exist_ok=True)
            
            ascii_art = ascii_converter.convert(
                image_path=image_path,
                width=80,
                output_format="text"
            )
            with open(ascii_path, "w") as f:
                f.write(ascii_art)
            
            ascii_arts.append(ascii_path)
            print(f"  Created ASCII art: {ascii_path}")
        except Exception as e:
            print(f"  Failed to create ASCII art: {e}")
        
        # Try to convert to 3D model
        try:
            # Convert to height map
            heightmap_path = model_converter.image_to_heightmap(image_path)
            
            # Convert to 3D mesh
            mesh_path = model_converter.heightmap_to_mesh(
                heightmap_path=heightmap_path,
                scale_z=0.1,
                output_format="obj"
            )
            
            models.append(mesh_path)
            print(f"  Created 3D model: {mesh_path}")
        except Exception as e:
            print(f"  Failed to create 3D model: {e}")
    
    # Create summary report
    summary_path = os.path.join(output_dir, "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# PDF Analysis Summary\n\n")
        f.write(f"## Source Document\n\n")
        f.write(f"- PDF: {pdf_path}\n")
        f.write(f"- Markdown: {markdown_path}\n\n")
        
        f.write(f"## Extracted Images ({len(extracted_images)})\n\n")
        for image in extracted_images:
            f.write(f"- {image}\n")
        f.write("\n")
        
        f.write(f"## Mermaid Diagrams ({len(mermaid_diagrams)})\n\n")
        for diagram in mermaid_diagrams:
            f.write(f"- {diagram}\n")
        f.write("\n")
        
        f.write(f"## ASCII Art ({len(ascii_arts)})\n\n")
        for art in ascii_arts:
            f.write(f"- {art}\n")
        f.write("\n")
        
        f.write(f"## 3D Models ({len(models)})\n\n")
        for model in models:
            f.write(f"- {model}\n")
    
    print(f"Analysis complete! Summary saved to {summary_path}")
    return summary_path

# Usage
analyze_pdf("document.pdf", "analysis_output")
```

## Troubleshooting

### Common Issues

#### OCR Not Working

If OCR is not working properly:

1. Ensure Tesseract is installed on your system:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   
   # Windows
   # Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Verify the language data is installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr-eng  # For English
   sudo apt-get install tesseract-ocr-fra  # For French
   ```

3. Set the correct path to Tesseract:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
   
   converter = PDFToMarkdownConverter(
       use_ocr=True,
       tesseract_path=r'/path/to/tesseract'
   )
   ```

#### Image Extraction Issues

If images are not being extracted properly:

1. Check if the PDF contains actual images or vector graphics
2. Try adjusting the minimum image size:
   ```python
   converter = PDFToMarkdownConverter(
       extract_images=True,
       min_image_size=50  # Lower threshold to catch smaller images
   )
   ```

3. For complex PDFs, try using PyMuPDF instead of PyPDF2:
   ```python
   converter = PDFToMarkdownConverter(
       extract_images=True,
       pdf_engine="pymupdf"  # Use PyMuPDF instead of PyPDF2
   )
   ```

#### Table Detection Issues

If tables are not being detected properly:

1. Try adjusting the table detection parameters:
   ```python
   converter = PDFToMarkdownConverter(
       table_detection=True,
       table_options={
           "min_rows": 2,
           "min_cols": 2,
           "line_detection_threshold": 0.8
       }
   )
   ```

2. For complex tables, consider using OCR with table detection:
   ```python
   converter = PDFToMarkdownConverter(
       use_ocr=True,
       table_detection=True,
       ocr_config="--psm 6"  # Assume a single uniform block of text
   )
   ```

## Performance Optimization

For large PDFs or batch processing:

```python
from twinizer.converters.pdf2md import PDFToMarkdownConverter
import os
import multiprocessing

def process_pdf(pdf_path, output_dir):
    """Process a single PDF."""
    try:
        # Create output path
        base_name = os.path.basename(pdf_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}.md")
        
        # Create converter
        converter = PDFToMarkdownConverter(
            use_ocr=True,
            extract_images=True,
            images_dir=os.path.join(output_dir, "images", name_without_ext)
        )
        
        # Convert PDF to Markdown
        markdown = converter.convert(pdf_path)
        
        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        
        return output_path
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

def batch_process_pdfs(pdf_dir, output_dir, num_processes=None):
    """Process multiple PDFs in parallel."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of PDF files
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) 
                if f.lower().endswith('.pdf')]
    
    # Set up multiprocessing pool
    num_processes = num_processes or multiprocessing.cpu_count()
    
    # Process PDFs in parallel
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = [pool.apply_async(process_pdf, (pdf, output_dir)) 
                  for pdf in pdf_files]
        
        # Get results
        outputs = [result.get() for result in results]
    
    # Filter out None values (errors)
    successful = [out for out in outputs if out]
    
    print(f"Successfully processed {len(successful)} out of {len(pdf_files)} PDFs")
    return successful

# Usage
batch_process_pdfs("pdf_directory", "output_directory", num_processes=4)
```

## Conclusion

The PDF to Markdown converter in Twinizer is a powerful tool for extracting and transforming content from PDF documents. With its extensive feature set and customization options, it can handle a wide range of PDF documents and use cases.

For more information and examples, refer to the [Twinizer User Guide](user_guide.md) or the example scripts in the `examples/` directory.
