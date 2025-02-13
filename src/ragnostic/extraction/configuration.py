from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
)
def get_default_pipeline_configuration()->PdfPipelineOptions:
    
    pipeline_options = PdfPipelineOptions()

    # Table extraction options
    pipeline_options.do_table_structure = True  # Enable table structure recognition
    pipeline_options.table_structure_options.do_cell_matching = True  # Map structure back to PDF cells
    pipeline_options.generate_table_images = True

    # Image handling options
    pipeline_options.images_scale = 2.0  # Control image resolution/quality
    pipeline_options.generate_picture_images = True  # Ensure images are extracted
    pipeline_options.generate_page_images = True  # Keep page images for reference

    # Performance options
    accelerator_options = AcceleratorOptions(
        num_threads=4, 
        device = AcceleratorDevice.CPU,  # AUTO will Let Docling choose best device (CPU/GPU/MPS)
    )
    pipeline_options.accelerator_options = accelerator_options

    # Set OCR in pipeline options
    ocr_options = TesseractOcrOptions(
        lang=["eng"],  # Default is ["eng"]. Use ISO 639-2 codes, e.g., ["eng", "fra", "deu"]. 
                    # Use ["auto"] for automatic language detection
        
        force_full_page_ocr=False,  # Default False. Set True to OCR entire pages instead of 
                                    # just areas without programmatic text
    )

    pipeline_options.do_ocr = True  # Enable OCR processing
    pipeline_options.ocr_options = ocr_options
    return pipeline_options

