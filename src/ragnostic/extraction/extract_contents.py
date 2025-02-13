import uuid
import io
import base64

from docling_core.types.doc import TextItem, PictureItem, TableItem
from docling_core.types.doc.document import DoclingDocument
from .core.schema import ContentType, ContentLocation
from .core.schema import ExtractedContent, ExtractedText, ExtractedImage, ExtractedTable

def extract_contents_from_doc(doc : DoclingDocument)->list[ExtractedText | ExtractedImage | ExtractedTable]:
    """Extract contents into pydantic classes"""
    extracted_contents = []
        
    # Iterate through document items in reading order
    for item, level in doc.iterate_items():
        # Handle text content
        if isinstance(item, TextItem):
            location = ContentLocation(
                page=item.prov[0].page_no,
                bbox=(
                    item.prov[0].bbox.l,
                    item.prov[0].bbox.t,
                    item.prov[0].bbox.r,
                    item.prov[0].bbox.b
                )
            )
            
            extracted_text = ExtractedText(
                content_id=str(uuid.uuid4()),
                location=location,
                text=item.text,
                is_header=item.label == "section_header",
                header_level=item.level if hasattr(item, 'level') else None
            )
            extracted_contents.append(extracted_text)
            
        # Handle images
        elif isinstance(item, PictureItem):
            if item.image:
                image_data = item.get_image(doc)  # Get PIL image
                # Convert PIL image to bytes

                img_byte_arr = io.BytesIO()
                image_data.save(img_byte_arr, format='PNG')
                
                img_bytes = img_byte_arr.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')  # Convert to base64 string

                location = ContentLocation(
                    page=item.prov[0].page_no if item.prov else 1,
                    bbox=(
                        item.prov[0].bbox.l,
                        item.prov[0].bbox.t,
                        item.prov[0].bbox.r,
                        item.prov[0].bbox.b
                    )
                )
                
                extracted_image = ExtractedImage(
                    content_id=str(uuid.uuid4()),
                    location=location,
                    image_data=img_base64,
                    format='png',
                    size_bytes=len(img_bytes),
                    caption=None #update this later
                )
                extracted_contents.append(extracted_image)
                
        # Handle tables
        elif isinstance(item, TableItem):
            # Convert table to 2D array
            table_data = []
            for row in range(item.data.num_rows):
                table_row = []
                for col in range(item.data.num_cols):
                    cell_text = ""
                    for cell in item.data.table_cells:
                        if (cell.start_row_offset_idx <= row <= cell.end_row_offset_idx and 
                            cell.start_col_offset_idx <= col <= cell.end_col_offset_idx):
                            cell_text = cell.text
                            break
                    table_row.append(cell_text)
                table_data.append(table_row)
            
            location = ContentLocation(
                page=item.prov[0].page_no if item.prov else 1,
                bbox=(0, 0, 0, 0)  # Extract from item metadata if needed
            )
            
            extracted_table = ExtractedTable(
                content_id=str(uuid.uuid4()),
                location=location,
                table_data=table_data,
                caption=None #update this later
            )
            extracted_contents.append(extracted_table)
    return extracted_contents