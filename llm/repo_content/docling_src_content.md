<file_1>
<path>__init__.py</path>
<content>
```python

```
</content>
</file_1>

<file_2>
<path>backend/__init__.py</path>
<content>
```python

```
</content>
</file_2>

<file_3>
<path>backend/abstract_backend.py</path>
<content>
```python
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Set, Union

from docling_core.types.doc import DoclingDocument

if TYPE_CHECKING:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.document import InputDocument


class AbstractDocumentBackend(ABC):
    @abstractmethod
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        self.file = in_doc.file
        self.path_or_stream = path_or_stream
        self.document_hash = in_doc.document_hash
        self.input_format = in_doc.format

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @classmethod
    @abstractmethod
    def supports_pagination(cls) -> bool:
        pass

    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()

        self.path_or_stream = None

    @classmethod
    @abstractmethod
    def supported_formats(cls) -> Set["InputFormat"]:
        pass


class PaginatedDocumentBackend(AbstractDocumentBackend):
    """DeclarativeDocumentBackend.

    A declarative document backend is a backend that can transform to DoclingDocument
    straight without a recognition pipeline.
    """

    @abstractmethod
    def page_count(self) -> int:
        pass


class DeclarativeDocumentBackend(AbstractDocumentBackend):
    """DeclarativeDocumentBackend.

    A declarative document backend is a backend that can transform to DoclingDocument
    straight without a recognition pipeline.
    """

    @abstractmethod
    def convert(self) -> DoclingDocument:
        pass

```
</content>
</file_3>

<file_4>
<path>backend/asciidoc_backend.py</path>
<content>
```python
import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Set, Union

from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupItem,
    GroupLabel,
    ImageRef,
    Size,
    TableCell,
    TableData,
)

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class AsciiDocBackend(DeclarativeDocumentBackend):
    def __init__(self, in_doc: InputDocument, path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        self.path_or_stream = path_or_stream

        try:
            if isinstance(self.path_or_stream, BytesIO):
                text_stream = self.path_or_stream.getvalue().decode("utf-8")
                self.lines = text_stream.split("\n")
            if isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, "r", encoding="utf-8") as f:
                    self.lines = f.readlines()
            self.valid = True

        except Exception as e:
            raise RuntimeError(
                f"Could not initialize AsciiDoc backend for file with hash {self.document_hash}."
            ) from e
        return

    def is_valid(self) -> bool:
        return self.valid

    @classmethod
    def supports_pagination(cls) -> bool:
        return False

    def unload(self):
        return

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.ASCIIDOC}

    def convert(self) -> DoclingDocument:
        """
        Parses the ASCII into a structured document model.
        """

        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="text/asciidoc",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)

        doc = self._parse(doc)

        return doc

    def _parse(self, doc: DoclingDocument):
        """
        Main function that orchestrates the parsing by yielding components:
        title, section headers, text, lists, and tables.
        """

        content = ""

        in_list = False
        in_table = False

        text_data: list[str] = []
        table_data: list[str] = []
        caption_data: list[str] = []

        # parents: dict[int, Union[DocItem, GroupItem, None]] = {}
        parents: dict[int, Union[GroupItem, None]] = {}
        # indents: dict[int, Union[DocItem, GroupItem, None]] = {}
        indents: dict[int, Union[GroupItem, None]] = {}

        for i in range(0, 10):
            parents[i] = None
            indents[i] = None

        for line in self.lines:
            # line = line.strip()

            # Title
            if self._is_title(line):
                item = self._parse_title(line)
                level = item["level"]

                parents[level] = doc.add_text(
                    text=item["text"], label=DocItemLabel.TITLE
                )

            # Section headers
            elif self._is_section_header(line):
                item = self._parse_section_header(line)
                level = item["level"]

                parents[level] = doc.add_heading(
                    text=item["text"], level=item["level"], parent=parents[level - 1]
                )
                for k, v in parents.items():
                    if k > level:
                        parents[k] = None

            # Lists
            elif self._is_list_item(line):

                _log.debug(f"line: {line}")
                item = self._parse_list_item(line)
                _log.debug(f"parsed list-item: {item}")

                level = self._get_current_level(parents)

                if not in_list:
                    in_list = True

                    parents[level + 1] = doc.add_group(
                        parent=parents[level], name="list", label=GroupLabel.LIST
                    )
                    indents[level + 1] = item["indent"]

                elif in_list and item["indent"] > indents[level]:
                    parents[level + 1] = doc.add_group(
                        parent=parents[level], name="list", label=GroupLabel.LIST
                    )
                    indents[level + 1] = item["indent"]

                elif in_list and item["indent"] < indents[level]:

                    # print(item["indent"], " => ", indents[level])
                    while item["indent"] < indents[level]:
                        # print(item["indent"], " => ", indents[level])
                        parents[level] = None
                        indents[level] = None
                        level -= 1

                doc.add_list_item(
                    item["text"], parent=self._get_current_parent(parents)
                )

            elif in_list and not self._is_list_item(line):
                in_list = False

                level = self._get_current_level(parents)
                parents[level] = None

            # Tables
            elif line.strip() == "|===" and not in_table:  # start of table
                in_table = True

            elif self._is_table_line(line):  # within a table
                in_table = True
                table_data.append(self._parse_table_line(line))

            elif in_table and (
                (not self._is_table_line(line)) or line.strip() == "|==="
            ):  # end of table

                caption = None
                if len(caption_data) > 0:
                    caption = doc.add_text(
                        text=" ".join(caption_data), label=DocItemLabel.CAPTION
                    )

                caption_data = []

                data = self._populate_table_as_grid(table_data)
                doc.add_table(
                    data=data, parent=self._get_current_parent(parents), caption=caption
                )

                in_table = False
                table_data = []

            # Picture
            elif self._is_picture(line):

                caption = None
                if len(caption_data) > 0:
                    caption = doc.add_text(
                        text=" ".join(caption_data), label=DocItemLabel.CAPTION
                    )

                caption_data = []

                item = self._parse_picture(line)

                size = None
                if "width" in item and "height" in item:
                    size = Size(width=int(item["width"]), height=int(item["height"]))

                uri = None
                if (
                    "uri" in item
                    and not item["uri"].startswith("http")
                    and item["uri"].startswith("//")
                ):
                    uri = "file:" + item["uri"]
                elif (
                    "uri" in item
                    and not item["uri"].startswith("http")
                    and item["uri"].startswith("/")
                ):
                    uri = "file:/" + item["uri"]
                elif "uri" in item and not item["uri"].startswith("http"):
                    uri = "file://" + item["uri"]

                image = ImageRef(mimetype="image/png", size=size, dpi=70, uri=uri)
                doc.add_picture(image=image, caption=caption)

            # Caption
            elif self._is_caption(line) and len(caption_data) == 0:
                item = self._parse_caption(line)
                caption_data.append(item["text"])

            elif (
                len(line.strip()) > 0 and len(caption_data) > 0
            ):  # allow multiline captions
                item = self._parse_text(line)
                caption_data.append(item["text"])

            # Plain text
            elif len(line.strip()) == 0 and len(text_data) > 0:
                doc.add_text(
                    text=" ".join(text_data),
                    label=DocItemLabel.PARAGRAPH,
                    parent=self._get_current_parent(parents),
                )
                text_data = []

            elif len(line.strip()) > 0:  # allow multiline texts

                item = self._parse_text(line)
                text_data.append(item["text"])

        if len(text_data) > 0:
            doc.add_text(
                text=" ".join(text_data),
                label=DocItemLabel.PARAGRAPH,
                parent=self._get_current_parent(parents),
            )
            text_data = []

        if in_table and len(table_data) > 0:
            data = self._populate_table_as_grid(table_data)
            doc.add_table(data=data, parent=self._get_current_parent(parents))

            in_table = False
            table_data = []

        return doc

    def _get_current_level(self, parents):
        for k, v in parents.items():
            if v == None and k > 0:
                return k - 1

        return 0

    def _get_current_parent(self, parents):
        for k, v in parents.items():
            if v == None and k > 0:
                return parents[k - 1]

        return None

    #   =========   Title
    def _is_title(self, line):
        return re.match(r"^= ", line)

    def _parse_title(self, line):
        return {"type": "title", "text": line[2:].strip(), "level": 0}

    #   =========   Section headers
    def _is_section_header(self, line):
        return re.match(r"^==+", line)

    def _parse_section_header(self, line):
        match = re.match(r"^(=+)\s+(.*)", line)

        marker = match.group(1)  # The list marker (e.g., "*", "-", "1.")
        text = match.group(2)  # The actual text of the list item

        header_level = marker.count("=")  # number of '=' represents level
        return {
            "type": "header",
            "level": header_level - 1,
            "text": text.strip(),
        }

    #   =========   Lists
    def _is_list_item(self, line):
        return re.match(r"^(\s)*(\*|-|\d+\.|\w+\.) ", line)

    def _parse_list_item(self, line):
        """Extract the item marker (number or bullet symbol) and the text of the item."""

        match = re.match(r"^(\s*)(\*|-|\d+\.)\s+(.*)", line)
        if match:
            indent = match.group(1)
            marker = match.group(2)  # The list marker (e.g., "*", "-", "1.")
            text = match.group(3)  # The actual text of the list item

            if marker == "*" or marker == "-":
                return {
                    "type": "list_item",
                    "marker": marker,
                    "text": text.strip(),
                    "numbered": False,
                    "indent": 0 if indent == None else len(indent),
                }
            else:
                return {
                    "type": "list_item",
                    "marker": marker,
                    "text": text.strip(),
                    "numbered": True,
                    "indent": 0 if indent == None else len(indent),
                }
        else:
            # Fallback if no match
            return {
                "type": "list_item",
                "marker": "-",
                "text": line,
                "numbered": False,
                "indent": 0,
            }

    #   =========   Tables
    def _is_table_line(self, line):
        return re.match(r"^\|.*\|", line)

    def _parse_table_line(self, line):
        # Split table cells and trim extra spaces
        return [cell.strip() for cell in line.split("|") if cell.strip()]

    def _populate_table_as_grid(self, table_data):

        num_rows = len(table_data)

        # Adjust the table data into a grid format
        num_cols = max(len(row) for row in table_data)

        data = TableData(num_rows=num_rows, num_cols=num_cols, table_cells=[])
        for row_idx, row in enumerate(table_data):
            # Pad rows with empty strings to match column count
            # grid.append(row + [''] * (max_cols - len(row)))

            for col_idx, text in enumerate(row):
                row_span = 1
                col_span = 1

                cell = TableCell(
                    text=text,
                    row_span=row_span,
                    col_span=col_span,
                    start_row_offset_idx=row_idx,
                    end_row_offset_idx=row_idx + row_span,
                    start_col_offset_idx=col_idx,
                    end_col_offset_idx=col_idx + col_span,
                    col_header=False,
                    row_header=False,
                )
                data.table_cells.append(cell)

        return data

    #   =========   Pictures
    def _is_picture(self, line):
        return re.match(r"^image::", line)

    def _parse_picture(self, line):
        """
        Parse an image macro, extracting its path and attributes.
        Syntax: image::path/to/image.png[Alt Text, width=200, height=150, align=center]
        """
        mtch = re.match(r"^image::(.+)\[(.*)\]$", line)
        if mtch:
            picture_path = mtch.group(1).strip()
            attributes = mtch.group(2).split(",")
            picture_info = {"type": "picture", "uri": picture_path}

            # Extract optional attributes (alt text, width, height, alignment)
            if attributes:
                picture_info["alt"] = attributes[0].strip() if attributes[0] else ""
                for attr in attributes[1:]:
                    key, value = attr.split("=")
                    picture_info[key.strip()] = value.strip()

            return picture_info

        return {"type": "picture", "uri": line}

    #   =========   Captions
    def _is_caption(self, line):
        return re.match(r"^\.(.+)", line)

    def _parse_caption(self, line):
        mtch = re.match(r"^\.(.+)", line)
        if mtch:
            text = mtch.group(1)
            return {"type": "caption", "text": text}

        return {"type": "caption", "text": ""}

    #   =========   Plain text
    def _parse_text(self, line):
        return {"type": "text", "text": line.strip()}

```
</content>
</file_4>

<file_5>
<path>backend/docling_parse_backend.py</path>
<content>
```python
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Optional, Union

import pypdfium2 as pdfium
from docling_core.types.doc import BoundingBox, CoordOrigin, Size
from docling_parse.pdf_parsers import pdf_parser_v1
from PIL import Image, ImageDraw
from pypdfium2 import PdfPage

from docling.backend.pdf_backend import PdfDocumentBackend, PdfPageBackend
from docling.datamodel.base_models import Cell
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class DoclingParsePageBackend(PdfPageBackend):
    def __init__(
        self, parser: pdf_parser_v1, document_hash: str, page_no: int, page_obj: PdfPage
    ):
        self._ppage = page_obj
        parsed_page = parser.parse_pdf_from_key_on_page(document_hash, page_no)

        self.valid = "pages" in parsed_page
        if self.valid:
            self._dpage = parsed_page["pages"][0]
        else:
            _log.info(
                f"An error occurred when loading page {page_no} of document {document_hash}."
            )

    def is_valid(self) -> bool:
        return self.valid

    def get_text_in_rect(self, bbox: BoundingBox) -> str:
        if not self.valid:
            return ""
        # Find intersecting cells on the page
        text_piece = ""
        page_size = self.get_size()
        parser_width = self._dpage["width"]
        parser_height = self._dpage["height"]

        scale = (
            1  # FIX - Replace with param in get_text_in_rect across backends (optional)
        )

        for i in range(len(self._dpage["cells"])):
            rect = self._dpage["cells"][i]["box"]["device"]
            x0, y0, x1, y1 = rect
            cell_bbox = BoundingBox(
                l=x0 * scale * page_size.width / parser_width,
                b=y0 * scale * page_size.height / parser_height,
                r=x1 * scale * page_size.width / parser_width,
                t=y1 * scale * page_size.height / parser_height,
                coord_origin=CoordOrigin.BOTTOMLEFT,
            ).to_top_left_origin(page_height=page_size.height * scale)

            overlap_frac = cell_bbox.intersection_area_with(bbox) / cell_bbox.area()

            if overlap_frac > 0.5:
                if len(text_piece) > 0:
                    text_piece += " "
                text_piece += self._dpage["cells"][i]["content"]["rnormalized"]

        return text_piece

    def get_text_cells(self) -> Iterable[Cell]:
        cells: List[Cell] = []
        cell_counter = 0

        if not self.valid:
            return cells

        page_size = self.get_size()

        parser_width = self._dpage["width"]
        parser_height = self._dpage["height"]

        for i in range(len(self._dpage["cells"])):
            rect = self._dpage["cells"][i]["box"]["device"]
            x0, y0, x1, y1 = rect

            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0

            text_piece = self._dpage["cells"][i]["content"]["rnormalized"]
            cells.append(
                Cell(
                    id=cell_counter,
                    text=text_piece,
                    bbox=BoundingBox(
                        # l=x0, b=y0, r=x1, t=y1,
                        l=x0 * page_size.width / parser_width,
                        b=y0 * page_size.height / parser_height,
                        r=x1 * page_size.width / parser_width,
                        t=y1 * page_size.height / parser_height,
                        coord_origin=CoordOrigin.BOTTOMLEFT,
                    ).to_top_left_origin(page_size.height),
                )
            )
            cell_counter += 1

        def draw_clusters_and_cells():
            image = (
                self.get_page_image()
            )  # make new image to avoid drawing on the saved ones
            draw = ImageDraw.Draw(image)
            for c in cells:
                x0, y0, x1, y1 = c.bbox.as_tuple()
                cell_color = (
                    random.randint(30, 140),
                    random.randint(30, 140),
                    random.randint(30, 140),
                )
                draw.rectangle([(x0, y0), (x1, y1)], outline=cell_color)
            image.show()

        # before merge:
        # draw_clusters_and_cells()

        # cells = merge_horizontal_cells(cells)

        # after merge:
        # draw_clusters_and_cells()

        return cells

    def get_bitmap_rects(self, scale: float = 1) -> Iterable[BoundingBox]:
        AREA_THRESHOLD = 0  # 32 * 32

        for i in range(len(self._dpage["images"])):
            bitmap = self._dpage["images"][i]
            cropbox = BoundingBox.from_tuple(
                bitmap["box"], origin=CoordOrigin.BOTTOMLEFT
            ).to_top_left_origin(self.get_size().height)

            if cropbox.area() > AREA_THRESHOLD:
                cropbox = cropbox.scaled(scale=scale)

                yield cropbox

    def get_page_image(
        self, scale: float = 1, cropbox: Optional[BoundingBox] = None
    ) -> Image.Image:

        page_size = self.get_size()

        if not cropbox:
            cropbox = BoundingBox(
                l=0,
                r=page_size.width,
                t=0,
                b=page_size.height,
                coord_origin=CoordOrigin.TOPLEFT,
            )
            padbox = BoundingBox(
                l=0, r=0, t=0, b=0, coord_origin=CoordOrigin.BOTTOMLEFT
            )
        else:
            padbox = cropbox.to_bottom_left_origin(page_size.height).model_copy()
            padbox.r = page_size.width - padbox.r
            padbox.t = page_size.height - padbox.t

        image = (
            self._ppage.render(
                scale=scale * 1.5,
                rotation=0,  # no additional rotation
                crop=padbox.as_tuple(),
            )
            .to_pil()
            .resize(size=(round(cropbox.width * scale), round(cropbox.height * scale)))
        )  # We resize the image from 1.5x the given scale to make it sharper.

        return image

    def get_size(self) -> Size:
        return Size(width=self._ppage.get_width(), height=self._ppage.get_height())

    def unload(self):
        self._ppage = None
        self._dpage = None


class DoclingParseDocumentBackend(PdfDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        self._pdoc = pdfium.PdfDocument(self.path_or_stream)
        self.parser = pdf_parser_v1()

        success = False
        if isinstance(self.path_or_stream, BytesIO):
            success = self.parser.load_document_from_bytesio(
                self.document_hash, self.path_or_stream
            )
        elif isinstance(self.path_or_stream, Path):
            success = self.parser.load_document(
                self.document_hash, str(self.path_or_stream)
            )

        if not success:
            raise RuntimeError(
                f"docling-parse could not load document with hash {self.document_hash}."
            )

    def page_count(self) -> int:
        return len(self._pdoc)  # To be replaced with docling-parse API

    def load_page(self, page_no: int) -> DoclingParsePageBackend:
        return DoclingParsePageBackend(
            self.parser, self.document_hash, page_no, self._pdoc[page_no]
        )

    def is_valid(self) -> bool:
        return self.page_count() > 0

    def unload(self):
        super().unload()
        self.parser.unload_document(self.document_hash)
        self._pdoc.close()
        self._pdoc = None

```
</content>
</file_5>

<file_6>
<path>backend/docling_parse_v2_backend.py</path>
<content>
```python
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, Union

import pypdfium2 as pdfium
from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_parse.pdf_parsers import pdf_parser_v2
from PIL import Image, ImageDraw
from pypdfium2 import PdfPage

from docling.backend.pdf_backend import PdfDocumentBackend, PdfPageBackend
from docling.datamodel.base_models import Cell, Size

if TYPE_CHECKING:
    from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class DoclingParseV2PageBackend(PdfPageBackend):
    def __init__(
        self, parser: pdf_parser_v2, document_hash: str, page_no: int, page_obj: PdfPage
    ):
        self._ppage = page_obj
        parsed_page = parser.parse_pdf_from_key_on_page(document_hash, page_no)

        self.valid = "pages" in parsed_page and len(parsed_page["pages"]) == 1
        if self.valid:
            self._dpage = parsed_page["pages"][0]
        else:
            _log.info(
                f"An error occurred when loading page {page_no} of document {document_hash}."
            )

    def is_valid(self) -> bool:
        return self.valid

    def get_text_in_rect(self, bbox: BoundingBox) -> str:
        if not self.valid:
            return ""
        # Find intersecting cells on the page
        text_piece = ""
        page_size = self.get_size()

        parser_width = self._dpage["sanitized"]["dimension"]["width"]
        parser_height = self._dpage["sanitized"]["dimension"]["height"]

        scale = (
            1  # FIX - Replace with param in get_text_in_rect across backends (optional)
        )

        cells_data = self._dpage["sanitized"]["cells"]["data"]
        cells_header = self._dpage["sanitized"]["cells"]["header"]

        for i, cell_data in enumerate(cells_data):
            x0 = cell_data[cells_header.index("x0")]
            y0 = cell_data[cells_header.index("y0")]
            x1 = cell_data[cells_header.index("x1")]
            y1 = cell_data[cells_header.index("y1")]

            cell_bbox = BoundingBox(
                l=x0 * scale * page_size.width / parser_width,
                b=y0 * scale * page_size.height / parser_height,
                r=x1 * scale * page_size.width / parser_width,
                t=y1 * scale * page_size.height / parser_height,
                coord_origin=CoordOrigin.BOTTOMLEFT,
            ).to_top_left_origin(page_height=page_size.height * scale)

            overlap_frac = cell_bbox.intersection_area_with(bbox) / cell_bbox.area()

            if overlap_frac > 0.5:
                if len(text_piece) > 0:
                    text_piece += " "
                text_piece += cell_data[cells_header.index("text")]

        return text_piece

    def get_text_cells(self) -> Iterable[Cell]:
        cells: List[Cell] = []
        cell_counter = 0

        if not self.valid:
            return cells

        page_size = self.get_size()

        parser_width = self._dpage["sanitized"]["dimension"]["width"]
        parser_height = self._dpage["sanitized"]["dimension"]["height"]

        cells_data = self._dpage["sanitized"]["cells"]["data"]
        cells_header = self._dpage["sanitized"]["cells"]["header"]

        for i, cell_data in enumerate(cells_data):
            x0 = cell_data[cells_header.index("x0")]
            y0 = cell_data[cells_header.index("y0")]
            x1 = cell_data[cells_header.index("x1")]
            y1 = cell_data[cells_header.index("y1")]

            if x1 < x0:
                x0, x1 = x1, x0
            if y1 < y0:
                y0, y1 = y1, y0

            text_piece = cell_data[cells_header.index("text")]
            cells.append(
                Cell(
                    id=cell_counter,
                    text=text_piece,
                    bbox=BoundingBox(
                        # l=x0, b=y0, r=x1, t=y1,
                        l=x0 * page_size.width / parser_width,
                        b=y0 * page_size.height / parser_height,
                        r=x1 * page_size.width / parser_width,
                        t=y1 * page_size.height / parser_height,
                        coord_origin=CoordOrigin.BOTTOMLEFT,
                    ).to_top_left_origin(page_size.height),
                )
            )
            cell_counter += 1

        def draw_clusters_and_cells():
            image = (
                self.get_page_image()
            )  # make new image to avoid drawing on the saved ones
            draw = ImageDraw.Draw(image)
            for c in cells:
                x0, y0, x1, y1 = c.bbox.as_tuple()
                cell_color = (
                    random.randint(30, 140),
                    random.randint(30, 140),
                    random.randint(30, 140),
                )
                draw.rectangle([(x0, y0), (x1, y1)], outline=cell_color)
            image.show()

        # draw_clusters_and_cells()

        return cells

    def get_bitmap_rects(self, scale: float = 1) -> Iterable[BoundingBox]:
        AREA_THRESHOLD = 0  # 32 * 32

        images = self._dpage["sanitized"]["images"]["data"]
        images_header = self._dpage["sanitized"]["images"]["header"]

        for row in images:
            x0 = row[images_header.index("x0")]
            y0 = row[images_header.index("y0")]
            x1 = row[images_header.index("x1")]
            y1 = row[images_header.index("y1")]

            cropbox = BoundingBox.from_tuple(
                (x0, y0, x1, y1), origin=CoordOrigin.BOTTOMLEFT
            ).to_top_left_origin(self.get_size().height)

            if cropbox.area() > AREA_THRESHOLD:
                cropbox = cropbox.scaled(scale=scale)

                yield cropbox

    def get_page_image(
        self, scale: float = 1, cropbox: Optional[BoundingBox] = None
    ) -> Image.Image:

        page_size = self.get_size()

        if not cropbox:
            cropbox = BoundingBox(
                l=0,
                r=page_size.width,
                t=0,
                b=page_size.height,
                coord_origin=CoordOrigin.TOPLEFT,
            )
            padbox = BoundingBox(
                l=0, r=0, t=0, b=0, coord_origin=CoordOrigin.BOTTOMLEFT
            )
        else:
            padbox = cropbox.to_bottom_left_origin(page_size.height).model_copy()
            padbox.r = page_size.width - padbox.r
            padbox.t = page_size.height - padbox.t

        image = (
            self._ppage.render(
                scale=scale * 1.5,
                rotation=0,  # no additional rotation
                crop=padbox.as_tuple(),
            )
            .to_pil()
            .resize(size=(round(cropbox.width * scale), round(cropbox.height * scale)))
        )  # We resize the image from 1.5x the given scale to make it sharper.

        return image

    def get_size(self) -> Size:
        return Size(width=self._ppage.get_width(), height=self._ppage.get_height())

    def unload(self):
        self._ppage = None
        self._dpage = None


class DoclingParseV2DocumentBackend(PdfDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        self._pdoc = pdfium.PdfDocument(self.path_or_stream)
        self.parser = pdf_parser_v2("fatal")

        success = False
        if isinstance(self.path_or_stream, BytesIO):
            success = self.parser.load_document_from_bytesio(
                self.document_hash, self.path_or_stream
            )
        elif isinstance(self.path_or_stream, Path):
            success = self.parser.load_document(
                self.document_hash, str(self.path_or_stream)
            )

        if not success:
            raise RuntimeError(
                f"docling-parse v2 could not load document {self.document_hash}."
            )

    def page_count(self) -> int:
        # return len(self._pdoc)  # To be replaced with docling-parse API

        len_1 = len(self._pdoc)
        len_2 = self.parser.number_of_pages(self.document_hash)

        if len_1 != len_2:
            _log.error(f"Inconsistent number of pages: {len_1}!={len_2}")

        return len_2

    def load_page(self, page_no: int) -> DoclingParseV2PageBackend:
        return DoclingParseV2PageBackend(
            self.parser, self.document_hash, page_no, self._pdoc[page_no]
        )

    def is_valid(self) -> bool:
        return self.page_count() > 0

    def unload(self):
        super().unload()
        self.parser.unload_document(self.document_hash)
        self._pdoc.close()
        self._pdoc = None

```
</content>
</file_6>

<file_7>
<path>backend/html_backend.py</path>
<content>
```python
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional, Set, Union

from bs4 import BeautifulSoup, Tag
from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    TableCell,
    TableData,
)

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class HTMLDocumentBackend(DeclarativeDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)
        _log.debug("About to init HTML backend...")
        self.soup: Optional[Tag] = None
        # HTML file:
        self.path_or_stream = path_or_stream
        # Initialise the parents for the hierarchy
        self.max_levels = 10
        self.level = 0
        self.parents = {}  # type: ignore
        for i in range(0, self.max_levels):
            self.parents[i] = None
        self.labels = {}  # type: ignore

        try:
            if isinstance(self.path_or_stream, BytesIO):
                text_stream = self.path_or_stream.getvalue()
                self.soup = BeautifulSoup(text_stream, "html.parser")
            if isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, "rb") as f:
                    html_content = f.read()
                    self.soup = BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            raise RuntimeError(
                f"Could not initialize HTML backend for file with hash {self.document_hash}."
            ) from e

    def is_valid(self) -> bool:
        return self.soup is not None

    @classmethod
    def supports_pagination(cls) -> bool:
        return False

    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()

        self.path_or_stream = None

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.HTML}

    def convert(self) -> DoclingDocument:
        # access self.path_or_stream to load stuff
        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="text/html",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)
        _log.debug("Trying to convert HTML...")

        if self.is_valid():
            assert self.soup is not None
            content = self.soup.body or self.soup
            # Replace <br> tags with newline characters
            for br in content.find_all("br"):
                br.replace_with("\n")
            doc = self.walk(content, doc)
        else:
            raise RuntimeError(
                f"Cannot convert doc with {self.document_hash} because the backend failed to init."
            )
        return doc

    def walk(self, element: Tag, doc: DoclingDocument):
        try:
            # Iterate over elements in the body of the document
            for idx, element in enumerate(element.children):
                try:
                    self.analyse_element(element, idx, doc)
                except Exception as exc_child:

                    _log.error(" -> error treating child: ", exc_child)
                    _log.error(" => element: ", element, "\n")
                    raise exc_child

        except Exception as exc:
            pass

        return doc

    def analyse_element(self, element: Tag, idx: int, doc: DoclingDocument):
        """
        if element.name!=None:
            _log.debug("\t"*self.level, idx, "\t", f"{element.name} ({self.level})")
        """

        if element.name in self.labels:
            self.labels[element.name] += 1
        else:
            self.labels[element.name] = 1

        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.handle_header(element, idx, doc)
        elif element.name in ["p"]:
            self.handle_paragraph(element, idx, doc)
        elif element.name in ["pre"]:
            self.handle_code(element, idx, doc)
        elif element.name in ["ul", "ol"]:
            self.handle_list(element, idx, doc)
        elif element.name in ["li"]:
            self.handle_listitem(element, idx, doc)
        elif element.name == "table":
            self.handle_table(element, idx, doc)
        elif element.name == "figure":
            self.handle_figure(element, idx, doc)
        elif element.name == "img":
            self.handle_image(element, idx, doc)
        else:
            self.walk(element, doc)

    def get_direct_text(self, item: Tag):
        """Get the direct text of the <li> element (ignoring nested lists)."""
        text = item.find(string=True, recursive=False)
        if isinstance(text, str):
            return text.strip()

        return ""

    # Function to recursively extract text from all child nodes
    def extract_text_recursively(self, item: Tag):
        result = []

        if isinstance(item, str):
            return [item]

        if item.name not in ["ul", "ol"]:
            try:
                # Iterate over the children (and their text and tails)
                for child in item:
                    try:
                        # Recursively get the child's text content
                        result.extend(self.extract_text_recursively(child))
                    except:
                        pass
            except:
                _log.warn("item has no children")
                pass

        return "".join(result) + " "

    def handle_header(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles header tags (h1, h2, etc.)."""
        hlevel = int(element.name.replace("h", ""))
        slevel = hlevel - 1

        label = DocItemLabel.SECTION_HEADER
        text = element.text.strip()

        if hlevel == 1:
            for key, val in self.parents.items():
                self.parents[key] = None

            self.level = 1
            self.parents[self.level] = doc.add_text(
                parent=self.parents[0], label=DocItemLabel.TITLE, text=text
            )
        else:
            if hlevel > self.level:

                # add invisible group
                for i in range(self.level + 1, hlevel):
                    self.parents[i] = doc.add_group(
                        name=f"header-{i}",
                        label=GroupLabel.SECTION,
                        parent=self.parents[i - 1],
                    )
                self.level = hlevel

            elif hlevel < self.level:

                # remove the tail
                for key, val in self.parents.items():
                    if key > hlevel:
                        self.parents[key] = None
                self.level = hlevel

            self.parents[hlevel] = doc.add_heading(
                parent=self.parents[hlevel - 1],
                text=text,
                level=hlevel,
            )

    def handle_code(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles monospace code snippets (pre)."""
        if element.text is None:
            return
        text = element.text.strip()
        label = DocItemLabel.CODE
        if len(text) == 0:
            return
        doc.add_code(parent=self.parents[self.level], text=text)

    def handle_paragraph(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles paragraph tags (p)."""
        if element.text is None:
            return
        text = element.text.strip()
        label = DocItemLabel.PARAGRAPH
        if len(text) == 0:
            return
        doc.add_text(parent=self.parents[self.level], label=label, text=text)

    def handle_list(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles list tags (ul, ol) and their list items."""

        if element.name == "ul":
            # create a list group
            self.parents[self.level + 1] = doc.add_group(
                parent=self.parents[self.level], name="list", label=GroupLabel.LIST
            )
        elif element.name == "ol":
            # create a list group
            self.parents[self.level + 1] = doc.add_group(
                parent=self.parents[self.level],
                name="ordered list",
                label=GroupLabel.ORDERED_LIST,
            )
        self.level += 1

        self.walk(element, doc)

        self.parents[self.level + 1] = None
        self.level -= 1

    def handle_listitem(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles listitem tags (li)."""
        nested_lists = element.find(["ul", "ol"])

        parent_list_label = self.parents[self.level].label
        index_in_list = len(self.parents[self.level].children) + 1

        if nested_lists:
            name = element.name
            # Text in list item can be hidden within hierarchy, hence
            # we need to extract it recursively
            text = self.extract_text_recursively(element)
            # Flatten text, remove break lines:
            text = text.replace("\n", "").replace("\r", "")
            text = " ".join(text.split()).strip()

            marker = ""
            enumerated = False
            if parent_list_label == GroupLabel.ORDERED_LIST:
                marker = str(index_in_list)
                enumerated = True

            if len(text) > 0:
                # create a list-item
                self.parents[self.level + 1] = doc.add_list_item(
                    text=text,
                    enumerated=enumerated,
                    marker=marker,
                    parent=self.parents[self.level],
                )
                self.level += 1

            self.walk(element, doc)

            self.parents[self.level + 1] = None
            self.level -= 1

        elif isinstance(element.text, str):
            text = element.text.strip()

            marker = ""
            enumerated = False
            if parent_list_label == GroupLabel.ORDERED_LIST:
                marker = f"{str(index_in_list)}."
                enumerated = True
            doc.add_list_item(
                text=text,
                enumerated=enumerated,
                marker=marker,
                parent=self.parents[self.level],
            )
        else:
            _log.warn("list-item has no text: ", element)

    def handle_table(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles table tags."""

        nested_tables = element.find("table")
        if nested_tables is not None:
            _log.warn("detected nested tables: skipping for now")
            return

        # Count the number of rows (number of <tr> elements)
        num_rows = len(element.find_all("tr"))

        # Find the number of columns (taking into account colspan)
        num_cols = 0
        for row in element.find_all("tr"):
            col_count = 0
            for cell in row.find_all(["td", "th"]):
                colspan = int(cell.get("colspan", 1))
                col_count += colspan
            num_cols = max(num_cols, col_count)

        grid = [[None for _ in range(num_cols)] for _ in range(num_rows)]

        data = TableData(num_rows=num_rows, num_cols=num_cols, table_cells=[])

        # Iterate over the rows in the table
        for row_idx, row in enumerate(element.find_all("tr")):

            # For each row, find all the column cells (both <td> and <th>)
            cells = row.find_all(["td", "th"])

            # Check if each cell in the row is a header -> means it is a column header
            col_header = True
            for j, html_cell in enumerate(cells):
                if html_cell.name == "td":
                    col_header = False

            col_idx = 0
            # Extract and print the text content of each cell
            for _, html_cell in enumerate(cells):

                text = html_cell.text
                try:
                    text = self.extract_table_cell_text(html_cell)
                except Exception as exc:
                    _log.warn("exception: ", exc)
                    exit(-1)

                # label = html_cell.name

                col_span = int(html_cell.get("colspan", 1))
                row_span = int(html_cell.get("rowspan", 1))

                while grid[row_idx][col_idx] is not None:
                    col_idx += 1
                for r in range(row_span):
                    for c in range(col_span):
                        grid[row_idx + r][col_idx + c] = text

                cell = TableCell(
                    text=text,
                    row_span=row_span,
                    col_span=col_span,
                    start_row_offset_idx=row_idx,
                    end_row_offset_idx=row_idx + row_span,
                    start_col_offset_idx=col_idx,
                    end_col_offset_idx=col_idx + col_span,
                    col_header=col_header,
                    row_header=((not col_header) and html_cell.name == "th"),
                )
                data.table_cells.append(cell)

        doc.add_table(data=data, parent=self.parents[self.level])

    def get_list_text(self, list_element: Tag, level=0):
        """Recursively extract text from <ul> or <ol> with proper indentation."""
        result = []
        bullet_char = "*"  # Default bullet character for unordered lists

        if list_element.name == "ol":  # For ordered lists, use numbers
            for i, li in enumerate(list_element.find_all("li", recursive=False), 1):
                # Add numbering for ordered lists
                result.append(f"{'    ' * level}{i}. {li.get_text(strip=True)}")
                # Handle nested lists
                nested_list = li.find(["ul", "ol"])
                if nested_list:
                    result.extend(self.get_list_text(nested_list, level + 1))
        elif list_element.name == "ul":  # For unordered lists, use bullet points
            for li in list_element.find_all("li", recursive=False):
                # Add bullet points for unordered lists
                result.append(
                    f"{'    ' * level}{bullet_char} {li.get_text(strip=True)}"
                )
                # Handle nested lists
                nested_list = li.find(["ul", "ol"])
                if nested_list:
                    result.extend(self.get_list_text(nested_list, level + 1))

        return result

    def extract_table_cell_text(self, cell: Tag):
        """Extract text from a table cell, including lists with indents."""
        contains_lists = cell.find(["ul", "ol"])
        if contains_lists is None:
            return cell.text
        else:
            _log.debug(
                "should extract the content correctly for table-cells with lists ..."
            )
            return cell.text

    def handle_figure(self, element: Tag, idx: int, doc: DoclingDocument):
        """Handles image tags (img)."""

        # Extract the image URI from the <img> tag
        # image_uri = root.xpath('//figure//img/@src')[0]

        contains_captions = element.find(["figcaption"])
        if contains_captions is None:
            doc.add_picture(parent=self.parents[self.level], caption=None)

        else:
            texts = []
            for item in contains_captions:
                texts.append(item.text)

            fig_caption = doc.add_text(
                label=DocItemLabel.CAPTION, text=("".join(texts)).strip()
            )
            doc.add_picture(
                parent=self.parents[self.level],
                caption=fig_caption,
            )

    def handle_image(self, element: Tag, idx, doc: DoclingDocument):
        """Handles image tags (img)."""
        doc.add_picture(parent=self.parents[self.level], caption=None)

```
</content>
</file_7>

<file_8>
<path>backend/json/__init__.py</path>
<content>
```python

```
</content>
</file_8>

<file_9>
<path>backend/json/docling_json_backend.py</path>
<content>
```python
from io import BytesIO
from pathlib import Path
from typing import Union

from docling_core.types.doc import DoclingDocument
from typing_extensions import override

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument


class DoclingJSONBackend(DeclarativeDocumentBackend):
    @override
    def __init__(
        self, in_doc: InputDocument, path_or_stream: Union[BytesIO, Path]
    ) -> None:
        super().__init__(in_doc, path_or_stream)

        # given we need to store any actual conversion exception for raising it from
        # convert(), this captures the successful result or the actual error in a
        # mutually exclusive way:
        self._doc_or_err = self._get_doc_or_err()

    @override
    def is_valid(self) -> bool:
        return isinstance(self._doc_or_err, DoclingDocument)

    @classmethod
    @override
    def supports_pagination(cls) -> bool:
        return False

    @classmethod
    @override
    def supported_formats(cls) -> set[InputFormat]:
        return {InputFormat.JSON_DOCLING}

    def _get_doc_or_err(self) -> Union[DoclingDocument, Exception]:
        try:
            json_data: Union[str, bytes]
            if isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, encoding="utf-8") as f:
                    json_data = f.read()
            elif isinstance(self.path_or_stream, BytesIO):
                json_data = self.path_or_stream.getvalue()
            else:
                raise RuntimeError(f"Unexpected: {type(self.path_or_stream)=}")
            return DoclingDocument.model_validate_json(json_data=json_data)
        except Exception as e:
            return e

    @override
    def convert(self) -> DoclingDocument:
        if isinstance(self._doc_or_err, DoclingDocument):
            return self._doc_or_err
        else:
            raise self._doc_or_err

```
</content>
</file_9>

<file_10>
<path>backend/md_backend.py</path>
<content>
```python
import logging
import re
import warnings
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Set, Union

import marko
import marko.element
import marko.ext
import marko.ext.gfm
import marko.inline
from docling_core.types.doc import (
    DocItem,
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    NodeItem,
    TableCell,
    TableData,
    TextItem,
)
from marko import Markdown

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)

_MARKER_BODY = "DOCLING_DOC_MD_HTML_EXPORT"
_START_MARKER = f"#_#_{_MARKER_BODY}_START_#_#"
_STOP_MARKER = f"#_#_{_MARKER_BODY}_STOP_#_#"


class MarkdownDocumentBackend(DeclarativeDocumentBackend):
    def shorten_underscore_sequences(self, markdown_text: str, max_length: int = 10):
        # This regex will match any sequence of underscores
        pattern = r"_+"

        def replace_match(match):
            underscore_sequence = match.group(
                0
            )  # Get the full match (sequence of underscores)

            # Shorten the sequence if it exceeds max_length
            if len(underscore_sequence) > max_length:
                return "_" * max_length
            else:
                return underscore_sequence  # Leave it unchanged if it is shorter or equal to max_length

        # Use re.sub to replace long underscore sequences
        shortened_text = re.sub(pattern, replace_match, markdown_text)

        if len(shortened_text) != len(markdown_text):
            warnings.warn("Detected potentially incorrect Markdown, correcting...")

        return shortened_text

    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        _log.debug("MD INIT!!!")

        # Markdown file:
        self.path_or_stream = path_or_stream
        self.valid = True
        self.markdown = ""  # To store original Markdown string

        self.in_table = False
        self.md_table_buffer: list[str] = []
        self.inline_texts: list[str] = []
        self._html_blocks: int = 0

        try:
            if isinstance(self.path_or_stream, BytesIO):
                text_stream = self.path_or_stream.getvalue().decode("utf-8")
                # remove invalid sequences
                # very long sequences of underscores will lead to unnecessary long processing times.
                # In any proper Markdown files, underscores have to be escaped,
                # otherwise they represent emphasis (bold or italic)
                self.markdown = self.shorten_underscore_sequences(text_stream)
            if isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, "r", encoding="utf-8") as f:
                    md_content = f.read()
                    # remove invalid sequences
                    # very long sequences of underscores will lead to unnecessary long processing times.
                    # In any proper Markdown files, underscores have to be escaped,
                    # otherwise they represent emphasis (bold or italic)
                    self.markdown = self.shorten_underscore_sequences(md_content)
            self.valid = True

            _log.debug(self.markdown)
        except Exception as e:
            raise RuntimeError(
                f"Could not initialize MD backend for file with hash {self.document_hash}."
            ) from e
        return

    def close_table(self, doc: DoclingDocument):
        if self.in_table:
            _log.debug("=== TABLE START ===")
            for md_table_row in self.md_table_buffer:
                _log.debug(md_table_row)
            _log.debug("=== TABLE END ===")
            tcells: List[TableCell] = []
            result_table = []
            for n, md_table_row in enumerate(self.md_table_buffer):
                data = []
                if n == 0:
                    header = [t.strip() for t in md_table_row.split("|")[1:-1]]
                    for value in header:
                        data.append(value)
                    result_table.append(data)
                if n > 1:
                    values = [t.strip() for t in md_table_row.split("|")[1:-1]]
                    for value in values:
                        data.append(value)
                    result_table.append(data)

            for trow_ind, trow in enumerate(result_table):
                for tcol_ind, cellval in enumerate(trow):
                    row_span = (
                        1  # currently supporting just simple tables (without spans)
                    )
                    col_span = (
                        1  # currently supporting just simple tables (without spans)
                    )
                    icell = TableCell(
                        text=cellval.strip(),
                        row_span=row_span,
                        col_span=col_span,
                        start_row_offset_idx=trow_ind,
                        end_row_offset_idx=trow_ind + row_span,
                        start_col_offset_idx=tcol_ind,
                        end_col_offset_idx=tcol_ind + col_span,
                        col_header=False,
                        row_header=False,
                    )
                    tcells.append(icell)

            num_rows = len(result_table)
            num_cols = len(result_table[0])
            self.in_table = False
            self.md_table_buffer = []  # clean table markdown buffer
            # Initialize Docling TableData
            table_data = TableData(
                num_rows=num_rows, num_cols=num_cols, table_cells=tcells
            )
            # Populate
            for tcell in tcells:
                table_data.table_cells.append(tcell)
            if len(tcells) > 0:
                doc.add_table(data=table_data)
        return

    def process_inline_text(
        self, parent_element: Optional[NodeItem], doc: DoclingDocument
    ):
        txt = " ".join(self.inline_texts)
        if len(txt) > 0:
            doc.add_text(
                label=DocItemLabel.PARAGRAPH,
                parent=parent_element,
                text=txt,
            )
        self.inline_texts = []

    def iterate_elements(
        self,
        element: marko.element.Element,
        depth: int,
        doc: DoclingDocument,
        parent_element: Optional[NodeItem] = None,
    ):
        # Iterates over all elements in the AST
        # Check for different element types and process relevant details
        if isinstance(element, marko.block.Heading) and len(element.children) > 0:
            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(
                f" - Heading level {element.level}, content: {element.children[0].children}"  # type: ignore
            )
            if element.level == 1:
                doc_label = DocItemLabel.TITLE
            else:
                doc_label = DocItemLabel.SECTION_HEADER

            # Header could have arbitrary inclusion of bold, italic or emphasis,
            # hence we need to traverse the tree to get full text of a header
            strings: List[str] = []

            # Define a recursive function to traverse the tree
            def traverse(node: marko.block.BlockElement):
                # Check if the node has a "children" attribute
                if hasattr(node, "children"):
                    # If "children" is a list, continue traversal
                    if isinstance(node.children, list):
                        for child in node.children:
                            traverse(child)
                    # If "children" is text, add it to header text
                    elif isinstance(node.children, str):
                        strings.append(node.children)

            traverse(element)
            snippet_text = "".join(strings)
            if len(snippet_text) > 0:
                parent_element = doc.add_text(
                    label=doc_label, parent=parent_element, text=snippet_text
                )

        elif isinstance(element, marko.block.List):
            has_non_empty_list_items = False
            for child in element.children:
                if isinstance(child, marko.block.ListItem) and len(child.children) > 0:
                    has_non_empty_list_items = True
                    break

            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(f" - List {'ordered' if element.ordered else 'unordered'}")
            if has_non_empty_list_items:
                label = GroupLabel.ORDERED_LIST if element.ordered else GroupLabel.LIST
                parent_element = doc.add_group(
                    label=label, name=f"list", parent=parent_element
                )

        elif isinstance(element, marko.block.ListItem) and len(element.children) > 0:
            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(" - List item")

            snippet_text = str(element.children[0].children[0].children)  # type: ignore
            is_numbered = False
            if (
                parent_element is not None
                and isinstance(parent_element, DocItem)
                and parent_element.label == GroupLabel.ORDERED_LIST
            ):
                is_numbered = True
            doc.add_list_item(
                enumerated=is_numbered, parent=parent_element, text=snippet_text
            )

        elif isinstance(element, marko.inline.Image):
            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(f" - Image with alt: {element.title}, url: {element.dest}")

            fig_caption: Optional[TextItem] = None
            if element.title is not None and element.title != "":
                fig_caption = doc.add_text(
                    label=DocItemLabel.CAPTION, text=element.title
                )

            doc.add_picture(parent=parent_element, caption=fig_caption)

        elif isinstance(element, marko.block.Paragraph) and len(element.children) > 0:
            self.process_inline_text(parent_element, doc)

        elif isinstance(element, marko.inline.RawText):
            _log.debug(f" - Paragraph (raw text): {element.children}")
            snippet_text = element.children.strip()
            # Detect start of the table:
            if "|" in snippet_text:
                # most likely part of the markdown table
                self.in_table = True
                if len(self.md_table_buffer) > 0:
                    self.md_table_buffer[len(self.md_table_buffer) - 1] += snippet_text
                else:
                    self.md_table_buffer.append(snippet_text)
            else:
                self.close_table(doc)
                self.in_table = False
                # most likely just inline text
                self.inline_texts.append(str(element.children))

        elif isinstance(element, marko.inline.CodeSpan):
            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(f" - Code Span: {element.children}")
            snippet_text = str(element.children).strip()
            doc.add_code(parent=parent_element, text=snippet_text)

        elif (
            isinstance(element, (marko.block.CodeBlock, marko.block.FencedCode))
            and len(element.children) > 0
            and isinstance((first_child := element.children[0]), marko.inline.RawText)
            and len(snippet_text := (first_child.children.strip())) > 0
        ):
            self.close_table(doc)
            self.process_inline_text(parent_element, doc)
            _log.debug(f" - Code Block: {element.children}")
            doc.add_code(parent=parent_element, text=snippet_text)

        elif isinstance(element, marko.inline.LineBreak):
            if self.in_table:
                _log.debug("Line break in a table")
                self.md_table_buffer.append("")

        elif isinstance(element, marko.block.HTMLBlock):
            self._html_blocks += 1
            self.process_inline_text(parent_element, doc)
            self.close_table(doc)
            _log.debug("HTML Block: {}".format(element))
            if (
                len(element.body) > 0
            ):  # If Marko doesn't return any content for HTML block, skip it
                html_block = element.body.strip()

                # wrap in markers to enable post-processing in convert()
                text_to_add = f"{_START_MARKER}{html_block}{_STOP_MARKER}"
                doc.add_code(parent=parent_element, text=text_to_add)
        else:
            if not isinstance(element, str):
                self.close_table(doc)
                _log.debug("Some other element: {}".format(element))

        processed_block_types = (
            marko.block.ListItem,
            marko.block.Heading,
            marko.block.CodeBlock,
            marko.block.FencedCode,
            # marko.block.Paragraph,
            marko.inline.RawText,
        )

        # Iterate through the element's children (if any)
        if hasattr(element, "children") and not isinstance(
            element, processed_block_types
        ):
            for child in element.children:
                self.iterate_elements(child, depth + 1, doc, parent_element)

    def is_valid(self) -> bool:
        return self.valid

    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()
        self.path_or_stream = None

    @classmethod
    def supports_pagination(cls) -> bool:
        return False

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.MD}

    def convert(self) -> DoclingDocument:
        _log.debug("converting Markdown...")

        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="text/markdown",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)

        if self.is_valid():
            # Parse the markdown into an abstract syntax tree (AST)
            marko_parser = Markdown()
            parsed_ast = marko_parser.parse(self.markdown)
            # Start iterating from the root of the AST
            self.iterate_elements(parsed_ast, 0, doc, None)
            self.process_inline_text(None, doc)  # handle last hanging inline text
            self.close_table(doc=doc)  # handle any last hanging table

            # if HTML blocks were detected, export to HTML and delegate to HTML backend
            if self._html_blocks > 0:

                # export to HTML
                html_backend_cls = HTMLDocumentBackend
                html_str = doc.export_to_html()

                def _restore_original_html(txt, regex):
                    _txt, count = re.subn(regex, "", txt)
                    if count != self._html_blocks:
                        raise RuntimeError(
                            "An internal error has occurred during Markdown conversion."
                        )
                    return _txt

                # restore original HTML by removing previouly added markers
                for regex in [
                    rf"<pre>\s*<code>\s*{_START_MARKER}",
                    rf"{_STOP_MARKER}\s*</code>\s*</pre>",
                ]:
                    html_str = _restore_original_html(txt=html_str, regex=regex)
                self._html_blocks = 0

                # delegate to HTML backend
                stream = BytesIO(bytes(html_str, encoding="utf-8"))
                in_doc = InputDocument(
                    path_or_stream=stream,
                    format=InputFormat.HTML,
                    backend=html_backend_cls,
                    filename=self.file.name,
                )
                html_backend_obj = html_backend_cls(
                    in_doc=in_doc, path_or_stream=stream
                )
                doc = html_backend_obj.convert()
        else:
            raise RuntimeError(
                f"Cannot convert md with {self.document_hash} because the backend failed to init."
            )
        return doc

```
</content>
</file_10>

<file_11>
<path>backend/msexcel_backend.py</path>
<content>
```python
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, Set, Tuple, Union

from docling_core.types.doc import (
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    ImageRef,
    TableCell,
    TableData,
)

# from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import Cell
from openpyxl.drawing.image import Image
from openpyxl.worksheet.worksheet import Worksheet

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)

from typing import Any, List

from PIL import Image as PILImage
from pydantic import BaseModel


class ExcelCell(BaseModel):
    row: int
    col: int
    text: str
    row_span: int
    col_span: int


class ExcelTable(BaseModel):
    num_rows: int
    num_cols: int
    data: List[ExcelCell]


class MsExcelDocumentBackend(DeclarativeDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        # Initialise the parents for the hierarchy
        self.max_levels = 10

        self.parents: Dict[int, Any] = {}
        for i in range(-1, self.max_levels):
            self.parents[i] = None

        self.workbook = None
        try:
            if isinstance(self.path_or_stream, BytesIO):
                self.workbook = load_workbook(filename=self.path_or_stream)

            elif isinstance(self.path_or_stream, Path):
                self.workbook = load_workbook(filename=str(self.path_or_stream))

            self.valid = True
        except Exception as e:
            self.valid = False

            raise RuntimeError(
                f"MsPowerpointDocumentBackend could not load document with hash {self.document_hash}"
            ) from e

    def is_valid(self) -> bool:
        _log.info(f"valid: {self.valid}")
        return self.valid

    @classmethod
    def supports_pagination(cls) -> bool:
        return True

    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()

        self.path_or_stream = None

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.XLSX}

    def convert(self) -> DoclingDocument:
        # Parses the XLSX into a structured document model.

        origin = DocumentOrigin(
            filename=self.file.name or "file.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(name=self.file.stem or "file.xlsx", origin=origin)

        if self.is_valid():
            doc = self._convert_workbook(doc)
        else:
            raise RuntimeError(
                f"Cannot convert doc with {self.document_hash} because the backend failed to init."
            )

        return doc

    def _convert_workbook(self, doc: DoclingDocument) -> DoclingDocument:

        if self.workbook is not None:

            # Iterate over all sheets
            for sheet_name in self.workbook.sheetnames:
                _log.info(f"Processing sheet: {sheet_name}")

                # Access the sheet by name
                sheet = self.workbook[sheet_name]

                self.parents[0] = doc.add_group(
                    parent=None,
                    label=GroupLabel.SECTION,
                    name=f"sheet: {sheet_name}",
                )

                doc = self._convert_sheet(doc, sheet)
        else:
            _log.error("Workbook is not initialized.")

        return doc

    def _convert_sheet(self, doc: DoclingDocument, sheet: Worksheet):

        doc = self._find_tables_in_sheet(doc, sheet)

        doc = self._find_images_in_sheet(doc, sheet)

        return doc

    def _find_tables_in_sheet(self, doc: DoclingDocument, sheet: Worksheet):

        tables = self._find_data_tables(sheet)

        for excel_table in tables:
            num_rows = excel_table.num_rows
            num_cols = excel_table.num_cols

            table_data = TableData(
                num_rows=num_rows,
                num_cols=num_cols,
                table_cells=[],
            )

            for excel_cell in excel_table.data:

                cell = TableCell(
                    text=excel_cell.text,
                    row_span=excel_cell.row_span,
                    col_span=excel_cell.col_span,
                    start_row_offset_idx=excel_cell.row,
                    end_row_offset_idx=excel_cell.row + excel_cell.row_span,
                    start_col_offset_idx=excel_cell.col,
                    end_col_offset_idx=excel_cell.col + excel_cell.col_span,
                    col_header=False,
                    row_header=False,
                )
                table_data.table_cells.append(cell)

            doc.add_table(data=table_data, parent=self.parents[0])

        return doc

    def _find_data_tables(self, sheet: Worksheet):
        """
        Find all compact rectangular data tables in a sheet.
        """
        # _log.info("find_data_tables")

        tables = []  # List to store found tables
        visited: set[Tuple[int, int]] = set()  # Track already visited cells

        # Iterate over all cells in the sheet
        for ri, row in enumerate(sheet.iter_rows(values_only=False)):
            for rj, cell in enumerate(row):

                # Skip empty or already visited cells
                if cell.value is None or (ri, rj) in visited:
                    continue

                # If the cell starts a new table, find its bounds
                table_bounds, visited_cells = self._find_table_bounds(
                    sheet, ri, rj, visited
                )

                visited.update(visited_cells)  # Mark these cells as visited
                tables.append(table_bounds)

        return tables

    def _find_table_bounds(
        self,
        sheet: Worksheet,
        start_row: int,
        start_col: int,
        visited: set[Tuple[int, int]],
    ):
        """
        Determine the bounds of a compact rectangular table.
        Returns:
        - A dictionary with the bounds and data.
        - A set of visited cell coordinates.
        """
        _log.info("find_table_bounds")

        max_row = self._find_table_bottom(sheet, start_row, start_col)
        max_col = self._find_table_right(sheet, start_row, start_col)

        # Collect the data within the bounds
        data = []
        visited_cells = set()
        for ri in range(start_row, max_row + 1):
            for rj in range(start_col, max_col + 1):

                cell = sheet.cell(row=ri + 1, column=rj + 1)  # 1-based indexing

                # Check if the cell belongs to a merged range
                row_span = 1
                col_span = 1

                # _log.info(sheet.merged_cells.ranges)
                for merged_range in sheet.merged_cells.ranges:

                    if (
                        merged_range.min_row <= ri + 1
                        and ri + 1 <= merged_range.max_row
                        and merged_range.min_col <= rj + 1
                        and rj + 1 <= merged_range.max_col
                    ):

                        row_span = merged_range.max_row - merged_range.min_row + 1
                        col_span = merged_range.max_col - merged_range.min_col + 1
                        break

                if (ri, rj) not in visited_cells:
                    data.append(
                        ExcelCell(
                            row=ri - start_row,
                            col=rj - start_col,
                            text=str(cell.value),
                            row_span=row_span,
                            col_span=col_span,
                        )
                    )
                    # _log.info(f"cell: {ri}, {rj} -> {ri - start_row}, {rj - start_col}, {row_span}, {col_span}: {str(cell.value)}")

                    # Mark all cells in the span as visited
                    for span_row in range(ri, ri + row_span):
                        for span_col in range(rj, rj + col_span):
                            visited_cells.add((span_row, span_col))

        return (
            ExcelTable(
                num_rows=max_row + 1 - start_row,
                num_cols=max_col + 1 - start_col,
                data=data,
            ),
            visited_cells,
        )

    def _find_table_bottom(self, sheet: Worksheet, start_row: int, start_col: int):
        """Function to find the bottom boundary of the table"""

        max_row = start_row

        while max_row < sheet.max_row - 1:
            # Get the cell value or check if it is part of a merged cell
            cell = sheet.cell(row=max_row + 2, column=start_col + 1)

            # Check if the cell is part of a merged range
            merged_range = next(
                (mr for mr in sheet.merged_cells.ranges if cell.coordinate in mr),
                None,
            )

            if cell.value is None and not merged_range:
                break  # Stop if the cell is empty and not merged

            # Expand max_row to include the merged range if applicable
            if merged_range:
                max_row = max(max_row, merged_range.max_row - 1)
            else:
                max_row += 1

        return max_row

    def _find_table_right(self, sheet: Worksheet, start_row: int, start_col: int):
        """Function to find the right boundary of the table"""

        max_col = start_col

        while max_col < sheet.max_column - 1:
            # Get the cell value or check if it is part of a merged cell
            cell = sheet.cell(row=start_row + 1, column=max_col + 2)

            # Check if the cell is part of a merged range
            merged_range = next(
                (mr for mr in sheet.merged_cells.ranges if cell.coordinate in mr),
                None,
            )

            if cell.value is None and not merged_range:
                break  # Stop if the cell is empty and not merged

            # Expand max_col to include the merged range if applicable
            if merged_range:
                max_col = max(max_col, merged_range.max_col - 1)
            else:
                max_col += 1

        return max_col

    def _find_images_in_sheet(
        self, doc: DoclingDocument, sheet: Worksheet
    ) -> DoclingDocument:

        # Iterate over byte images in the sheet
        for idx, image in enumerate(sheet._images):  # type: ignore

            try:
                pil_image = PILImage.open(image.ref)

                doc.add_picture(
                    parent=self.parents[0],
                    image=ImageRef.from_pil(image=pil_image, dpi=72),
                    caption=None,
                )
            except:
                _log.error("could not extract the image from excel sheets")

        """
        for idx, chart in enumerate(sheet._charts):  # type: ignore
            try:
                chart_path = f"chart_{idx + 1}.png"
                _log.info(
                    f"Chart found, but dynamic rendering is required for: {chart_path}"
                )

                _log.info(f"Chart {idx + 1}:")
                
                # Chart type
                # _log.info(f"Type: {type(chart).__name__}")
                print(f"Type: {type(chart).__name__}")

                # Extract series data
                for series_idx, series in enumerate(chart.series):
                    #_log.info(f"Series {series_idx + 1}:")
                    print(f"Series {series_idx + 1} type: {type(series).__name__}")
                    #print(f"x-values: {series.xVal}")
                    #print(f"y-values: {series.yVal}")

                    print(f"xval type: {type(series.xVal).__name__}")
                    
                    xvals = []
                    for _ in series.xVal.numLit.pt:
                        print(f"xval type: {type(_).__name__}")
                        if hasattr(_, 'v'):
                            xvals.append(_.v)

                    print(f"x-values: {xvals}")
                            
                    yvals = []
                    for _ in series.yVal:
                        if hasattr(_, 'v'):
                            yvals.append(_.v)
                            
                    print(f"y-values: {yvals}")                    
                    
            except Exception as exc:
                print(exc)
                continue
        """

        return doc

```
</content>
</file_11>

<file_12>
<path>backend/mspowerpoint_backend.py</path>
<content>
```python
import logging
from io import BytesIO
from pathlib import Path
from typing import Set, Union

from docling_core.types.doc import (
    BoundingBox,
    CoordOrigin,
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    ImageRef,
    ProvenanceItem,
    Size,
    TableCell,
    TableData,
)
from PIL import Image, UnidentifiedImageError
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER

from docling.backend.abstract_backend import (
    DeclarativeDocumentBackend,
    PaginatedDocumentBackend,
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class MsPowerpointDocumentBackend(DeclarativeDocumentBackend, PaginatedDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)
        self.namespaces = {
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
            "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
            "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
        }
        # Powerpoint file:
        self.path_or_stream = path_or_stream

        self.pptx_obj = None
        self.valid = False
        try:
            if isinstance(self.path_or_stream, BytesIO):
                self.pptx_obj = Presentation(self.path_or_stream)
            elif isinstance(self.path_or_stream, Path):
                self.pptx_obj = Presentation(str(self.path_or_stream))

            self.valid = True
        except Exception as e:
            raise RuntimeError(
                f"MsPowerpointDocumentBackend could not load document with hash {self.document_hash}"
            ) from e

        return

    def page_count(self) -> int:
        if self.is_valid():
            assert self.pptx_obj is not None
            return len(self.pptx_obj.slides)
        else:
            return 0

    def is_valid(self) -> bool:
        return self.valid

    @classmethod
    def supports_pagination(cls) -> bool:
        return True  # True? if so, how to handle pages...

    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()

        self.path_or_stream = None

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.PPTX}

    def convert(self) -> DoclingDocument:
        # Parses the PPTX into a structured document model.
        # origin = DocumentOrigin(filename=self.path_or_stream.name, mimetype=next(iter(FormatToMimeType.get(InputFormat.PPTX))), binary_hash=self.document_hash)

        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="application/vnd.ms-powerpoint",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(
            name=self.file.stem or "file", origin=origin
        )  # must add origin information
        doc = self.walk_linear(self.pptx_obj, doc)

        return doc

    def generate_prov(
        self, shape, slide_ind, text="", slide_size=Size(width=1, height=1)
    ):
        if shape.left:
            left = shape.left
            top = shape.top
            width = shape.width
            height = shape.height
        else:
            left = 0
            top = 0
            width = slide_size.width
            height = slide_size.height
        shape_bbox = [left, top, left + width, top + height]
        shape_bbox = BoundingBox.from_tuple(shape_bbox, origin=CoordOrigin.BOTTOMLEFT)
        prov = ProvenanceItem(
            page_no=slide_ind + 1, charspan=[0, len(text)], bbox=shape_bbox
        )

        return prov

    def handle_text_elements(self, shape, parent_slide, slide_ind, doc, slide_size):
        is_a_list = False
        is_list_group_created = False
        enum_list_item_value = 0
        new_list = None
        bullet_type = "None"
        list_text = ""
        list_label = GroupLabel.LIST
        doc_label = DocItemLabel.LIST_ITEM
        prov = self.generate_prov(shape, slide_ind, shape.text.strip(), slide_size)

        # Identify if shape contains lists
        for paragraph in shape.text_frame.paragraphs:
            # Check if paragraph is a bullet point using the `element` XML
            p = paragraph._element
            if (
                p.find(".//a:buChar", namespaces={"a": self.namespaces["a"]})
                is not None
            ):
                bullet_type = "Bullet"
                is_a_list = True
            elif (
                p.find(".//a:buAutoNum", namespaces={"a": self.namespaces["a"]})
                is not None
            ):
                bullet_type = "Numbered"
                is_a_list = True
            else:
                is_a_list = False

            if paragraph.level > 0:
                # Most likely a sub-list
                is_a_list = True

            if is_a_list:
                # Determine if this is an unordered list or an ordered list.
                # Set GroupLabel.ORDERED_LIST when it fits.
                if bullet_type == "Numbered":
                    list_label = GroupLabel.ORDERED_LIST

            if is_a_list:
                _log.debug("LIST DETECTED!")
            else:
                _log.debug("No List")

        # If there is a list inside of the shape, create a new docling list to assign list items to
        # if is_a_list:
        #     new_list = doc.add_group(
        #         label=list_label, name=f"list", parent=parent_slide
        #     )

        # Iterate through paragraphs to build up text
        for paragraph in shape.text_frame.paragraphs:
            # p_text = paragraph.text.strip()
            p = paragraph._element
            enum_list_item_value += 1
            inline_paragraph_text = ""
            inline_list_item_text = ""

            for e in p.iterfind(".//a:r", namespaces={"a": self.namespaces["a"]}):
                if len(e.text.strip()) > 0:
                    e_is_a_list_item = False
                    is_numbered = False
                    if (
                        p.find(".//a:buChar", namespaces={"a": self.namespaces["a"]})
                        is not None
                    ):
                        bullet_type = "Bullet"
                        e_is_a_list_item = True
                    elif (
                        p.find(".//a:buAutoNum", namespaces={"a": self.namespaces["a"]})
                        is not None
                    ):
                        bullet_type = "Numbered"
                        is_numbered = True
                        e_is_a_list_item = True
                    else:
                        e_is_a_list_item = False

                    if e_is_a_list_item:
                        if len(inline_paragraph_text) > 0:
                            # output accumulated inline text:
                            doc.add_text(
                                label=doc_label,
                                parent=parent_slide,
                                text=inline_paragraph_text,
                                prov=prov,
                            )
                        # Set marker and enumerated arguments if this is an enumeration element.
                        inline_list_item_text += e.text
                        # print(e.text)
                    else:
                        # Assign proper label to the text, depending if it's a Title or Section Header
                        # For other types of text, assign - PARAGRAPH
                        doc_label = DocItemLabel.PARAGRAPH
                        if shape.is_placeholder:
                            placeholder_type = shape.placeholder_format.type
                            if placeholder_type in [
                                PP_PLACEHOLDER.CENTER_TITLE,
                                PP_PLACEHOLDER.TITLE,
                            ]:
                                # It's a title
                                doc_label = DocItemLabel.TITLE
                            elif placeholder_type == PP_PLACEHOLDER.SUBTITLE:
                                DocItemLabel.SECTION_HEADER
                        enum_list_item_value = 0
                        inline_paragraph_text += e.text

            if len(inline_paragraph_text) > 0:
                # output accumulated inline text:
                doc.add_text(
                    label=doc_label,
                    parent=parent_slide,
                    text=inline_paragraph_text,
                    prov=prov,
                )

            if len(inline_list_item_text) > 0:
                enum_marker = ""
                if is_numbered:
                    enum_marker = str(enum_list_item_value) + "."
                if not is_list_group_created:
                    new_list = doc.add_group(
                        label=list_label, name=f"list", parent=parent_slide
                    )
                    is_list_group_created = True
                doc.add_list_item(
                    marker=enum_marker,
                    enumerated=is_numbered,
                    parent=new_list,
                    text=inline_list_item_text,
                    prov=prov,
                )
        return

    def handle_title(self, shape, parent_slide, slide_ind, doc):
        placeholder_type = shape.placeholder_format.type
        txt = shape.text.strip()
        prov = self.generate_prov(shape, slide_ind, txt)

        if len(txt.strip()) > 0:
            # title = slide.shapes.title.text if slide.shapes.title else "No title"
            if placeholder_type in [PP_PLACEHOLDER.CENTER_TITLE, PP_PLACEHOLDER.TITLE]:
                _log.info(f"Title found: {shape.text}")
                doc.add_text(
                    label=DocItemLabel.TITLE, parent=parent_slide, text=txt, prov=prov
                )
            elif placeholder_type == PP_PLACEHOLDER.SUBTITLE:
                _log.info(f"Subtitle found: {shape.text}")
                # Using DocItemLabel.FOOTNOTE, while SUBTITLE label is not avail.
                doc.add_text(
                    label=DocItemLabel.SECTION_HEADER,
                    parent=parent_slide,
                    text=txt,
                    prov=prov,
                )
        return

    def handle_pictures(self, shape, parent_slide, slide_ind, doc, slide_size):
        # Open it with PIL
        try:
            # Get the image bytes
            image = shape.image
            image_bytes = image.blob
            im_dpi, _ = image.dpi
            pil_image = Image.open(BytesIO(image_bytes))

            # shape has picture
            prov = self.generate_prov(shape, slide_ind, "", slide_size)
            doc.add_picture(
                parent=parent_slide,
                image=ImageRef.from_pil(image=pil_image, dpi=im_dpi),
                caption=None,
                prov=prov,
            )
        except (UnidentifiedImageError, OSError) as e:
            _log.warning(f"Warning: image cannot be loaded by Pillow: {e}")
        return

    def handle_tables(self, shape, parent_slide, slide_ind, doc, slide_size):
        # Handling tables, images, charts
        if shape.has_table:
            table = shape.table
            table_xml = shape._element

            prov = self.generate_prov(shape, slide_ind, "", slide_size)

            num_cols = 0
            num_rows = len(table.rows)
            tcells = []
            # Access the XML element for the shape that contains the table
            table_xml = shape._element

            for row_idx, row in enumerate(table.rows):
                if len(row.cells) > num_cols:
                    num_cols = len(row.cells)
                for col_idx, cell in enumerate(row.cells):
                    # Access the XML of the cell (this is the 'tc' element in table XML)
                    cell_xml = table_xml.xpath(
                        f".//a:tbl/a:tr[{row_idx + 1}]/a:tc[{col_idx + 1}]"
                    )

                    if not cell_xml:
                        continue  # If no cell XML is found, skip

                    cell_xml = cell_xml[0]  # Get the first matching XML node
                    row_span = cell_xml.get("rowSpan")  # Vertical span
                    col_span = cell_xml.get("gridSpan")  # Horizontal span

                    if row_span is None:
                        row_span = 1
                    else:
                        row_span = int(row_span)

                    if col_span is None:
                        col_span = 1
                    else:
                        col_span = int(col_span)

                    icell = TableCell(
                        text=cell.text.strip(),
                        row_span=row_span,
                        col_span=col_span,
                        start_row_offset_idx=row_idx,
                        end_row_offset_idx=row_idx + row_span,
                        start_col_offset_idx=col_idx,
                        end_col_offset_idx=col_idx + col_span,
                        col_header=False,
                        row_header=False,
                    )
                    if len(cell.text.strip()) > 0:
                        tcells.append(icell)
            # Initialize Docling TableData
            data = TableData(num_rows=num_rows, num_cols=num_cols, table_cells=[])
            # Populate
            for tcell in tcells:
                data.table_cells.append(tcell)
            if len(tcells) > 0:
                # If table is not fully empty...
                # Create Docling table
                doc.add_table(parent=parent_slide, data=data, prov=prov)
        return

    def walk_linear(self, pptx_obj, doc) -> DoclingDocument:
        # Units of size in PPTX by default are EMU units (English Metric Units)
        slide_width = pptx_obj.slide_width
        slide_height = pptx_obj.slide_height

        text_content = []  # type: ignore

        max_levels = 10
        parents = {}  # type: ignore
        for i in range(0, max_levels):
            parents[i] = None

        # Loop through each slide
        for slide_num, slide in enumerate(pptx_obj.slides):
            slide_ind = pptx_obj.slides.index(slide)
            parent_slide = doc.add_group(
                name=f"slide-{slide_ind}", label=GroupLabel.CHAPTER, parent=parents[0]
            )

            slide_size = Size(width=slide_width, height=slide_height)
            parent_page = doc.add_page(page_no=slide_ind + 1, size=slide_size)

            def handle_shapes(shape, parent_slide, slide_ind, doc, slide_size):
                handle_groups(shape, parent_slide, slide_ind, doc, slide_size)
                if shape.has_table:
                    # Handle Tables
                    self.handle_tables(shape, parent_slide, slide_ind, doc, slide_size)
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    # Handle Pictures
                    self.handle_pictures(
                        shape, parent_slide, slide_ind, doc, slide_size
                    )
                # If shape doesn't have any text, move on to the next shape
                if not hasattr(shape, "text"):
                    return
                if shape.text is None:
                    return
                if len(shape.text.strip()) == 0:
                    return
                if not shape.has_text_frame:
                    _log.warning("Warning: shape has text but not text_frame")
                    return
                # Handle other text elements, including lists (bullet lists, numbered lists)
                self.handle_text_elements(
                    shape, parent_slide, slide_ind, doc, slide_size
                )
                return

            def handle_groups(shape, parent_slide, slide_ind, doc, slide_size):
                if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                    for groupedshape in shape.shapes:
                        handle_shapes(
                            groupedshape, parent_slide, slide_ind, doc, slide_size
                        )

            # Loop through each shape in the slide
            for shape in slide.shapes:
                handle_shapes(shape, parent_slide, slide_ind, doc, slide_size)

        return doc

```
</content>
</file_12>

<file_13>
<path>backend/msword_backend.py</path>
<content>
```python
import logging
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Optional, Union

from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    ImageRef,
    NodeItem,
    TableCell,
    TableData,
)
from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tc
from docx.oxml.xmlchemy import BaseOxmlElement
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from lxml import etree
from lxml.etree import XPath
from PIL import Image, UnidentifiedImageError
from typing_extensions import override

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class MsWordDocumentBackend(DeclarativeDocumentBackend):
    @override
    def __init__(
        self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]
    ) -> None:
        super().__init__(in_doc, path_or_stream)
        self.XML_KEY = (
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
        )
        self.xml_namespaces = {
            "w": "http://schemas.microsoft.com/office/word/2003/wordml"
        }
        # self.initialise(path_or_stream)
        # Word file:
        self.path_or_stream: Union[BytesIO, Path] = path_or_stream
        self.valid: bool = False
        # Initialise the parents for the hierarchy
        self.max_levels: int = 10
        self.level_at_new_list: Optional[int] = None
        self.parents: dict[int, Optional[NodeItem]] = {}
        for i in range(-1, self.max_levels):
            self.parents[i] = None

        self.level = 0
        self.listIter = 0

        self.history: dict[str, Any] = {
            "names": [None],
            "levels": [None],
            "numids": [None],
            "indents": [None],
        }

        self.docx_obj = None
        try:
            if isinstance(self.path_or_stream, BytesIO):
                self.docx_obj = Document(self.path_or_stream)
            elif isinstance(self.path_or_stream, Path):
                self.docx_obj = Document(str(self.path_or_stream))

            self.valid = True
        except Exception as e:
            raise RuntimeError(
                f"MsPowerpointDocumentBackend could not load document with hash {self.document_hash}"
            ) from e

    @override
    def is_valid(self) -> bool:
        return self.valid

    @classmethod
    @override
    def supports_pagination(cls) -> bool:
        return False

    @override
    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()

        self.path_or_stream = None

    @classmethod
    @override
    def supported_formats(cls) -> set[InputFormat]:
        return {InputFormat.DOCX}

    @override
    def convert(self) -> DoclingDocument:
        """Parses the DOCX into a structured document model.

        Returns:
            The parsed document.
        """

        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            binary_hash=self.document_hash,
        )

        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)
        if self.is_valid():
            assert self.docx_obj is not None
            doc = self.walk_linear(self.docx_obj.element.body, self.docx_obj, doc)
            return doc
        else:
            raise RuntimeError(
                f"Cannot convert doc with {self.document_hash} because the backend failed to init."
            )

    def update_history(
        self,
        name: str,
        level: Optional[int],
        numid: Optional[int],
        ilevel: Optional[int],
    ):
        self.history["names"].append(name)
        self.history["levels"].append(level)

        self.history["numids"].append(numid)
        self.history["indents"].append(ilevel)

    def prev_name(self) -> Optional[str]:
        return self.history["names"][-1]

    def prev_level(self) -> Optional[int]:
        return self.history["levels"][-1]

    def prev_numid(self) -> Optional[int]:
        return self.history["numids"][-1]

    def prev_indent(self) -> Optional[int]:
        return self.history["indents"][-1]

    def get_level(self) -> int:
        """Return the first None index."""
        for k, v in self.parents.items():
            if k >= 0 and v == None:
                return k
        return 0

    def walk_linear(
        self,
        body: BaseOxmlElement,
        docx_obj: DocxDocument,
        doc: DoclingDocument,
    ) -> DoclingDocument:
        for element in body:
            tag_name = etree.QName(element).localname
            # Check for Inline Images (blip elements)
            namespaces = {
                "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            }
            xpath_expr = XPath(".//a:blip", namespaces=namespaces)
            drawing_blip = xpath_expr(element)

            # Check for Tables
            if element.tag.endswith("tbl"):
                try:
                    self.handle_tables(element, docx_obj, doc)
                except Exception:
                    _log.debug("could not parse a table, broken docx table")

            elif drawing_blip:
                self.handle_pictures(docx_obj, drawing_blip, doc)
            # Check for the sdt containers, like table of contents
            elif tag_name in ["sdt"]:
                sdt_content = element.find(".//w:sdtContent", namespaces=namespaces)
                if sdt_content is not None:
                    # Iterate paragraphs, runs, or text inside <w:sdtContent>.
                    paragraphs = sdt_content.findall(".//w:p", namespaces=namespaces)
                    for p in paragraphs:
                        self.handle_text_elements(p, docx_obj, doc)
            # Check for Text
            elif tag_name in ["p"]:
                # "tcPr", "sectPr"
                self.handle_text_elements(element, docx_obj, doc)
            else:
                _log.debug(f"Ignoring element in DOCX with tag: {tag_name}")
        return doc

    def str_to_int(self, s: Optional[str], default: Optional[int] = 0) -> Optional[int]:
        if s is None:
            return None
        try:
            return int(s)
        except ValueError:
            return default

    def split_text_and_number(self, input_string: str) -> list[str]:
        match = re.match(r"(\D+)(\d+)$|^(\d+)(\D+)", input_string)
        if match:
            parts = list(filter(None, match.groups()))
            return parts
        else:
            return [input_string]

    def get_numId_and_ilvl(
        self, paragraph: Paragraph
    ) -> tuple[Optional[int], Optional[int]]:
        # Access the XML element of the paragraph
        numPr = paragraph._element.find(
            ".//w:numPr", namespaces=paragraph._element.nsmap
        )

        if numPr is not None:
            # Get the numId element and extract the value
            numId_elem = numPr.find("w:numId", namespaces=paragraph._element.nsmap)
            ilvl_elem = numPr.find("w:ilvl", namespaces=paragraph._element.nsmap)
            numId = numId_elem.get(self.XML_KEY) if numId_elem is not None else None
            ilvl = ilvl_elem.get(self.XML_KEY) if ilvl_elem is not None else None

            return self.str_to_int(numId, None), self.str_to_int(ilvl, None)

        return None, None  # If the paragraph is not part of a list

    def get_label_and_level(self, paragraph: Paragraph) -> tuple[str, Optional[int]]:
        if paragraph.style is None:
            return "Normal", None
        label = paragraph.style.style_id
        if label is None:
            return "Normal", None
        if ":" in label:
            parts = label.split(":")

            if len(parts) == 2:
                return parts[0], int(parts[1])

        parts = self.split_text_and_number(label)

        if "Heading" in label and len(parts) == 2:
            parts.sort()
            label_str: str = ""
            label_level: Optional[int] = 0
            if parts[0] == "Heading":
                label_str = parts[0]
                label_level = self.str_to_int(parts[1], None)
            if parts[1] == "Heading":
                label_str = parts[1]
                label_level = self.str_to_int(parts[0], None)
            return label_str, label_level
        else:
            return label, None

    def handle_text_elements(
        self,
        element: BaseOxmlElement,
        docx_obj: DocxDocument,
        doc: DoclingDocument,
    ) -> None:
        paragraph = Paragraph(element, docx_obj)

        if paragraph.text is None:
            return
        text = paragraph.text.strip()

        # Common styles for bullet and numbered lists.
        # "List Bullet", "List Number", "List Paragraph"
        # Identify wether list is a numbered list or not
        # is_numbered = "List Bullet" not in paragraph.style.name
        is_numbered = False
        p_style_id, p_level = self.get_label_and_level(paragraph)
        numid, ilevel = self.get_numId_and_ilvl(paragraph)

        if numid == 0:
            numid = None

        # Handle lists
        if (
            numid is not None
            and ilevel is not None
            and p_style_id not in ["Title", "Heading"]
        ):
            self.add_listitem(
                doc,
                numid,
                ilevel,
                text,
                is_numbered,
            )
            self.update_history(p_style_id, p_level, numid, ilevel)
            return
        elif (
            numid is None
            and self.prev_numid() is not None
            and p_style_id not in ["Title", "Heading"]
        ):  # Close list
            if self.level_at_new_list:
                for key in range(len(self.parents)):
                    if key >= self.level_at_new_list:
                        self.parents[key] = None
                self.level = self.level_at_new_list - 1
                self.level_at_new_list = None
            else:
                for key in range(len(self.parents)):
                    self.parents[key] = None
                self.level = 0

        if p_style_id in ["Title"]:
            for key in range(len(self.parents)):
                self.parents[key] = None
            self.parents[0] = doc.add_text(
                parent=None, label=DocItemLabel.TITLE, text=text
            )
        elif "Heading" in p_style_id:
            self.add_header(doc, p_level, text)

        elif p_style_id in [
            "Paragraph",
            "Normal",
            "Subtitle",
            "Author",
            "DefaultText",
            "ListParagraph",
            "ListBullet",
            "Quote",
        ]:
            level = self.get_level()
            doc.add_text(
                label=DocItemLabel.PARAGRAPH, parent=self.parents[level - 1], text=text
            )

        else:
            # Text style names can, and will have, not only default values but user values too
            # hence we treat all other labels as pure text
            level = self.get_level()
            doc.add_text(
                label=DocItemLabel.PARAGRAPH, parent=self.parents[level - 1], text=text
            )

        self.update_history(p_style_id, p_level, numid, ilevel)
        return

    def add_header(
        self, doc: DoclingDocument, curr_level: Optional[int], text: str
    ) -> None:
        level = self.get_level()
        if isinstance(curr_level, int):
            if curr_level > level:
                # add invisible group
                for i in range(level, curr_level):
                    self.parents[i] = doc.add_group(
                        parent=self.parents[i - 1],
                        label=GroupLabel.SECTION,
                        name=f"header-{i}",
                    )
            elif curr_level < level:
                # remove the tail
                for key in range(len(self.parents)):
                    if key >= curr_level:
                        self.parents[key] = None

            self.parents[curr_level] = doc.add_heading(
                parent=self.parents[curr_level - 1],
                text=text,
                level=curr_level,
            )
        else:
            self.parents[self.level] = doc.add_heading(
                parent=self.parents[self.level - 1],
                text=text,
                level=1,
            )
        return

    def add_listitem(
        self,
        doc: DoclingDocument,
        numid: int,
        ilevel: int,
        text: str,
        is_numbered: bool = False,
    ) -> None:
        enum_marker = ""

        level = self.get_level()
        prev_indent = self.prev_indent()
        if self.prev_numid() is None:  # Open new list
            self.level_at_new_list = level

            self.parents[level] = doc.add_group(
                label=GroupLabel.LIST, name="list", parent=self.parents[level - 1]
            )

            # Set marker and enumerated arguments if this is an enumeration element.
            self.listIter += 1
            if is_numbered:
                enum_marker = str(self.listIter) + "."
                is_numbered = True
            doc.add_list_item(
                marker=enum_marker,
                enumerated=is_numbered,
                parent=self.parents[level],
                text=text,
            )

        elif (
            self.prev_numid() == numid
            and self.level_at_new_list is not None
            and prev_indent is not None
            and prev_indent < ilevel
        ):  # Open indented list
            for i in range(
                self.level_at_new_list + prev_indent + 1,
                self.level_at_new_list + ilevel + 1,
            ):
                # Determine if this is an unordered list or an ordered list.
                # Set GroupLabel.ORDERED_LIST when it fits.
                self.listIter = 0
                if is_numbered:
                    self.parents[i] = doc.add_group(
                        label=GroupLabel.ORDERED_LIST,
                        name="list",
                        parent=self.parents[i - 1],
                    )
                else:
                    self.parents[i] = doc.add_group(
                        label=GroupLabel.LIST, name="list", parent=self.parents[i - 1]
                    )

            # TODO: Set marker and enumerated arguments if this is an enumeration element.
            self.listIter += 1
            if is_numbered:
                enum_marker = str(self.listIter) + "."
                is_numbered = True
            doc.add_list_item(
                marker=enum_marker,
                enumerated=is_numbered,
                parent=self.parents[self.level_at_new_list + ilevel],
                text=text,
            )

        elif (
            self.prev_numid() == numid
            and self.level_at_new_list is not None
            and prev_indent is not None
            and ilevel < prev_indent
        ):  # Close list
            for k, v in self.parents.items():
                if k > self.level_at_new_list + ilevel:
                    self.parents[k] = None

            # TODO: Set marker and enumerated arguments if this is an enumeration element.
            self.listIter += 1
            if is_numbered:
                enum_marker = str(self.listIter) + "."
                is_numbered = True
            doc.add_list_item(
                marker=enum_marker,
                enumerated=is_numbered,
                parent=self.parents[self.level_at_new_list + ilevel],
                text=text,
            )
            self.listIter = 0

        elif self.prev_numid() == numid or prev_indent == ilevel:
            # TODO: Set marker and enumerated arguments if this is an enumeration element.
            self.listIter += 1
            if is_numbered:
                enum_marker = str(self.listIter) + "."
                is_numbered = True
            doc.add_list_item(
                marker=enum_marker,
                enumerated=is_numbered,
                parent=self.parents[level - 1],
                text=text,
            )
        return

    def handle_tables(
        self,
        element: BaseOxmlElement,
        docx_obj: DocxDocument,
        doc: DoclingDocument,
    ) -> None:
        table: Table = Table(element, docx_obj)
        num_rows = len(table.rows)
        num_cols = len(table.columns)
        _log.debug(f"Table grid with {num_rows} rows and {num_cols} columns")

        if num_rows == 1 and num_cols == 1:
            cell_element = table.rows[0].cells[0]
            # In case we have a table of only 1 cell, we consider it furniture
            # And proceed processing the content of the cell as though it's in the document body
            self.walk_linear(cell_element._element, docx_obj, doc)
            return

        data = TableData(num_rows=num_rows, num_cols=num_cols)
        cell_set: set[CT_Tc] = set()
        for row_idx, row in enumerate(table.rows):
            _log.debug(f"Row index {row_idx} with {len(row.cells)} populated cells")
            col_idx = 0
            while col_idx < num_cols:
                cell: _Cell = row.cells[col_idx]
                _log.debug(
                    f" col {col_idx} grid_span {cell.grid_span} grid_cols_before {row.grid_cols_before}"
                )
                if cell is None or cell._tc in cell_set:
                    _log.debug(f"  skipped since repeated content")
                    col_idx += cell.grid_span
                    continue
                else:
                    cell_set.add(cell._tc)

                spanned_idx = row_idx
                spanned_tc: Optional[CT_Tc] = cell._tc
                while spanned_tc == cell._tc:
                    spanned_idx += 1
                    spanned_tc = (
                        table.rows[spanned_idx].cells[col_idx]._tc
                        if spanned_idx < num_rows
                        else None
                    )
                _log.debug(f"  spanned before row {spanned_idx}")

                table_cell = TableCell(
                    text=cell.text,
                    row_span=spanned_idx - row_idx,
                    col_span=cell.grid_span,
                    start_row_offset_idx=row.grid_cols_before + row_idx,
                    end_row_offset_idx=row.grid_cols_before + spanned_idx,
                    start_col_offset_idx=col_idx,
                    end_col_offset_idx=col_idx + cell.grid_span,
                    col_header=False,
                    row_header=False,
                )
                data.table_cells.append(table_cell)
                col_idx += cell.grid_span

        level = self.get_level()
        doc.add_table(data=data, parent=self.parents[level - 1])
        return

    def handle_pictures(
        self, docx_obj: DocxDocument, drawing_blip: Any, doc: DoclingDocument
    ) -> None:
        def get_docx_image(drawing_blip):
            rId = drawing_blip[0].get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
            )
            if rId in docx_obj.part.rels:
                # Access the image part using the relationship ID
                image_part = docx_obj.part.rels[rId].target_part
                image_data = image_part.blob  # Get the binary image data
            return image_data

        level = self.get_level()
        # Open the BytesIO object with PIL to create an Image
        try:
            image_data = get_docx_image(drawing_blip)
            image_bytes = BytesIO(image_data)
            pil_image = Image.open(image_bytes)
            doc.add_picture(
                parent=self.parents[level - 1],
                image=ImageRef.from_pil(image=pil_image, dpi=72),
                caption=None,
            )
        except (UnidentifiedImageError, OSError) as e:
            _log.warning("Warning: image cannot be loaded by Pillow")
            doc.add_picture(
                parent=self.parents[level - 1],
                caption=None,
            )
        return

```
</content>
</file_13>

<file_14>
<path>backend/pdf_backend.py</path>
<content>
```python
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Iterable, Optional, Set, Union

from docling_core.types.doc import BoundingBox, Size
from PIL import Image

from docling.backend.abstract_backend import PaginatedDocumentBackend
from docling.datamodel.base_models import Cell, InputFormat
from docling.datamodel.document import InputDocument


class PdfPageBackend(ABC):
    @abstractmethod
    def get_text_in_rect(self, bbox: BoundingBox) -> str:
        pass

    @abstractmethod
    def get_text_cells(self) -> Iterable[Cell]:
        pass

    @abstractmethod
    def get_bitmap_rects(self, float: int = 1) -> Iterable[BoundingBox]:
        pass

    @abstractmethod
    def get_page_image(
        self, scale: float = 1, cropbox: Optional[BoundingBox] = None
    ) -> Image.Image:
        pass

    @abstractmethod
    def get_size(self) -> Size:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def unload(self):
        pass


class PdfDocumentBackend(PaginatedDocumentBackend):
    def __init__(self, in_doc: InputDocument, path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        if self.input_format is not InputFormat.PDF:
            if self.input_format is InputFormat.IMAGE:
                buf = BytesIO()
                img = Image.open(self.path_or_stream)
                img.save(buf, "PDF")
                buf.seek(0)
                self.path_or_stream = buf
            else:
                raise RuntimeError(
                    f"Incompatible file format {self.input_format} was passed to a PdfDocumentBackend."
                )

    @abstractmethod
    def load_page(self, page_no: int) -> PdfPageBackend:
        pass

    @abstractmethod
    def page_count(self) -> int:
        pass

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.PDF}

    @classmethod
    def supports_pagination(cls) -> bool:
        return True

```
</content>
</file_14>

<file_15>
<path>backend/pypdfium2_backend.py</path>
<content>
```python
import logging
import random
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, Union

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from docling_core.types.doc import BoundingBox, CoordOrigin, Size
from PIL import Image, ImageDraw
from pypdfium2 import PdfTextPage
from pypdfium2._helpers.misc import PdfiumError

from docling.backend.pdf_backend import PdfDocumentBackend, PdfPageBackend
from docling.datamodel.base_models import Cell

if TYPE_CHECKING:
    from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class PyPdfiumPageBackend(PdfPageBackend):
    def __init__(
        self, pdfium_doc: pdfium.PdfDocument, document_hash: str, page_no: int
    ):
        self.valid = True  # No better way to tell from pypdfium.
        try:
            self._ppage: pdfium.PdfPage = pdfium_doc[page_no]
        except PdfiumError as e:
            _log.info(
                f"An exception occurred when loading page {page_no} of document {document_hash}.",
                exc_info=True,
            )
            self.valid = False
        self.text_page: Optional[PdfTextPage] = None

    def is_valid(self) -> bool:
        return self.valid

    def get_bitmap_rects(self, scale: float = 1) -> Iterable[BoundingBox]:
        AREA_THRESHOLD = 0  # 32 * 32
        for obj in self._ppage.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]):
            pos = obj.get_pos()
            cropbox = BoundingBox.from_tuple(
                pos, origin=CoordOrigin.BOTTOMLEFT
            ).to_top_left_origin(page_height=self.get_size().height)

            if cropbox.area() > AREA_THRESHOLD:
                cropbox = cropbox.scaled(scale=scale)

                yield cropbox

    def get_text_in_rect(self, bbox: BoundingBox) -> str:
        if not self.text_page:
            self.text_page = self._ppage.get_textpage()

        if bbox.coord_origin != CoordOrigin.BOTTOMLEFT:
            bbox = bbox.to_bottom_left_origin(self.get_size().height)

        text_piece = self.text_page.get_text_bounded(*bbox.as_tuple())

        return text_piece

    def get_text_cells(self) -> Iterable[Cell]:
        if not self.text_page:
            self.text_page = self._ppage.get_textpage()

        cells = []
        cell_counter = 0

        page_size = self.get_size()

        for i in range(self.text_page.count_rects()):
            rect = self.text_page.get_rect(i)
            text_piece = self.text_page.get_text_bounded(*rect)
            x0, y0, x1, y1 = rect
            cells.append(
                Cell(
                    id=cell_counter,
                    text=text_piece,
                    bbox=BoundingBox(
                        l=x0, b=y0, r=x1, t=y1, coord_origin=CoordOrigin.BOTTOMLEFT
                    ).to_top_left_origin(page_size.height),
                )
            )
            cell_counter += 1

        # PyPdfium2 produces very fragmented cells, with sub-word level boundaries, in many PDFs.
        # The cell merging code below is to clean this up.
        def merge_horizontal_cells(
            cells: List[Cell],
            horizontal_threshold_factor: float = 1.0,
            vertical_threshold_factor: float = 0.5,
        ) -> List[Cell]:
            if not cells:
                return []

            def group_rows(cells: List[Cell]) -> List[List[Cell]]:
                rows = []
                current_row = [cells[0]]
                row_top = cells[0].bbox.t
                row_bottom = cells[0].bbox.b
                row_height = cells[0].bbox.height

                for cell in cells[1:]:
                    vertical_threshold = row_height * vertical_threshold_factor
                    if (
                        abs(cell.bbox.t - row_top) <= vertical_threshold
                        and abs(cell.bbox.b - row_bottom) <= vertical_threshold
                    ):
                        current_row.append(cell)
                        row_top = min(row_top, cell.bbox.t)
                        row_bottom = max(row_bottom, cell.bbox.b)
                        row_height = row_bottom - row_top
                    else:
                        rows.append(current_row)
                        current_row = [cell]
                        row_top = cell.bbox.t
                        row_bottom = cell.bbox.b
                        row_height = cell.bbox.height

                if current_row:
                    rows.append(current_row)

                return rows

            def merge_row(row: List[Cell]) -> List[Cell]:
                merged = []
                current_group = [row[0]]

                for cell in row[1:]:
                    prev_cell = current_group[-1]
                    avg_height = (prev_cell.bbox.height + cell.bbox.height) / 2
                    if (
                        cell.bbox.l - prev_cell.bbox.r
                        <= avg_height * horizontal_threshold_factor
                    ):
                        current_group.append(cell)
                    else:
                        merged.append(merge_group(current_group))
                        current_group = [cell]

                if current_group:
                    merged.append(merge_group(current_group))

                return merged

            def merge_group(group: List[Cell]) -> Cell:
                if len(group) == 1:
                    return group[0]

                merged_text = "".join(cell.text for cell in group)
                merged_bbox = BoundingBox(
                    l=min(cell.bbox.l for cell in group),
                    t=min(cell.bbox.t for cell in group),
                    r=max(cell.bbox.r for cell in group),
                    b=max(cell.bbox.b for cell in group),
                )
                return Cell(id=group[0].id, text=merged_text, bbox=merged_bbox)

            rows = group_rows(cells)
            merged_cells = [cell for row in rows for cell in merge_row(row)]

            for i, cell in enumerate(merged_cells, 1):
                cell.id = i

            return merged_cells

        def draw_clusters_and_cells():
            image = (
                self.get_page_image()
            )  # make new image to avoid drawing on the saved ones
            draw = ImageDraw.Draw(image)
            for c in cells:
                x0, y0, x1, y1 = c.bbox.as_tuple()
                cell_color = (
                    random.randint(30, 140),
                    random.randint(30, 140),
                    random.randint(30, 140),
                )
                draw.rectangle([(x0, y0), (x1, y1)], outline=cell_color)
            image.show()

        # before merge:
        # draw_clusters_and_cells()

        cells = merge_horizontal_cells(cells)

        # after merge:
        # draw_clusters_and_cells()

        return cells

    def get_page_image(
        self, scale: float = 1, cropbox: Optional[BoundingBox] = None
    ) -> Image.Image:

        page_size = self.get_size()

        if not cropbox:
            cropbox = BoundingBox(
                l=0,
                r=page_size.width,
                t=0,
                b=page_size.height,
                coord_origin=CoordOrigin.TOPLEFT,
            )
            padbox = BoundingBox(
                l=0, r=0, t=0, b=0, coord_origin=CoordOrigin.BOTTOMLEFT
            )
        else:
            padbox = cropbox.to_bottom_left_origin(page_size.height).model_copy()
            padbox.r = page_size.width - padbox.r
            padbox.t = page_size.height - padbox.t

        image = (
            self._ppage.render(
                scale=scale * 1.5,
                rotation=0,  # no additional rotation
                crop=padbox.as_tuple(),
            )
            .to_pil()
            .resize(size=(round(cropbox.width * scale), round(cropbox.height * scale)))
        )  # We resize the image from 1.5x the given scale to make it sharper.

        return image

    def get_size(self) -> Size:
        return Size(width=self._ppage.get_width(), height=self._ppage.get_height())

    def unload(self):
        self._ppage = None
        self.text_page = None


class PyPdfiumDocumentBackend(PdfDocumentBackend):
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)

        try:
            self._pdoc = pdfium.PdfDocument(self.path_or_stream)
        except PdfiumError as e:
            raise RuntimeError(
                f"pypdfium could not load document with hash {self.document_hash}"
            ) from e

    def page_count(self) -> int:
        return len(self._pdoc)

    def load_page(self, page_no: int) -> PyPdfiumPageBackend:
        return PyPdfiumPageBackend(self._pdoc, self.document_hash, page_no)

    def is_valid(self) -> bool:
        return self.page_count() > 0

    def unload(self):
        super().unload()
        self._pdoc.close()
        self._pdoc = None

```
</content>
</file_15>

<file_16>
<path>backend/xml/__init__.py</path>
<content>
```python

```
</content>
</file_16>

<file_17>
<path>backend/xml/pubmed_backend.py</path>
<content>
```python
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Set, Union

import lxml
from bs4 import BeautifulSoup
from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    TableCell,
    TableData,
)
from lxml import etree
from typing_extensions import TypedDict, override

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)


class Paragraph(TypedDict):
    text: str
    headers: list[str]


class Author(TypedDict):
    name: str
    affiliation_names: list[str]


class Table(TypedDict):
    label: str
    caption: str
    content: str


class FigureCaption(TypedDict):
    label: str
    caption: str


class Reference(TypedDict):
    author_names: str
    title: str
    journal: str
    year: str


class XMLComponents(TypedDict):
    title: str
    authors: list[Author]
    abstract: str
    paragraphs: list[Paragraph]
    tables: list[Table]
    figure_captions: list[FigureCaption]
    references: list[Reference]


class PubMedDocumentBackend(DeclarativeDocumentBackend):
    """
    The code from this document backend has been developed by modifying parts of the PubMed Parser library (version 0.5.0, released on 12.08.2024):
    Achakulvisut et al., (2020).
    Pubmed Parser: A Python Parser for PubMed Open-Access XML Subset and MEDLINE XML Dataset XML Dataset.
    Journal of Open Source Software, 5(46), 1979,
    https://doi.org/10.21105/joss.01979
    """

    @override
    def __init__(self, in_doc: "InputDocument", path_or_stream: Union[BytesIO, Path]):
        super().__init__(in_doc, path_or_stream)
        self.path_or_stream = path_or_stream

        # Initialize parents for the document hierarchy
        self.parents: dict = {}

        self.valid = False
        try:
            if isinstance(self.path_or_stream, BytesIO):
                self.path_or_stream.seek(0)
            self.tree: lxml.etree._ElementTree = etree.parse(self.path_or_stream)
            if "/NLM//DTD JATS" in self.tree.docinfo.public_id:
                self.valid = True
        except Exception as exc:
            raise RuntimeError(
                f"Could not initialize PubMed backend for file with hash {self.document_hash}."
            ) from exc

    @override
    def is_valid(self) -> bool:
        return self.valid

    @classmethod
    @override
    def supports_pagination(cls) -> bool:
        return False

    @override
    def unload(self):
        if isinstance(self.path_or_stream, BytesIO):
            self.path_or_stream.close()
        self.path_or_stream = None

    @classmethod
    @override
    def supported_formats(cls) -> Set[InputFormat]:
        return {InputFormat.XML_PUBMED}

    @override
    def convert(self) -> DoclingDocument:
        # Create empty document
        origin = DocumentOrigin(
            filename=self.file.name or "file",
            mimetype="application/xml",
            binary_hash=self.document_hash,
        )
        doc = DoclingDocument(name=self.file.stem or "file", origin=origin)

        _log.debug("Trying to convert PubMed XML document...")

        # Get parsed XML components
        xml_components: XMLComponents = self._parse()

        # Add XML components to the document
        doc = self._populate_document(doc, xml_components)
        return doc

    def _parse_title(self) -> str:
        title: str = " ".join(
            [
                t.replace("\n", "")
                for t in self.tree.xpath(".//title-group/article-title")[0].itertext()
            ]
        )
        return title

    def _parse_authors(self) -> list[Author]:
        # Get mapping between affiliation ids and names
        affiliation_names = []
        for affiliation_node in self.tree.xpath(".//aff[@id]"):
            affiliation_names.append(
                ": ".join([t for t in affiliation_node.itertext() if t != "\n"])
            )
        affiliation_ids_names = {
            id: name
            for id, name in zip(self.tree.xpath(".//aff[@id]/@id"), affiliation_names)
        }

        # Get author names and affiliation names
        authors: list[Author] = []
        for author_node in self.tree.xpath(
            './/contrib-group/contrib[@contrib-type="author"]'
        ):
            author: Author = {
                "name": "",
                "affiliation_names": [],
            }

            # Affiliation names
            affiliation_ids = [
                a.attrib["rid"] for a in author_node.xpath('xref[@ref-type="aff"]')
            ]
            for id in affiliation_ids:
                if id in affiliation_ids_names:
                    author["affiliation_names"].append(affiliation_ids_names[id])

            # Name
            author["name"] = (
                author_node.xpath("name/surname")[0].text
                + " "
                + author_node.xpath("name/given-names")[0].text
            )

            authors.append(author)
        return authors

    def _parse_abstract(self) -> str:
        texts = []
        for abstract_node in self.tree.xpath(".//abstract"):
            for text in abstract_node.itertext():
                texts.append(text.replace("\n", ""))
        abstract: str = "".join(texts)
        return abstract

    def _parse_main_text(self) -> list[Paragraph]:
        paragraphs: list[Paragraph] = []
        for paragraph_node in self.tree.xpath("//body//p"):
            # Skip captions
            if "/caption" in paragraph_node.getroottree().getpath(paragraph_node):
                continue

            paragraph: Paragraph = {"text": "", "headers": []}

            # Text
            paragraph["text"] = "".join(
                [t.replace("\n", "") for t in paragraph_node.itertext()]
            )

            # Header
            path = "../title"
            while len(paragraph_node.xpath(path)) > 0:
                paragraph["headers"].append(
                    "".join(
                        [
                            t.replace("\n", "")
                            for t in paragraph_node.xpath(path)[0].itertext()
                        ]
                    )
                )
                path = "../" + path

            paragraphs.append(paragraph)

        return paragraphs

    def _parse_tables(self) -> list[Table]:
        tables: list[Table] = []
        for table_node in self.tree.xpath(".//body//table-wrap"):
            table: Table = {"label": "", "caption": "", "content": ""}

            # Content
            if len(table_node.xpath("table")) > 0:
                table_content_node = table_node.xpath("table")[0]
            elif len(table_node.xpath("alternatives/table")) > 0:
                table_content_node = table_node.xpath("alternatives/table")[0]
            else:
                table_content_node = None
            if table_content_node != None:
                table["content"] = etree.tostring(table_content_node).decode("utf-8")

            # Caption
            if len(table_node.xpath("caption/p")) > 0:
                caption_node = table_node.xpath("caption/p")[0]
            elif len(table_node.xpath("caption/title")) > 0:
                caption_node = table_node.xpath("caption/title")[0]
            else:
                caption_node = None
            if caption_node != None:
                table["caption"] = "".join(
                    [t.replace("\n", "") for t in caption_node.itertext()]
                )

            # Label
            if len(table_node.xpath("label")) > 0:
                table["label"] = table_node.xpath("label")[0].text

            tables.append(table)
        return tables

    def _parse_figure_captions(self) -> list[FigureCaption]:
        figure_captions: list[FigureCaption] = []

        if not (self.tree.xpath(".//fig")):
            return figure_captions

        for figure_node in self.tree.xpath(".//fig"):
            figure_caption: FigureCaption = {
                "caption": "",
                "label": "",
            }

            # Label
            if figure_node.xpath("label"):
                figure_caption["label"] = "".join(
                    [
                        t.replace("\n", "")
                        for t in figure_node.xpath("label")[0].itertext()
                    ]
                )

            # Caption
            if figure_node.xpath("caption"):
                caption = ""
                for caption_node in figure_node.xpath("caption")[0].getchildren():
                    caption += (
                        "".join([t.replace("\n", "") for t in caption_node.itertext()])
                        + "\n"
                    )
                figure_caption["caption"] = caption

            figure_captions.append(figure_caption)

        return figure_captions

    def _parse_references(self) -> list[Reference]:
        references: list[Reference] = []
        for reference_node_abs in self.tree.xpath(".//ref-list/ref"):
            reference: Reference = {
                "author_names": "",
                "title": "",
                "journal": "",
                "year": "",
            }
            reference_node: Any = None
            for tag in ["mixed-citation", "element-citation", "citation"]:
                if len(reference_node_abs.xpath(tag)) > 0:
                    reference_node = reference_node_abs.xpath(tag)[0]
                    break

            if reference_node is None:
                continue

            if all(
                not (ref_type in ["citation-type", "publication-type"])
                for ref_type in reference_node.attrib.keys()
            ):
                continue

            # Author names
            names = []
            if len(reference_node.xpath("name")) > 0:
                for name_node in reference_node.xpath("name"):
                    name_str = " ".join(
                        [t.text for t in name_node.getchildren() if (t.text != None)]
                    )
                    names.append(name_str)
            elif len(reference_node.xpath("person-group")) > 0:
                for name_node in reference_node.xpath("person-group")[0]:
                    name_str = (
                        name_node.xpath("given-names")[0].text
                        + " "
                        + name_node.xpath("surname")[0].text
                    )
                    names.append(name_str)
            reference["author_names"] = "; ".join(names)

            # Title
            if len(reference_node.xpath("article-title")) > 0:
                reference["title"] = " ".join(
                    [
                        t.replace("\n", " ")
                        for t in reference_node.xpath("article-title")[0].itertext()
                    ]
                )

            # Journal
            if len(reference_node.xpath("source")) > 0:
                reference["journal"] = reference_node.xpath("source")[0].text

            # Year
            if len(reference_node.xpath("year")) > 0:
                reference["year"] = reference_node.xpath("year")[0].text

            if (
                not (reference_node.xpath("article-title"))
                and not (reference_node.xpath("journal"))
                and not (reference_node.xpath("year"))
            ):
                reference["title"] = reference_node.text

            references.append(reference)
        return references

    def _parse(self) -> XMLComponents:
        """Parsing PubMed document."""
        xml_components: XMLComponents = {
            "title": self._parse_title(),
            "authors": self._parse_authors(),
            "abstract": self._parse_abstract(),
            "paragraphs": self._parse_main_text(),
            "tables": self._parse_tables(),
            "figure_captions": self._parse_figure_captions(),
            "references": self._parse_references(),
        }
        return xml_components

    def _populate_document(
        self, doc: DoclingDocument, xml_components: XMLComponents
    ) -> DoclingDocument:
        self._add_title(doc, xml_components)
        self._add_authors(doc, xml_components)
        self._add_abstract(doc, xml_components)
        self._add_main_text(doc, xml_components)

        if xml_components["tables"]:
            self._add_tables(doc, xml_components)

        if xml_components["figure_captions"]:
            self._add_figure_captions(doc, xml_components)

        self._add_references(doc, xml_components)
        return doc

    def _add_figure_captions(
        self, doc: DoclingDocument, xml_components: XMLComponents
    ) -> None:
        self.parents["Figures"] = doc.add_heading(
            parent=self.parents["Title"], text="Figures"
        )
        for figure_caption_xml_component in xml_components["figure_captions"]:
            figure_caption_text = (
                figure_caption_xml_component["label"]
                + ": "
                + figure_caption_xml_component["caption"].strip()
            )
            fig_caption = doc.add_text(
                label=DocItemLabel.CAPTION, text=figure_caption_text
            )
            doc.add_picture(
                parent=self.parents["Figures"],
                caption=fig_caption,
            )
        return

    def _add_title(self, doc: DoclingDocument, xml_components: XMLComponents) -> None:
        self.parents["Title"] = doc.add_text(
            parent=None,
            text=xml_components["title"],
            label=DocItemLabel.TITLE,
        )
        return

    def _add_authors(self, doc: DoclingDocument, xml_components: XMLComponents) -> None:
        authors_affiliations: list = []
        for author in xml_components["authors"]:
            authors_affiliations.append(author["name"])
            authors_affiliations.append(", ".join(author["affiliation_names"]))
        authors_affiliations_str = "; ".join(authors_affiliations)

        doc.add_text(
            parent=self.parents["Title"],
            text=authors_affiliations_str,
            label=DocItemLabel.PARAGRAPH,
        )
        return

    def _add_abstract(
        self, doc: DoclingDocument, xml_components: XMLComponents
    ) -> None:
        abstract_text: str = xml_components["abstract"]
        self.parents["Abstract"] = doc.add_heading(
            parent=self.parents["Title"], text="Abstract"
        )
        doc.add_text(
            parent=self.parents["Abstract"],
            text=abstract_text,
            label=DocItemLabel.TEXT,
        )
        return

    def _add_main_text(
        self, doc: DoclingDocument, xml_components: XMLComponents
    ) -> None:
        added_headers: list = []
        for paragraph in xml_components["paragraphs"]:
            if not (paragraph["headers"]):
                continue

            # Header
            for i, header in enumerate(reversed(paragraph["headers"])):
                if header in added_headers:
                    continue
                added_headers.append(header)

                if ((i - 1) >= 0) and list(reversed(paragraph["headers"]))[
                    i - 1
                ] in self.parents:
                    parent = self.parents[list(reversed(paragraph["headers"]))[i - 1]]
                else:
                    parent = self.parents["Title"]

                self.parents[header] = doc.add_heading(parent=parent, text=header)

            # Paragraph text
            if paragraph["headers"][0] in self.parents:
                parent = self.parents[paragraph["headers"][0]]
            else:
                parent = self.parents["Title"]

            doc.add_text(parent=parent, label=DocItemLabel.TEXT, text=paragraph["text"])
        return

    def _add_references(
        self, doc: DoclingDocument, xml_components: XMLComponents
    ) -> None:
        self.parents["References"] = doc.add_heading(
            parent=self.parents["Title"], text="References"
        )
        current_list = doc.add_group(
            parent=self.parents["References"], label=GroupLabel.LIST, name="list"
        )
        for reference in xml_components["references"]:
            reference_text: str = ""
            if reference["author_names"]:
                reference_text += reference["author_names"] + ". "

            if reference["title"]:
                reference_text += reference["title"]
                if reference["title"][-1] != ".":
                    reference_text += "."
                reference_text += " "

            if reference["journal"]:
                reference_text += reference["journal"]

            if reference["year"]:
                reference_text += " (" + reference["year"] + ")"

            if not (reference_text):
                _log.debug(f"Skipping reference for: {str(self.file)}")
                continue

            doc.add_list_item(
                text=reference_text, enumerated=False, parent=current_list
            )
        return

    def _add_tables(self, doc: DoclingDocument, xml_components: XMLComponents) -> None:
        self.parents["Tables"] = doc.add_heading(
            parent=self.parents["Title"], text="Tables"
        )
        for table_xml_component in xml_components["tables"]:
            try:
                self._add_table(doc, table_xml_component)
            except Exception as e:
                _log.debug(f"Skipping unsupported table for: {str(self.file)}")
                pass
        return

    def _add_table(self, doc: DoclingDocument, table_xml_component: Table) -> None:
        soup = BeautifulSoup(table_xml_component["content"], "html.parser")
        table_tag = soup.find("table")

        nested_tables = table_tag.find("table")
        if nested_tables:
            _log.debug(f"Skipping nested table for: {str(self.file)}")
            return

        # Count the number of rows (number of <tr> elements)
        num_rows = len(table_tag.find_all("tr"))

        # Find the number of columns (taking into account colspan)
        num_cols = 0
        for row in table_tag.find_all("tr"):
            col_count = 0
            for cell in row.find_all(["td", "th"]):
                colspan = int(cell.get("colspan", 1))
                col_count += colspan
            num_cols = max(num_cols, col_count)

        grid = [[None for _ in range(num_cols)] for _ in range(num_rows)]

        data = TableData(num_rows=num_rows, num_cols=num_cols, table_cells=[])

        # Iterate over the rows in the table
        for row_idx, row in enumerate(table_tag.find_all("tr")):
            # For each row, find all the column cells (both <td> and <th>)
            cells = row.find_all(["td", "th"])

            # Check if each cell in the row is a header -> means it is a column header
            col_header = True
            for j, html_cell in enumerate(cells):
                if html_cell.name == "td":
                    col_header = False

            # Extract and print the text content of each cell
            col_idx = 0
            for _, html_cell in enumerate(cells):
                text = html_cell.text

                col_span = int(html_cell.get("colspan", 1))
                row_span = int(html_cell.get("rowspan", 1))

                while grid[row_idx][col_idx] != None:
                    col_idx += 1
                for r in range(row_span):
                    for c in range(col_span):
                        grid[row_idx + r][col_idx + c] = text

                cell = TableCell(
                    text=text,
                    row_span=row_span,
                    col_span=col_span,
                    start_row_offset_idx=row_idx,
                    end_row_offset_idx=row_idx + row_span,
                    start_col_offset_idx=col_idx,
                    end_col_offset_idx=col_idx + col_span,
                    col_header=col_header,
                    row_header=((not col_header) and html_cell.name == "th"),
                )
                data.table_cells.append(cell)

        table_caption = doc.add_text(
            label=DocItemLabel.CAPTION,
            text=table_xml_component["label"] + ": " + table_xml_component["caption"],
        )
        doc.add_table(data=data, parent=self.parents["Tables"], caption=table_caption)
        return

```
</content>
</file_17>

<file_18>
<path>backend/xml/uspto_backend.py</path>
<content>
```python
"""Backend to parse patents from the United States Patent Office (USPTO).

The parsers included in this module can handle patent grants pubished since 1976 and
patent applications since 2001.
The original files can be found in https://bulkdata.uspto.gov.
"""

import html
import logging
import re
import xml.sax
import xml.sax.xmlreader
from abc import ABC, abstractmethod
from enum import Enum, unique
from io import BytesIO
from pathlib import Path
from typing import Any, Final, Optional, Union

from bs4 import BeautifulSoup, Tag
from docling_core.types.doc import (
    DocItem,
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    TableCell,
    TableData,
    TextItem,
)
from docling_core.types.doc.document import LevelNumber
from pydantic import NonNegativeInt
from typing_extensions import Self, TypedDict, override

from docling.backend.abstract_backend import DeclarativeDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

_log = logging.getLogger(__name__)

XML_DECLARATION: Final = '<?xml version="1.0" encoding="UTF-8"?>'


@unique
class PatentHeading(Enum):
    """Text of docling headings for tagged sections in USPTO patent documents."""

    ABSTRACT = "ABSTRACT", 2
    CLAIMS = "CLAIMS", 2

    @override
    def __new__(cls, value: str, _) -> Self:
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    @override
    def __init__(self, _, level: LevelNumber) -> None:
        self.level: LevelNumber = level


class PatentUsptoDocumentBackend(DeclarativeDocumentBackend):
    @override
    def __init__(
        self, in_doc: InputDocument, path_or_stream: Union[BytesIO, Path]
    ) -> None:
        super().__init__(in_doc, path_or_stream)

        self.patent_content: str = ""
        self.parser: Optional[PatentUspto] = None

        try:
            if isinstance(self.path_or_stream, BytesIO):
                while line := self.path_or_stream.readline().decode("utf-8"):
                    if line.startswith("<!DOCTYPE") or line == "PATN\n":
                        self._set_parser(line)
                    self.patent_content += line
            elif isinstance(self.path_or_stream, Path):
                with open(self.path_or_stream, encoding="utf-8") as file_obj:
                    while line := file_obj.readline():
                        if line.startswith("<!DOCTYPE") or line == "PATN\n":
                            self._set_parser(line)
                        self.patent_content += line
        except Exception as exc:
            raise RuntimeError(
                f"Could not initialize USPTO backend for file with hash {self.document_hash}."
            ) from exc

    def _set_parser(self, doctype: str) -> None:
        doctype_line = doctype.lower()
        if doctype == "PATN\n":
            self.parser = PatentUsptoGrantAps()
        elif "us-patent-application-v4" in doctype_line:
            self.parser = PatentUsptoIce()
        elif "us-patent-grant-v4" in doctype_line:
            self.parser = PatentUsptoIce()
        elif "us-grant-025" in doctype_line:
            self.parser = PatentUsptoGrantV2()
        elif all(
            item in doctype_line
            for item in ("patent-application-publication", "pap-v1")
        ):
            self.parser = PatentUsptoAppV1()
        else:
            self.parser = None

    @override
    def is_valid(self) -> bool:
        return bool(self.patent_content) and bool(self.parser)

    @classmethod
    @override
    def supports_pagination(cls) -> bool:
        return False

    @override
    def unload(self) -> None:
        return

    @classmethod
    @override
    def supported_formats(cls) -> set[InputFormat]:
        return {InputFormat.XML_USPTO}

    @override
    def convert(self) -> DoclingDocument:

        if self.parser is not None:
            doc = self.parser.parse(self.patent_content)
            if doc is None:
                raise RuntimeError(
                    f"Failed to convert doc (hash={self.document_hash}, "
                    f"name={self.file.name})."
                )
            doc.name = self.file.name or "file"
            mime_type = (
                "text/plain"
                if isinstance(self.parser, PatentUsptoGrantAps)
                else "application/xml"
            )
            doc.origin = DocumentOrigin(
                mimetype=mime_type,
                binary_hash=self.document_hash,
                filename=self.file.name or "file",
            )

            return doc
        else:
            raise RuntimeError(
                f"Cannot convert doc (hash={self.document_hash}, "
                f"name={self.file.name}) because the backend failed to init."
            )


class PatentUspto(ABC):
    """Parser of patent documents from the US Patent Office."""

    @abstractmethod
    def parse(self, patent_content: str) -> Optional[DoclingDocument]:
        """Parse a USPTO patent.

        Parameters:
            patent_content: The content of a single patent in a USPTO file.

        Returns:
            The patent parsed as a docling document.
        """
        pass


class PatentUsptoIce(PatentUspto):
    """Parser of patent documents from the US Patent Office (ICE).

    The compatible formats are:
    - Patent Grant Full Text Data/XML Version 4.x ICE (from January 2005)
    - Patent Application Full Text Data/XML Version 4.x ICE (from January 2005)
    """

    def __init__(self) -> None:
        """Build an instance of PatentUsptoIce class."""
        self.handler = PatentUsptoIce.PatentHandler()
        self.pattern = re.compile(r"^(<table .*?</table>)", re.MULTILINE | re.DOTALL)

    def parse(self, patent_content: str) -> Optional[DoclingDocument]:
        try:
            xml.sax.parseString(patent_content, self.handler)
        except xml.sax._exceptions.SAXParseException as exc_sax:
            _log.error(f"Error in parsing USPTO document: {exc_sax}")

            return None

        doc = self.handler.doc
        if doc:
            raw_tables = re.findall(self.pattern, patent_content)
            parsed_tables: list[TableData] = []
            _log.debug(f"Found {len(raw_tables)} tables to be parsed with XmlTable.")
            for table in raw_tables:
                table_parser = XmlTable(XML_DECLARATION + "\n" + table)
                try:
                    table_data = table_parser.parse()
                    if table_data:
                        parsed_tables.append(table_data)
                except Exception as exc_table:
                    _log.error(f"Error in parsing USPTO tables: {exc_table}")
            if len(parsed_tables) != len(doc.tables):
                _log.error(
                    f"Number of referenced ({len(doc.tables)}) and parsed "
                    f"({len(parsed_tables)}) tables differ."
                )
            else:
                for idx, item in enumerate(parsed_tables):
                    doc.tables[idx].data = item

        return doc

    class PatentHandler(xml.sax.handler.ContentHandler):
        """SAX ContentHandler for patent documents."""

        APP_DOC_ELEMENT: Final = "us-patent-application"
        GRANT_DOC_ELEMENT: Final = "us-patent-grant"

        @unique
        class Element(Enum):
            """Represents an element of interest in the patent application document."""

            ABSTRACT = "abstract", True
            TITLE = "invention-title", True
            CLAIMS = "claims", False
            CLAIM = "claim", False
            CLAIM_TEXT = "claim-text", True
            PARAGRAPH = "p", True
            HEADING = "heading", True
            DESCRIPTION = "description", False
            TABLE = "table", False  # to track its position, without text
            DRAWINGS = "description-of-drawings", True
            STYLE_SUPERSCRIPT = "sup", True
            STYLE_SUBSCRIPT = "sub", True
            MATHS = "maths", False  # to avoid keeping formulas

            @override
            def __new__(cls, value: str, _) -> Self:
                obj = object.__new__(cls)
                obj._value_ = value
                return obj

            @override
            def __init__(self, _, is_text: bool) -> None:
                self.is_text: bool = is_text

        @override
        def __init__(self) -> None:
            """Build an instance of the patent handler."""
            # Current patent being parsed
            self.doc: Optional[DoclingDocument] = None
            # Keep track of docling hierarchy level
            self.level: LevelNumber = 1
            # Keep track of docling parents by level
            self.parents: dict[LevelNumber, Optional[DocItem]] = {1: None}
            # Content to retain for the current patent
            self.property: list[str]
            self.claim: str
            self.claims: list[str]
            self.abstract: str
            self.text: str
            self._clean_data()
            # To handle mathematical styling
            self.style_html = HtmlEntity()

        @override
        def startElement(self, tag, attributes):  # noqa: N802
            """Signal the start of an element.

            Args:
                tag: The element tag.
                attributes: The element attributes.
            """
            if tag in (
                self.APP_DOC_ELEMENT,
                self.GRANT_DOC_ELEMENT,
            ):
                self.doc = DoclingDocument(name="file")
                self.text = ""
            self._start_registered_elements(tag, attributes)

        @override
        def skippedEntity(self, name):  # noqa: N802
            """Receive notification of a skipped entity.

            HTML entities will be skipped by the parser. This method will unescape them
            and add them to the text.

            Args:
                name: Entity name.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    escaped = self.style_html.get_greek_from_iso8879(f"&{name};")
                    unescaped = html.unescape(escaped)
                    if unescaped == escaped:
                        _log.debug(f"Unrecognized HTML entity: {name}")
                        return

                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(unescaped, elm_val)
                    else:
                        self.text += unescaped

        @override
        def endElement(self, tag):  # noqa: N802
            """Signal the end of an element.

            Args:
                tag: The element tag.
            """
            if tag in (
                self.APP_DOC_ELEMENT,
                self.GRANT_DOC_ELEMENT,
            ):
                self._clean_data()
            self._end_registered_element(tag)

        @override
        def characters(self, content):
            """Receive notification of character data.

            Args:
                content: Data reported by the handler.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(content, elm_val)
                    else:
                        self.text += content

        def _start_registered_elements(
            self, tag: str, attributes: xml.sax.xmlreader.AttributesImpl
        ) -> None:
            if tag in [member.value for member in self.Element]:
                # special case for claims: claim lines may start before the
                # previous one is closed
                if (
                    tag == self.Element.CLAIM_TEXT.value
                    and self.property
                    and self.property[-1] == tag
                    and self.text.strip()
                ):
                    self.claim += " " + self.text.strip()
                    self.text = ""
                elif tag == self.Element.HEADING.value:
                    level_attr: str = attributes.get("level", "")
                    new_level: int = int(level_attr) if level_attr.isnumeric() else 1
                    max_level = min(self.parents.keys())
                    # increase heading level with 1 for title, if any
                    self.level = (
                        new_level + 1 if (new_level + 1) in self.parents else max_level
                    )
                self.property.append(tag)

        def _end_registered_element(self, tag: str) -> None:
            if tag in [item.value for item in self.Element] and self.property:
                current_tag = self.property.pop()
                self._add_property(current_tag, self.text.strip())

        def _add_property(self, name: str, text: str) -> None:
            if not name or not self.doc:
                return

            if name == self.Element.TITLE.value:
                if text:
                    self.parents[self.level + 1] = self.doc.add_title(
                        parent=self.parents[self.level],
                        text=text,
                    )
                    self.level += 1
                self.text = ""

            elif name == self.Element.ABSTRACT.value:
                if self.abstract:
                    heading_text = PatentHeading.ABSTRACT.value
                    heading_level = (
                        PatentHeading.ABSTRACT.level
                        if PatentHeading.ABSTRACT.level in self.parents
                        else 1
                    )
                    abstract_item = self.doc.add_heading(
                        heading_text,
                        level=heading_level,
                        parent=self.parents[heading_level],
                    )
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH,
                        text=self.abstract,
                        parent=abstract_item,
                    )

            elif name == self.Element.CLAIM_TEXT.value:
                text = re.sub("\\s+", " ", text).strip()
                if text:
                    self.claim += " " + text
                self.text = ""

            elif name == self.Element.CLAIM.value and self.claim:
                self.claims.append(self.claim.strip())
                self.claim = ""

            elif name == self.Element.CLAIMS.value and self.claims:
                heading_text = PatentHeading.CLAIMS.value
                heading_level = (
                    PatentHeading.CLAIMS.level
                    if PatentHeading.CLAIMS.level in self.parents
                    else 1
                )
                claims_item = self.doc.add_heading(
                    heading_text,
                    level=heading_level,
                    parent=self.parents[heading_level],
                )
                for text in self.claims:
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH, text=text, parent=claims_item
                    )

            elif name == self.Element.PARAGRAPH.value and text:
                # remmove blank spaces added in paragraphs
                text = re.sub("\\s+", " ", text)
                if self.Element.ABSTRACT.value in self.property:
                    self.abstract = (
                        (self.abstract + " " + text) if self.abstract else text
                    )
                else:
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH,
                        text=text,
                        parent=self.parents[self.level],
                    )
                self.text = ""

            elif name == self.Element.HEADING.value and text:
                self.parents[self.level + 1] = self.doc.add_heading(
                    text=text,
                    level=self.level,
                    parent=self.parents[self.level],
                )
                self.level += 1
                self.text = ""

            elif name == self.Element.TABLE.value:
                # set an empty table as placeholder
                empty_table = TableData(num_rows=0, num_cols=0, table_cells=[])
                self.doc.add_table(
                    data=empty_table,
                    parent=self.parents[self.level],
                )

        def _apply_style(self, text: str, style_tag: str) -> str:
            """Apply an HTML style to text.

            Args:
                text: A string containing plain text.
                style_tag: An HTML tag name for styling text. If the tag name is not
                  recognized as one of the supported styles, the method will return
                  the original `text`.

            Returns:
                A string after applying the style.
            """
            formatted = text

            if style_tag == self.Element.STYLE_SUPERSCRIPT.value:
                formatted = html.unescape(self.style_html.get_superscript(text))
            elif style_tag == self.Element.STYLE_SUBSCRIPT.value:
                formatted = html.unescape(self.style_html.get_subscript(text))

            return formatted

        def _clean_data(self) -> None:
            """Reset the variables from stream data."""
            self.property = []
            self.claim = ""
            self.claims = []
            self.abstract = ""


class PatentUsptoGrantV2(PatentUspto):
    """Parser of patent documents from the US Patent Office (grants v2.5).

    The compatible format is:
    - Patent Grant Full Text Data/XML Version 2.5 (from January 2002 till December 2004)
    """

    @override
    def __init__(self) -> None:
        """Build an instance of PatentUsptoGrantV2 class."""
        self.handler = PatentUsptoGrantV2.PatentHandler()
        self.pattern = re.compile(r"^(<table .*?</table>)", re.MULTILINE | re.DOTALL)

    @override
    def parse(self, patent_content: str) -> Optional[DoclingDocument]:
        try:
            xml.sax.parseString(patent_content, self.handler)
        except xml.sax._exceptions.SAXParseException as exc_sax:
            _log.error(f"Error in parsing USPTO document: {exc_sax}")

            return None

        doc = self.handler.doc
        if doc:
            raw_tables = re.findall(self.pattern, patent_content)
            parsed_tables: list[TableData] = []
            _log.debug(f"Found {len(raw_tables)} tables to be parsed with XmlTable.")
            for table in raw_tables:
                table_parser = XmlTable(XML_DECLARATION + "\n" + table)
                try:
                    table_data = table_parser.parse()
                    if table_data:
                        parsed_tables.append(table_data)
                except Exception as exc_table:
                    _log.error(f"Error in parsing USPTO tables: {exc_table}")
            if len(parsed_tables) != len(doc.tables):
                _log.error(
                    f"Number of referenced ({len(doc.tables)}) and parsed "
                    f"({len(parsed_tables)}) tables differ."
                )
            else:
                for idx, item in enumerate(parsed_tables):
                    doc.tables[idx].data = item

        return doc

    class PatentHandler(xml.sax.handler.ContentHandler):
        """SAX ContentHandler for patent documents."""

        GRANT_DOC_ELEMENT: Final = "PATDOC"
        CLAIM_STATEMENT: Final = "What is claimed is:"

        @unique
        class Element(Enum):
            """Represents an element of interest in the patent application document."""

            PDAT = "PDAT", True  # any type of data
            ABSTRACT = ("SDOAB", False)
            SDOCL = ("SDOCL", False)
            TITLE = ("B540", False)
            CLAIMS = ("CL", False)
            CLAIM = ("CLM", False)
            PARAGRAPH = ("PARA", True)
            HEADING = ("H", True)
            DRAWINGS = ("DRWDESC", False)
            STYLE_SUPERSCRIPT = ("SP", False)
            STYLE_SUBSCRIPT = ("SB", False)
            STYLE_ITALIC = ("ITALIC", False)
            CWU = ("CWU", False)  # avoid tables, chemicals, formulas
            TABLE = ("table", False)  # to keep track of table positions

            @override
            def __new__(cls, value: str, _) -> Self:
                obj = object.__new__(cls)
                obj._value_ = value
                return obj

            @override
            def __init__(self, _, is_text: bool) -> None:
                self.is_text: bool = is_text

        @override
        def __init__(self) -> None:
            """Build an instance of the patent handler."""
            # Current patent being parsed
            self.doc: Optional[DoclingDocument] = None
            # Keep track of docling hierarchy level
            self.level: LevelNumber = 1
            # Keep track of docling parents by level
            self.parents: dict[LevelNumber, Optional[DocItem]] = {1: None}
            # Content to retain for the current patent
            self.property: list[str]
            self.claim: str
            self.claims: list[str]
            self.paragraph: str
            self.abstract: str
            self._clean_data()
            # To handle mathematical styling
            self.style_html = HtmlEntity()

        @override
        def startElement(self, tag, attributes):  # noqa: N802
            """Signal the start of an element.

            Args:
                tag: The element tag.
                attributes: The element attributes.
            """
            if tag == self.GRANT_DOC_ELEMENT:
                self.doc = DoclingDocument(name="file")
                self.text = ""
            self._start_registered_elements(tag, attributes)

        @override
        def skippedEntity(self, name):  # noqa: N802
            """Receive notification of a skipped entity.

            HTML entities will be skipped by the parser. This method will unescape them
            and add them to the text.

            Args:
                name: Entity name.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    escaped = self.style_html.get_greek_from_iso8879(f"&{name};")
                    unescaped = html.unescape(escaped)
                    if unescaped == escaped:
                        logging.debug("Unrecognized HTML entity: " + name)
                        return

                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(unescaped, elm_val)
                    else:
                        self.text += unescaped

        @override
        def endElement(self, tag):  # noqa: N802
            """Signal the end of an element.

            Args:
                tag: The element tag.
            """
            if tag == self.GRANT_DOC_ELEMENT:
                self._clean_data()
            self._end_registered_element(tag)

        @override
        def characters(self, content):
            """Receive notification of character data.

            Args:
                content: Data reported by the handler.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(content, elm_val)
                    else:
                        self.text += content

        def _start_registered_elements(
            self, tag: str, attributes: xml.sax.xmlreader.AttributesImpl
        ) -> None:
            if tag in [member.value for member in self.Element]:
                if (
                    tag == self.Element.HEADING.value
                    and not self.Element.SDOCL.value in self.property
                ):
                    level_attr: str = attributes.get("LVL", "")
                    new_level: int = int(level_attr) if level_attr.isnumeric() else 1
                    max_level = min(self.parents.keys())
                    # increase heading level with 1 for title, if any
                    self.level = (
                        new_level + 1 if (new_level + 1) in self.parents else max_level
                    )
                self.property.append(tag)

        def _end_registered_element(self, tag: str) -> None:
            if tag in [elm.value for elm in self.Element] and self.property:
                current_tag = self.property.pop()
                self._add_property(current_tag, self.text)

        def _add_property(self, name: str, text: str) -> None:
            if not name or not self.doc:
                return
            if name == self.Element.PDAT.value and text:
                if not self.property:
                    self.text = ""
                    return

                wrapper = self.property[-1]
                text = self._apply_style(text, wrapper)

                if self.Element.TITLE.value in self.property and text.strip():
                    title = text.strip()
                    self.parents[self.level + 1] = self.doc.add_title(
                        parent=self.parents[self.level],
                        text=title,
                    )
                    self.level += 1

                elif self.Element.ABSTRACT.value in self.property:
                    self.abstract += text

                elif self.Element.CLAIM.value in self.property:
                    self.claim += text

                # Paragraph text not in claims or abstract
                elif (
                    self.Element.PARAGRAPH.value in self.property
                    and self.Element.CLAIM.value not in self.property
                    and self.Element.ABSTRACT.value not in self.property
                ):
                    self.paragraph += text

                # headers except claims statement
                elif (
                    self.Element.HEADING.value in self.property
                    and not self.Element.SDOCL.value in self.property
                    and text.strip()
                ):
                    self.parents[self.level + 1] = self.doc.add_heading(
                        text=text.strip(),
                        level=self.level,
                        parent=self.parents[self.level],
                    )
                    self.level += 1

                self.text = ""

            elif name == self.Element.CLAIM.value and self.claim.strip():
                self.claims.append(self.claim.strip())
                self.claim = ""

            elif name == self.Element.CLAIMS.value and self.claims:
                heading_text = PatentHeading.CLAIMS.value
                heading_level = (
                    PatentHeading.CLAIMS.level
                    if PatentHeading.CLAIMS.level in self.parents
                    else 1
                )
                claims_item = self.doc.add_heading(
                    heading_text,
                    level=heading_level,
                    parent=self.parents[heading_level],
                )
                for text in self.claims:
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH, text=text, parent=claims_item
                    )

            elif name == self.Element.ABSTRACT.value and self.abstract.strip():
                abstract = self.abstract.strip()
                heading_text = PatentHeading.ABSTRACT.value
                heading_level = (
                    PatentHeading.ABSTRACT.level
                    if PatentHeading.ABSTRACT.level in self.parents
                    else 1
                )
                abstract_item = self.doc.add_heading(
                    heading_text,
                    level=heading_level,
                    parent=self.parents[heading_level],
                )
                self.doc.add_text(
                    label=DocItemLabel.PARAGRAPH, text=abstract, parent=abstract_item
                )

            elif name == self.Element.PARAGRAPH.value:
                paragraph = self.paragraph.strip()
                if paragraph and self.Element.CLAIM.value not in self.property:
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH,
                        text=paragraph,
                        parent=self.parents[self.level],
                    )
                elif self.Element.CLAIM.value in self.property:
                    # we may need a space after a paragraph in claim text
                    self.claim += " "
                self.paragraph = ""

            elif name == self.Element.TABLE.value:
                # set an empty table as placeholder
                empty_table = TableData(num_rows=0, num_cols=0, table_cells=[])
                self.doc.add_table(
                    data=empty_table,
                    parent=self.parents[self.level],
                )

        def _apply_style(self, text: str, style_tag: str) -> str:
            """Apply an HTML style to text.

            Args:
                text: A string containing plain text.
                style_tag: An HTML tag name for styling text. If the tag name is not
                  recognized as one of the supported styles, the method will return
                  the original `text`.

            Returns:
                A string after applying the style.
            """
            formatted = text

            if style_tag == self.Element.STYLE_SUPERSCRIPT.value:
                formatted = html.unescape(self.style_html.get_superscript(text))
            elif style_tag == self.Element.STYLE_SUBSCRIPT.value:
                formatted = html.unescape(self.style_html.get_subscript(text))
            elif style_tag == self.Element.STYLE_ITALIC.value:
                formatted = html.unescape(self.style_html.get_math_italic(text))

            return formatted

        def _clean_data(self) -> None:
            """Reset the variables from stream data."""
            self.text = ""
            self.property = []
            self.claim = ""
            self.claims = []
            self.paragraph = ""
            self.abstract = ""


class PatentUsptoGrantAps(PatentUspto):
    """Parser of patents documents from the US Patent Office (grants APS).

    The compatible format is:
    - Patent Grant Full Text Data/APS (from January 1976 till December 2001)
    """

    @unique
    class Section(Enum):
        """Represent a section in a patent APS document."""

        ABSTRACT = "ABST"
        SUMMARY = "BSUM"
        DETAILS = "DETD"
        CLAIMS = "CLMS"
        DRAWINGS = "DRWD"

    @unique
    class Field(Enum):
        """Represent a field in a patent APS document."""

        DOC_NUMBER = "WKU"
        TITLE = "TTL"
        PARAGRAPH = "PAR"
        PARAGRAPH_1 = "PA1"
        PARAGRAPH_2 = "PA2"
        PARAGRAPH_3 = "PA3"
        TEXT = "PAL"
        CAPTION = "PAC"
        NUMBER = "NUM"
        NAME = "NAM"
        IPC = "ICL"
        ISSUED = "ISD"
        FILED = "APD"
        PATENT_NUMBER = "PNO"
        APPLICATION_NUMBER = "APN"
        APPLICATION_TYPE = "APT"
        COUNTRY = "CNT"

    @override
    def __init__(self) -> None:
        """Build an instance of PatentUsptoGrantAps class."""
        self.doc: Optional[DoclingDocument] = None
        # Keep track of docling hierarchy level
        self.level: LevelNumber = 1
        # Keep track of docling parents by level
        self.parents: dict[LevelNumber, Optional[DocItem]] = {1: None}

    def get_last_text_item(self) -> Optional[TextItem]:
        """Get the last text item at the current document level.

        Returns:
            The text item or None, if the current level parent has no children."""
        if self.doc:
            parent = self.parents[self.level]
            children = parent.children if parent is not None else []
        else:
            return None
        text_list: list[TextItem] = [
            item
            for item in self.doc.texts
            if isinstance(item, TextItem) and item.get_ref() in children
        ]

        if text_list:
            return text_list[-1]
        else:
            return None

    def store_section(self, section: str) -> None:
        """Store the section heading in the docling document.

        Only the predefined sections from PatentHeading will be handled.
        The other sections are created by the Field.CAPTION field.

        Args:
            section: A patent section name."""
        heading: PatentHeading
        if self.doc is None:
            return
        elif section == self.Section.ABSTRACT.value:
            heading = PatentHeading.ABSTRACT
        elif section == self.Section.CLAIMS.value:
            heading = PatentHeading.CLAIMS
        else:
            return None

        self.level = heading.level if heading.level in self.parents else 1
        self.parents[self.level + 1] = self.doc.add_heading(
            heading.value,
            level=self.level,
            parent=self.parents[self.level],
        )
        self.level += 1

    def store_content(self, section: str, field: str, value: str) -> None:
        """Store the key value within a document section in the docling document.

        Args:
            section: A patent section name.
            field: A field name.
            value: A field value name.
        """
        if (
            not self.doc
            or not field
            or field not in [item.value for item in PatentUsptoGrantAps.Field]
        ):
            return

        if field == self.Field.TITLE.value:
            self.parents[self.level + 1] = self.doc.add_title(
                parent=self.parents[self.level], text=value
            )
            self.level += 1

        elif field == self.Field.TEXT.value and section == self.Section.ABSTRACT.value:
            abst_item = self.get_last_text_item()
            if abst_item:
                abst_item.text += " " + value
            else:
                self.doc.add_text(
                    label=DocItemLabel.PARAGRAPH,
                    text=value,
                    parent=self.parents[self.level],
                )

        elif field == self.Field.NUMBER.value and section == self.Section.CLAIMS.value:
            self.doc.add_text(
                label=DocItemLabel.PARAGRAPH,
                text="",
                parent=self.parents[self.level],
            )

        elif (
            field
            in (
                self.Field.PARAGRAPH.value,
                self.Field.PARAGRAPH_1.value,
                self.Field.PARAGRAPH_2.value,
                self.Field.PARAGRAPH_3.value,
            )
            and section == self.Section.CLAIMS.value
        ):
            last_claim = self.get_last_text_item()
            if last_claim is None:
                last_claim = self.doc.add_text(
                    label=DocItemLabel.PARAGRAPH,
                    text="",
                    parent=self.parents[self.level],
                )

            last_claim.text += f" {value}" if last_claim.text else value

        elif field == self.Field.CAPTION.value and section in (
            self.Section.SUMMARY.value,
            self.Section.DETAILS.value,
            self.Section.DRAWINGS.value,
        ):
            # captions are siblings of abstract since no level info is provided
            head_item = PatentHeading.ABSTRACT
            self.level = head_item.level if head_item.level in self.parents else 1
            self.parents[self.level + 1] = self.doc.add_heading(
                value,
                level=self.level,
                parent=self.parents[self.level],
            )
            self.level += 1

        elif field in (
            self.Field.PARAGRAPH.value,
            self.Field.PARAGRAPH_1.value,
            self.Field.PARAGRAPH_2.value,
            self.Field.PARAGRAPH_3.value,
        ) and section in (
            self.Section.SUMMARY.value,
            self.Section.DETAILS.value,
            self.Section.DRAWINGS.value,
        ):
            self.doc.add_text(
                label=DocItemLabel.PARAGRAPH,
                text=value,
                parent=self.parents[self.level],
            )

    def parse(self, patent_content: str) -> Optional[DoclingDocument]:
        self.doc = self.doc = DoclingDocument(name="file")
        section: str = ""
        key: str = ""
        value: str = ""
        line_num = 0
        for line in patent_content.splitlines():
            cols = re.split("\\s{2,}", line, maxsplit=1)
            if key and value and (len(cols) == 1 or (len(cols) == 2 and cols[0])):
                self.store_content(section, key, value)
                key = ""
                value = ""
            if len(cols) == 1:  # section title
                section = cols[0]
                self.store_section(section)
                _log.debug(f"Parsing section {section}")
            elif len(cols) == 2:  # key value
                if cols[0]:  # key present
                    key = cols[0]
                    value = cols[1]
                elif not re.match(r"^##STR\d+##$", cols[1]):  # line continues
                    value += " " + cols[1]
            line_num += 1
        if key and value:
            self.store_content(section, key, value)

        # TODO: parse tables
        return self.doc


class PatentUsptoAppV1(PatentUspto):
    """Parser of patent documents from the US Patent Office (applications v1.x)

    The compatible format is:
    - Patent Application Full Text Data/XML Version 1.x (from March 2001 till December
      2004)
    """

    @override
    def __init__(self) -> None:
        """Build an instance of PatentUsptoAppV1 class."""
        self.handler = PatentUsptoAppV1.PatentHandler()
        self.pattern = re.compile(r"^(<table .*?</table>)", re.MULTILINE | re.DOTALL)

    @override
    def parse(self, patent_content: str) -> Optional[DoclingDocument]:
        try:
            xml.sax.parseString(patent_content, self.handler)
        except xml.sax._exceptions.SAXParseException as exc_sax:
            _log.error(f"Error in parsing USPTO document: {exc_sax}")

            return None

        doc = self.handler.doc
        if doc:
            raw_tables = re.findall(self.pattern, patent_content)
            parsed_tables: list[TableData] = []
            _log.debug(f"Found {len(raw_tables)} tables to be parsed with XmlTable.")
            for table in raw_tables:
                table_parser = XmlTable(XML_DECLARATION + "\n" + table)
                try:
                    table_data = table_parser.parse()
                    if table_data:
                        parsed_tables.append(table_data)
                except Exception as exc_table:
                    _log.error(f"Error in parsing USPTO tables: {exc_table}")
            if len(parsed_tables) != len(doc.tables):
                _log.error(
                    f"Number of referenced ({len(doc.tables)}) and parsed "
                    f"({len(parsed_tables)}) tables differ."
                )
            else:
                for idx, item in enumerate(parsed_tables):
                    doc.tables[idx].data = item

        return doc

    class PatentHandler(xml.sax.handler.ContentHandler):
        """SAX ContentHandler for patent documents."""

        APP_DOC_ELEMENT: Final = "patent-application-publication"

        @unique
        class Element(Enum):
            """Represents an element of interest in the patent application document."""

            DRAWINGS = "brief-description-of-drawings", False
            ABSTRACT = "subdoc-abstract", False
            TITLE = "title-of-invention", True
            CLAIMS = "subdoc-claims", False
            CLAIM = "claim", False
            CLAIM_TEXT = "claim-text", True
            NUMBER = ("number", False)
            PARAGRAPH = "paragraph", True
            HEADING = "heading", True
            STYLE_SUPERSCRIPT = "superscript", True
            STYLE_SUBSCRIPT = "subscript", True
            # do not store text of a table, since it can be within paragraph
            TABLE = "table", False
            # do not store text of a formula, since it can be within paragraph
            MATH = "math-cwu", False

            @override
            def __new__(cls, value: str, _) -> Self:
                obj = object.__new__(cls)
                obj._value_ = value
                return obj

            @override
            def __init__(self, _, is_text: bool) -> None:
                self.is_text: bool = is_text

        @override
        def __init__(self) -> None:
            """Build an instance of the patent handler."""
            # Current patent being parsed
            self.doc: Optional[DoclingDocument] = None
            # Keep track of docling hierarchy level
            self.level: LevelNumber = 1
            # Keep track of docling parents by level
            self.parents: dict[LevelNumber, Optional[DocItem]] = {1: None}
            # Content to retain for the current patent
            self.property: list[str]
            self.claim: str
            self.claims: list[str]
            self.abstract: str
            self.text: str
            self._clean_data()
            # To handle mathematical styling
            self.style_html = HtmlEntity()

        @override
        def startElement(self, tag, attributes):  # noqa: N802
            """Signal the start of an element.

            Args:
                tag: The element tag.
                attributes: The element attributes.
            """
            if tag == self.APP_DOC_ELEMENT:
                self.doc = DoclingDocument(name="file")
                self.text = ""
            self._start_registered_elements(tag, attributes)

        @override
        def skippedEntity(self, name):  # noqa: N802
            """Receive notification of a skipped entity.

            HTML entities will be skipped by the parser. This method will unescape them
            and add them to the text.

            Args:
                name: Entity name.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    escaped = self.style_html.get_greek_from_iso8879(f"&{name};")
                    unescaped = html.unescape(escaped)
                    if unescaped == escaped:
                        logging.debug("Unrecognized HTML entity: " + name)
                        return

                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(unescaped, elm_val)
                    else:
                        self.text += unescaped

        @override
        def endElement(self, tag):  # noqa: N802
            """Signal the end of an element.

            Args:
                tag: The element tag.
            """
            if tag == self.APP_DOC_ELEMENT:
                self._clean_data()
            self._end_registered_element(tag)

        @override
        def characters(self, content):
            """Receive notification of character data.

            Args:
                content: Data reported by the handler.
            """
            if self.property:
                elm_val = self.property[-1]
                element = self.Element(elm_val)
                if element.is_text:
                    if element in (
                        self.Element.STYLE_SUPERSCRIPT,
                        self.Element.STYLE_SUBSCRIPT,
                    ):
                        # superscripts and subscripts need to be under text elements
                        if len(self.property) < 2:
                            return
                        parent_val = self.property[-2]
                        parent = self.Element(parent_val)
                        if parent.is_text:
                            self.text += self._apply_style(content, elm_val)
                    else:
                        self.text += content

        def _start_registered_elements(
            self, tag: str, attributes: xml.sax.xmlreader.AttributesImpl
        ) -> None:
            if tag in [member.value for member in self.Element]:
                # special case for claims: claim lines may start before the
                # previous one is closed
                if (
                    tag == self.Element.CLAIM_TEXT.value
                    and self.property
                    and self.property[-1] == tag
                    and self.text.strip()
                ):
                    self.claim += " " + self.text.strip("\n")
                    self.text = ""
                elif tag == self.Element.HEADING.value:
                    level_attr: str = attributes.get("lvl", "")
                    new_level: int = int(level_attr) if level_attr.isnumeric() else 1
                    max_level = min(self.parents.keys())
                    # increase heading level with 1 for title, if any
                    self.level = (
                        new_level + 1 if (new_level + 1) in self.parents else max_level
                    )
                self.property.append(tag)

        def _end_registered_element(self, tag: str) -> None:
            if tag in [elm.value for elm in self.Element] and self.property:
                current_tag = self.property.pop()
                self._add_property(current_tag, self.text)

        def _add_property(self, name: str, text: str) -> None:
            if not name or not self.doc:
                return

            if name == self.Element.TITLE.value:
                title = text.strip()
                if title:
                    self.parents[self.level + 1] = self.doc.add_text(
                        parent=self.parents[self.level],
                        label=DocItemLabel.TITLE,
                        text=title,
                    )
                    self.level += 1
                self.text = ""
            elif name == self.Element.ABSTRACT.value:
                abstract = self.abstract.strip()
                if abstract:
                    heading_text = PatentHeading.ABSTRACT.value
                    heading_level = (
                        PatentHeading.ABSTRACT.level
                        if PatentHeading.ABSTRACT.level in self.parents
                        else 1
                    )
                    abstract_item = self.doc.add_heading(
                        heading_text,
                        level=heading_level,
                        parent=self.parents[heading_level],
                    )
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH,
                        text=self.abstract,
                        parent=abstract_item,
                    )
                    self.abstract = ""
                self.text = ""
            elif name == self.Element.CLAIM_TEXT.value:
                if text:
                    self.claim += self.text.strip("\n")
                self.text = ""

            elif name == self.Element.CLAIM.value:
                claim = self.claim.strip()
                if claim:
                    self.claims.append(claim)
                self.claim = ""

            elif name == self.Element.CLAIMS.value and self.claims:
                heading_text = PatentHeading.CLAIMS.value
                heading_level = (
                    PatentHeading.CLAIMS.level
                    if PatentHeading.CLAIMS.level in self.parents
                    else 1
                )
                claims_item = self.doc.add_heading(
                    heading_text,
                    level=heading_level,
                    parent=self.parents[heading_level],
                )
                for text in self.claims:
                    self.doc.add_text(
                        label=DocItemLabel.PARAGRAPH, text=text, parent=claims_item
                    )

            elif name in (
                self.Element.PARAGRAPH.value,
                self.Element.HEADING.value,
            ):
                if text and self.Element.ABSTRACT.value in self.property:
                    self.abstract = (self.abstract + text) if self.abstract else text
                elif text.strip():
                    text = re.sub("\\s+", " ", text).strip()
                    if name == self.Element.HEADING.value:
                        self.parents[self.level + 1] = self.doc.add_heading(
                            text=text,
                            level=self.level,
                            parent=self.parents[self.level],
                        )
                        self.level += 1
                    else:
                        self.doc.add_text(
                            label=DocItemLabel.PARAGRAPH,
                            text=text,
                            parent=self.parents[self.level],
                        )
                self.text = ""

            elif name == self.Element.TABLE.value:
                # set an empty table as placeholder
                empty_table = TableData(num_rows=0, num_cols=0, table_cells=[])
                self.doc.add_table(
                    data=empty_table,
                    parent=self.parents[self.level],
                )

        def _apply_style(self, text: str, style_tag: str) -> str:
            """Apply an HTML style to text.

            Args:
                text: A string containing plain text.
                style_tag: An HTML tag name for styling text. If the tag name is not
                  recognized as one of the supported styles, the method will return
                  the original `text`.

            Returns:
                A string after applying the style.
            """
            formatted = html.unescape(text)

            if style_tag == self.Element.STYLE_SUPERSCRIPT.value:
                formatted = html.unescape(self.style_html.get_superscript(formatted))
            elif style_tag == self.Element.STYLE_SUBSCRIPT.value:
                formatted = html.unescape(self.style_html.get_subscript(formatted))

            return formatted

        def _clean_data(self):
            """Reset the variables from stream data."""
            self.property = []
            self.abstract = ""
            self.claim = ""
            self.claims = []
            self.text = ""


class XmlTable:
    """Provide a table parser for xml tables in USPTO patent documents.

    The OASIS Open XML Exchange Table Model can be downloaded from:
    http://oasis-open.org/specs/soextblx.dtd
    """

    class MinColInfoType(TypedDict):
        offset: list[int]
        colwidth: list[int]

    class ColInfoType(MinColInfoType):
        cell_range: list[int]
        cell_offst: list[int]

    def __init__(self, input: str) -> None:
        """Initialize the table parser with the xml content.

        Args:
            input: The xml content.
        """
        self.max_nbr_messages = 2
        self.nbr_messages = 0
        self.empty_text = ""
        self._soup = BeautifulSoup(input, features="xml")

    def _create_tg_range(self, tgs: list[dict[str, Any]]) -> dict[int, ColInfoType]:
        """Create a unified range along the table groups.

        Args:
            tgs: Table group column specifications.

        Returns:
            Unified group column specifications.
        """
        colinfo: dict[int, XmlTable.ColInfoType] = {}

        if len(tgs) == 0:
            return colinfo

        for itg, tg in enumerate(tgs):
            colinfo[itg] = {
                "offset": [],
                "colwidth": [],
                "cell_range": [],
                "cell_offst": [0],
            }
            offst = 0
            for info in tg["colinfo"]:
                cw = info["colwidth"]
                cw = re.sub("pt", "", cw, flags=re.I)
                cw = re.sub("mm", "", cw, flags=re.I)
                try:
                    cw = int(cw)
                except BaseException:
                    cw = float(cw)
                colinfo[itg]["colwidth"].append(cw)
                colinfo[itg]["offset"].append(offst)
                offst += cw
            colinfo[itg]["offset"].append(offst)

        min_colinfo: XmlTable.MinColInfoType = {"offset": [], "colwidth": []}

        min_colinfo["offset"] = colinfo[0]["offset"]
        offset_w0 = []
        for itg, col in colinfo.items():
            # keep track of col with 0 width
            for ic, cw in enumerate(col["colwidth"]):
                if cw == 0:
                    offset_w0.append(col["offset"][ic])

            min_colinfo["offset"] = sorted(
                list(set(col["offset"] + min_colinfo["offset"]))
            )

        # add back the 0 width cols to offset list
        offset_w0 = list(set(offset_w0))
        min_colinfo["offset"] = sorted(min_colinfo["offset"] + offset_w0)

        for i in range(len(min_colinfo["offset"]) - 1):
            min_colinfo["colwidth"].append(
                min_colinfo["offset"][i + 1] - min_colinfo["offset"][i]
            )

        for itg, col in colinfo.items():
            i = 1
            range_ = 1
            for min_i in range(1, len(min_colinfo["offset"])):
                min_offst = min_colinfo["offset"][min_i]
                offst = col["offset"][i]
                if min_offst == offst:
                    if (
                        len(col["offset"]) == i + 1
                        and len(min_colinfo["offset"]) > min_i + 1
                    ):
                        range_ += 1
                    else:
                        col["cell_range"].append(range_)
                        col["cell_offst"].append(col["cell_offst"][-1] + range_)
                        range_ = 1
                        i += 1
                elif min_offst < offst:
                    range_ += 1
                else:
                    _log.debug("A USPTO XML table has wrong offsets.")
                    return {}

        return colinfo

    def _get_max_ncols(self, tgs_info: dict[int, ColInfoType]) -> NonNegativeInt:
        """Get the maximum number of columns across table groups.

        Args:
            tgs_info: Unified group column specifications.

        Return:
            The maximum number of columns.
        """
        ncols_max = 0
        for rowinfo in tgs_info.values():
            ncols_max = max(ncols_max, len(rowinfo["colwidth"]))

        return ncols_max

    def _parse_table(self, table: Tag) -> TableData:
        """Parse the content of a table tag.

        Args:
            The table element.

        Returns:
            A docling table object.
        """
        tgs_align = []
        tg_secs = table.find_all("tgroup")
        if tg_secs:
            for tg_sec in tg_secs:
                ncols = tg_sec.get("cols", None)
                if ncols:
                    ncols = int(ncols)
                tg_align = {"ncols": ncols, "colinfo": []}
                cs_secs = tg_sec.find_all("colspec")
                if cs_secs:
                    for cs_sec in cs_secs:
                        colname = cs_sec.get("colname", None)
                        colwidth = cs_sec.get("colwidth", None)
                        tg_align["colinfo"].append(
                            {"colname": colname, "colwidth": colwidth}
                        )

                tgs_align.append(tg_align)

        # create unified range along the table groups
        tgs_range = self._create_tg_range(tgs_align)

        # if the structure is broken, return an empty table
        if not tgs_range:
            dl_table = TableData(num_rows=0, num_cols=0, table_cells=[])
            return dl_table

        ncols_max = self._get_max_ncols(tgs_range)

        # extract table data
        table_data: list[TableCell] = []
        i_row_global = 0
        is_row_empty: bool = True
        tg_secs = table.find_all("tgroup")
        if tg_secs:
            for itg, tg_sec in enumerate(tg_secs):
                tg_range = tgs_range[itg]
                row_secs = tg_sec.find_all(["row", "tr"])

                if row_secs:
                    for row_sec in row_secs:
                        entry_secs = row_sec.find_all(["entry", "td"])
                        is_header: bool = row_sec.parent.name in ["thead"]

                        ncols = 0
                        local_row: list[TableCell] = []
                        is_row_empty = True
                        if entry_secs:
                            wrong_nbr_cols = False
                            for ientry, entry_sec in enumerate(entry_secs):
                                text = entry_sec.get_text().strip()

                                # start-end
                                namest = entry_sec.attrs.get("namest", None)
                                nameend = entry_sec.attrs.get("nameend", None)
                                if isinstance(namest, str) and namest.isnumeric():
                                    namest = int(namest)
                                else:
                                    namest = ientry + 1
                                if isinstance(nameend, str) and nameend.isnumeric():
                                    nameend = int(nameend)
                                    shift = 0
                                else:
                                    nameend = ientry + 2
                                    shift = 1

                                if nameend > len(tg_range["cell_offst"]):
                                    wrong_nbr_cols = True
                                    self.nbr_messages += 1
                                    if self.nbr_messages <= self.max_nbr_messages:
                                        _log.debug(
                                            "USPTO table has # entries != # columns"
                                        )
                                    break

                                range_ = [
                                    tg_range["cell_offst"][namest - 1],
                                    tg_range["cell_offst"][nameend - 1] - shift,
                                ]

                                # add row and replicate cell if needed
                                cell_text = text if text else self.empty_text
                                if cell_text != self.empty_text:
                                    is_row_empty = False
                                for irep in range(range_[0], range_[1] + 1):
                                    ncols += 1
                                    local_row.append(
                                        TableCell(
                                            column_header=is_header,
                                            text=cell_text,
                                            start_row_offset_idx=i_row_global,
                                            end_row_offset_idx=i_row_global + 1,
                                            row_span=1,
                                            start_col_offset_idx=range_[0],
                                            end_col_offset_idx=range_[1] + 1,
                                            col_span=range_[1] - range_[0] + 1,
                                        )
                                    )

                            if wrong_nbr_cols:
                                # keep empty text, not to introduce noise
                                local_row = []
                                ncols = 0

                            # add empty cell up to ncols_max
                            for irep in range(ncols, ncols_max):
                                local_row.append(
                                    TableCell(
                                        column_header=is_header,
                                        text=self.empty_text,
                                        start_row_offset_idx=i_row_global,
                                        end_row_offset_idx=i_row_global + 1,
                                        row_span=1,
                                        start_col_offset_idx=irep,
                                        end_col_offset_idx=irep + 1,
                                        col_span=1,
                                    )
                                )
                        # do not add empty rows
                        if not is_row_empty:
                            table_data.extend(local_row)
                            i_row_global += 1

        dl_table = TableData(
            num_rows=i_row_global, num_cols=ncols_max, table_cells=table_data
        )

        return dl_table

    def parse(self) -> Optional[TableData]:
        """Parse the first table from an xml content.

        Returns:
            A docling table data.
        """
        section = self._soup.find("table")
        if section is not None:
            table = self._parse_table(section)
            if table.num_rows == 0 or table.num_cols == 0:
                _log.warning("The parsed USPTO table is empty")
            return table
        else:
            return None


class HtmlEntity:
    """Provide utility functions to get the HTML entities of styled characters.

    This class has been developped from:
    https://unicode-table.com/en/html-entities/
    https://www.w3.org/TR/WD-math-970515/table03.html
    """

    def __init__(self):
        """Initialize this class by loading the HTML entity dictionaries."""
        self.superscript = str.maketrans(
            {
                "1": "&sup1;",
                "2": "&sup2;",
                "3": "&sup3;",
                "4": "&#8308;",
                "5": "&#8309;",
                "6": "&#8310;",
                "7": "&#8311;",
                "8": "&#8312;",
                "9": "&#8313;",
                "0": "&#8304;",
                "+": "&#8314;",
                "-": "&#8315;",
                "−": "&#8315;",
                "=": "&#8316;",
                "(": "&#8317;",
                ")": "&#8318;",
                "a": "&#170;",
                "o": "&#186;",
                "i": "&#8305;",
                "n": "&#8319;",
            }
        )
        self.subscript = str.maketrans(
            {
                "1": "&#8321;",
                "2": "&#8322;",
                "3": "&#8323;",
                "4": "&#8324;",
                "5": "&#8325;",
                "6": "&#8326;",
                "7": "&#8327;",
                "8": "&#8328;",
                "9": "&#8329;",
                "0": "&#8320;",
                "+": "&#8330;",
                "-": "&#8331;",
                "−": "&#8331;",
                "=": "&#8332;",
                "(": "&#8333;",
                ")": "&#8334;",
                "a": "&#8336;",
                "e": "&#8337;",
                "o": "&#8338;",
                "x": "&#8339;",
            }
        )
        self.mathematical_italic = str.maketrans(
            {
                "A": "&#119860;",
                "B": "&#119861;",
                "C": "&#119862;",
                "D": "&#119863;",
                "E": "&#119864;",
                "F": "&#119865;",
                "G": "&#119866;",
                "H": "&#119867;",
                "I": "&#119868;",
                "J": "&#119869;",
                "K": "&#119870;",
                "L": "&#119871;",
                "M": "&#119872;",
                "N": "&#119873;",
                "O": "&#119874;",
                "P": "&#119875;",
                "Q": "&#119876;",
                "R": "&#119877;",
                "S": "&#119878;",
                "T": "&#119879;",
                "U": "&#119880;",
                "V": "&#119881;",
                "W": "&#119882;",
                "Y": "&#119884;",
                "Z": "&#119885;",
                "a": "&#119886;",
                "b": "&#119887;",
                "c": "&#119888;",
                "d": "&#119889;",
                "e": "&#119890;",
                "f": "&#119891;",
                "g": "&#119892;",
                "h": "&#119893;",
                "i": "&#119894;",
                "j": "&#119895;",
                "k": "&#119896;",
                "l": "&#119897;",
                "m": "&#119898;",
                "n": "&#119899;",
                "o": "&#119900;",
                "p": "&#119901;",
                "q": "&#119902;",
                "r": "&#119903;",
                "s": "&#119904;",
                "t": "&#119905;",
                "u": "&#119906;",
                "v": "&#119907;",
                "w": "&#119908;",
                "x": "&#119909;",
                "y": "&#119910;",
                "z": "&#119911;",
            }
        )

        self.lookup_iso8879 = {
            "&Agr;": "&Alpha;",
            "&Bgr;": "&Beta;",
            "&Ggr;": "&Gamma;",
            "&Dgr;": "&Delta;",
            "&Egr;": "&Epsilon;",
            "&Zgr;": "&Zeta;",
            "&EEgr;": "&Eta;",
            "&THgr;": "&Theta;",
            "&Igr;": "&Iota;",
            "&Kgr;": "&Kappa;",
            "&Lgr;": "&Lambda;",
            "&Mgr;": "&Mu;",
            "&Ngr;": "&Nu;",
            "&Xgr;": "&Xi;",
            "&Ogr;": "&Omicron;",
            "&Pgr;": "&Pi;",
            "&Rgr;": "&Rho;",
            "&Sgr;": "&Sigma;",
            "&Tgr;": "&Tau;",
            "&Ugr;": "&Upsilon;",
            "&PHgr;": "&Phi;",
            "&KHgr;": "&Chi;",
            "&PSgr;": "&Psi;",
            "&OHgr;": "&Omega;",
            "&agr;": "&alpha;",
            "&bgr;": "&beta;",
            "&ggr;": "&gamma;",
            "&dgr;": "&delta;",
            "&egr;": "&epsilon;",
            "&zgr;": "&zeta;",
            "&eegr;": "&eta;",
            "&thgr;": "&theta;",
            "&igr;": "&iota;",
            "&kgr;": "&kappa;",
            "&lgr;": "&lambda;",
            "&mgr;": "&mu;",
            "&ngr;": "&nu;",
            "&xgr;": "&xi;",
            "&ogr;": "&omicron;",
            "&pgr;": "&pi;",
            "&rgr;": "&rho;",
            "&sgr;": "&sigmaf;",
            "&tgr;": "&tau;",
            "&ugr;": "&upsilon;",
            "&phgr;": "&phi;",
            "&khgr;": "&chi;",
            "&psgr;": "&psi;",
            "&ohgr;": "&omega;",
        }

    def get_superscript(self, text: str) -> str:
        """Get a text in superscript as HTML entities.

        Args:
            text: The text to transform.

        Returns:
            The text in superscript as HTML entities.
        """
        return text.translate(self.superscript)

    def get_subscript(self, text: str) -> str:
        """Get a text in subscript as HTML entities.

        Args:
            The text to transform.

        Returns:
            The text in subscript as HTML entities.
        """
        return text.translate(self.subscript)

    def get_math_italic(self, text: str) -> str:
        """Get a text in italic as HTML entities.

        Args:
            The text to transform.

        Returns:
            The text in italics as HTML entities.
        """
        return text.translate(self.mathematical_italic)

    def get_greek_from_iso8879(self, text: str) -> str:
        """Get an HTML entity of a greek letter in ISO 8879.

        Args:
            The text to transform, as an ISO 8879 entitiy.

        Returns:
            The HTML entity representing a greek letter. If the input text is not
              supported, the original text is returned.
        """
        return self.lookup_iso8879.get(text, text)

```
</content>
</file_18>

<file_19>
<path>chunking/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

from docling_core.transforms.chunker.base import BaseChunk, BaseChunker, BaseMeta
from docling_core.transforms.chunker.hierarchical_chunker import (
    DocChunk,
    DocMeta,
    HierarchicalChunker,
)
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker

```
</content>
</file_19>

<file_20>
<path>cli/__init__.py</path>
<content>
```python

```
</content>
</file_20>

<file_21>
<path>cli/main.py</path>
<content>
```python
import importlib
import logging
import platform
import re
import sys
import tempfile
import time
import warnings
from pathlib import Path
from typing import Annotated, Dict, Iterable, List, Optional, Type

import typer
from docling_core.types.doc import ImageRefMode
from docling_core.utils.file import resolve_source_to_path
from pydantic import TypeAdapter

from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import (
    ConversionStatus,
    FormatToExtensions,
    InputFormat,
    OutputFormat,
)
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    EasyOcrOptions,
    OcrEngine,
    OcrMacOptions,
    OcrOptions,
    PdfBackend,
    PdfPipelineOptions,
    RapidOcrOptions,
    TableFormerMode,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.datamodel.settings import settings
from docling.document_converter import DocumentConverter, FormatOption, PdfFormatOption

warnings.filterwarnings(action="ignore", category=UserWarning, module="pydantic|torch")
warnings.filterwarnings(action="ignore", category=FutureWarning, module="easyocr")

_log = logging.getLogger(__name__)
from rich.console import Console

err_console = Console(stderr=True)


app = typer.Typer(
    name="Docling",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)


def version_callback(value: bool):
    if value:
        docling_version = importlib.metadata.version("docling")
        docling_core_version = importlib.metadata.version("docling-core")
        docling_ibm_models_version = importlib.metadata.version("docling-ibm-models")
        docling_parse_version = importlib.metadata.version("docling-parse")
        platform_str = platform.platform()
        py_impl_version = sys.implementation.cache_tag
        py_lang_version = platform.python_version()
        print(f"Docling version: {docling_version}")
        print(f"Docling Core version: {docling_core_version}")
        print(f"Docling IBM Models version: {docling_ibm_models_version}")
        print(f"Docling Parse version: {docling_parse_version}")
        print(f"Python: {py_impl_version} ({py_lang_version})")
        print(f"Platform: {platform_str}")
        raise typer.Exit()


def export_documents(
    conv_results: Iterable[ConversionResult],
    output_dir: Path,
    export_json: bool,
    export_html: bool,
    export_md: bool,
    export_txt: bool,
    export_doctags: bool,
    image_export_mode: ImageRefMode,
):

    success_count = 0
    failure_count = 0

    for conv_res in conv_results:
        if conv_res.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = conv_res.input.file.stem

            # Export JSON format:
            if export_json:
                fname = output_dir / f"{doc_filename}.json"
                _log.info(f"writing JSON output to {fname}")
                conv_res.document.save_as_json(
                    filename=fname, image_mode=image_export_mode
                )

            # Export HTML format:
            if export_html:
                fname = output_dir / f"{doc_filename}.html"
                _log.info(f"writing HTML output to {fname}")
                conv_res.document.save_as_html(
                    filename=fname, image_mode=image_export_mode
                )

            # Export Text format:
            if export_txt:
                fname = output_dir / f"{doc_filename}.txt"
                _log.info(f"writing TXT output to {fname}")
                conv_res.document.save_as_markdown(
                    filename=fname,
                    strict_text=True,
                    image_mode=ImageRefMode.PLACEHOLDER,
                )

            # Export Markdown format:
            if export_md:
                fname = output_dir / f"{doc_filename}.md"
                _log.info(f"writing Markdown output to {fname}")
                conv_res.document.save_as_markdown(
                    filename=fname, image_mode=image_export_mode
                )

            # Export Document Tags format:
            if export_doctags:
                fname = output_dir / f"{doc_filename}.doctags"
                _log.info(f"writing Doc Tags output to {fname}")
                conv_res.document.save_as_document_tokens(filename=fname)

        else:
            _log.warning(f"Document {conv_res.input.file} failed to convert.")
            failure_count += 1

    _log.info(
        f"Processed {success_count + failure_count} docs, of which {failure_count} failed"
    )


def _split_list(raw: Optional[str]) -> Optional[List[str]]:
    if raw is None:
        return None
    return re.split(r"[;,]", raw)


@app.command(no_args_is_help=True)
def convert(
    input_sources: Annotated[
        List[str],
        typer.Argument(
            ...,
            metavar="source",
            help="PDF files to convert. Can be local file / directory paths or URL.",
        ),
    ],
    from_formats: List[InputFormat] = typer.Option(
        None,
        "--from",
        help="Specify input formats to convert from. Defaults to all formats.",
    ),
    to_formats: List[OutputFormat] = typer.Option(
        None, "--to", help="Specify output formats. Defaults to Markdown."
    ),
    headers: str = typer.Option(
        None,
        "--headers",
        help="Specify http request headers used when fetching url input sources in the form of a JSON string",
    ),
    image_export_mode: Annotated[
        ImageRefMode,
        typer.Option(
            ...,
            help="Image export mode for the document (only in case of JSON, Markdown or HTML). With `placeholder`, only the position of the image is marked in the output. In `embedded` mode, the image is embedded as base64 encoded string. In `referenced` mode, the image is exported in PNG format and referenced from the main exported document.",
        ),
    ] = ImageRefMode.EMBEDDED,
    ocr: Annotated[
        bool,
        typer.Option(
            ..., help="If enabled, the bitmap content will be processed using OCR."
        ),
    ] = True,
    force_ocr: Annotated[
        bool,
        typer.Option(
            ...,
            help="Replace any existing text with OCR generated text over the full content.",
        ),
    ] = False,
    ocr_engine: Annotated[
        OcrEngine, typer.Option(..., help="The OCR engine to use.")
    ] = OcrEngine.EASYOCR,
    ocr_lang: Annotated[
        Optional[str],
        typer.Option(
            ...,
            help="Provide a comma-separated list of languages used by the OCR engine. Note that each OCR engine has different values for the language names.",
        ),
    ] = None,
    pdf_backend: Annotated[
        PdfBackend, typer.Option(..., help="The PDF backend to use.")
    ] = PdfBackend.DLPARSE_V2,
    table_mode: Annotated[
        TableFormerMode,
        typer.Option(..., help="The mode to use in the table structure model."),
    ] = TableFormerMode.FAST,
    enrich_code: Annotated[
        bool,
        typer.Option(..., help="Enable the code enrichment model in the pipeline."),
    ] = False,
    enrich_formula: Annotated[
        bool,
        typer.Option(..., help="Enable the formula enrichment model in the pipeline."),
    ] = False,
    artifacts_path: Annotated[
        Optional[Path],
        typer.Option(..., help="If provided, the location of the model artifacts."),
    ] = None,
    abort_on_error: Annotated[
        bool,
        typer.Option(
            ...,
            "--abort-on-error/--no-abort-on-error",
            help="If enabled, the bitmap content will be processed using OCR.",
        ),
    ] = False,
    output: Annotated[
        Path, typer.Option(..., help="Output directory where results are saved.")
    ] = Path("."),
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Set the verbosity level. -v for info logging, -vv for debug logging.",
        ),
    ] = 0,
    debug_visualize_cells: Annotated[
        bool,
        typer.Option(..., help="Enable debug output which visualizes the PDF cells"),
    ] = False,
    debug_visualize_ocr: Annotated[
        bool,
        typer.Option(..., help="Enable debug output which visualizes the OCR cells"),
    ] = False,
    debug_visualize_layout: Annotated[
        bool,
        typer.Option(
            ..., help="Enable debug output which visualizes the layour clusters"
        ),
    ] = False,
    debug_visualize_tables: Annotated[
        bool,
        typer.Option(..., help="Enable debug output which visualizes the table cells"),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version information.",
        ),
    ] = None,
    document_timeout: Annotated[
        Optional[float],
        typer.Option(
            ...,
            help="The timeout for processing each document, in seconds.",
        ),
    ] = None,
    num_threads: Annotated[int, typer.Option(..., help="Number of threads")] = 4,
    device: Annotated[
        AcceleratorDevice, typer.Option(..., help="Accelerator device")
    ] = AcceleratorDevice.AUTO,
):
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    settings.debug.visualize_cells = debug_visualize_cells
    settings.debug.visualize_layout = debug_visualize_layout
    settings.debug.visualize_tables = debug_visualize_tables
    settings.debug.visualize_ocr = debug_visualize_ocr

    if from_formats is None:
        from_formats = [e for e in InputFormat]

    parsed_headers: Optional[Dict[str, str]] = None
    if headers is not None:
        headers_t = TypeAdapter(Dict[str, str])
        parsed_headers = headers_t.validate_json(headers)

    with tempfile.TemporaryDirectory() as tempdir:
        input_doc_paths: List[Path] = []
        for src in input_sources:
            try:
                # check if we can fetch some remote url
                source = resolve_source_to_path(
                    source=src, headers=parsed_headers, workdir=Path(tempdir)
                )
                input_doc_paths.append(source)
            except FileNotFoundError:
                err_console.print(
                    f"[red]Error: The input file {src} does not exist.[/red]"
                )
                raise typer.Abort()
            except IsADirectoryError:
                # if the input matches to a file or a folder
                try:
                    local_path = TypeAdapter(Path).validate_python(src)
                    if local_path.exists() and local_path.is_dir():
                        for fmt in from_formats:
                            for ext in FormatToExtensions[fmt]:
                                input_doc_paths.extend(
                                    list(local_path.glob(f"**/*.{ext}"))
                                )
                                input_doc_paths.extend(
                                    list(local_path.glob(f"**/*.{ext.upper()}"))
                                )
                    elif local_path.exists():
                        input_doc_paths.append(local_path)
                    else:
                        err_console.print(
                            f"[red]Error: The input file {src} does not exist.[/red]"
                        )
                        raise typer.Abort()
                except Exception as err:
                    err_console.print(f"[red]Error: Cannot read the input {src}.[/red]")
                    _log.info(err)  # will print more details if verbose is activated
                    raise typer.Abort()

        if to_formats is None:
            to_formats = [OutputFormat.MARKDOWN]

        export_json = OutputFormat.JSON in to_formats
        export_html = OutputFormat.HTML in to_formats
        export_md = OutputFormat.MARKDOWN in to_formats
        export_txt = OutputFormat.TEXT in to_formats
        export_doctags = OutputFormat.DOCTAGS in to_formats

        if ocr_engine == OcrEngine.EASYOCR:
            ocr_options: OcrOptions = EasyOcrOptions(force_full_page_ocr=force_ocr)
        elif ocr_engine == OcrEngine.TESSERACT_CLI:
            ocr_options = TesseractCliOcrOptions(force_full_page_ocr=force_ocr)
        elif ocr_engine == OcrEngine.TESSERACT:
            ocr_options = TesseractOcrOptions(force_full_page_ocr=force_ocr)
        elif ocr_engine == OcrEngine.OCRMAC:
            ocr_options = OcrMacOptions(force_full_page_ocr=force_ocr)
        elif ocr_engine == OcrEngine.RAPIDOCR:
            ocr_options = RapidOcrOptions(force_full_page_ocr=force_ocr)
        else:
            raise RuntimeError(f"Unexpected OCR engine type {ocr_engine}")

        ocr_lang_list = _split_list(ocr_lang)
        if ocr_lang_list is not None:
            ocr_options.lang = ocr_lang_list

        accelerator_options = AcceleratorOptions(num_threads=num_threads, device=device)
        pipeline_options = PdfPipelineOptions(
            accelerator_options=accelerator_options,
            do_ocr=ocr,
            ocr_options=ocr_options,
            do_table_structure=True,
            do_code_enrichment=enrich_code,
            do_formula_enrichment=enrich_formula,
            document_timeout=document_timeout,
        )
        pipeline_options.table_structure_options.do_cell_matching = (
            True  # do_cell_matching
        )
        pipeline_options.table_structure_options.mode = table_mode

        if image_export_mode != ImageRefMode.PLACEHOLDER:
            pipeline_options.generate_page_images = True
            pipeline_options.generate_picture_images = (
                True  # FIXME: to be deprecated in verson 3
            )
            pipeline_options.images_scale = 2

        if artifacts_path is not None:
            pipeline_options.artifacts_path = artifacts_path

        if pdf_backend == PdfBackend.DLPARSE_V1:
            backend: Type[PdfDocumentBackend] = DoclingParseDocumentBackend
        elif pdf_backend == PdfBackend.DLPARSE_V2:
            backend = DoclingParseV2DocumentBackend
        elif pdf_backend == PdfBackend.PYPDFIUM2:
            backend = PyPdfiumDocumentBackend
        else:
            raise RuntimeError(f"Unexpected PDF backend type {pdf_backend}")

        pdf_format_option = PdfFormatOption(
            pipeline_options=pipeline_options,
            backend=backend,  # pdf_backend
        )
        format_options: Dict[InputFormat, FormatOption] = {
            InputFormat.PDF: pdf_format_option,
            InputFormat.IMAGE: pdf_format_option,
        }
        doc_converter = DocumentConverter(
            allowed_formats=from_formats,
            format_options=format_options,
        )

        start_time = time.time()

        conv_results = doc_converter.convert_all(
            input_doc_paths, headers=parsed_headers, raises_on_error=abort_on_error
        )

        output.mkdir(parents=True, exist_ok=True)
        export_documents(
            conv_results,
            output_dir=output,
            export_json=export_json,
            export_html=export_html,
            export_md=export_md,
            export_txt=export_txt,
            export_doctags=export_doctags,
            image_export_mode=image_export_mode,
        )

        end_time = time.time() - start_time

    _log.info(f"All documents were converted in {end_time:.2f} seconds.")


click_app = typer.main.get_command(app)

if __name__ == "__main__":
    app()

```
</content>
</file_21>

<file_22>
<path>datamodel/__init__.py</path>
<content>
```python

```
</content>
</file_22>

<file_23>
<path>datamodel/base_models.py</path>
<content>
```python
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from docling_core.types.doc import (
    BoundingBox,
    DocItemLabel,
    NodeItem,
    PictureDataType,
    Size,
    TableCell,
)
from docling_core.types.io import (  # DO ΝΟΤ REMOVE; explicitly exposed from this location
    DocumentStream,
)
from PIL.Image import Image
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from docling.backend.pdf_backend import PdfPageBackend


class ConversionStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    FAILURE = "failure"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"


class InputFormat(str, Enum):
    """A document format supported by document backend parsers."""

    DOCX = "docx"
    PPTX = "pptx"
    HTML = "html"
    XML_PUBMED = "xml_pubmed"
    IMAGE = "image"
    PDF = "pdf"
    ASCIIDOC = "asciidoc"
    MD = "md"
    XLSX = "xlsx"
    XML_USPTO = "xml_uspto"
    JSON_DOCLING = "json_docling"


class OutputFormat(str, Enum):
    MARKDOWN = "md"
    JSON = "json"
    HTML = "html"
    TEXT = "text"
    DOCTAGS = "doctags"


FormatToExtensions: Dict[InputFormat, List[str]] = {
    InputFormat.DOCX: ["docx", "dotx", "docm", "dotm"],
    InputFormat.PPTX: ["pptx", "potx", "ppsx", "pptm", "potm", "ppsm"],
    InputFormat.PDF: ["pdf"],
    InputFormat.MD: ["md"],
    InputFormat.HTML: ["html", "htm", "xhtml"],
    InputFormat.XML_PUBMED: ["xml", "nxml"],
    InputFormat.IMAGE: ["jpg", "jpeg", "png", "tif", "tiff", "bmp"],
    InputFormat.ASCIIDOC: ["adoc", "asciidoc", "asc"],
    InputFormat.XLSX: ["xlsx"],
    InputFormat.XML_USPTO: ["xml", "txt"],
    InputFormat.JSON_DOCLING: ["json"],
}

FormatToMimeType: Dict[InputFormat, List[str]] = {
    InputFormat.DOCX: [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    ],
    InputFormat.PPTX: [
        "application/vnd.openxmlformats-officedocument.presentationml.template",
        "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ],
    InputFormat.HTML: ["text/html", "application/xhtml+xml"],
    InputFormat.XML_PUBMED: ["application/xml"],
    InputFormat.IMAGE: [
        "image/png",
        "image/jpeg",
        "image/tiff",
        "image/gif",
        "image/bmp",
    ],
    InputFormat.PDF: ["application/pdf"],
    InputFormat.ASCIIDOC: ["text/asciidoc"],
    InputFormat.MD: ["text/markdown", "text/x-markdown"],
    InputFormat.XLSX: [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ],
    InputFormat.XML_USPTO: ["application/xml", "text/plain"],
    InputFormat.JSON_DOCLING: ["application/json"],
}

MimeTypeToFormat: dict[str, list[InputFormat]] = {
    mime: [fmt for fmt in FormatToMimeType if mime in FormatToMimeType[fmt]]
    for value in FormatToMimeType.values()
    for mime in value
}


class DocInputType(str, Enum):
    PATH = "path"
    STREAM = "stream"


class DoclingComponentType(str, Enum):
    DOCUMENT_BACKEND = "document_backend"
    MODEL = "model"
    DOC_ASSEMBLER = "doc_assembler"
    USER_INPUT = "user_input"


class ErrorItem(BaseModel):
    component_type: DoclingComponentType
    module_name: str
    error_message: str


class Cell(BaseModel):
    id: int
    text: str
    bbox: BoundingBox


class OcrCell(Cell):
    confidence: float


class Cluster(BaseModel):
    id: int
    label: DocItemLabel
    bbox: BoundingBox
    confidence: float = 1.0
    cells: List[Cell] = []
    children: List["Cluster"] = []  # Add child cluster support


class BasePageElement(BaseModel):
    label: DocItemLabel
    id: int
    page_no: int
    cluster: Cluster
    text: Optional[str] = None


class LayoutPrediction(BaseModel):
    clusters: List[Cluster] = []


class ContainerElement(
    BasePageElement
):  # Used for Form and Key-Value-Regions, only for typing.
    pass


class Table(BasePageElement):
    otsl_seq: List[str]
    num_rows: int = 0
    num_cols: int = 0
    table_cells: List[TableCell]


class TableStructurePrediction(BaseModel):
    table_map: Dict[int, Table] = {}


class TextElement(BasePageElement):
    text: str


class FigureElement(BasePageElement):
    annotations: List[PictureDataType] = []
    provenance: Optional[str] = None
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None


class FigureClassificationPrediction(BaseModel):
    figure_count: int = 0
    figure_map: Dict[int, FigureElement] = {}


class EquationPrediction(BaseModel):
    equation_count: int = 0
    equation_map: Dict[int, TextElement] = {}


class PagePredictions(BaseModel):
    layout: Optional[LayoutPrediction] = None
    tablestructure: Optional[TableStructurePrediction] = None
    figures_classification: Optional[FigureClassificationPrediction] = None
    equations_prediction: Optional[EquationPrediction] = None


PageElement = Union[TextElement, Table, FigureElement, ContainerElement]


class AssembledUnit(BaseModel):
    elements: List[PageElement] = []
    body: List[PageElement] = []
    headers: List[PageElement] = []


class ItemAndImageEnrichmentElement(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    item: NodeItem
    image: Image


class Page(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_no: int
    # page_hash: Optional[str] = None
    size: Optional[Size] = None
    cells: List[Cell] = []
    predictions: PagePredictions = PagePredictions()
    assembled: Optional[AssembledUnit] = None

    _backend: Optional["PdfPageBackend"] = (
        None  # Internal PDF backend. By default it is cleared during assembling.
    )
    _default_image_scale: float = 1.0  # Default image scale for external usage.
    _image_cache: Dict[float, Image] = (
        {}
    )  # Cache of images in different scales. By default it is cleared during assembling.

    def get_image(
        self, scale: float = 1.0, cropbox: Optional[BoundingBox] = None
    ) -> Optional[Image]:
        if self._backend is None:
            return self._image_cache.get(scale, None)

        if not scale in self._image_cache:
            if cropbox is None:
                self._image_cache[scale] = self._backend.get_page_image(scale=scale)
            else:
                return self._backend.get_page_image(scale=scale, cropbox=cropbox)

        if cropbox is None:
            return self._image_cache[scale]
        else:
            page_im = self._image_cache[scale]
            assert self.size is not None
            return page_im.crop(
                cropbox.to_top_left_origin(page_height=self.size.height)
                .scaled(scale=scale)
                .as_tuple()
            )

    @property
    def image(self) -> Optional[Image]:
        return self.get_image(scale=self._default_image_scale)

```
</content>
</file_23>

<file_24>
<path>datamodel/document.py</path>
<content>
```python
import logging
import re
from enum import Enum
from io import BytesIO
from pathlib import Path, PurePath
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Set,
    Type,
    Union,
)

import filetype
from docling_core.types.doc import (
    DocItem,
    DocItemLabel,
    DoclingDocument,
    PictureItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
)
from docling_core.types.doc.document import ListItem
from docling_core.types.legacy_doc.base import (
    BaseText,
    Figure,
    GlmTableCell,
    PageDimensions,
    PageReference,
    Prov,
    Ref,
)
from docling_core.types.legacy_doc.base import Table as DsSchemaTable
from docling_core.types.legacy_doc.base import TableCell
from docling_core.types.legacy_doc.document import (
    CCSDocumentDescription as DsDocumentDescription,
)
from docling_core.types.legacy_doc.document import CCSFileInfoObject as DsFileInfoObject
from docling_core.types.legacy_doc.document import ExportedCCSDocument as DsDocument
from docling_core.utils.file import resolve_source_to_stream
from docling_core.utils.legacy import docling_document_to_legacy
from pydantic import BaseModel
from typing_extensions import deprecated

from docling.backend.abstract_backend import (
    AbstractDocumentBackend,
    PaginatedDocumentBackend,
)
from docling.datamodel.base_models import (
    AssembledUnit,
    ConversionStatus,
    DocumentStream,
    ErrorItem,
    FormatToExtensions,
    FormatToMimeType,
    InputFormat,
    MimeTypeToFormat,
    Page,
)
from docling.datamodel.settings import DocumentLimits
from docling.utils.profiling import ProfilingItem
from docling.utils.utils import create_file_hash, create_hash

if TYPE_CHECKING:
    from docling.document_converter import FormatOption

_log = logging.getLogger(__name__)

layout_label_to_ds_type = {
    DocItemLabel.TITLE: "title",
    DocItemLabel.DOCUMENT_INDEX: "table",
    DocItemLabel.SECTION_HEADER: "subtitle-level-1",
    DocItemLabel.CHECKBOX_SELECTED: "checkbox-selected",
    DocItemLabel.CHECKBOX_UNSELECTED: "checkbox-unselected",
    DocItemLabel.CAPTION: "caption",
    DocItemLabel.PAGE_HEADER: "page-header",
    DocItemLabel.PAGE_FOOTER: "page-footer",
    DocItemLabel.FOOTNOTE: "footnote",
    DocItemLabel.TABLE: "table",
    DocItemLabel.FORMULA: "equation",
    DocItemLabel.LIST_ITEM: "paragraph",
    DocItemLabel.CODE: "paragraph",
    DocItemLabel.PICTURE: "figure",
    DocItemLabel.TEXT: "paragraph",
    DocItemLabel.PARAGRAPH: "paragraph",
    DocItemLabel.FORM: DocItemLabel.FORM.value,
    DocItemLabel.KEY_VALUE_REGION: DocItemLabel.KEY_VALUE_REGION.value,
}

_EMPTY_DOCLING_DOC = DoclingDocument(name="dummy")


class InputDocument(BaseModel):
    file: PurePath
    document_hash: str  # = None
    valid: bool = True
    limits: DocumentLimits = DocumentLimits()
    format: InputFormat  # = None

    filesize: Optional[int] = None
    page_count: int = 0

    _backend: AbstractDocumentBackend  # Internal PDF backend used

    def __init__(
        self,
        path_or_stream: Union[BytesIO, Path],
        format: InputFormat,
        backend: Type[AbstractDocumentBackend],
        filename: Optional[str] = None,
        limits: Optional[DocumentLimits] = None,
    ):
        super().__init__(
            file="", document_hash="", format=InputFormat.PDF
        )  # initialize with dummy values

        self.limits = limits or DocumentLimits()
        self.format = format

        try:
            if isinstance(path_or_stream, Path):
                self.file = path_or_stream
                self.filesize = path_or_stream.stat().st_size
                if self.filesize > self.limits.max_file_size:
                    self.valid = False
                else:
                    self.document_hash = create_file_hash(path_or_stream)
                    self._init_doc(backend, path_or_stream)

            elif isinstance(path_or_stream, BytesIO):
                assert (
                    filename is not None
                ), "Can't construct InputDocument from stream without providing filename arg."
                self.file = PurePath(filename)
                self.filesize = path_or_stream.getbuffer().nbytes

                if self.filesize > self.limits.max_file_size:
                    self.valid = False
                else:
                    self.document_hash = create_file_hash(path_or_stream)
                    self._init_doc(backend, path_or_stream)
            else:
                raise RuntimeError(
                    f"Unexpected type path_or_stream: {type(path_or_stream)}"
                )

            # For paginated backends, check if the maximum page count is exceeded.
            if self.valid and self._backend.is_valid():
                if self._backend.supports_pagination() and isinstance(
                    self._backend, PaginatedDocumentBackend
                ):
                    self.page_count = self._backend.page_count()
                    if not self.page_count <= self.limits.max_num_pages:
                        self.valid = False
                    elif self.page_count < self.limits.page_range[0]:
                        self.valid = False

        except (FileNotFoundError, OSError) as e:
            self.valid = False
            _log.exception(
                f"File {self.file.name} not found or cannot be opened.", exc_info=e
            )
            # raise
        except RuntimeError as e:
            self.valid = False
            _log.exception(
                f"An unexpected error occurred while opening the document {self.file.name}",
                exc_info=e,
            )
            # raise

    def _init_doc(
        self,
        backend: Type[AbstractDocumentBackend],
        path_or_stream: Union[BytesIO, Path],
    ) -> None:
        self._backend = backend(self, path_or_stream=path_or_stream)
        if not self._backend.is_valid():
            self.valid = False


class DocumentFormat(str, Enum):
    V2 = "v2"
    V1 = "v1"


class ConversionResult(BaseModel):
    input: InputDocument

    status: ConversionStatus = ConversionStatus.PENDING  # failure, success
    errors: List[ErrorItem] = []  # structure to keep errors

    pages: List[Page] = []
    assembled: AssembledUnit = AssembledUnit()
    timings: Dict[str, ProfilingItem] = {}

    document: DoclingDocument = _EMPTY_DOCLING_DOC

    @property
    @deprecated("Use document instead.")
    def legacy_document(self):
        return docling_document_to_legacy(self.document)


class _DummyBackend(AbstractDocumentBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_valid(self) -> bool:
        return False

    @classmethod
    def supported_formats(cls) -> Set[InputFormat]:
        return set()

    @classmethod
    def supports_pagination(cls) -> bool:
        return False

    def unload(self):
        return super().unload()


class _DocumentConversionInput(BaseModel):

    path_or_stream_iterator: Iterable[Union[Path, str, DocumentStream]]
    headers: Optional[Dict[str, str]] = None
    limits: Optional[DocumentLimits] = DocumentLimits()

    def docs(
        self, format_options: Dict[InputFormat, "FormatOption"]
    ) -> Iterable[InputDocument]:
        for item in self.path_or_stream_iterator:
            obj = (
                resolve_source_to_stream(item, self.headers)
                if isinstance(item, str)
                else item
            )
            format = self._guess_format(obj)
            backend: Type[AbstractDocumentBackend]
            if format not in format_options.keys():
                _log.error(
                    f"Input document {obj.name} does not match any allowed format."
                )
                backend = _DummyBackend
            else:
                backend = format_options[format].backend

            if isinstance(obj, Path):
                yield InputDocument(
                    path_or_stream=obj,
                    format=format,  # type: ignore[arg-type]
                    filename=obj.name,
                    limits=self.limits,
                    backend=backend,
                )
            elif isinstance(obj, DocumentStream):
                yield InputDocument(
                    path_or_stream=obj.stream,
                    format=format,  # type: ignore[arg-type]
                    filename=obj.name,
                    limits=self.limits,
                    backend=backend,
                )
            else:
                raise RuntimeError(f"Unexpected obj type in iterator: {type(obj)}")

    def _guess_format(self, obj: Union[Path, DocumentStream]) -> Optional[InputFormat]:
        content = b""  # empty binary blob
        formats: list[InputFormat] = []

        if isinstance(obj, Path):
            mime = filetype.guess_mime(str(obj))
            if mime is None:
                ext = obj.suffix[1:]
                mime = _DocumentConversionInput._mime_from_extension(ext)
            if mime is None:  # must guess from
                with obj.open("rb") as f:
                    content = f.read(1024)  # Read first 1KB

        elif isinstance(obj, DocumentStream):
            content = obj.stream.read(8192)
            obj.stream.seek(0)
            mime = filetype.guess_mime(content)
            if mime is None:
                ext = (
                    obj.name.rsplit(".", 1)[-1]
                    if ("." in obj.name and not obj.name.startswith("."))
                    else ""
                )
                mime = _DocumentConversionInput._mime_from_extension(ext)

        mime = mime or _DocumentConversionInput._detect_html_xhtml(content)
        mime = mime or "text/plain"
        formats = MimeTypeToFormat.get(mime, [])
        if formats:
            if len(formats) == 1 and mime not in ("text/plain"):
                return formats[0]
            else:  # ambiguity in formats
                return _DocumentConversionInput._guess_from_content(
                    content, mime, formats
                )
        else:
            return None

    @staticmethod
    def _guess_from_content(
        content: bytes, mime: str, formats: list[InputFormat]
    ) -> Optional[InputFormat]:
        """Guess the input format of a document by checking part of its content."""
        input_format: Optional[InputFormat] = None
        content_str = content.decode("utf-8")

        if mime == "application/xml":
            match_doctype = re.search(r"<!DOCTYPE [^>]+>", content_str)
            if match_doctype:
                xml_doctype = match_doctype.group()
                if InputFormat.XML_USPTO in formats and any(
                    item in xml_doctype
                    for item in (
                        "us-patent-application-v4",
                        "us-patent-grant-v4",
                        "us-grant-025",
                        "patent-application-publication",
                    )
                ):
                    input_format = InputFormat.XML_USPTO

                if (
                    InputFormat.XML_PUBMED in formats
                    and "/NLM//DTD JATS" in xml_doctype
                ):
                    input_format = InputFormat.XML_PUBMED

        elif mime == "text/plain":
            if InputFormat.XML_USPTO in formats and content_str.startswith("PATN\r\n"):
                input_format = InputFormat.XML_USPTO

        return input_format

    @staticmethod
    def _mime_from_extension(ext):
        mime = None
        if ext in FormatToExtensions[InputFormat.ASCIIDOC]:
            mime = FormatToMimeType[InputFormat.ASCIIDOC][0]
        elif ext in FormatToExtensions[InputFormat.HTML]:
            mime = FormatToMimeType[InputFormat.HTML][0]
        elif ext in FormatToExtensions[InputFormat.MD]:
            mime = FormatToMimeType[InputFormat.MD][0]
        elif ext in FormatToExtensions[InputFormat.JSON_DOCLING]:
            mime = FormatToMimeType[InputFormat.JSON_DOCLING][0]
        elif ext in FormatToExtensions[InputFormat.PDF]:
            mime = FormatToMimeType[InputFormat.PDF][0]
        return mime

    @staticmethod
    def _detect_html_xhtml(
        content: bytes,
    ) -> Optional[Literal["application/xhtml+xml", "application/xml", "text/html"]]:
        """Guess the mime type of an XHTML, HTML, or XML file from its content.

        Args:
            content: A short piece of a document from its beginning.

        Returns:
            The mime type of an XHTML, HTML, or XML file, or None if the content does
              not match any of these formats.
        """
        content_str = content.decode("ascii", errors="ignore").lower()
        # Remove XML comments
        content_str = re.sub(r"<!--(.*?)-->", "", content_str, flags=re.DOTALL)
        content_str = content_str.lstrip()

        if re.match(r"<\?xml", content_str):
            if "xhtml" in content_str[:1000]:
                return "application/xhtml+xml"
            else:
                return "application/xml"

        if re.match(r"<!doctype\s+html|<html|<head|<body", content_str):
            return "text/html"

        p = re.compile(
            r"<!doctype\s+(?P<root>[a-zA-Z_:][a-zA-Z0-9_:.-]*)\s+.*>\s*<(?P=root)\b"
        )
        if p.search(content_str):
            return "application/xml"

        return None

```
</content>
</file_24>

<file_25>
<path>datamodel/pipeline_options.py</path>
<content>
```python
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_log = logging.getLogger(__name__)


class AcceleratorDevice(str, Enum):
    """Devices to run model inference"""

    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class AcceleratorOptions(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DOCLING_", env_nested_delimiter="_", populate_by_name=True
    )

    num_threads: int = 4
    device: AcceleratorDevice = AcceleratorDevice.AUTO

    @model_validator(mode="before")
    @classmethod
    def check_alternative_envvars(cls, data: Any) -> Any:
        r"""
        Set num_threads from the "alternative" envvar OMP_NUM_THREADS.
        The alternative envvar is used only if it is valid and the regular envvar is not set.

        Notice: The standard pydantic settings mechanism with parameter "aliases" does not provide
        the same functionality. In case the alias envvar is set and the user tries to override the
        parameter in settings initialization, Pydantic treats the parameter provided in __init__()
        as an extra input instead of simply overwriting the evvar value for that parameter.
        """
        if isinstance(data, dict):
            input_num_threads = data.get("num_threads")

            # Check if to set the num_threads from the alternative envvar
            if input_num_threads is None:
                docling_num_threads = os.getenv("DOCLING_NUM_THREADS")
                omp_num_threads = os.getenv("OMP_NUM_THREADS")
                if docling_num_threads is None and omp_num_threads is not None:
                    try:
                        data["num_threads"] = int(omp_num_threads)
                    except ValueError:
                        _log.error(
                            "Ignoring misformatted envvar OMP_NUM_THREADS '%s'",
                            omp_num_threads,
                        )
        return data


class TableFormerMode(str, Enum):
    """Modes for the TableFormer model."""

    FAST = "fast"
    ACCURATE = "accurate"


class TableStructureOptions(BaseModel):
    """Options for the table structure."""

    do_cell_matching: bool = (
        True
        # True:  Matches predictions back to PDF cells. Can break table output if PDF cells
        #        are merged across table columns.
        # False: Let table structure model define the text cells, ignore PDF cells.
    )
    mode: TableFormerMode = TableFormerMode.FAST


class OcrOptions(BaseModel):
    """OCR options."""

    kind: str
    lang: List[str]
    force_full_page_ocr: bool = False  # If enabled a full page OCR is always applied
    bitmap_area_threshold: float = (
        0.05  # percentage of the area for a bitmap to processed with OCR
    )


class RapidOcrOptions(OcrOptions):
    """Options for the RapidOCR engine."""

    kind: Literal["rapidocr"] = "rapidocr"

    # English and chinese are the most commly used models and have been tested with RapidOCR.
    lang: List[str] = [
        "english",
        "chinese",
    ]  # However, language as a parameter is not supported by rapidocr yet and hence changing this options doesn't affect anything.
    # For more details on supported languages by RapidOCR visit https://rapidai.github.io/RapidOCRDocs/blog/2022/09/28/%E6%94%AF%E6%8C%81%E8%AF%86%E5%88%AB%E8%AF%AD%E8%A8%80/

    # For more details on the following options visit https://rapidai.github.io/RapidOCRDocs/install_usage/api/RapidOCR/
    text_score: float = 0.5  # same default as rapidocr

    use_det: Optional[bool] = None  # same default as rapidocr
    use_cls: Optional[bool] = None  # same default as rapidocr
    use_rec: Optional[bool] = None  # same default as rapidocr

    # class Device(Enum):
    #     CPU = "CPU"
    #     CUDA = "CUDA"
    #     DIRECTML = "DIRECTML"
    #     AUTO = "AUTO"

    # device: Device = Device.AUTO  # Default value is AUTO

    print_verbose: bool = False  # same default as rapidocr

    det_model_path: Optional[str] = None  # same default as rapidocr
    cls_model_path: Optional[str] = None  # same default as rapidocr
    rec_model_path: Optional[str] = None  # same default as rapidocr
    rec_keys_path: Optional[str] = None  # same default as rapidocr

    model_config = ConfigDict(
        extra="forbid",
    )


class EasyOcrOptions(OcrOptions):
    """Options for the EasyOCR engine."""

    kind: Literal["easyocr"] = "easyocr"
    lang: List[str] = ["fr", "de", "es", "en"]

    use_gpu: Optional[bool] = None

    confidence_threshold: float = 0.5

    model_storage_directory: Optional[str] = None
    recog_network: Optional[str] = "standard"
    download_enabled: bool = True

    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
    )


class TesseractCliOcrOptions(OcrOptions):
    """Options for the TesseractCli engine."""

    kind: Literal["tesseract"] = "tesseract"
    lang: List[str] = ["fra", "deu", "spa", "eng"]
    tesseract_cmd: str = "tesseract"
    path: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
    )


class TesseractOcrOptions(OcrOptions):
    """Options for the Tesseract engine."""

    kind: Literal["tesserocr"] = "tesserocr"
    lang: List[str] = ["fra", "deu", "spa", "eng"]
    path: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
    )


class OcrMacOptions(OcrOptions):
    """Options for the Mac OCR engine."""

    kind: Literal["ocrmac"] = "ocrmac"
    lang: List[str] = ["fr-FR", "de-DE", "es-ES", "en-US"]
    recognition: str = "accurate"
    framework: str = "vision"

    model_config = ConfigDict(
        extra="forbid",
    )


# Define an enum for the backend options
class PdfBackend(str, Enum):
    """Enum of valid PDF backends."""

    PYPDFIUM2 = "pypdfium2"
    DLPARSE_V1 = "dlparse_v1"
    DLPARSE_V2 = "dlparse_v2"


# Define an enum for the ocr engines
class OcrEngine(str, Enum):
    """Enum of valid OCR engines."""

    EASYOCR = "easyocr"
    TESSERACT_CLI = "tesseract_cli"
    TESSERACT = "tesseract"
    OCRMAC = "ocrmac"
    RAPIDOCR = "rapidocr"


class PipelineOptions(BaseModel):
    """Base pipeline options."""

    create_legacy_output: bool = (
        True  # This default will be set to False on a future version of docling
    )
    document_timeout: Optional[float] = None
    accelerator_options: AcceleratorOptions = AcceleratorOptions()


class PdfPipelineOptions(PipelineOptions):
    """Options for the PDF pipeline."""

    artifacts_path: Optional[Union[Path, str]] = None
    do_table_structure: bool = True  # True: perform table structure extraction
    do_ocr: bool = True  # True: perform OCR, replace programmatic PDF text
    do_code_enrichment: bool = False  # True: perform code OCR
    do_formula_enrichment: bool = False  # True: perform formula OCR, return Latex code
    do_picture_classification: bool = False  # True: classify pictures in documents

    table_structure_options: TableStructureOptions = TableStructureOptions()
    ocr_options: Union[
        EasyOcrOptions,
        TesseractCliOcrOptions,
        TesseractOcrOptions,
        OcrMacOptions,
        RapidOcrOptions,
    ] = Field(EasyOcrOptions(), discriminator="kind")

    images_scale: float = 1.0
    generate_page_images: bool = False
    generate_picture_images: bool = False
    generate_table_images: bool = Field(
        default=False,
        deprecated=(
            "Field `generate_table_images` is deprecated. "
            "To obtain table images, set `PdfPipelineOptions.generate_page_images = True` "
            "before conversion and then use the `TableItem.get_image` function."
        ),
    )

```
</content>
</file_25>

<file_26>
<path>datamodel/settings.py</path>
<content>
```python
import sys
from pathlib import Path
from typing import Annotated, Tuple

from pydantic import BaseModel, PlainValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _validate_page_range(v: Tuple[int, int]) -> Tuple[int, int]:
    if v[0] < 1 or v[1] < v[0]:
        raise ValueError(
            "Invalid page range: start must be ≥ 1 and end must be ≥ start."
        )
    return v


PageRange = Annotated[Tuple[int, int], PlainValidator(_validate_page_range)]

DEFAULT_PAGE_RANGE: PageRange = (1, sys.maxsize)


class DocumentLimits(BaseModel):
    max_num_pages: int = sys.maxsize
    max_file_size: int = sys.maxsize
    page_range: PageRange = DEFAULT_PAGE_RANGE


class BatchConcurrencySettings(BaseModel):
    doc_batch_size: int = 2
    doc_batch_concurrency: int = 2
    page_batch_size: int = 4
    page_batch_concurrency: int = 2
    elements_batch_size: int = 16

    # doc_batch_size: int = 1
    # doc_batch_concurrency: int = 1
    # page_batch_size: int = 1
    # page_batch_concurrency: int = 1

    # model_concurrency: int = 2

    # To force models into single core: export OMP_NUM_THREADS=1


class DebugSettings(BaseModel):
    visualize_cells: bool = False
    visualize_ocr: bool = False
    visualize_layout: bool = False
    visualize_raw_layout: bool = False
    visualize_tables: bool = False

    profile_pipeline_timings: bool = False

    # Path used to output debug information.
    debug_output_path: str = str(Path.cwd() / "debug")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCLING_", env_nested_delimiter="_")

    perf: BatchConcurrencySettings
    debug: DebugSettings


settings = AppSettings(perf=BatchConcurrencySettings(), debug=DebugSettings())

```
</content>
</file_26>

<file_27>
<path>document_converter.py</path>
<content>
```python
import logging
import math
import sys
import time
from functools import partial
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Type, Union

from pydantic import BaseModel, ConfigDict, model_validator, validate_call

from docling.backend.abstract_backend import AbstractDocumentBackend
from docling.backend.asciidoc_backend import AsciiDocBackend
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
from docling.backend.html_backend import HTMLDocumentBackend
from docling.backend.json.docling_json_backend import DoclingJSONBackend
from docling.backend.md_backend import MarkdownDocumentBackend
from docling.backend.msexcel_backend import MsExcelDocumentBackend
from docling.backend.mspowerpoint_backend import MsPowerpointDocumentBackend
from docling.backend.msword_backend import MsWordDocumentBackend
from docling.backend.xml.pubmed_backend import PubMedDocumentBackend
from docling.backend.xml.uspto_backend import PatentUsptoDocumentBackend
from docling.datamodel.base_models import (
    ConversionStatus,
    DoclingComponentType,
    DocumentStream,
    ErrorItem,
    InputFormat,
)
from docling.datamodel.document import (
    ConversionResult,
    InputDocument,
    _DocumentConversionInput,
)
from docling.datamodel.pipeline_options import PipelineOptions
from docling.datamodel.settings import (
    DEFAULT_PAGE_RANGE,
    DocumentLimits,
    PageRange,
    settings,
)
from docling.exceptions import ConversionError
from docling.pipeline.base_pipeline import BasePipeline
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.utils.utils import chunkify

_log = logging.getLogger(__name__)


class FormatOption(BaseModel):
    pipeline_cls: Type[BasePipeline]
    pipeline_options: Optional[PipelineOptions] = None
    backend: Type[AbstractDocumentBackend]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def set_optional_field_default(self) -> "FormatOption":
        if self.pipeline_options is None:
            self.pipeline_options = self.pipeline_cls.get_default_options()
        return self


class ExcelFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = MsExcelDocumentBackend


class WordFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = MsWordDocumentBackend


class PowerpointFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = MsPowerpointDocumentBackend


class MarkdownFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = MarkdownDocumentBackend


class AsciiDocFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = AsciiDocBackend


class HTMLFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = HTMLDocumentBackend


class PatentUsptoFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[PatentUsptoDocumentBackend] = PatentUsptoDocumentBackend


class XMLPubMedFormatOption(FormatOption):
    pipeline_cls: Type = SimplePipeline
    backend: Type[AbstractDocumentBackend] = PubMedDocumentBackend


class ImageFormatOption(FormatOption):
    pipeline_cls: Type = StandardPdfPipeline
    backend: Type[AbstractDocumentBackend] = DoclingParseV2DocumentBackend


class PdfFormatOption(FormatOption):
    pipeline_cls: Type = StandardPdfPipeline
    backend: Type[AbstractDocumentBackend] = DoclingParseV2DocumentBackend


def _get_default_option(format: InputFormat) -> FormatOption:
    format_to_default_options = {
        InputFormat.XLSX: FormatOption(
            pipeline_cls=SimplePipeline, backend=MsExcelDocumentBackend
        ),
        InputFormat.DOCX: FormatOption(
            pipeline_cls=SimplePipeline, backend=MsWordDocumentBackend
        ),
        InputFormat.PPTX: FormatOption(
            pipeline_cls=SimplePipeline, backend=MsPowerpointDocumentBackend
        ),
        InputFormat.MD: FormatOption(
            pipeline_cls=SimplePipeline, backend=MarkdownDocumentBackend
        ),
        InputFormat.ASCIIDOC: FormatOption(
            pipeline_cls=SimplePipeline, backend=AsciiDocBackend
        ),
        InputFormat.HTML: FormatOption(
            pipeline_cls=SimplePipeline, backend=HTMLDocumentBackend
        ),
        InputFormat.XML_USPTO: FormatOption(
            pipeline_cls=SimplePipeline, backend=PatentUsptoDocumentBackend
        ),
        InputFormat.XML_PUBMED: FormatOption(
            pipeline_cls=SimplePipeline, backend=PubMedDocumentBackend
        ),
        InputFormat.IMAGE: FormatOption(
            pipeline_cls=StandardPdfPipeline, backend=DoclingParseV2DocumentBackend
        ),
        InputFormat.PDF: FormatOption(
            pipeline_cls=StandardPdfPipeline, backend=DoclingParseV2DocumentBackend
        ),
        InputFormat.JSON_DOCLING: FormatOption(
            pipeline_cls=SimplePipeline, backend=DoclingJSONBackend
        ),
    }
    if (options := format_to_default_options.get(format)) is not None:
        return options
    else:
        raise RuntimeError(f"No default options configured for {format}")


class DocumentConverter:
    _default_download_filename = "file"

    def __init__(
        self,
        allowed_formats: Optional[List[InputFormat]] = None,
        format_options: Optional[Dict[InputFormat, FormatOption]] = None,
    ):
        self.allowed_formats = (
            allowed_formats if allowed_formats is not None else [e for e in InputFormat]
        )
        self.format_to_options = {
            format: (
                _get_default_option(format=format)
                if (custom_option := (format_options or {}).get(format)) is None
                else custom_option
            )
            for format in self.allowed_formats
        }
        self.initialized_pipelines: Dict[Type[BasePipeline], BasePipeline] = {}

    def initialize_pipeline(self, format: InputFormat):
        """Initialize the conversion pipeline for the selected format."""
        pipeline = self._get_pipeline(doc_format=format)
        if pipeline is None:
            raise ConversionError(
                f"No pipeline could be initialized for format {format}"
            )

    @validate_call(config=ConfigDict(strict=True))
    def convert(
        self,
        source: Union[Path, str, DocumentStream],  # TODO review naming
        headers: Optional[Dict[str, str]] = None,
        raises_on_error: bool = True,
        max_num_pages: int = sys.maxsize,
        max_file_size: int = sys.maxsize,
        page_range: PageRange = DEFAULT_PAGE_RANGE,
    ) -> ConversionResult:
        all_res = self.convert_all(
            source=[source],
            raises_on_error=raises_on_error,
            max_num_pages=max_num_pages,
            max_file_size=max_file_size,
            headers=headers,
            page_range=page_range,
        )
        return next(all_res)

    @validate_call(config=ConfigDict(strict=True))
    def convert_all(
        self,
        source: Iterable[Union[Path, str, DocumentStream]],  # TODO review naming
        headers: Optional[Dict[str, str]] = None,
        raises_on_error: bool = True,  # True: raises on first conversion error; False: does not raise on conv error
        max_num_pages: int = sys.maxsize,
        max_file_size: int = sys.maxsize,
        page_range: PageRange = DEFAULT_PAGE_RANGE,
    ) -> Iterator[ConversionResult]:
        limits = DocumentLimits(
            max_num_pages=max_num_pages,
            max_file_size=max_file_size,
            page_range=page_range,
        )
        conv_input = _DocumentConversionInput(
            path_or_stream_iterator=source, limits=limits, headers=headers
        )
        conv_res_iter = self._convert(conv_input, raises_on_error=raises_on_error)

        had_result = False
        for conv_res in conv_res_iter:
            had_result = True
            if raises_on_error and conv_res.status not in {
                ConversionStatus.SUCCESS,
                ConversionStatus.PARTIAL_SUCCESS,
            }:
                raise ConversionError(
                    f"Conversion failed for: {conv_res.input.file} with status: {conv_res.status}"
                )
            else:
                yield conv_res

        if not had_result and raises_on_error:
            raise ConversionError(
                f"Conversion failed because the provided file has no recognizable format or it wasn't in the list of allowed formats."
            )

    def _convert(
        self, conv_input: _DocumentConversionInput, raises_on_error: bool
    ) -> Iterator[ConversionResult]:
        start_time = time.monotonic()

        for input_batch in chunkify(
            conv_input.docs(self.format_to_options),
            settings.perf.doc_batch_size,  # pass format_options
        ):
            _log.info(f"Going to convert document batch...")

            # parallel processing only within input_batch
            # with ThreadPoolExecutor(
            #    max_workers=settings.perf.doc_batch_concurrency
            # ) as pool:
            #   yield from pool.map(self.process_document, input_batch)
            # Note: PDF backends are not thread-safe, thread pool usage was disabled.

            for item in map(
                partial(self._process_document, raises_on_error=raises_on_error),
                input_batch,
            ):
                elapsed = time.monotonic() - start_time
                start_time = time.monotonic()
                _log.info(
                    f"Finished converting document {item.input.file.name} in {elapsed:.2f} sec."
                )
                yield item

    def _get_pipeline(self, doc_format: InputFormat) -> Optional[BasePipeline]:
        fopt = self.format_to_options.get(doc_format)

        if fopt is None:
            return None
        else:
            pipeline_class = fopt.pipeline_cls
            pipeline_options = fopt.pipeline_options

        if pipeline_options is None:
            return None
        # TODO this will ignore if different options have been defined for the same pipeline class.
        if (
            pipeline_class not in self.initialized_pipelines
            or self.initialized_pipelines[pipeline_class].pipeline_options
            != pipeline_options
        ):
            self.initialized_pipelines[pipeline_class] = pipeline_class(
                pipeline_options=pipeline_options
            )
        return self.initialized_pipelines[pipeline_class]

    def _process_document(
        self, in_doc: InputDocument, raises_on_error: bool
    ) -> ConversionResult:

        valid = (
            self.allowed_formats is not None and in_doc.format in self.allowed_formats
        )
        if valid:
            conv_res = self._execute_pipeline(in_doc, raises_on_error=raises_on_error)
        else:
            error_message = f"File format not allowed: {in_doc.file}"
            if raises_on_error:
                raise ConversionError(error_message)
            else:
                error_item = ErrorItem(
                    component_type=DoclingComponentType.USER_INPUT,
                    module_name="",
                    error_message=error_message,
                )
                conv_res = ConversionResult(
                    input=in_doc, status=ConversionStatus.SKIPPED, errors=[error_item]
                )

        return conv_res

    def _execute_pipeline(
        self, in_doc: InputDocument, raises_on_error: bool
    ) -> ConversionResult:
        if in_doc.valid:
            pipeline = self._get_pipeline(in_doc.format)
            if pipeline is not None:
                conv_res = pipeline.execute(in_doc, raises_on_error=raises_on_error)
            else:
                if raises_on_error:
                    raise ConversionError(
                        f"No pipeline could be initialized for {in_doc.file}."
                    )
                else:
                    conv_res = ConversionResult(
                        input=in_doc,
                        status=ConversionStatus.FAILURE,
                    )
        else:
            if raises_on_error:
                raise ConversionError(f"Input document {in_doc.file} is not valid.")

            else:
                # invalid doc or not of desired format
                conv_res = ConversionResult(
                    input=in_doc,
                    status=ConversionStatus.FAILURE,
                )
                # TODO add error log why it failed.

        return conv_res

```
</content>
</file_27>

<file_28>
<path>exceptions.py</path>
<content>
```python
class BaseError(RuntimeError):
    pass


class ConversionError(BaseError):
    pass

```
</content>
</file_28>

<file_29>
<path>models/__init__.py</path>
<content>
```python

```
</content>
</file_29>

<file_30>
<path>models/base_model.py</path>
<content>
```python
from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, Optional

from docling_core.types.doc import BoundingBox, DoclingDocument, NodeItem, TextItem
from typing_extensions import TypeVar

from docling.datamodel.base_models import ItemAndImageEnrichmentElement, Page
from docling.datamodel.document import ConversionResult


class BasePageModel(ABC):
    @abstractmethod
    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        pass


EnrichElementT = TypeVar("EnrichElementT", default=NodeItem)


class GenericEnrichmentModel(ABC, Generic[EnrichElementT]):

    @abstractmethod
    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        pass

    @abstractmethod
    def prepare_element(
        self, conv_res: ConversionResult, element: NodeItem
    ) -> Optional[EnrichElementT]:
        pass

    @abstractmethod
    def __call__(
        self, doc: DoclingDocument, element_batch: Iterable[EnrichElementT]
    ) -> Iterable[NodeItem]:
        pass


class BaseEnrichmentModel(GenericEnrichmentModel[NodeItem]):

    def prepare_element(
        self, conv_res: ConversionResult, element: NodeItem
    ) -> Optional[NodeItem]:
        if self.is_processable(doc=conv_res.document, element=element):
            return element
        return None


class BaseItemAndImageEnrichmentModel(
    GenericEnrichmentModel[ItemAndImageEnrichmentElement]
):

    images_scale: float
    expansion_factor: float = 0.0

    def prepare_element(
        self, conv_res: ConversionResult, element: NodeItem
    ) -> Optional[ItemAndImageEnrichmentElement]:
        if not self.is_processable(doc=conv_res.document, element=element):
            return None

        assert isinstance(element, TextItem)
        element_prov = element.prov[0]

        bbox = element_prov.bbox
        width = bbox.r - bbox.l
        height = bbox.t - bbox.b

        # TODO: move to a utility in the BoundingBox class
        expanded_bbox = BoundingBox(
            l=bbox.l - width * self.expansion_factor,
            t=bbox.t + height * self.expansion_factor,
            r=bbox.r + width * self.expansion_factor,
            b=bbox.b - height * self.expansion_factor,
            coord_origin=bbox.coord_origin,
        )

        page_ix = element_prov.page_no - 1
        cropped_image = conv_res.pages[page_ix].get_image(
            scale=self.images_scale, cropbox=expanded_bbox
        )
        return ItemAndImageEnrichmentElement(item=element, image=cropped_image)

```
</content>
</file_30>

<file_31>
<path>models/base_ocr_model.py</path>
<content>
```python
import copy
import logging
from abc import abstractmethod
from pathlib import Path
from typing import Iterable, List

import numpy as np
from docling_core.types.doc import BoundingBox, CoordOrigin
from PIL import Image, ImageDraw
from rtree import index
from scipy.ndimage import binary_dilation, find_objects, label

from docling.datamodel.base_models import Cell, OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import OcrOptions
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel

_log = logging.getLogger(__name__)


class BaseOcrModel(BasePageModel):
    def __init__(self, enabled: bool, options: OcrOptions):
        self.enabled = enabled
        self.options = options

    # Computes the optimum amount and coordinates of rectangles to OCR on a given page
    def get_ocr_rects(self, page: Page) -> List[BoundingBox]:
        BITMAP_COVERAGE_TRESHOLD = 0.75
        assert page.size is not None

        def find_ocr_rects(size, bitmap_rects):
            image = Image.new(
                "1", (round(size.width), round(size.height))
            )  # '1' mode is binary

            # Draw all bitmap rects into a binary image
            draw = ImageDraw.Draw(image)
            for rect in bitmap_rects:
                x0, y0, x1, y1 = rect.as_tuple()
                x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
                draw.rectangle([(x0, y0), (x1, y1)], fill=1)

            np_image = np.array(image)

            # Dilate the image by 10 pixels to merge nearby bitmap rectangles
            structure = np.ones(
                (20, 20)
            )  # Create a 20x20 structure element (10 pixels in all directions)
            np_image = binary_dilation(np_image > 0, structure=structure)

            # Find the connected components
            labeled_image, num_features = label(
                np_image > 0
            )  # Label black (0 value) regions

            # Find enclosing bounding boxes for each connected component.
            slices = find_objects(labeled_image)
            bounding_boxes = [
                BoundingBox(
                    l=slc[1].start,
                    t=slc[0].start,
                    r=slc[1].stop - 1,
                    b=slc[0].stop - 1,
                    coord_origin=CoordOrigin.TOPLEFT,
                )
                for slc in slices
            ]

            # Compute area fraction on page covered by bitmaps
            area_frac = np.sum(np_image > 0) / (size.width * size.height)

            return (area_frac, bounding_boxes)  # fraction covered  # boxes

        if page._backend is not None:
            bitmap_rects = page._backend.get_bitmap_rects()
        else:
            bitmap_rects = []
        coverage, ocr_rects = find_ocr_rects(page.size, bitmap_rects)

        # return full-page rectangle if page is dominantly covered with bitmaps
        if self.options.force_full_page_ocr or coverage > max(
            BITMAP_COVERAGE_TRESHOLD, self.options.bitmap_area_threshold
        ):
            return [
                BoundingBox(
                    l=0,
                    t=0,
                    r=page.size.width,
                    b=page.size.height,
                    coord_origin=CoordOrigin.TOPLEFT,
                )
            ]
        # return individual rectangles if the bitmap coverage is above the threshold
        elif coverage > self.options.bitmap_area_threshold:
            return ocr_rects
        else:  # overall coverage of bitmaps is too low, drop all bitmap rectangles.
            return []

    # Filters OCR cells by dropping any OCR cell that intersects with an existing programmatic cell.
    def _filter_ocr_cells(self, ocr_cells, programmatic_cells):
        # Create R-tree index for programmatic cells
        p = index.Property()
        p.dimension = 2
        idx = index.Index(properties=p)
        for i, cell in enumerate(programmatic_cells):
            idx.insert(i, cell.bbox.as_tuple())

        def is_overlapping_with_existing_cells(ocr_cell):
            # Query the R-tree to get overlapping rectangles
            possible_matches_index = list(idx.intersection(ocr_cell.bbox.as_tuple()))

            return (
                len(possible_matches_index) > 0
            )  # this is a weak criterion but it works.

        filtered_ocr_cells = [
            rect for rect in ocr_cells if not is_overlapping_with_existing_cells(rect)
        ]
        return filtered_ocr_cells

    def post_process_cells(self, ocr_cells, programmatic_cells):
        r"""
        Post-process the ocr and programmatic cells and return the final list of of cells
        """
        if self.options.force_full_page_ocr:
            # If a full page OCR is forced, use only the OCR cells
            cells = [
                Cell(id=c_ocr.id, text=c_ocr.text, bbox=c_ocr.bbox)
                for c_ocr in ocr_cells
            ]
            return cells

        ## Remove OCR cells which overlap with programmatic cells.
        filtered_ocr_cells = self._filter_ocr_cells(ocr_cells, programmatic_cells)
        programmatic_cells.extend(filtered_ocr_cells)
        return programmatic_cells

    def draw_ocr_rects_and_cells(self, conv_res, page, ocr_rects, show: bool = False):
        image = copy.deepcopy(page.image)
        scale_x = image.width / page.size.width
        scale_y = image.height / page.size.height

        draw = ImageDraw.Draw(image, "RGBA")

        # Draw OCR rectangles as yellow filled rect
        for rect in ocr_rects:
            x0, y0, x1, y1 = rect.as_tuple()
            y0 *= scale_x
            y1 *= scale_y
            x0 *= scale_x
            x1 *= scale_x

            shade_color = (255, 255, 0, 40)  # transparent yellow
            draw.rectangle([(x0, y0), (x1, y1)], fill=shade_color, outline=None)

        # Draw OCR and programmatic cells
        for tc in page.cells:
            x0, y0, x1, y1 = tc.bbox.as_tuple()
            y0 *= scale_x
            y1 *= scale_y
            x0 *= scale_x
            x1 *= scale_x

            if y1 <= y0:
                y1, y0 = y0, y1

            color = "gray"
            if isinstance(tc, OcrCell):
                color = "magenta"
            draw.rectangle([(x0, y0), (x1, y1)], outline=color)

        if show:
            image.show()
        else:
            out_path: Path = (
                Path(settings.debug.debug_output_path)
                / f"debug_{conv_res.input.file.stem}"
            )
            out_path.mkdir(parents=True, exist_ok=True)

            out_file = out_path / f"ocr_page_{page.page_no:05}.png"
            image.save(str(out_file), format="png")

    @abstractmethod
    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        pass

```
</content>
</file_31>

<file_32>
<path>models/code_formula_model.py</path>
<content>
```python
import re
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Tuple, Union

from docling_core.types.doc import (
    CodeItem,
    DocItemLabel,
    DoclingDocument,
    NodeItem,
    TextItem,
)
from docling_core.types.doc.labels import CodeLanguageLabel
from PIL import Image
from pydantic import BaseModel

from docling.datamodel.base_models import ItemAndImageEnrichmentElement
from docling.datamodel.pipeline_options import AcceleratorOptions
from docling.models.base_model import BaseItemAndImageEnrichmentModel
from docling.utils.accelerator_utils import decide_device


class CodeFormulaModelOptions(BaseModel):
    """
    Configuration options for the CodeFormulaModel.

    Attributes
    ----------
    kind : str
        Type of the model. Fixed value "code_formula".
    do_code_enrichment : bool
        True if code enrichment is enabled, False otherwise.
    do_formula_enrichment : bool
        True if formula enrichment is enabled, False otherwise.
    """

    kind: Literal["code_formula"] = "code_formula"
    do_code_enrichment: bool = True
    do_formula_enrichment: bool = True


class CodeFormulaModel(BaseItemAndImageEnrichmentModel):
    """
    Model for processing and enriching documents with code and formula predictions.

    Attributes
    ----------
    enabled : bool
        True if the model is enabled, False otherwise.
    options : CodeFormulaModelOptions
        Configuration options for the CodeFormulaModel.
    code_formula_model : CodeFormulaPredictor
        The predictor model for code and formula processing.

    Methods
    -------
    __init__(self, enabled, artifacts_path, accelerator_options, code_formula_options)
        Initializes the CodeFormulaModel with the given configuration options.
    is_processable(self, doc, element)
        Determines if a given element in a document can be processed by the model.
    __call__(self, doc, element_batch)
        Processes the given batch of elements and enriches them with predictions.
    """

    images_scale = 1.66  # = 120 dpi, aligned with training data resolution
    expansion_factor = 0.03

    def __init__(
        self,
        enabled: bool,
        artifacts_path: Optional[Union[Path, str]],
        options: CodeFormulaModelOptions,
        accelerator_options: AcceleratorOptions,
    ):
        """
        Initializes the CodeFormulaModel with the given configuration.

        Parameters
        ----------
        enabled : bool
            True if the model is enabled, False otherwise.
        artifacts_path : Path
            Path to the directory containing the model artifacts.
        options : CodeFormulaModelOptions
            Configuration options for the model.
        accelerator_options : AcceleratorOptions
            Options specifying the device and number of threads for acceleration.
        """
        self.enabled = enabled
        self.options = options

        if self.enabled:
            device = decide_device(accelerator_options.device)

            from docling_ibm_models.code_formula_model.code_formula_predictor import (
                CodeFormulaPredictor,
            )

            if artifacts_path is None:
                artifacts_path = self.download_models_hf()
            else:
                artifacts_path = Path(artifacts_path)

            self.code_formula_model = CodeFormulaPredictor(
                artifacts_path=artifacts_path,
                device=device,
                num_threads=accelerator_options.num_threads,
            )

    @staticmethod
    def download_models_hf(
        local_dir: Optional[Path] = None, force: bool = False
    ) -> Path:
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import disable_progress_bars

        disable_progress_bars()
        download_path = snapshot_download(
            repo_id="ds4sd/CodeFormula",
            force_download=force,
            local_dir=local_dir,
            revision="v1.0.0",
        )

        return Path(download_path)

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        """
        Determines if a given element in a document can be processed by the model.

        Parameters
        ----------
        doc : DoclingDocument
            The document being processed.
        element : NodeItem
            The element within the document to check.

        Returns
        -------
        bool
            True if the element can be processed, False otherwise.
        """
        return self.enabled and (
            (isinstance(element, CodeItem) and self.options.do_code_enrichment)
            or (
                isinstance(element, TextItem)
                and element.label == DocItemLabel.FORMULA
                and self.options.do_formula_enrichment
            )
        )

    def _extract_code_language(self, input_string: str) -> Tuple[str, Optional[str]]:
        """Extracts a programming language from the beginning of a string.

        This function checks if the input string starts with a pattern of the form
        ``<_some_language_>``. If it does, it extracts the language string and returns
        a tuple of (remainder, language). Otherwise, it returns the original string
        and `None`.

        Args:
            input_string (str): The input string, which may start with ``<_language_>``.

        Returns:
            Tuple[str, Optional[str]]:
                A tuple where:
                - The first element is either:
                    - The remainder of the string (everything after ``<_language_>``),
                    if a match is found; or
                    - The original string, if no match is found.
                - The second element is the extracted language if a match is found;
                otherwise, `None`.
        """
        pattern = r"^<_([^>]+)_>\s*(.*)"
        match = re.match(pattern, input_string, flags=re.DOTALL)
        if match:
            language = str(match.group(1))  # the captured programming language
            remainder = str(match.group(2))  # everything after the <_language_>
            return remainder, language
        else:
            return input_string, None

    def _get_code_language_enum(self, value: Optional[str]) -> CodeLanguageLabel:
        """
        Converts a string to a corresponding `CodeLanguageLabel` enum member.

        If the provided string does not match any value in `CodeLanguageLabel`,
        it defaults to `CodeLanguageLabel.UNKNOWN`.

        Args:
            value (Optional[str]): The string representation of the code language or None.

        Returns:
            CodeLanguageLabel: The corresponding enum member if the value is valid,
            otherwise `CodeLanguageLabel.UNKNOWN`.
        """
        if not isinstance(value, str):
            return CodeLanguageLabel.UNKNOWN

        try:
            return CodeLanguageLabel(value)
        except ValueError:
            return CodeLanguageLabel.UNKNOWN

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[ItemAndImageEnrichmentElement],
    ) -> Iterable[NodeItem]:
        """
        Processes the given batch of elements and enriches them with predictions.

        Parameters
        ----------
        doc : DoclingDocument
            The document being processed.
        element_batch : Iterable[ItemAndImageEnrichmentElement]
            A batch of elements to be processed.

        Returns
        -------
        Iterable[Any]
            An iterable of enriched elements.
        """
        if not self.enabled:
            for element in element_batch:
                yield element.item
            return

        labels: List[str] = []
        images: List[Image.Image] = []
        elements: List[TextItem] = []
        for el in element_batch:
            assert isinstance(el.item, TextItem)
            elements.append(el.item)
            labels.append(el.item.label)
            images.append(el.image)

        outputs = self.code_formula_model.predict(images, labels)

        for item, output in zip(elements, outputs):
            if isinstance(item, CodeItem):
                output, code_language = self._extract_code_language(output)
                item.code_language = self._get_code_language_enum(code_language)
            item.text = output

            yield item

```
</content>
</file_32>

<file_33>
<path>models/document_picture_classifier.py</path>
<content>
```python
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Tuple, Union

from docling_core.types.doc import (
    DoclingDocument,
    NodeItem,
    PictureClassificationClass,
    PictureClassificationData,
    PictureItem,
)
from PIL import Image
from pydantic import BaseModel

from docling.datamodel.pipeline_options import AcceleratorOptions
from docling.models.base_model import BaseEnrichmentModel
from docling.utils.accelerator_utils import decide_device


class DocumentPictureClassifierOptions(BaseModel):
    """
    Options for configuring the DocumentPictureClassifier.

    Attributes
    ----------
    kind : Literal["document_picture_classifier"]
        Identifier for the type of classifier.
    """

    kind: Literal["document_picture_classifier"] = "document_picture_classifier"


class DocumentPictureClassifier(BaseEnrichmentModel):
    """
    A model for classifying pictures in documents.

    This class enriches document pictures with predicted classifications
    based on a predefined set of classes.

    Attributes
    ----------
    enabled : bool
        Whether the classifier is enabled for use.
    options : DocumentPictureClassifierOptions
        Configuration options for the classifier.
    document_picture_classifier : DocumentPictureClassifierPredictor
        The underlying prediction model, loaded if the classifier is enabled.

    Methods
    -------
    __init__(enabled, artifacts_path, options, accelerator_options)
        Initializes the classifier with specified configurations.
    is_processable(doc, element)
        Checks if the given element can be processed by the classifier.
    __call__(doc, element_batch)
        Processes a batch of elements and adds classification annotations.
    """

    images_scale = 2

    def __init__(
        self,
        enabled: bool,
        artifacts_path: Optional[Union[Path, str]],
        options: DocumentPictureClassifierOptions,
        accelerator_options: AcceleratorOptions,
    ):
        """
        Initializes the DocumentPictureClassifier.

        Parameters
        ----------
        enabled : bool
            Indicates whether the classifier is enabled.
        artifacts_path : Optional[Union[Path, str]],
            Path to the directory containing model artifacts.
        options : DocumentPictureClassifierOptions
            Configuration options for the classifier.
        accelerator_options : AcceleratorOptions
            Options for configuring the device and parallelism.
        """
        self.enabled = enabled
        self.options = options

        if self.enabled:
            device = decide_device(accelerator_options.device)
            from docling_ibm_models.document_figure_classifier_model.document_figure_classifier_predictor import (
                DocumentFigureClassifierPredictor,
            )

            if artifacts_path is None:
                artifacts_path = self.download_models_hf()
            else:
                artifacts_path = Path(artifacts_path)

            self.document_picture_classifier = DocumentFigureClassifierPredictor(
                artifacts_path=artifacts_path,
                device=device,
                num_threads=accelerator_options.num_threads,
            )

    @staticmethod
    def download_models_hf(
        local_dir: Optional[Path] = None, force: bool = False
    ) -> Path:
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import disable_progress_bars

        disable_progress_bars()
        download_path = snapshot_download(
            repo_id="ds4sd/DocumentFigureClassifier",
            force_download=force,
            local_dir=local_dir,
            revision="v1.0.0",
        )

        return Path(download_path)

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        """
        Determines if the given element can be processed by the classifier.

        Parameters
        ----------
        doc : DoclingDocument
            The document containing the element.
        element : NodeItem
            The element to be checked.

        Returns
        -------
        bool
            True if the element is a PictureItem and processing is enabled; False otherwise.
        """
        return self.enabled and isinstance(element, PictureItem)

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[NodeItem],
    ) -> Iterable[NodeItem]:
        """
        Processes a batch of elements and enriches them with classification predictions.

        Parameters
        ----------
        doc : DoclingDocument
            The document containing the elements to be processed.
        element_batch : Iterable[NodeItem]
            A batch of pictures to classify.

        Returns
        -------
        Iterable[NodeItem]
            An iterable of NodeItem objects after processing. The field
            'data.classification' is added containing the classification for each picture.
        """
        if not self.enabled:
            for element in element_batch:
                yield element
            return

        images: List[Image.Image] = []
        elements: List[PictureItem] = []
        for el in element_batch:
            assert isinstance(el, PictureItem)
            elements.append(el)
            img = el.get_image(doc)
            assert img is not None
            images.append(img)

        outputs = self.document_picture_classifier.predict(images)

        for element, output in zip(elements, outputs):
            element.annotations.append(
                PictureClassificationData(
                    provenance="DocumentPictureClassifier",
                    predicted_classes=[
                        PictureClassificationClass(
                            class_name=pred[0],
                            confidence=pred[1],
                        )
                        for pred in output
                    ],
                )
            )

            yield element

```
</content>
</file_33>

<file_34>
<path>models/ds_glm_model.py</path>
<content>
```python
import copy
import random
from pathlib import Path
from typing import List, Union

from deepsearch_glm.andromeda_nlp import nlp_model
from docling_core.types.doc import BoundingBox, CoordOrigin, DoclingDocument
from docling_core.types.legacy_doc.base import BoundingBox as DsBoundingBox
from docling_core.types.legacy_doc.base import (
    Figure,
    PageDimensions,
    PageReference,
    Prov,
    Ref,
)
from docling_core.types.legacy_doc.base import Table as DsSchemaTable
from docling_core.types.legacy_doc.base import TableCell
from docling_core.types.legacy_doc.document import BaseText
from docling_core.types.legacy_doc.document import (
    CCSDocumentDescription as DsDocumentDescription,
)
from docling_core.types.legacy_doc.document import CCSFileInfoObject as DsFileInfoObject
from docling_core.types.legacy_doc.document import ExportedCCSDocument as DsDocument
from PIL import ImageDraw
from pydantic import BaseModel, ConfigDict, TypeAdapter

from docling.datamodel.base_models import (
    Cluster,
    ContainerElement,
    FigureElement,
    Table,
    TextElement,
)
from docling.datamodel.document import ConversionResult, layout_label_to_ds_type
from docling.datamodel.settings import settings
from docling.utils.glm_utils import to_docling_document
from docling.utils.profiling import ProfilingScope, TimeRecorder
from docling.utils.utils import create_hash


class GlmOptions(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_names: str = ""  # e.g. "language;term;reference"


class GlmModel:
    def __init__(self, options: GlmOptions):
        self.options = options

        self.model = nlp_model(loglevel="error", text_ordering=True)

    def _to_legacy_document(self, conv_res) -> DsDocument:
        title = ""
        desc: DsDocumentDescription = DsDocumentDescription(logs=[])

        page_hashes = [
            PageReference(
                hash=create_hash(conv_res.input.document_hash + ":" + str(p.page_no)),
                page=p.page_no + 1,
                model="default",
            )
            for p in conv_res.pages
        ]

        file_info = DsFileInfoObject(
            filename=conv_res.input.file.name,
            document_hash=conv_res.input.document_hash,
            num_pages=conv_res.input.page_count,
            page_hashes=page_hashes,
        )

        main_text: List[Union[Ref, BaseText]] = []
        tables: List[DsSchemaTable] = []
        figures: List[Figure] = []

        page_no_to_page = {p.page_no: p for p in conv_res.pages}

        for element in conv_res.assembled.elements:
            # Convert bboxes to lower-left origin.
            target_bbox = DsBoundingBox(
                element.cluster.bbox.to_bottom_left_origin(
                    page_no_to_page[element.page_no].size.height
                ).as_tuple()
            )

            if isinstance(element, TextElement):
                main_text.append(
                    BaseText(
                        text=element.text,
                        obj_type=layout_label_to_ds_type.get(element.label),
                        name=element.label,
                        prov=[
                            Prov(
                                bbox=target_bbox,
                                page=element.page_no + 1,
                                span=[0, len(element.text)],
                            )
                        ],
                    )
                )
            elif isinstance(element, Table):
                index = len(tables)
                ref_str = f"#/tables/{index}"
                main_text.append(
                    Ref(
                        name=element.label,
                        obj_type=layout_label_to_ds_type.get(element.label),
                        ref=ref_str,
                    ),
                )

                # Initialise empty table data grid (only empty cells)
                table_data = [
                    [
                        TableCell(
                            text="",
                            # bbox=[0,0,0,0],
                            spans=[[i, j]],
                            obj_type="body",
                        )
                        for j in range(element.num_cols)
                    ]
                    for i in range(element.num_rows)
                ]

                # Overwrite cells in table data for which there is actual cell content.
                for cell in element.table_cells:
                    for i in range(
                        min(cell.start_row_offset_idx, element.num_rows),
                        min(cell.end_row_offset_idx, element.num_rows),
                    ):
                        for j in range(
                            min(cell.start_col_offset_idx, element.num_cols),
                            min(cell.end_col_offset_idx, element.num_cols),
                        ):
                            celltype = "body"
                            if cell.column_header:
                                celltype = "col_header"
                            elif cell.row_header:
                                celltype = "row_header"
                            elif cell.row_section:
                                celltype = "row_section"

                            def make_spans(cell):
                                for rspan in range(
                                    min(cell.start_row_offset_idx, element.num_rows),
                                    min(cell.end_row_offset_idx, element.num_rows),
                                ):
                                    for cspan in range(
                                        min(
                                            cell.start_col_offset_idx, element.num_cols
                                        ),
                                        min(cell.end_col_offset_idx, element.num_cols),
                                    ):
                                        yield [rspan, cspan]

                            spans = list(make_spans(cell))
                            if cell.bbox is not None:
                                bbox = cell.bbox.to_bottom_left_origin(
                                    page_no_to_page[element.page_no].size.height
                                ).as_tuple()
                            else:
                                bbox = None

                            table_data[i][j] = TableCell(
                                text=cell.text,
                                bbox=bbox,
                                # col=j,
                                # row=i,
                                spans=spans,
                                obj_type=celltype,
                                # col_span=[cell.start_col_offset_idx, cell.end_col_offset_idx],
                                # row_span=[cell.start_row_offset_idx, cell.end_row_offset_idx]
                            )

                tables.append(
                    DsSchemaTable(
                        num_cols=element.num_cols,
                        num_rows=element.num_rows,
                        obj_type=layout_label_to_ds_type.get(element.label),
                        data=table_data,
                        prov=[
                            Prov(
                                bbox=target_bbox,
                                page=element.page_no + 1,
                                span=[0, 0],
                            )
                        ],
                    )
                )

            elif isinstance(element, FigureElement):
                index = len(figures)
                ref_str = f"#/figures/{index}"
                main_text.append(
                    Ref(
                        name=element.label,
                        obj_type=layout_label_to_ds_type.get(element.label),
                        ref=ref_str,
                    ),
                )
                figures.append(
                    Figure(
                        prov=[
                            Prov(
                                bbox=target_bbox,
                                page=element.page_no + 1,
                                span=[0, 0],
                            )
                        ],
                        obj_type=layout_label_to_ds_type.get(element.label),
                        payload={
                            "children": TypeAdapter(List[Cluster]).dump_python(
                                element.cluster.children
                            )
                        },  # hack to channel child clusters through GLM
                    )
                )
            elif isinstance(element, ContainerElement):
                main_text.append(
                    BaseText(
                        text="",
                        payload={
                            "children": TypeAdapter(List[Cluster]).dump_python(
                                element.cluster.children
                            )
                        },  # hack to channel child clusters through GLM
                        obj_type=layout_label_to_ds_type.get(element.label),
                        name=element.label,
                        prov=[
                            Prov(
                                bbox=target_bbox,
                                page=element.page_no + 1,
                                span=[0, 0],
                            )
                        ],
                    )
                )

        page_dimensions = [
            PageDimensions(page=p.page_no + 1, height=p.size.height, width=p.size.width)
            for p in conv_res.pages
            if p.size is not None
        ]

        ds_doc: DsDocument = DsDocument(
            name=title,
            description=desc,
            file_info=file_info,
            main_text=main_text,
            tables=tables,
            figures=figures,
            page_dimensions=page_dimensions,
        )

        return ds_doc

    def __call__(self, conv_res: ConversionResult) -> DoclingDocument:
        with TimeRecorder(conv_res, "glm", scope=ProfilingScope.DOCUMENT):
            ds_doc = self._to_legacy_document(conv_res)
            ds_doc_dict = ds_doc.model_dump(by_alias=True, exclude_none=True)

            glm_doc = self.model.apply_on_doc(ds_doc_dict)

            docling_doc: DoclingDocument = to_docling_document(glm_doc)  # Experimental

        # DEBUG code:
        def draw_clusters_and_cells(ds_document, page_no, show: bool = False):
            clusters_to_draw = []
            image = copy.deepcopy(conv_res.pages[page_no].image)
            for ix, elem in enumerate(ds_document.main_text):
                if isinstance(elem, BaseText):
                    prov = elem.prov[0]  # type: ignore
                elif isinstance(elem, Ref):
                    _, arr, index = elem.ref.split("/")
                    index = int(index)  # type: ignore
                    if arr == "tables":
                        prov = ds_document.tables[index].prov[0]
                    elif arr == "figures":
                        prov = ds_document.pictures[index].prov[0]
                    else:
                        prov = None

                if prov and prov.page == page_no:
                    clusters_to_draw.append(
                        Cluster(
                            id=ix,
                            label=elem.name,
                            bbox=BoundingBox.from_tuple(
                                coord=prov.bbox,  # type: ignore
                                origin=CoordOrigin.BOTTOMLEFT,
                            ).to_top_left_origin(conv_res.pages[page_no].size.height),
                        )
                    )

            draw = ImageDraw.Draw(image)
            for c in clusters_to_draw:
                x0, y0, x1, y1 = c.bbox.as_tuple()
                draw.rectangle([(x0, y0), (x1, y1)], outline="red")
                draw.text((x0 + 2, y0 + 2), f"{c.id}:{c.label}", fill=(255, 0, 0, 255))

                cell_color = (
                    random.randint(30, 140),
                    random.randint(30, 140),
                    random.randint(30, 140),
                )
                for tc in c.cells:  # [:1]:
                    x0, y0, x1, y1 = tc.bbox.as_tuple()
                    draw.rectangle([(x0, y0), (x1, y1)], outline=cell_color)

            if show:
                image.show()
            else:
                out_path: Path = (
                    Path(settings.debug.debug_output_path)
                    / f"debug_{conv_res.input.file.stem}"
                )
                out_path.mkdir(parents=True, exist_ok=True)

                out_file = out_path / f"doc_page_{page_no:05}.png"
                image.save(str(out_file), format="png")

        # for item in ds_doc.page_dimensions:
        #    page_no = item.page
        #    draw_clusters_and_cells(ds_doc, page_no)

        return docling_doc

```
</content>
</file_34>

<file_35>
<path>models/easyocr_model.py</path>
<content>
```python
import logging
import warnings
from typing import Iterable

import numpy
import torch
from docling_core.types.doc import BoundingBox, CoordOrigin

from docling.datamodel.base_models import Cell, OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    EasyOcrOptions,
)
from docling.datamodel.settings import settings
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.accelerator_utils import decide_device
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class EasyOcrModel(BaseOcrModel):
    def __init__(
        self,
        enabled: bool,
        options: EasyOcrOptions,
        accelerator_options: AcceleratorOptions,
    ):
        super().__init__(enabled=enabled, options=options)
        self.options: EasyOcrOptions

        self.scale = 3  # multiplier for 72 dpi == 216 dpi.

        if self.enabled:
            try:
                import easyocr
            except ImportError:
                raise ImportError(
                    "EasyOCR is not installed. Please install it via `pip install easyocr` to use this OCR engine. "
                    "Alternatively, Docling has support for other OCR engines. See the documentation."
                )

            if self.options.use_gpu is None:
                device = decide_device(accelerator_options.device)
                # Enable easyocr GPU if running on CUDA, MPS
                use_gpu = any(
                    [
                        device.startswith(x)
                        for x in [
                            AcceleratorDevice.CUDA.value,
                            AcceleratorDevice.MPS.value,
                        ]
                    ]
                )
            else:
                warnings.warn(
                    "Deprecated field. Better to set the `accelerator_options.device` in `pipeline_options`. "
                    "When `use_gpu and accelerator_options.device == AcceleratorDevice.CUDA` the GPU is used "
                    "to run EasyOCR. Otherwise, EasyOCR runs in CPU."
                )
                use_gpu = self.options.use_gpu

            self.reader = easyocr.Reader(
                lang_list=self.options.lang,
                gpu=use_gpu,
                model_storage_directory=self.options.model_storage_directory,
                recog_network=self.options.recog_network,
                download_enabled=self.options.download_enabled,
                verbose=False,
            )

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:

            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "ocr"):
                    ocr_rects = self.get_ocr_rects(page)

                    all_ocr_cells = []
                    for ocr_rect in ocr_rects:
                        # Skip zero area boxes
                        if ocr_rect.area() == 0:
                            continue
                        high_res_image = page._backend.get_page_image(
                            scale=self.scale, cropbox=ocr_rect
                        )
                        im = numpy.array(high_res_image)
                        result = self.reader.readtext(im)

                        del high_res_image
                        del im

                        cells = [
                            OcrCell(
                                id=ix,
                                text=line[1],
                                confidence=line[2],
                                bbox=BoundingBox.from_tuple(
                                    coord=(
                                        (line[0][0][0] / self.scale) + ocr_rect.l,
                                        (line[0][0][1] / self.scale) + ocr_rect.t,
                                        (line[0][2][0] / self.scale) + ocr_rect.l,
                                        (line[0][2][1] / self.scale) + ocr_rect.t,
                                    ),
                                    origin=CoordOrigin.TOPLEFT,
                                ),
                            )
                            for ix, line in enumerate(result)
                            if line[2] >= self.options.confidence_threshold
                        ]
                        all_ocr_cells.extend(cells)

                    # Post-process the cells
                    page.cells = self.post_process_cells(all_ocr_cells, page.cells)

                # DEBUG code:
                if settings.debug.visualize_ocr:
                    self.draw_ocr_rects_and_cells(conv_res, page, ocr_rects)

                yield page

```
</content>
</file_35>

<file_36>
<path>models/layout_model.py</path>
<content>
```python
import copy
import logging
from pathlib import Path
from typing import Iterable

from docling_core.types.doc import DocItemLabel
from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor
from PIL import Image

from docling.datamodel.base_models import BoundingBox, Cluster, LayoutPrediction, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import AcceleratorOptions
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel
from docling.utils.accelerator_utils import decide_device
from docling.utils.layout_postprocessor import LayoutPostprocessor
from docling.utils.profiling import TimeRecorder
from docling.utils.visualization import draw_clusters

_log = logging.getLogger(__name__)


class LayoutModel(BasePageModel):

    TEXT_ELEM_LABELS = [
        DocItemLabel.TEXT,
        DocItemLabel.FOOTNOTE,
        DocItemLabel.CAPTION,
        DocItemLabel.CHECKBOX_UNSELECTED,
        DocItemLabel.CHECKBOX_SELECTED,
        DocItemLabel.SECTION_HEADER,
        DocItemLabel.PAGE_HEADER,
        DocItemLabel.PAGE_FOOTER,
        DocItemLabel.CODE,
        DocItemLabel.LIST_ITEM,
        DocItemLabel.FORMULA,
    ]
    PAGE_HEADER_LABELS = [DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER]

    TABLE_LABELS = [DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX]
    FIGURE_LABEL = DocItemLabel.PICTURE
    FORMULA_LABEL = DocItemLabel.FORMULA
    CONTAINER_LABELS = [DocItemLabel.FORM, DocItemLabel.KEY_VALUE_REGION]

    def __init__(self, artifacts_path: Path, accelerator_options: AcceleratorOptions):
        device = decide_device(accelerator_options.device)

        self.layout_predictor = LayoutPredictor(
            artifact_path=str(artifacts_path),
            device=device,
            num_threads=accelerator_options.num_threads,
        )

    def draw_clusters_and_cells_side_by_side(
        self, conv_res, page, clusters, mode_prefix: str, show: bool = False
    ):
        """
        Draws a page image side by side with clusters filtered into two categories:
        - Left: Clusters excluding FORM, KEY_VALUE_REGION, and PICTURE.
        - Right: Clusters including FORM, KEY_VALUE_REGION, and PICTURE.
        Includes label names and confidence scores for each cluster.
        """
        scale_x = page.image.width / page.size.width
        scale_y = page.image.height / page.size.height

        # Filter clusters for left and right images
        exclude_labels = {
            DocItemLabel.FORM,
            DocItemLabel.KEY_VALUE_REGION,
            DocItemLabel.PICTURE,
        }
        left_clusters = [c for c in clusters if c.label not in exclude_labels]
        right_clusters = [c for c in clusters if c.label in exclude_labels]
        # Create a deep copy of the original image for both sides
        left_image = copy.deepcopy(page.image)
        right_image = copy.deepcopy(page.image)

        # Draw clusters on both images
        draw_clusters(left_image, left_clusters, scale_x, scale_y)
        draw_clusters(right_image, right_clusters, scale_x, scale_y)
        # Combine the images side by side
        combined_width = left_image.width * 2
        combined_height = left_image.height
        combined_image = Image.new("RGB", (combined_width, combined_height))
        combined_image.paste(left_image, (0, 0))
        combined_image.paste(right_image, (left_image.width, 0))
        if show:
            combined_image.show()
        else:
            out_path: Path = (
                Path(settings.debug.debug_output_path)
                / f"debug_{conv_res.input.file.stem}"
            )
            out_path.mkdir(parents=True, exist_ok=True)
            out_file = out_path / f"{mode_prefix}_layout_page_{page.page_no:05}.png"
            combined_image.save(str(out_file), format="png")

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "layout"):
                    assert page.size is not None

                    clusters = []
                    for ix, pred_item in enumerate(
                        self.layout_predictor.predict(page.get_image(scale=1.0))
                    ):
                        label = DocItemLabel(
                            pred_item["label"]
                            .lower()
                            .replace(" ", "_")
                            .replace("-", "_")
                        )  # Temporary, until docling-ibm-model uses docling-core types
                        cluster = Cluster(
                            id=ix,
                            label=label,
                            confidence=pred_item["confidence"],
                            bbox=BoundingBox.model_validate(pred_item),
                            cells=[],
                        )
                        clusters.append(cluster)

                    if settings.debug.visualize_raw_layout:
                        self.draw_clusters_and_cells_side_by_side(
                            conv_res, page, clusters, mode_prefix="raw"
                        )

                    # Apply postprocessing

                    processed_clusters, processed_cells = LayoutPostprocessor(
                        page.cells, clusters, page.size
                    ).postprocess()
                    # processed_clusters, processed_cells = clusters, page.cells

                    page.cells = processed_cells
                    page.predictions.layout = LayoutPrediction(
                        clusters=processed_clusters
                    )

                if settings.debug.visualize_layout:
                    self.draw_clusters_and_cells_side_by_side(
                        conv_res, page, processed_clusters, mode_prefix="postprocessed"
                    )

                yield page

```
</content>
</file_36>

<file_37>
<path>models/ocr_mac_model.py</path>
<content>
```python
import logging
import tempfile
from typing import Iterable, Optional, Tuple

from docling_core.types.doc import BoundingBox, CoordOrigin

from docling.datamodel.base_models import OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import OcrMacOptions
from docling.datamodel.settings import settings
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class OcrMacModel(BaseOcrModel):
    def __init__(self, enabled: bool, options: OcrMacOptions):
        super().__init__(enabled=enabled, options=options)
        self.options: OcrMacOptions

        self.scale = 3  # multiplier for 72 dpi == 216 dpi.

        if self.enabled:
            install_errmsg = (
                "ocrmac is not correctly installed. "
                "Please install it via `pip install ocrmac` to use this OCR engine. "
                "Alternatively, Docling has support for other OCR engines. See the documentation: "
                "https://ds4sd.github.io/docling/installation/"
            )
            try:
                from ocrmac import ocrmac
            except ImportError:
                raise ImportError(install_errmsg)

            self.reader_RIL = ocrmac.OCR

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "ocr"):

                    ocr_rects = self.get_ocr_rects(page)

                    all_ocr_cells = []
                    for ocr_rect in ocr_rects:
                        # Skip zero area boxes
                        if ocr_rect.area() == 0:
                            continue
                        high_res_image = page._backend.get_page_image(
                            scale=self.scale, cropbox=ocr_rect
                        )

                        with tempfile.NamedTemporaryFile(
                            suffix=".png", mode="w"
                        ) as image_file:
                            fname = image_file.name
                            high_res_image.save(fname)

                            boxes = self.reader_RIL(
                                fname,
                                recognition_level=self.options.recognition,
                                framework=self.options.framework,
                                language_preference=self.options.lang,
                            ).recognize()

                        im_width, im_height = high_res_image.size
                        cells = []
                        for ix, (text, confidence, box) in enumerate(boxes):
                            x = float(box[0])
                            y = float(box[1])
                            w = float(box[2])
                            h = float(box[3])

                            x1 = x * im_width
                            y2 = (1 - y) * im_height

                            x2 = x1 + w * im_width
                            y1 = y2 - h * im_height

                            left = x1 / self.scale
                            top = y1 / self.scale
                            right = x2 / self.scale
                            bottom = y2 / self.scale

                            cells.append(
                                OcrCell(
                                    id=ix,
                                    text=text,
                                    confidence=confidence,
                                    bbox=BoundingBox.from_tuple(
                                        coord=(left, top, right, bottom),
                                        origin=CoordOrigin.TOPLEFT,
                                    ),
                                )
                            )

                        # del high_res_image
                        all_ocr_cells.extend(cells)

                    # Post-process the cells
                    page.cells = self.post_process_cells(all_ocr_cells, page.cells)

                # DEBUG code:
                if settings.debug.visualize_ocr:
                    self.draw_ocr_rects_and_cells(conv_res, page, ocr_rects)

                yield page

```
</content>
</file_37>

<file_38>
<path>models/page_assemble_model.py</path>
<content>
```python
import logging
import re
from typing import Iterable, List

from pydantic import BaseModel

from docling.datamodel.base_models import (
    AssembledUnit,
    ContainerElement,
    FigureElement,
    Page,
    PageElement,
    Table,
    TextElement,
)
from docling.datamodel.document import ConversionResult
from docling.models.base_model import BasePageModel
from docling.models.layout_model import LayoutModel
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class PageAssembleOptions(BaseModel):
    pass


class PageAssembleModel(BasePageModel):
    def __init__(self, options: PageAssembleOptions):
        self.options = options

    def sanitize_text(self, lines):
        if len(lines) <= 1:
            return " ".join(lines)

        for ix, line in enumerate(lines[1:]):
            prev_line = lines[ix]

            if prev_line.endswith("-"):
                prev_words = re.findall(r"\b[\w]+\b", prev_line)
                line_words = re.findall(r"\b[\w]+\b", line)

                if (
                    len(prev_words)
                    and len(line_words)
                    and prev_words[-1].isalnum()
                    and line_words[0].isalnum()
                ):
                    lines[ix] = prev_line[:-1]
            else:
                lines[ix] += " "

        sanitized_text = "".join(lines)

        return sanitized_text.strip()  # Strip any leading or trailing whitespace

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "page_assemble"):

                    assert page.predictions.layout is not None

                    # assembles some JSON output page by page.

                    elements: List[PageElement] = []
                    headers: List[PageElement] = []
                    body: List[PageElement] = []

                    for cluster in page.predictions.layout.clusters:
                        # _log.info("Cluster label seen:", cluster.label)
                        if cluster.label in LayoutModel.TEXT_ELEM_LABELS:

                            textlines = [
                                cell.text.replace("\x02", "-").strip()
                                for cell in cluster.cells
                                if len(cell.text.strip()) > 0
                            ]
                            text = self.sanitize_text(textlines)
                            text_el = TextElement(
                                label=cluster.label,
                                id=cluster.id,
                                text=text,
                                page_no=page.page_no,
                                cluster=cluster,
                            )
                            elements.append(text_el)

                            if cluster.label in LayoutModel.PAGE_HEADER_LABELS:
                                headers.append(text_el)
                            else:
                                body.append(text_el)
                        elif cluster.label in LayoutModel.TABLE_LABELS:
                            tbl = None
                            if page.predictions.tablestructure:
                                tbl = page.predictions.tablestructure.table_map.get(
                                    cluster.id, None
                                )
                            if (
                                not tbl
                            ):  # fallback: add table without structure, if it isn't present
                                tbl = Table(
                                    label=cluster.label,
                                    id=cluster.id,
                                    text="",
                                    otsl_seq=[],
                                    table_cells=[],
                                    cluster=cluster,
                                    page_no=page.page_no,
                                )

                            elements.append(tbl)
                            body.append(tbl)
                        elif cluster.label == LayoutModel.FIGURE_LABEL:
                            fig = None
                            if page.predictions.figures_classification:
                                fig = page.predictions.figures_classification.figure_map.get(
                                    cluster.id, None
                                )
                            if (
                                not fig
                            ):  # fallback: add figure without classification, if it isn't present
                                fig = FigureElement(
                                    label=cluster.label,
                                    id=cluster.id,
                                    text="",
                                    data=None,
                                    cluster=cluster,
                                    page_no=page.page_no,
                                )
                            elements.append(fig)
                            body.append(fig)
                        elif cluster.label in LayoutModel.CONTAINER_LABELS:
                            container_el = ContainerElement(
                                label=cluster.label,
                                id=cluster.id,
                                page_no=page.page_no,
                                cluster=cluster,
                            )
                            elements.append(container_el)
                            body.append(container_el)

                    page.assembled = AssembledUnit(
                        elements=elements, headers=headers, body=body
                    )

                yield page

```
</content>
</file_38>

<file_39>
<path>models/page_preprocessing_model.py</path>
<content>
```python
from pathlib import Path
from typing import Iterable, Optional

from PIL import ImageDraw
from pydantic import BaseModel

from docling.datamodel.base_models import Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel
from docling.utils.profiling import TimeRecorder


class PagePreprocessingOptions(BaseModel):
    images_scale: Optional[float]


class PagePreprocessingModel(BasePageModel):
    def __init__(self, options: PagePreprocessingOptions):
        self.options = options

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "page_parse"):
                    page = self._populate_page_images(page)
                    page = self._parse_page_cells(conv_res, page)
                yield page

    # Generate the page image and store it in the page object
    def _populate_page_images(self, page: Page) -> Page:
        # default scale
        page.get_image(
            scale=1.0
        )  # puts the page image on the image cache at default scale

        images_scale = self.options.images_scale
        # user requested scales
        if images_scale is not None:
            page._default_image_scale = images_scale
            page.get_image(
                scale=images_scale
            )  # this will trigger storing the image in the internal cache

        return page

    # Extract and populate the page cells and store it in the page object
    def _parse_page_cells(self, conv_res: ConversionResult, page: Page) -> Page:
        assert page._backend is not None

        page.cells = list(page._backend.get_text_cells())

        # DEBUG code:
        def draw_text_boxes(image, cells, show: bool = False):
            draw = ImageDraw.Draw(image)
            for c in cells:
                x0, y0, x1, y1 = c.bbox.as_tuple()
                draw.rectangle([(x0, y0), (x1, y1)], outline="red")
            if show:
                image.show()
            else:
                out_path: Path = (
                    Path(settings.debug.debug_output_path)
                    / f"debug_{conv_res.input.file.stem}"
                )
                out_path.mkdir(parents=True, exist_ok=True)

                out_file = out_path / f"cells_page_{page.page_no:05}.png"
                image.save(str(out_file), format="png")

        if settings.debug.visualize_cells:
            draw_text_boxes(page.get_image(scale=1.0), page.cells)

        return page

```
</content>
</file_39>

<file_40>
<path>models/rapid_ocr_model.py</path>
<content>
```python
import logging
from typing import Iterable

import numpy
from docling_core.types.doc import BoundingBox, CoordOrigin

from docling.datamodel.base_models import OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    RapidOcrOptions,
)
from docling.datamodel.settings import settings
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.accelerator_utils import decide_device
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class RapidOcrModel(BaseOcrModel):
    def __init__(
        self,
        enabled: bool,
        options: RapidOcrOptions,
        accelerator_options: AcceleratorOptions,
    ):
        super().__init__(enabled=enabled, options=options)
        self.options: RapidOcrOptions

        self.scale = 3  # multiplier for 72 dpi == 216 dpi.

        if self.enabled:
            try:
                from rapidocr_onnxruntime import RapidOCR  # type: ignore
            except ImportError:
                raise ImportError(
                    "RapidOCR is not installed. Please install it via `pip install rapidocr_onnxruntime` to use this OCR engine. "
                    "Alternatively, Docling has support for other OCR engines. See the documentation."
                )

            # Decide the accelerator devices
            device = decide_device(accelerator_options.device)
            use_cuda = str(AcceleratorDevice.CUDA.value).lower() in device
            use_dml = accelerator_options.device == AcceleratorDevice.AUTO
            intra_op_num_threads = accelerator_options.num_threads

            self.reader = RapidOCR(
                text_score=self.options.text_score,
                cls_use_cuda=use_cuda,
                rec_use_cuda=use_cuda,
                det_use_cuda=use_cuda,
                det_use_dml=use_dml,
                cls_use_dml=use_dml,
                rec_use_dml=use_dml,
                intra_op_num_threads=intra_op_num_threads,
                print_verbose=self.options.print_verbose,
                det_model_path=self.options.det_model_path,
                cls_model_path=self.options.cls_model_path,
                rec_model_path=self.options.rec_model_path,
                rec_keys_path=self.options.rec_keys_path,
            )

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:

            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "ocr"):
                    ocr_rects = self.get_ocr_rects(page)

                    all_ocr_cells = []
                    for ocr_rect in ocr_rects:
                        # Skip zero area boxes
                        if ocr_rect.area() == 0:
                            continue
                        high_res_image = page._backend.get_page_image(
                            scale=self.scale, cropbox=ocr_rect
                        )
                        im = numpy.array(high_res_image)
                        result, _ = self.reader(
                            im,
                            use_det=self.options.use_det,
                            use_cls=self.options.use_cls,
                            use_rec=self.options.use_rec,
                        )

                        del high_res_image
                        del im

                        if result is not None:
                            cells = [
                                OcrCell(
                                    id=ix,
                                    text=line[1],
                                    confidence=line[2],
                                    bbox=BoundingBox.from_tuple(
                                        coord=(
                                            (line[0][0][0] / self.scale) + ocr_rect.l,
                                            (line[0][0][1] / self.scale) + ocr_rect.t,
                                            (line[0][2][0] / self.scale) + ocr_rect.l,
                                            (line[0][2][1] / self.scale) + ocr_rect.t,
                                        ),
                                        origin=CoordOrigin.TOPLEFT,
                                    ),
                                )
                                for ix, line in enumerate(result)
                            ]
                            all_ocr_cells.extend(cells)

                    # Post-process the cells
                    page.cells = self.post_process_cells(all_ocr_cells, page.cells)

                # DEBUG code:
                if settings.debug.visualize_ocr:
                    self.draw_ocr_rects_and_cells(conv_res, page, ocr_rects)

                yield page

```
</content>
</file_40>

<file_41>
<path>models/table_structure_model.py</path>
<content>
```python
import copy
from pathlib import Path
from typing import Iterable

import numpy
from docling_core.types.doc import BoundingBox, DocItemLabel, TableCell
from docling_ibm_models.tableformer.data_management.tf_predictor import TFPredictor
from PIL import ImageDraw

from docling.datamodel.base_models import Page, Table, TableStructurePrediction
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel
from docling.utils.accelerator_utils import decide_device
from docling.utils.profiling import TimeRecorder


class TableStructureModel(BasePageModel):
    def __init__(
        self,
        enabled: bool,
        artifacts_path: Path,
        options: TableStructureOptions,
        accelerator_options: AcceleratorOptions,
    ):
        self.options = options
        self.do_cell_matching = self.options.do_cell_matching
        self.mode = self.options.mode

        self.enabled = enabled
        if self.enabled:
            if self.mode == TableFormerMode.ACCURATE:
                artifacts_path = artifacts_path / "accurate"
            else:
                artifacts_path = artifacts_path / "fast"

            # Third Party
            import docling_ibm_models.tableformer.common as c

            device = decide_device(accelerator_options.device)

            # Disable MPS here, until we know why it makes things slower.
            if device == AcceleratorDevice.MPS.value:
                device = AcceleratorDevice.CPU.value

            self.tm_config = c.read_config(f"{artifacts_path}/tm_config.json")
            self.tm_config["model"]["save_dir"] = artifacts_path
            self.tm_model_type = self.tm_config["model"]["type"]

            self.tf_predictor = TFPredictor(
                self.tm_config, device, accelerator_options.num_threads
            )
            self.scale = 2.0  # Scale up table input images to 144 dpi

    def draw_table_and_cells(
        self,
        conv_res: ConversionResult,
        page: Page,
        tbl_list: Iterable[Table],
        show: bool = False,
    ):
        assert page._backend is not None
        assert page.size is not None

        image = (
            page._backend.get_page_image()
        )  # make new image to avoid drawing on the saved ones

        scale_x = image.width / page.size.width
        scale_y = image.height / page.size.height

        draw = ImageDraw.Draw(image)

        for table_element in tbl_list:
            x0, y0, x1, y1 = table_element.cluster.bbox.as_tuple()
            y0 *= scale_x
            y1 *= scale_y
            x0 *= scale_x
            x1 *= scale_x

            draw.rectangle([(x0, y0), (x1, y1)], outline="red")

            for cell in table_element.cluster.cells:
                x0, y0, x1, y1 = cell.bbox.as_tuple()
                x0 *= scale_x
                x1 *= scale_x
                y0 *= scale_x
                y1 *= scale_y

                draw.rectangle([(x0, y0), (x1, y1)], outline="green")

            for tc in table_element.table_cells:
                if tc.bbox is not None:
                    x0, y0, x1, y1 = tc.bbox.as_tuple()
                    x0 *= scale_x
                    x1 *= scale_x
                    y0 *= scale_x
                    y1 *= scale_y

                    if tc.column_header:
                        width = 3
                    else:
                        width = 1
                    draw.rectangle([(x0, y0), (x1, y1)], outline="blue", width=width)
                    draw.text(
                        (x0 + 3, y0 + 3),
                        text=f"{tc.start_row_offset_idx}, {tc.start_col_offset_idx}",
                        fill="black",
                    )
        if show:
            image.show()
        else:
            out_path: Path = (
                Path(settings.debug.debug_output_path)
                / f"debug_{conv_res.input.file.stem}"
            )
            out_path.mkdir(parents=True, exist_ok=True)

            out_file = out_path / f"table_struct_page_{page.page_no:05}.png"
            image.save(str(out_file), format="png")

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "table_structure"):

                    assert page.predictions.layout is not None
                    assert page.size is not None

                    page.predictions.tablestructure = (
                        TableStructurePrediction()
                    )  # dummy

                    in_tables = [
                        (
                            cluster,
                            [
                                round(cluster.bbox.l) * self.scale,
                                round(cluster.bbox.t) * self.scale,
                                round(cluster.bbox.r) * self.scale,
                                round(cluster.bbox.b) * self.scale,
                            ],
                        )
                        for cluster in page.predictions.layout.clusters
                        if cluster.label
                        in [DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX]
                    ]
                    if not len(in_tables):
                        yield page
                        continue

                    page_input = {
                        "width": page.size.width * self.scale,
                        "height": page.size.height * self.scale,
                        "image": numpy.asarray(page.get_image(scale=self.scale)),
                    }

                    table_clusters, table_bboxes = zip(*in_tables)

                    if len(table_bboxes):
                        for table_cluster, tbl_box in in_tables:

                            tokens = []
                            for c in table_cluster.cells:
                                # Only allow non empty stings (spaces) into the cells of a table
                                if len(c.text.strip()) > 0:
                                    new_cell = copy.deepcopy(c)
                                    new_cell.bbox = new_cell.bbox.scaled(
                                        scale=self.scale
                                    )

                                    tokens.append(new_cell.model_dump())
                            page_input["tokens"] = tokens

                            tf_output = self.tf_predictor.multi_table_predict(
                                page_input, [tbl_box], do_matching=self.do_cell_matching
                            )
                            table_out = tf_output[0]
                            table_cells = []
                            for element in table_out["tf_responses"]:

                                if not self.do_cell_matching:
                                    the_bbox = BoundingBox.model_validate(
                                        element["bbox"]
                                    ).scaled(1 / self.scale)
                                    text_piece = page._backend.get_text_in_rect(
                                        the_bbox
                                    )
                                    element["bbox"]["token"] = text_piece

                                tc = TableCell.model_validate(element)
                                if self.do_cell_matching and tc.bbox is not None:
                                    tc.bbox = tc.bbox.scaled(1 / self.scale)
                                table_cells.append(tc)

                            assert "predict_details" in table_out

                            # Retrieving cols/rows, after post processing:
                            num_rows = table_out["predict_details"].get("num_rows", 0)
                            num_cols = table_out["predict_details"].get("num_cols", 0)
                            otsl_seq = (
                                table_out["predict_details"]
                                .get("prediction", {})
                                .get("rs_seq", [])
                            )

                            tbl = Table(
                                otsl_seq=otsl_seq,
                                table_cells=table_cells,
                                num_rows=num_rows,
                                num_cols=num_cols,
                                id=table_cluster.id,
                                page_no=page.page_no,
                                cluster=table_cluster,
                                label=table_cluster.label,
                            )

                            page.predictions.tablestructure.table_map[
                                table_cluster.id
                            ] = tbl

                    # For debugging purposes:
                    if settings.debug.visualize_tables:
                        self.draw_table_and_cells(
                            conv_res,
                            page,
                            page.predictions.tablestructure.table_map.values(),
                        )

                yield page

```
</content>
</file_41>

<file_42>
<path>models/tesseract_ocr_cli_model.py</path>
<content>
```python
import csv
import io
import logging
import os
import tempfile
from subprocess import DEVNULL, PIPE, Popen
from typing import Iterable, List, Optional, Tuple

import pandas as pd
from docling_core.types.doc import BoundingBox, CoordOrigin

from docling.datamodel.base_models import Cell, OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import TesseractCliOcrOptions
from docling.datamodel.settings import settings
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.ocr_utils import map_tesseract_script
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class TesseractOcrCliModel(BaseOcrModel):
    def __init__(self, enabled: bool, options: TesseractCliOcrOptions):
        super().__init__(enabled=enabled, options=options)
        self.options: TesseractCliOcrOptions

        self.scale = 3  # multiplier for 72 dpi == 216 dpi.

        self._name: Optional[str] = None
        self._version: Optional[str] = None
        self._tesseract_languages: Optional[List[str]] = None
        self._script_prefix: Optional[str] = None

        if self.enabled:
            try:
                self._get_name_and_version()
                self._set_languages_and_prefix()

            except Exception as exc:
                raise RuntimeError(
                    f"Tesseract is not available, aborting: {exc} "
                    "Install tesseract on your system and the tesseract binary is discoverable. "
                    "The actual command for Tesseract can be specified in `pipeline_options.ocr_options.tesseract_cmd='tesseract'`. "
                    "Alternatively, Docling has support for other OCR engines. See the documentation."
                )

    def _get_name_and_version(self) -> Tuple[str, str]:

        if self._name != None and self._version != None:
            return self._name, self._version  # type: ignore

        cmd = [self.options.tesseract_cmd, "--version"]

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        proc.wait()

        # HACK: Windows versions of Tesseract output the version to stdout, Linux versions
        # to stderr, so check both.
        version_line = (
            (stdout.decode("utf8").strip() or stderr.decode("utf8").strip())
            .split("\n")[0]
            .strip()
        )

        # If everything else fails...
        if not version_line:
            version_line = "tesseract XXX"

        name, version = version_line.split(" ")

        self._name = name
        self._version = version

        return name, version

    def _run_tesseract(self, ifilename: str):
        r"""
        Run tesseract CLI
        """
        cmd = [self.options.tesseract_cmd]

        if "auto" in self.options.lang:
            lang = self._detect_language(ifilename)
            if lang is not None:
                cmd.append("-l")
                cmd.append(lang)
        elif self.options.lang is not None and len(self.options.lang) > 0:
            cmd.append("-l")
            cmd.append("+".join(self.options.lang))

        if self.options.path is not None:
            cmd.append("--tessdata-dir")
            cmd.append(self.options.path)

        cmd += [ifilename, "stdout", "tsv"]
        _log.info("command: {}".format(" ".join(cmd)))

        proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
        output, _ = proc.communicate()

        # _log.info(output)

        # Decode the byte string to a regular string
        decoded_data = output.decode("utf-8")
        # _log.info(decoded_data)

        # Read the TSV file generated by Tesseract
        df = pd.read_csv(io.StringIO(decoded_data), quoting=csv.QUOTE_NONE, sep="\t")

        # Display the dataframe (optional)
        # _log.info("df: ", df.head())

        # Filter rows that contain actual text (ignore header or empty rows)
        df_filtered = df[df["text"].notnull() & (df["text"].str.strip() != "")]

        return df_filtered

    def _detect_language(self, ifilename: str):
        r"""
        Run tesseract in PSM 0 mode to detect the language
        """
        assert self._tesseract_languages is not None

        cmd = [self.options.tesseract_cmd]
        cmd.extend(["--psm", "0", "-l", "osd", ifilename, "stdout"])
        _log.info("command: {}".format(" ".join(cmd)))
        proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
        output, _ = proc.communicate()
        decoded_data = output.decode("utf-8")
        df = pd.read_csv(
            io.StringIO(decoded_data), sep=":", header=None, names=["key", "value"]
        )
        scripts = df.loc[df["key"] == "Script"].value.tolist()
        if len(scripts) == 0:
            _log.warning("Tesseract cannot detect the script of the page")
            return None

        script = map_tesseract_script(scripts[0].strip())
        lang = f"{self._script_prefix}{script}"

        # Check if the detected language has been installed
        if lang not in self._tesseract_languages:
            msg = f"Tesseract detected the script '{script}' and language '{lang}'."
            msg += " However this language is not installed in your system and will be ignored."
            _log.warning(msg)
            return None

        _log.debug(
            f"Using tesseract model for the detected script '{script}' and language '{lang}'"
        )
        return lang

    def _set_languages_and_prefix(self):
        r"""
        Read and set the languages installed in tesseract and decide the script prefix
        """
        # Get all languages
        cmd = [self.options.tesseract_cmd]
        cmd.append("--list-langs")
        _log.info("command: {}".format(" ".join(cmd)))
        proc = Popen(cmd, stdout=PIPE, stderr=DEVNULL)
        output, _ = proc.communicate()
        decoded_data = output.decode("utf-8")
        df = pd.read_csv(io.StringIO(decoded_data), header=None)
        self._tesseract_languages = df[0].tolist()[1:]

        # Decide the script prefix
        if any([l.startswith("script/") for l in self._tesseract_languages]):
            script_prefix = "script/"
        else:
            script_prefix = ""

        self._script_prefix = script_prefix

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:

        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "ocr"):
                    ocr_rects = self.get_ocr_rects(page)

                    all_ocr_cells = []
                    for ocr_rect in ocr_rects:
                        # Skip zero area boxes
                        if ocr_rect.area() == 0:
                            continue
                        high_res_image = page._backend.get_page_image(
                            scale=self.scale, cropbox=ocr_rect
                        )
                        try:
                            with tempfile.NamedTemporaryFile(
                                suffix=".png", mode="w+b", delete=False
                            ) as image_file:
                                fname = image_file.name
                                high_res_image.save(image_file)

                            df = self._run_tesseract(fname)
                        finally:
                            if os.path.exists(fname):
                                os.remove(fname)

                        # _log.info(df)

                        # Print relevant columns (bounding box and text)
                        for ix, row in df.iterrows():
                            text = row["text"]
                            conf = row["conf"]

                            l = float(row["left"])
                            b = float(row["top"])
                            w = float(row["width"])
                            h = float(row["height"])

                            t = b + h
                            r = l + w

                            cell = OcrCell(
                                id=ix,
                                text=text,
                                confidence=conf / 100.0,
                                bbox=BoundingBox.from_tuple(
                                    coord=(
                                        (l / self.scale) + ocr_rect.l,
                                        (b / self.scale) + ocr_rect.t,
                                        (r / self.scale) + ocr_rect.l,
                                        (t / self.scale) + ocr_rect.t,
                                    ),
                                    origin=CoordOrigin.TOPLEFT,
                                ),
                            )
                            all_ocr_cells.append(cell)

                    # Post-process the cells
                    page.cells = self.post_process_cells(all_ocr_cells, page.cells)

                # DEBUG code:
                if settings.debug.visualize_ocr:
                    self.draw_ocr_rects_and_cells(conv_res, page, ocr_rects)

                yield page

```
</content>
</file_42>

<file_43>
<path>models/tesseract_ocr_model.py</path>
<content>
```python
import logging
from typing import Iterable

from docling_core.types.doc import BoundingBox, CoordOrigin

from docling.datamodel.base_models import Cell, OcrCell, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import TesseractOcrOptions
from docling.datamodel.settings import settings
from docling.models.base_ocr_model import BaseOcrModel
from docling.utils.ocr_utils import map_tesseract_script
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


class TesseractOcrModel(BaseOcrModel):
    def __init__(self, enabled: bool, options: TesseractOcrOptions):
        super().__init__(enabled=enabled, options=options)
        self.options: TesseractOcrOptions

        self.scale = 3  # multiplier for 72 dpi == 216 dpi.
        self.reader = None
        self.osd_reader = None

        if self.enabled:
            install_errmsg = (
                "tesserocr is not correctly installed. "
                "Please install it via `pip install tesserocr` to use this OCR engine. "
                "Note that tesserocr might have to be manually compiled for working with "
                "your Tesseract installation. The Docling documentation provides examples for it. "
                "Alternatively, Docling has support for other OCR engines. See the documentation: "
                "https://ds4sd.github.io/docling/installation/"
            )
            missing_langs_errmsg = (
                "tesserocr is not correctly configured. No language models have been detected. "
                "Please ensure that the TESSDATA_PREFIX envvar points to tesseract languages dir. "
                "You can find more information how to setup other OCR engines in Docling "
                "documentation: "
                "https://ds4sd.github.io/docling/installation/"
            )

            try:
                import tesserocr
            except ImportError:
                raise ImportError(install_errmsg)
            try:
                tesseract_version = tesserocr.tesseract_version()
            except:
                raise ImportError(install_errmsg)

            _, self._tesserocr_languages = tesserocr.get_languages()
            if not self._tesserocr_languages:
                raise ImportError(missing_langs_errmsg)

            # Initialize the tesseractAPI
            _log.debug("Initializing TesserOCR: %s", tesseract_version)
            lang = "+".join(self.options.lang)

            self.script_readers: dict[str, tesserocr.PyTessBaseAPI] = {}

            if any([l.startswith("script/") for l in self._tesserocr_languages]):
                self.script_prefix = "script/"
            else:
                self.script_prefix = ""

            tesserocr_kwargs = {
                "psm": tesserocr.PSM.AUTO,
                "init": True,
                "oem": tesserocr.OEM.DEFAULT,
            }

            if self.options.path is not None:
                tesserocr_kwargs["path"] = self.options.path

            if lang == "auto":
                self.reader = tesserocr.PyTessBaseAPI(**tesserocr_kwargs)
                self.osd_reader = tesserocr.PyTessBaseAPI(
                    **{"lang": "osd", "psm": tesserocr.PSM.OSD_ONLY} | tesserocr_kwargs
                )
            else:
                self.reader = tesserocr.PyTessBaseAPI(
                    **{"lang": lang} | tesserocr_kwargs,
                )
            self.reader_RIL = tesserocr.RIL

    def __del__(self):
        if self.reader is not None:
            # Finalize the tesseractAPI
            self.reader.End()
        for script in self.script_readers:
            self.script_readers[script].End()

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "ocr"):
                    assert self.reader is not None
                    assert self._tesserocr_languages is not None

                    ocr_rects = self.get_ocr_rects(page)

                    all_ocr_cells = []
                    for ocr_rect in ocr_rects:
                        # Skip zero area boxes
                        if ocr_rect.area() == 0:
                            continue
                        high_res_image = page._backend.get_page_image(
                            scale=self.scale, cropbox=ocr_rect
                        )

                        local_reader = self.reader
                        if "auto" in self.options.lang:
                            assert self.osd_reader is not None

                            self.osd_reader.SetImage(high_res_image)
                            osd = self.osd_reader.DetectOrientationScript()

                            # No text, probably
                            if osd is None:
                                continue

                            script = osd["script_name"]
                            script = map_tesseract_script(script)
                            lang = f"{self.script_prefix}{script}"

                            # Check if the detected languge is present in the system
                            if lang not in self._tesserocr_languages:
                                msg = f"Tesseract detected the script '{script}' and language '{lang}'."
                                msg += " However this language is not installed in your system and will be ignored."
                                _log.warning(msg)
                            else:
                                if script not in self.script_readers:
                                    import tesserocr

                                    self.script_readers[script] = (
                                        tesserocr.PyTessBaseAPI(
                                            path=self.reader.GetDatapath(),
                                            lang=lang,
                                            psm=tesserocr.PSM.AUTO,
                                            init=True,
                                            oem=tesserocr.OEM.DEFAULT,
                                        )
                                    )
                                local_reader = self.script_readers[script]

                        local_reader.SetImage(high_res_image)
                        boxes = local_reader.GetComponentImages(
                            self.reader_RIL.TEXTLINE, True
                        )

                        cells = []
                        for ix, (im, box, _, _) in enumerate(boxes):
                            # Set the area of interest. Tesseract uses Bottom-Left for the origin
                            local_reader.SetRectangle(
                                box["x"], box["y"], box["w"], box["h"]
                            )

                            # Extract text within the bounding box
                            text = local_reader.GetUTF8Text().strip()
                            confidence = local_reader.MeanTextConf()
                            left = box["x"] / self.scale
                            bottom = box["y"] / self.scale
                            right = (box["x"] + box["w"]) / self.scale
                            top = (box["y"] + box["h"]) / self.scale

                            cells.append(
                                OcrCell(
                                    id=ix,
                                    text=text,
                                    confidence=confidence,
                                    bbox=BoundingBox.from_tuple(
                                        coord=(left, top, right, bottom),
                                        origin=CoordOrigin.TOPLEFT,
                                    ),
                                )
                            )

                        # del high_res_image
                        all_ocr_cells.extend(cells)

                    # Post-process the cells
                    page.cells = self.post_process_cells(all_ocr_cells, page.cells)

                # DEBUG code:
                if settings.debug.visualize_ocr:
                    self.draw_ocr_rects_and_cells(conv_res, page, ocr_rects)

                yield page

```
</content>
</file_43>

<file_44>
<path>pipeline/__init__.py</path>
<content>
```python

```
</content>
</file_44>

<file_45>
<path>pipeline/base_pipeline.py</path>
<content>
```python
import functools
import logging
import time
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List

from docling_core.types.doc import DoclingDocument, NodeItem

from docling.backend.abstract_backend import AbstractDocumentBackend
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.datamodel.base_models import (
    ConversionStatus,
    DoclingComponentType,
    ErrorItem,
    Page,
)
from docling.datamodel.document import ConversionResult, InputDocument
from docling.datamodel.pipeline_options import PipelineOptions
from docling.datamodel.settings import settings
from docling.models.base_model import GenericEnrichmentModel
from docling.utils.profiling import ProfilingScope, TimeRecorder
from docling.utils.utils import chunkify

_log = logging.getLogger(__name__)


class BasePipeline(ABC):
    def __init__(self, pipeline_options: PipelineOptions):
        self.pipeline_options = pipeline_options
        self.keep_images = False
        self.build_pipe: List[Callable] = []
        self.enrichment_pipe: List[GenericEnrichmentModel[Any]] = []

    def execute(self, in_doc: InputDocument, raises_on_error: bool) -> ConversionResult:
        conv_res = ConversionResult(input=in_doc)

        _log.info(f"Processing document {in_doc.file.name}")
        try:
            with TimeRecorder(
                conv_res, "pipeline_total", scope=ProfilingScope.DOCUMENT
            ):
                # These steps are building and assembling the structure of the
                # output DoclingDocument.
                conv_res = self._build_document(conv_res)
                conv_res = self._assemble_document(conv_res)
                # From this stage, all operations should rely only on conv_res.output
                conv_res = self._enrich_document(conv_res)
                conv_res.status = self._determine_status(conv_res)
        except Exception as e:
            conv_res.status = ConversionStatus.FAILURE
            if raises_on_error:
                raise e
        finally:
            self._unload(conv_res)

        return conv_res

    @abstractmethod
    def _build_document(self, conv_res: ConversionResult) -> ConversionResult:
        pass

    def _assemble_document(self, conv_res: ConversionResult) -> ConversionResult:
        return conv_res

    def _enrich_document(self, conv_res: ConversionResult) -> ConversionResult:

        def _prepare_elements(
            conv_res: ConversionResult, model: GenericEnrichmentModel[Any]
        ) -> Iterable[NodeItem]:
            for doc_element, _level in conv_res.document.iterate_items():
                prepared_element = model.prepare_element(
                    conv_res=conv_res, element=doc_element
                )
                if prepared_element is not None:
                    yield prepared_element

        with TimeRecorder(conv_res, "doc_enrich", scope=ProfilingScope.DOCUMENT):
            for model in self.enrichment_pipe:
                for element_batch in chunkify(
                    _prepare_elements(conv_res, model),
                    settings.perf.elements_batch_size,
                ):
                    for element in model(
                        doc=conv_res.document, element_batch=element_batch
                    ):  # Must exhaust!
                        pass

        return conv_res

    @abstractmethod
    def _determine_status(self, conv_res: ConversionResult) -> ConversionStatus:
        pass

    def _unload(self, conv_res: ConversionResult):
        pass

    @classmethod
    @abstractmethod
    def get_default_options(cls) -> PipelineOptions:
        pass

    @classmethod
    @abstractmethod
    def is_backend_supported(cls, backend: AbstractDocumentBackend):
        pass

    # def _apply_on_elements(self, element_batch: Iterable[NodeItem]) -> Iterable[Any]:
    #    for model in self.build_pipe:
    #        element_batch = model(element_batch)
    #
    #    yield from element_batch


class PaginatedPipeline(BasePipeline):  # TODO this is a bad name.

    def __init__(self, pipeline_options: PipelineOptions):
        super().__init__(pipeline_options)
        self.keep_backend = False

    def _apply_on_pages(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        for model in self.build_pipe:
            page_batch = model(conv_res, page_batch)

        yield from page_batch

    def _build_document(self, conv_res: ConversionResult) -> ConversionResult:

        if not isinstance(conv_res.input._backend, PdfDocumentBackend):
            raise RuntimeError(
                f"The selected backend {type(conv_res.input._backend).__name__} for {conv_res.input.file} is not a PDF backend. "
                f"Can not convert this with a PDF pipeline. "
                f"Please check your format configuration on DocumentConverter."
            )
            # conv_res.status = ConversionStatus.FAILURE
            # return conv_res

        total_elapsed_time = 0.0
        with TimeRecorder(conv_res, "doc_build", scope=ProfilingScope.DOCUMENT):

            for i in range(0, conv_res.input.page_count):
                start_page, end_page = conv_res.input.limits.page_range
                if (start_page - 1) <= i <= (end_page - 1):
                    conv_res.pages.append(Page(page_no=i))

            try:
                # Iterate batches of pages (page_batch_size) in the doc
                for page_batch in chunkify(
                    conv_res.pages, settings.perf.page_batch_size
                ):
                    start_batch_time = time.monotonic()

                    # 1. Initialise the page resources
                    init_pages = map(
                        functools.partial(self.initialize_page, conv_res), page_batch
                    )

                    # 2. Run pipeline stages
                    pipeline_pages = self._apply_on_pages(conv_res, init_pages)

                    for p in pipeline_pages:  # Must exhaust!

                        # Cleanup cached images
                        if not self.keep_images:
                            p._image_cache = {}

                        # Cleanup page backends
                        if not self.keep_backend and p._backend is not None:
                            p._backend.unload()

                    end_batch_time = time.monotonic()
                    total_elapsed_time += end_batch_time - start_batch_time
                    if (
                        self.pipeline_options.document_timeout is not None
                        and total_elapsed_time > self.pipeline_options.document_timeout
                    ):
                        _log.warning(
                            f"Document processing time ({total_elapsed_time:.3f} seconds) exceeded the specified timeout of {self.pipeline_options.document_timeout:.3f} seconds"
                        )
                        conv_res.status = ConversionStatus.PARTIAL_SUCCESS
                        break

                    _log.debug(
                        f"Finished converting page batch time={end_batch_time:.3f}"
                    )

            except Exception as e:
                conv_res.status = ConversionStatus.FAILURE
                trace = "\n".join(
                    traceback.format_exception(type(e), e, e.__traceback__)
                )
                _log.warning(
                    f"Encountered an error during conversion of document {conv_res.input.document_hash}:\n"
                    f"{trace}"
                )
                raise e

        return conv_res

    def _unload(self, conv_res: ConversionResult) -> ConversionResult:
        for page in conv_res.pages:
            if page._backend is not None:
                page._backend.unload()

        if conv_res.input._backend:
            conv_res.input._backend.unload()

        return conv_res

    def _determine_status(self, conv_res: ConversionResult) -> ConversionStatus:
        status = ConversionStatus.SUCCESS
        for page in conv_res.pages:
            if page._backend is None or not page._backend.is_valid():
                conv_res.errors.append(
                    ErrorItem(
                        component_type=DoclingComponentType.DOCUMENT_BACKEND,
                        module_name=type(page._backend).__name__,
                        error_message=f"Page {page.page_no} failed to parse.",
                    )
                )
                status = ConversionStatus.PARTIAL_SUCCESS

        return status

    # Initialise and load resources for a page
    @abstractmethod
    def initialize_page(self, conv_res: ConversionResult, page: Page) -> Page:
        pass

```
</content>
</file_45>

<file_46>
<path>pipeline/simple_pipeline.py</path>
<content>
```python
import logging

from docling.backend.abstract_backend import (
    AbstractDocumentBackend,
    DeclarativeDocumentBackend,
)
from docling.datamodel.base_models import ConversionStatus
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PipelineOptions
from docling.pipeline.base_pipeline import BasePipeline
from docling.utils.profiling import ProfilingScope, TimeRecorder

_log = logging.getLogger(__name__)


class SimplePipeline(BasePipeline):
    """SimpleModelPipeline.

    This class is used at the moment for formats / backends
    which produce straight DoclingDocument output.
    """

    def __init__(self, pipeline_options: PipelineOptions):
        super().__init__(pipeline_options)

    def _build_document(self, conv_res: ConversionResult) -> ConversionResult:

        if not isinstance(conv_res.input._backend, DeclarativeDocumentBackend):
            raise RuntimeError(
                f"The selected backend {type(conv_res.input._backend).__name__} for {conv_res.input.file} is not a declarative backend. "
                f"Can not convert this with simple pipeline. "
                f"Please check your format configuration on DocumentConverter."
            )
            # conv_res.status = ConversionStatus.FAILURE
            # return conv_res

        # Instead of running a page-level pipeline to build up the document structure,
        # the backend is expected to be of type DeclarativeDocumentBackend, which can output
        # a DoclingDocument straight.
        with TimeRecorder(conv_res, "doc_build", scope=ProfilingScope.DOCUMENT):
            conv_res.document = conv_res.input._backend.convert()
        return conv_res

    def _determine_status(self, conv_res: ConversionResult) -> ConversionStatus:
        # This is called only if the previous steps didn't raise.
        # Since we don't have anything else to evaluate, we can
        # safely return SUCCESS.
        return ConversionStatus.SUCCESS

    @classmethod
    def get_default_options(cls) -> PipelineOptions:
        return PipelineOptions()

    @classmethod
    def is_backend_supported(cls, backend: AbstractDocumentBackend):
        return isinstance(backend, DeclarativeDocumentBackend)

```
</content>
</file_46>

<file_47>
<path>pipeline/standard_pdf_pipeline.py</path>
<content>
```python
import logging
import sys
from pathlib import Path
from typing import Optional

from docling_core.types.doc import DocItem, ImageRef, PictureItem, TableItem

from docling.backend.abstract_backend import AbstractDocumentBackend
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.datamodel.base_models import AssembledUnit, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.models.base_ocr_model import BaseOcrModel
from docling.models.code_formula_model import CodeFormulaModel, CodeFormulaModelOptions
from docling.models.document_picture_classifier import (
    DocumentPictureClassifier,
    DocumentPictureClassifierOptions,
)
from docling.models.ds_glm_model import GlmModel, GlmOptions
from docling.models.easyocr_model import EasyOcrModel
from docling.models.layout_model import LayoutModel
from docling.models.ocr_mac_model import OcrMacModel
from docling.models.page_assemble_model import PageAssembleModel, PageAssembleOptions
from docling.models.page_preprocessing_model import (
    PagePreprocessingModel,
    PagePreprocessingOptions,
)
from docling.models.rapid_ocr_model import RapidOcrModel
from docling.models.table_structure_model import TableStructureModel
from docling.models.tesseract_ocr_cli_model import TesseractOcrCliModel
from docling.models.tesseract_ocr_model import TesseractOcrModel
from docling.pipeline.base_pipeline import PaginatedPipeline
from docling.utils.profiling import ProfilingScope, TimeRecorder

_log = logging.getLogger(__name__)


class StandardPdfPipeline(PaginatedPipeline):
    _layout_model_path = "model_artifacts/layout"
    _table_model_path = "model_artifacts/tableformer"

    def __init__(self, pipeline_options: PdfPipelineOptions):
        super().__init__(pipeline_options)
        self.pipeline_options: PdfPipelineOptions

        if pipeline_options.artifacts_path is None:
            self.artifacts_path = self.download_models_hf()
        else:
            self.artifacts_path = Path(pipeline_options.artifacts_path)

        self.keep_images = (
            self.pipeline_options.generate_page_images
            or self.pipeline_options.generate_picture_images
            or self.pipeline_options.generate_table_images
        )

        self.glm_model = GlmModel(options=GlmOptions())

        if (ocr_model := self.get_ocr_model()) is None:
            raise RuntimeError(
                f"The specified OCR kind is not supported: {pipeline_options.ocr_options.kind}."
            )

        self.build_pipe = [
            # Pre-processing
            PagePreprocessingModel(
                options=PagePreprocessingOptions(
                    images_scale=pipeline_options.images_scale
                )
            ),
            # OCR
            ocr_model,
            # Layout model
            LayoutModel(
                artifacts_path=self.artifacts_path
                / StandardPdfPipeline._layout_model_path,
                accelerator_options=pipeline_options.accelerator_options,
            ),
            # Table structure model
            TableStructureModel(
                enabled=pipeline_options.do_table_structure,
                artifacts_path=self.artifacts_path
                / StandardPdfPipeline._table_model_path,
                options=pipeline_options.table_structure_options,
                accelerator_options=pipeline_options.accelerator_options,
            ),
            # Page assemble
            PageAssembleModel(options=PageAssembleOptions()),
        ]

        self.enrichment_pipe = [
            # Other models working on `NodeItem` elements in the DoclingDocument
            # Code Formula Enrichment Model
            CodeFormulaModel(
                enabled=pipeline_options.do_code_enrichment
                or pipeline_options.do_formula_enrichment,
                artifacts_path=pipeline_options.artifacts_path,
                options=CodeFormulaModelOptions(
                    do_code_enrichment=pipeline_options.do_code_enrichment,
                    do_formula_enrichment=pipeline_options.do_formula_enrichment,
                ),
                accelerator_options=pipeline_options.accelerator_options,
            ),
            # Document Picture Classifier
            DocumentPictureClassifier(
                enabled=pipeline_options.do_picture_classification,
                artifacts_path=pipeline_options.artifacts_path,
                options=DocumentPictureClassifierOptions(),
                accelerator_options=pipeline_options.accelerator_options,
            ),
        ]

        if (
            self.pipeline_options.do_formula_enrichment
            or self.pipeline_options.do_code_enrichment
        ):
            self.keep_backend = True

    @staticmethod
    def download_models_hf(
        local_dir: Optional[Path] = None, force: bool = False
    ) -> Path:
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import disable_progress_bars

        disable_progress_bars()
        download_path = snapshot_download(
            repo_id="ds4sd/docling-models",
            force_download=force,
            local_dir=local_dir,
            revision="v2.1.0",
        )

        return Path(download_path)

    def get_ocr_model(self) -> Optional[BaseOcrModel]:
        if isinstance(self.pipeline_options.ocr_options, EasyOcrOptions):
            return EasyOcrModel(
                enabled=self.pipeline_options.do_ocr,
                options=self.pipeline_options.ocr_options,
                accelerator_options=self.pipeline_options.accelerator_options,
            )
        elif isinstance(self.pipeline_options.ocr_options, TesseractCliOcrOptions):
            return TesseractOcrCliModel(
                enabled=self.pipeline_options.do_ocr,
                options=self.pipeline_options.ocr_options,
            )
        elif isinstance(self.pipeline_options.ocr_options, TesseractOcrOptions):
            return TesseractOcrModel(
                enabled=self.pipeline_options.do_ocr,
                options=self.pipeline_options.ocr_options,
            )
        elif isinstance(self.pipeline_options.ocr_options, RapidOcrOptions):
            return RapidOcrModel(
                enabled=self.pipeline_options.do_ocr,
                options=self.pipeline_options.ocr_options,
                accelerator_options=self.pipeline_options.accelerator_options,
            )
        elif isinstance(self.pipeline_options.ocr_options, OcrMacOptions):
            if "darwin" != sys.platform:
                raise RuntimeError(
                    f"The specified OCR type is only supported on Mac: {self.pipeline_options.ocr_options.kind}."
                )
            return OcrMacModel(
                enabled=self.pipeline_options.do_ocr,
                options=self.pipeline_options.ocr_options,
            )
        return None

    def initialize_page(self, conv_res: ConversionResult, page: Page) -> Page:
        with TimeRecorder(conv_res, "page_init"):
            page._backend = conv_res.input._backend.load_page(page.page_no)  # type: ignore
            if page._backend is not None and page._backend.is_valid():
                page.size = page._backend.get_size()

        return page

    def _assemble_document(self, conv_res: ConversionResult) -> ConversionResult:
        all_elements = []
        all_headers = []
        all_body = []

        with TimeRecorder(conv_res, "doc_assemble", scope=ProfilingScope.DOCUMENT):
            for p in conv_res.pages:
                if p.assembled is not None:
                    for el in p.assembled.body:
                        all_body.append(el)
                    for el in p.assembled.headers:
                        all_headers.append(el)
                    for el in p.assembled.elements:
                        all_elements.append(el)

            conv_res.assembled = AssembledUnit(
                elements=all_elements, headers=all_headers, body=all_body
            )

            conv_res.document = self.glm_model(conv_res)

            # Generate page images in the output
            if self.pipeline_options.generate_page_images:
                for page in conv_res.pages:
                    assert page.image is not None
                    page_no = page.page_no + 1
                    conv_res.document.pages[page_no].image = ImageRef.from_pil(
                        page.image, dpi=int(72 * self.pipeline_options.images_scale)
                    )

            # Generate images of the requested element types
            if (
                self.pipeline_options.generate_picture_images
                or self.pipeline_options.generate_table_images
            ):
                scale = self.pipeline_options.images_scale
                for element, _level in conv_res.document.iterate_items():
                    if not isinstance(element, DocItem) or len(element.prov) == 0:
                        continue
                    if (
                        isinstance(element, PictureItem)
                        and self.pipeline_options.generate_picture_images
                    ) or (
                        isinstance(element, TableItem)
                        and self.pipeline_options.generate_table_images
                    ):
                        page_ix = element.prov[0].page_no - 1
                        page = conv_res.pages[page_ix]
                        assert page.size is not None
                        assert page.image is not None

                        crop_bbox = (
                            element.prov[0]
                            .bbox.scaled(scale=scale)
                            .to_top_left_origin(page_height=page.size.height * scale)
                        )

                        cropped_im = page.image.crop(crop_bbox.as_tuple())
                        element.image = ImageRef.from_pil(
                            cropped_im, dpi=int(72 * scale)
                        )

        return conv_res

    @classmethod
    def get_default_options(cls) -> PdfPipelineOptions:
        return PdfPipelineOptions()

    @classmethod
    def is_backend_supported(cls, backend: AbstractDocumentBackend):
        return isinstance(backend, PdfDocumentBackend)

```
</content>
</file_47>

<file_48>
<path>py.typed</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_48>

<file_49>
<path>utils/__init__.py</path>
<content>
```python

```
</content>
</file_49>

<file_50>
<path>utils/accelerator_utils.py</path>
<content>
```python
import logging

import torch

from docling.datamodel.pipeline_options import AcceleratorDevice

_log = logging.getLogger(__name__)


def decide_device(accelerator_device: AcceleratorDevice) -> str:
    r"""
    Resolve the device based on the acceleration options and the available devices in the system
    Rules:
    1. AUTO: Check for the best available device on the system.
    2. User-defined: Check if the device actually exists, otherwise fall-back to CPU
    """
    cuda_index = 0
    device = "cpu"

    has_cuda = torch.backends.cuda.is_built() and torch.cuda.is_available()
    has_mps = torch.backends.mps.is_built() and torch.backends.mps.is_available()

    if accelerator_device == AcceleratorDevice.AUTO:
        if has_cuda:
            device = f"cuda:{cuda_index}"
        elif has_mps:
            device = "mps"

    else:
        if accelerator_device == AcceleratorDevice.CUDA:
            if has_cuda:
                device = f"cuda:{cuda_index}"
            else:
                _log.warning("CUDA is not available in the system. Fall back to 'CPU'")
        elif accelerator_device == AcceleratorDevice.MPS:
            if has_mps:
                device = "mps"
            else:
                _log.warning("MPS is not available in the system. Fall back to 'CPU'")

    _log.info("Accelerator device: '%s'", device)
    return device

```
</content>
</file_50>

<file_51>
<path>utils/export.py</path>
<content>
```python
import logging
from typing import Any, Dict, Iterable, List, Tuple, Union

from docling_core.types.doc import BoundingBox, CoordOrigin
from docling_core.types.legacy_doc.base import BaseCell, BaseText, Ref, Table

from docling.datamodel.base_models import OcrCell
from docling.datamodel.document import ConversionResult, Page

_log = logging.getLogger(__name__)


def generate_multimodal_pages(
    doc_result: ConversionResult,
) -> Iterable[Tuple[str, str, List[Dict[str, Any]], List[Dict[str, Any]], Page]]:

    label_to_doclaynet = {
        "title": "title",
        "table-of-contents": "document_index",
        "subtitle-level-1": "section_header",
        "checkbox-selected": "checkbox_selected",
        "checkbox-unselected": "checkbox_unselected",
        "caption": "caption",
        "page-header": "page_header",
        "page-footer": "page_footer",
        "footnote": "footnote",
        "table": "table",
        "formula": "formula",
        "list-item": "list_item",
        "code": "code",
        "figure": "picture",
        "picture": "picture",
        "reference": "text",
        "paragraph": "text",
        "text": "text",
    }

    content_text = ""
    page_no = 0
    start_ix = 0
    end_ix = 0
    doc_items: List[Tuple[int, Union[BaseCell, BaseText]]] = []

    doc = doc_result.legacy_document

    def _process_page_segments(doc_items: list[Tuple[int, BaseCell]], page: Page):
        segments = []

        for ix, item in doc_items:
            item_type = item.obj_type
            label = label_to_doclaynet.get(item_type, None)

            if label is None or item.prov is None or page.size is None:
                continue

            bbox = BoundingBox.from_tuple(
                tuple(item.prov[0].bbox), origin=CoordOrigin.BOTTOMLEFT
            )
            new_bbox = bbox.to_top_left_origin(page_height=page.size.height).normalized(
                page_size=page.size
            )

            new_segment = {
                "index_in_doc": ix,
                "label": label,
                "text": item.text if item.text is not None else "",
                "bbox": new_bbox.as_tuple(),
                "data": [],
            }

            if isinstance(item, Table):
                table_html = item.export_to_html()
                new_segment["data"].append(
                    {
                        "html_seq": table_html,
                        "otsl_seq": "",
                    }
                )

            segments.append(new_segment)

        return segments

    def _process_page_cells(page: Page):
        cells: List[dict] = []
        if page.size is None:
            return cells
        for cell in page.cells:
            new_bbox = cell.bbox.to_top_left_origin(
                page_height=page.size.height
            ).normalized(page_size=page.size)
            is_ocr = isinstance(cell, OcrCell)
            ocr_confidence = cell.confidence if isinstance(cell, OcrCell) else 1.0
            cells.append(
                {
                    "text": cell.text,
                    "bbox": new_bbox.as_tuple(),
                    "ocr": is_ocr,
                    "ocr_confidence": ocr_confidence,
                }
            )
        return cells

    def _process_page():
        page_ix = page_no - 1
        page = doc_result.pages[page_ix]

        page_cells = _process_page_cells(page=page)
        page_segments = _process_page_segments(doc_items=doc_items, page=page)
        content_md = doc.export_to_markdown(
            main_text_start=start_ix, main_text_stop=end_ix
        )
        # No page-tagging since we only do 1 page at the time
        content_dt = doc.export_to_document_tokens(
            main_text_start=start_ix, main_text_stop=end_ix, add_page_index=False
        )

        return content_text, content_md, content_dt, page_cells, page_segments, page

    if doc.main_text is None:
        return
    for ix, orig_item in enumerate(doc.main_text):

        item = doc._resolve_ref(orig_item) if isinstance(orig_item, Ref) else orig_item
        if item is None or item.prov is None or len(item.prov) == 0:
            _log.debug(f"Skipping item {orig_item}")
            continue

        item_page = item.prov[0].page

        # Page is complete
        if page_no > 0 and item_page > page_no:
            yield _process_page()

            start_ix = ix
            doc_items = []
            content_text = ""

        page_no = item_page
        end_ix = ix
        doc_items.append((ix, item))
        if item.text is not None and item.text != "":
            content_text += item.text + " "

    if len(doc_items) > 0:
        yield _process_page()

```
</content>
</file_51>

<file_52>
<path>utils/glm_utils.py</path>
<content>
```python
import re
from pathlib import Path
from typing import List

import pandas as pd
from docling_core.types.doc import (
    BoundingBox,
    CoordOrigin,
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    GroupLabel,
    ProvenanceItem,
    Size,
    TableCell,
    TableData,
)


def resolve_item(paths, obj):
    """Find item in document from a reference path"""

    if len(paths) == 0:
        return obj

    if paths[0] == "#":
        return resolve_item(paths[1:], obj)

    try:
        key = int(paths[0])
    except:
        key = paths[0]

    if len(paths) == 1:
        if isinstance(key, str) and key in obj:
            return obj[key]
        elif isinstance(key, int) and key < len(obj):
            return obj[key]
        else:
            return None

    elif len(paths) > 1:
        if isinstance(key, str) and key in obj:
            return resolve_item(paths[1:], obj[key])
        elif isinstance(key, int) and key < len(obj):
            return resolve_item(paths[1:], obj[key])
        else:
            return None

    else:
        return None


def _flatten_table_grid(grid: List[List[dict]]) -> List[dict]:
    unique_objects = []
    seen_spans = set()

    for sublist in grid:
        for obj in sublist:
            # Convert the spans list to a tuple of tuples for hashing
            spans_tuple = tuple(tuple(span) for span in obj["spans"])
            if spans_tuple not in seen_spans:
                seen_spans.add(spans_tuple)
                unique_objects.append(obj)

    return unique_objects


def to_docling_document(doc_glm, update_name_label=False) -> DoclingDocument:
    origin = DocumentOrigin(
        mimetype="application/pdf",
        filename=doc_glm["file-info"]["filename"],
        binary_hash=doc_glm["file-info"]["document-hash"],
    )
    doc_name = Path(origin.filename).stem

    doc: DoclingDocument = DoclingDocument(name=doc_name, origin=origin)

    for page_dim in doc_glm["page-dimensions"]:
        page_no = int(page_dim["page"])
        size = Size(width=page_dim["width"], height=page_dim["height"])

        doc.add_page(page_no=page_no, size=size)

    if "properties" in doc_glm:
        props = pd.DataFrame(
            doc_glm["properties"]["data"], columns=doc_glm["properties"]["headers"]
        )
    else:
        props = pd.DataFrame()

    current_list = None

    for ix, pelem in enumerate(doc_glm["page-elements"]):
        ptype = pelem["type"]
        span_i = pelem["span"][0]
        span_j = pelem["span"][1]

        if "iref" not in pelem:
            # print(json.dumps(pelem, indent=2))
            continue

        iref = pelem["iref"]

        if re.match("#/figures/(\\d+)/captions/(.+)", iref):
            # print(f"skip {iref}")
            continue

        if re.match("#/tables/(\\d+)/captions/(.+)", iref):
            # print(f"skip {iref}")
            continue

        path = iref.split("/")
        obj = resolve_item(path, doc_glm)

        if obj is None:
            current_list = None
            print(f"warning: undefined {path}")
            continue

        if ptype == "figure":
            current_list = None
            text = ""
            caption_refs = []
            for caption in obj["captions"]:
                text += caption["text"]

                for nprov in caption["prov"]:
                    npaths = nprov["$ref"].split("/")
                    nelem = resolve_item(npaths, doc_glm)

                    if nelem is None:
                        # print(f"warning: undefined caption {npaths}")
                        continue

                    span_i = nelem["span"][0]
                    span_j = nelem["span"][1]

                    cap_text = caption["text"][span_i:span_j]

                    # doc_glm["page-elements"].remove(nelem)

                    prov = ProvenanceItem(
                        page_no=nelem["page"],
                        charspan=tuple(nelem["span"]),
                        bbox=BoundingBox.from_tuple(
                            nelem["bbox"], origin=CoordOrigin.BOTTOMLEFT
                        ),
                    )

                    caption_obj = doc.add_text(
                        label=DocItemLabel.CAPTION, text=cap_text, prov=prov
                    )
                    caption_refs.append(caption_obj.get_ref())

            prov = ProvenanceItem(
                page_no=pelem["page"],
                charspan=(0, len(text)),
                bbox=BoundingBox.from_tuple(
                    pelem["bbox"], origin=CoordOrigin.BOTTOMLEFT
                ),
            )

            pic = doc.add_picture(prov=prov)
            pic.captions.extend(caption_refs)
            _add_child_elements(pic, doc, obj, pelem)

        elif ptype == "table":
            current_list = None
            text = ""
            caption_refs = []
            item_label = DocItemLabel(pelem["name"])

            for caption in obj["captions"]:
                text += caption["text"]

                for nprov in caption["prov"]:
                    npaths = nprov["$ref"].split("/")
                    nelem = resolve_item(npaths, doc_glm)

                    if nelem is None:
                        # print(f"warning: undefined caption {npaths}")
                        continue

                    span_i = nelem["span"][0]
                    span_j = nelem["span"][1]

                    cap_text = caption["text"][span_i:span_j]

                    # doc_glm["page-elements"].remove(nelem)

                    prov = ProvenanceItem(
                        page_no=nelem["page"],
                        charspan=tuple(nelem["span"]),
                        bbox=BoundingBox.from_tuple(
                            nelem["bbox"], origin=CoordOrigin.BOTTOMLEFT
                        ),
                    )

                    caption_obj = doc.add_text(
                        label=DocItemLabel.CAPTION, text=cap_text, prov=prov
                    )
                    caption_refs.append(caption_obj.get_ref())

            table_cells_glm = _flatten_table_grid(obj["data"])

            table_cells = []
            for tbl_cell_glm in table_cells_glm:
                if tbl_cell_glm["bbox"] is not None:
                    bbox = BoundingBox.from_tuple(
                        tbl_cell_glm["bbox"], origin=CoordOrigin.BOTTOMLEFT
                    )
                else:
                    bbox = None

                is_col_header = False
                is_row_header = False
                is_row_section = False

                if tbl_cell_glm["type"] == "col_header":
                    is_col_header = True
                elif tbl_cell_glm["type"] == "row_header":
                    is_row_header = True
                elif tbl_cell_glm["type"] == "row_section":
                    is_row_section = True

                table_cells.append(
                    TableCell(
                        row_span=tbl_cell_glm["row-span"][1]
                        - tbl_cell_glm["row-span"][0],
                        col_span=tbl_cell_glm["col-span"][1]
                        - tbl_cell_glm["col-span"][0],
                        start_row_offset_idx=tbl_cell_glm["row-span"][0],
                        end_row_offset_idx=tbl_cell_glm["row-span"][1],
                        start_col_offset_idx=tbl_cell_glm["col-span"][0],
                        end_col_offset_idx=tbl_cell_glm["col-span"][1],
                        text=tbl_cell_glm["text"],
                        bbox=bbox,
                        column_header=is_col_header,
                        row_header=is_row_header,
                        row_section=is_row_section,
                    )
                )

            tbl_data = TableData(
                num_rows=obj.get("#-rows", 0),
                num_cols=obj.get("#-cols", 0),
                table_cells=table_cells,
            )

            prov = ProvenanceItem(
                page_no=pelem["page"],
                charspan=(0, 0),
                bbox=BoundingBox.from_tuple(
                    pelem["bbox"], origin=CoordOrigin.BOTTOMLEFT
                ),
            )

            tbl = doc.add_table(data=tbl_data, prov=prov, label=item_label)
            tbl.captions.extend(caption_refs)

        elif ptype in [DocItemLabel.FORM.value, DocItemLabel.KEY_VALUE_REGION.value]:
            label = DocItemLabel(ptype)
            group_label = GroupLabel.UNSPECIFIED
            if label == DocItemLabel.FORM:
                group_label = GroupLabel.FORM_AREA
            elif label == DocItemLabel.KEY_VALUE_REGION:
                group_label = GroupLabel.KEY_VALUE_AREA

            container_el = doc.add_group(label=group_label)

            _add_child_elements(container_el, doc, obj, pelem)
        elif "text" in obj:
            text = obj["text"][span_i:span_j]

            type_label = pelem["type"]
            name_label = pelem["name"]
            if update_name_label and len(props) > 0 and type_label == "paragraph":
                prop = props[
                    (props["type"] == "semantic") & (props["subj_path"] == iref)
                ]
                if len(prop) == 1 and prop.iloc[0]["confidence"] > 0.85:
                    name_label = prop.iloc[0]["label"]

            prov = ProvenanceItem(
                page_no=pelem["page"],
                charspan=(0, len(text)),
                bbox=BoundingBox.from_tuple(
                    pelem["bbox"], origin=CoordOrigin.BOTTOMLEFT
                ),
            )
            label = DocItemLabel(name_label)

            if label == DocItemLabel.LIST_ITEM:
                if current_list is None:
                    current_list = doc.add_group(label=GroupLabel.LIST, name="list")

                # TODO: Infer if this is a numbered or a bullet list item
                doc.add_list_item(
                    text=text, enumerated=False, prov=prov, parent=current_list
                )
            elif label == DocItemLabel.SECTION_HEADER:
                current_list = None

                doc.add_heading(text=text, prov=prov)
            elif label == DocItemLabel.CODE:
                current_list = None

                doc.add_code(text=text, prov=prov)
            elif label == DocItemLabel.FORMULA:
                current_list = None

                doc.add_text(label=DocItemLabel.FORMULA, text="", orig=text, prov=prov)
            else:
                current_list = None

                doc.add_text(label=DocItemLabel(name_label), text=text, prov=prov)

    return doc


def _add_child_elements(container_el, doc, obj, pelem):
    payload = obj.get("payload")
    if payload is not None:
        children = payload.get("children", [])

        for child in children:
            c_label = DocItemLabel(child["label"])
            c_bbox = BoundingBox.model_validate(child["bbox"]).to_bottom_left_origin(
                doc.pages[pelem["page"]].size.height
            )
            c_text = " ".join(
                [
                    cell["text"].replace("\x02", "-").strip()
                    for cell in child["cells"]
                    if len(cell["text"].strip()) > 0
                ]
            )

            c_prov = ProvenanceItem(
                page_no=pelem["page"], charspan=(0, len(c_text)), bbox=c_bbox
            )
            if c_label == DocItemLabel.LIST_ITEM:
                # TODO: Infer if this is a numbered or a bullet list item
                doc.add_list_item(parent=container_el, text=c_text, prov=c_prov)
            elif c_label == DocItemLabel.SECTION_HEADER:
                doc.add_heading(parent=container_el, text=c_text, prov=c_prov)
            else:
                doc.add_text(
                    parent=container_el, label=c_label, text=c_text, prov=c_prov
                )

```
</content>
</file_52>

<file_53>
<path>utils/layout_postprocessor.py</path>
<content>
```python
import bisect
import logging
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from docling_core.types.doc import DocItemLabel, Size
from rtree import index

from docling.datamodel.base_models import BoundingBox, Cell, Cluster, OcrCell

_log = logging.getLogger(__name__)


class UnionFind:
    """Efficient Union-Find data structure for grouping elements."""

    def __init__(self, elements):
        self.parent = {elem: elem for elem in elements}
        self.rank = {elem: 0 for elem in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return

        if self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        elif self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

    def get_groups(self) -> Dict[int, List[int]]:
        """Returns groups as {root: [elements]}."""
        groups = defaultdict(list)
        for elem in self.parent:
            groups[self.find(elem)].append(elem)
        return groups


class SpatialClusterIndex:
    """Efficient spatial indexing for clusters using R-tree and interval trees."""

    def __init__(self, clusters: List[Cluster]):
        p = index.Property()
        p.dimension = 2
        self.spatial_index = index.Index(properties=p)
        self.x_intervals = IntervalTree()
        self.y_intervals = IntervalTree()
        self.clusters_by_id: Dict[int, Cluster] = {}

        for cluster in clusters:
            self.add_cluster(cluster)

    def add_cluster(self, cluster: Cluster):
        bbox = cluster.bbox
        self.spatial_index.insert(cluster.id, bbox.as_tuple())
        self.x_intervals.insert(bbox.l, bbox.r, cluster.id)
        self.y_intervals.insert(bbox.t, bbox.b, cluster.id)
        self.clusters_by_id[cluster.id] = cluster

    def remove_cluster(self, cluster: Cluster):
        self.spatial_index.delete(cluster.id, cluster.bbox.as_tuple())
        del self.clusters_by_id[cluster.id]

    def find_candidates(self, bbox: BoundingBox) -> Set[int]:
        """Find potential overlapping cluster IDs using all indexes."""
        spatial = set(self.spatial_index.intersection(bbox.as_tuple()))
        x_candidates = self.x_intervals.find_containing(
            bbox.l
        ) | self.x_intervals.find_containing(bbox.r)
        y_candidates = self.y_intervals.find_containing(
            bbox.t
        ) | self.y_intervals.find_containing(bbox.b)
        return spatial.union(x_candidates).union(y_candidates)

    def check_overlap(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox,
        overlap_threshold: float,
        containment_threshold: float,
    ) -> bool:
        """Check if two bboxes overlap sufficiently."""
        area1, area2 = bbox1.area(), bbox2.area()
        if area1 <= 0 or area2 <= 0:
            return False

        overlap_area = bbox1.intersection_area_with(bbox2)
        if overlap_area <= 0:
            return False

        iou = overlap_area / (area1 + area2 - overlap_area)
        containment1 = overlap_area / area1
        containment2 = overlap_area / area2

        return (
            iou > overlap_threshold
            or containment1 > containment_threshold
            or containment2 > containment_threshold
        )


class Interval:
    """Helper class for sortable intervals."""

    def __init__(self, min_val: float, max_val: float, id: int):
        self.min_val = min_val
        self.max_val = max_val
        self.id = id

    def __lt__(self, other):
        if isinstance(other, Interval):
            return self.min_val < other.min_val
        return self.min_val < other


class IntervalTree:
    """Memory-efficient interval tree for 1D overlap queries."""

    def __init__(self):
        self.intervals: List[Interval] = []  # Sorted by min_val

    def insert(self, min_val: float, max_val: float, id: int):
        interval = Interval(min_val, max_val, id)
        bisect.insort(self.intervals, interval)

    def find_containing(self, point: float) -> Set[int]:
        """Find all intervals containing the point."""
        pos = bisect.bisect_left(self.intervals, point)
        result = set()

        # Check intervals starting before point
        for interval in reversed(self.intervals[:pos]):
            if interval.min_val <= point <= interval.max_val:
                result.add(interval.id)
            else:
                break

        # Check intervals starting at/after point
        for interval in self.intervals[pos:]:
            if point <= interval.max_val:
                if interval.min_val <= point:
                    result.add(interval.id)
            else:
                break

        return result


class LayoutPostprocessor:
    """Postprocesses layout predictions by cleaning up clusters and mapping cells."""

    # Cluster type-specific parameters for overlap resolution
    OVERLAP_PARAMS = {
        "regular": {"area_threshold": 1.3, "conf_threshold": 0.05},
        "picture": {"area_threshold": 2.0, "conf_threshold": 0.3},
        "wrapper": {"area_threshold": 2.0, "conf_threshold": 0.2},
    }

    WRAPPER_TYPES = {
        DocItemLabel.FORM,
        DocItemLabel.KEY_VALUE_REGION,
        DocItemLabel.TABLE,
        DocItemLabel.DOCUMENT_INDEX,
    }
    SPECIAL_TYPES = WRAPPER_TYPES.union({DocItemLabel.PICTURE})

    CONFIDENCE_THRESHOLDS = {
        DocItemLabel.CAPTION: 0.5,
        DocItemLabel.FOOTNOTE: 0.5,
        DocItemLabel.FORMULA: 0.5,
        DocItemLabel.LIST_ITEM: 0.5,
        DocItemLabel.PAGE_FOOTER: 0.5,
        DocItemLabel.PAGE_HEADER: 0.5,
        DocItemLabel.PICTURE: 0.5,
        DocItemLabel.SECTION_HEADER: 0.45,
        DocItemLabel.TABLE: 0.5,
        DocItemLabel.TEXT: 0.5,  # 0.45,
        DocItemLabel.TITLE: 0.45,
        DocItemLabel.CODE: 0.45,
        DocItemLabel.CHECKBOX_SELECTED: 0.45,
        DocItemLabel.CHECKBOX_UNSELECTED: 0.45,
        DocItemLabel.FORM: 0.45,
        DocItemLabel.KEY_VALUE_REGION: 0.45,
        DocItemLabel.DOCUMENT_INDEX: 0.45,
    }

    LABEL_REMAPPING = {
        # DocItemLabel.DOCUMENT_INDEX: DocItemLabel.TABLE,
        DocItemLabel.TITLE: DocItemLabel.SECTION_HEADER,
    }

    def __init__(self, cells: List[Cell], clusters: List[Cluster], page_size: Size):
        """Initialize processor with cells and clusters."""
        """Initialize processor with cells and spatial indices."""
        self.cells = cells
        self.page_size = page_size
        self.regular_clusters = [
            c for c in clusters if c.label not in self.SPECIAL_TYPES
        ]
        self.special_clusters = [c for c in clusters if c.label in self.SPECIAL_TYPES]

        # Build spatial indices once
        self.regular_index = SpatialClusterIndex(self.regular_clusters)
        self.picture_index = SpatialClusterIndex(
            [c for c in self.special_clusters if c.label == DocItemLabel.PICTURE]
        )
        self.wrapper_index = SpatialClusterIndex(
            [c for c in self.special_clusters if c.label in self.WRAPPER_TYPES]
        )

    def postprocess(self) -> Tuple[List[Cluster], List[Cell]]:
        """Main processing pipeline."""
        self.regular_clusters = self._process_regular_clusters()
        self.special_clusters = self._process_special_clusters()

        # Remove regular clusters that are included in wrappers
        contained_ids = {
            child.id
            for wrapper in self.special_clusters
            if wrapper.label in self.SPECIAL_TYPES
            for child in wrapper.children
        }
        self.regular_clusters = [
            c for c in self.regular_clusters if c.id not in contained_ids
        ]

        # Combine and sort final clusters
        final_clusters = self._sort_clusters(
            self.regular_clusters + self.special_clusters, mode="id"
        )
        for cluster in final_clusters:
            cluster.cells = self._sort_cells(cluster.cells)
            # Also sort cells in children if any
            for child in cluster.children:
                child.cells = self._sort_cells(child.cells)

        return final_clusters, self.cells

    def _process_regular_clusters(self) -> List[Cluster]:
        """Process regular clusters with iterative refinement."""
        clusters = [
            c
            for c in self.regular_clusters
            if c.confidence >= self.CONFIDENCE_THRESHOLDS[c.label]
        ]

        # Apply label remapping
        for cluster in clusters:
            if cluster.label in self.LABEL_REMAPPING:
                cluster.label = self.LABEL_REMAPPING[cluster.label]

        # Initial cell assignment
        clusters = self._assign_cells_to_clusters(clusters)

        # Remove clusters with no cells
        clusters = [cluster for cluster in clusters if cluster.cells]

        # Handle orphaned cells
        unassigned = self._find_unassigned_cells(clusters)
        if unassigned:
            next_id = max((c.id for c in clusters), default=0) + 1
            orphan_clusters = []
            for i, cell in enumerate(unassigned):
                conf = 1.0
                if isinstance(cell, OcrCell):
                    conf = cell.confidence

                orphan_clusters.append(
                    Cluster(
                        id=next_id + i,
                        label=DocItemLabel.TEXT,
                        bbox=cell.bbox,
                        confidence=conf,
                        cells=[cell],
                    )
                )
            clusters.extend(orphan_clusters)

        # Iterative refinement
        prev_count = len(clusters) + 1
        for _ in range(3):  # Maximum 3 iterations
            if prev_count == len(clusters):
                break
            prev_count = len(clusters)
            clusters = self._adjust_cluster_bboxes(clusters)
            clusters = self._remove_overlapping_clusters(clusters, "regular")

        return clusters

    def _process_special_clusters(self) -> List[Cluster]:
        special_clusters = [
            c
            for c in self.special_clusters
            if c.confidence >= self.CONFIDENCE_THRESHOLDS[c.label]
        ]

        special_clusters = self._handle_cross_type_overlaps(special_clusters)

        # Calculate page area from known page size
        page_area = self.page_size.width * self.page_size.height
        if page_area > 0:
            # Filter out full-page pictures
            special_clusters = [
                cluster
                for cluster in special_clusters
                if not (
                    cluster.label == DocItemLabel.PICTURE
                    and cluster.bbox.area() / page_area > 0.90
                )
            ]

        for special in special_clusters:
            contained = []
            for cluster in self.regular_clusters:
                overlap = cluster.bbox.intersection_area_with(special.bbox)
                if overlap > 0:
                    containment = overlap / cluster.bbox.area()
                    if containment > 0.8:
                        contained.append(cluster)

            if contained:
                # Sort contained clusters by minimum cell ID:
                contained = self._sort_clusters(contained, mode="id")
                special.children = contained

                # Adjust bbox only for Form and Key-Value-Region, not Table or Picture
                if special.label in [DocItemLabel.FORM, DocItemLabel.KEY_VALUE_REGION]:
                    special.bbox = BoundingBox(
                        l=min(c.bbox.l for c in contained),
                        t=min(c.bbox.t for c in contained),
                        r=max(c.bbox.r for c in contained),
                        b=max(c.bbox.b for c in contained),
                    )

                # Collect all cells from children
                all_cells = []
                for child in contained:
                    all_cells.extend(child.cells)
                special.cells = self._deduplicate_cells(all_cells)
                special.cells = self._sort_cells(special.cells)

        picture_clusters = [
            c for c in special_clusters if c.label == DocItemLabel.PICTURE
        ]
        picture_clusters = self._remove_overlapping_clusters(
            picture_clusters, "picture"
        )

        wrapper_clusters = [
            c for c in special_clusters if c.label in self.WRAPPER_TYPES
        ]
        wrapper_clusters = self._remove_overlapping_clusters(
            wrapper_clusters, "wrapper"
        )

        return picture_clusters + wrapper_clusters

    def _handle_cross_type_overlaps(self, special_clusters) -> List[Cluster]:
        """Handle overlaps between regular and wrapper clusters before child assignment.

        In particular, KEY_VALUE_REGION proposals that are almost identical to a TABLE
        should be removed.
        """
        wrappers_to_remove = set()

        for wrapper in special_clusters:
            if wrapper.label not in self.WRAPPER_TYPES:
                continue  # only treat KEY_VALUE_REGION for now.

            for regular in self.regular_clusters:
                if regular.label == DocItemLabel.TABLE:
                    # Calculate overlap
                    overlap = regular.bbox.intersection_area_with(wrapper.bbox)
                    wrapper_area = wrapper.bbox.area()
                    overlap_ratio = overlap / wrapper_area

                    conf_diff = wrapper.confidence - regular.confidence

                    # If wrapper is mostly overlapping with a TABLE, remove the wrapper
                    if (
                        overlap_ratio > 0.9 and conf_diff < 0.1
                    ):  # self.OVERLAP_PARAMS["wrapper"]["conf_threshold"]):  # 80% overlap threshold
                        wrappers_to_remove.add(wrapper.id)
                        break

        # Filter out the identified wrappers
        special_clusters = [
            cluster
            for cluster in special_clusters
            if cluster.id not in wrappers_to_remove
        ]

        return special_clusters

    def _should_prefer_cluster(
        self, candidate: Cluster, other: Cluster, params: dict
    ) -> bool:
        """Determine if candidate cluster should be preferred over other cluster based on rules.
        Returns True if candidate should be preferred, False if not."""

        # Rule 1: LIST_ITEM vs TEXT
        if (
            candidate.label == DocItemLabel.LIST_ITEM
            and other.label == DocItemLabel.TEXT
        ):
            # Check if areas are similar (within 20% of each other)
            area_ratio = candidate.bbox.area() / other.bbox.area()
            area_similarity = abs(1 - area_ratio) < 0.2
            if area_similarity:
                return True

        # Rule 2: CODE vs others
        if candidate.label == DocItemLabel.CODE:
            # Calculate how much of the other cluster is contained within the CODE cluster
            overlap = other.bbox.intersection_area_with(candidate.bbox)
            containment = overlap / other.bbox.area()
            if containment > 0.8:  # other is 80% contained within CODE
                return True

        # If no label-based rules matched, fall back to area/confidence thresholds
        area_ratio = candidate.bbox.area() / other.bbox.area()
        conf_diff = other.confidence - candidate.confidence

        if (
            area_ratio <= params["area_threshold"]
            and conf_diff > params["conf_threshold"]
        ):
            return False

        return True  # Default to keeping candidate if no rules triggered rejection

    def _select_best_cluster_from_group(
        self,
        group_clusters: List[Cluster],
        params: dict,
    ) -> Cluster:
        """Select best cluster from a group of overlapping clusters based on all rules."""
        current_best = None

        for candidate in group_clusters:
            should_select = True

            for other in group_clusters:
                if other == candidate:
                    continue

                if not self._should_prefer_cluster(candidate, other, params):
                    should_select = False
                    break

            if should_select:
                if current_best is None:
                    current_best = candidate
                else:
                    # If both clusters pass rules, prefer the larger one unless confidence differs significantly
                    if (
                        candidate.bbox.area() > current_best.bbox.area()
                        and current_best.confidence - candidate.confidence
                        <= params["conf_threshold"]
                    ):
                        current_best = candidate

        return current_best if current_best else group_clusters[0]

    def _remove_overlapping_clusters(
        self,
        clusters: List[Cluster],
        cluster_type: str,
        overlap_threshold: float = 0.8,
        containment_threshold: float = 0.8,
    ) -> List[Cluster]:
        if not clusters:
            return []

        spatial_index = (
            self.regular_index
            if cluster_type == "regular"
            else self.picture_index if cluster_type == "picture" else self.wrapper_index
        )

        # Map of currently valid clusters
        valid_clusters = {c.id: c for c in clusters}
        uf = UnionFind(valid_clusters.keys())
        params = self.OVERLAP_PARAMS[cluster_type]

        for cluster in clusters:
            candidates = spatial_index.find_candidates(cluster.bbox)
            candidates &= valid_clusters.keys()  # Only keep existing candidates
            candidates.discard(cluster.id)

            for other_id in candidates:
                if spatial_index.check_overlap(
                    cluster.bbox,
                    valid_clusters[other_id].bbox,
                    overlap_threshold,
                    containment_threshold,
                ):
                    uf.union(cluster.id, other_id)

        result = []
        for group in uf.get_groups().values():
            if len(group) == 1:
                result.append(valid_clusters[group[0]])
                continue

            group_clusters = [valid_clusters[cid] for cid in group]
            best = self._select_best_cluster_from_group(group_clusters, params)

            # Simple cell merging - no special cases
            for cluster in group_clusters:
                if cluster != best:
                    best.cells.extend(cluster.cells)

            best.cells = self._deduplicate_cells(best.cells)
            best.cells = self._sort_cells(best.cells)
            result.append(best)

        return result

    def _select_best_cluster(
        self,
        clusters: List[Cluster],
        area_threshold: float,
        conf_threshold: float,
    ) -> Cluster:
        """Iteratively select best cluster based on area and confidence thresholds."""
        current_best = None
        for candidate in clusters:
            should_select = True
            for other in clusters:
                if other == candidate:
                    continue

                area_ratio = candidate.bbox.area() / other.bbox.area()
                conf_diff = other.confidence - candidate.confidence

                if area_ratio <= area_threshold and conf_diff > conf_threshold:
                    should_select = False
                    break

            if should_select:
                if current_best is None or (
                    candidate.bbox.area() > current_best.bbox.area()
                    and current_best.confidence - candidate.confidence <= conf_threshold
                ):
                    current_best = candidate

        return current_best if current_best else clusters[0]

    def _deduplicate_cells(self, cells: List[Cell]) -> List[Cell]:
        """Ensure each cell appears only once, maintaining order of first appearance."""
        seen_ids = set()
        unique_cells = []
        for cell in cells:
            if cell.id not in seen_ids:
                seen_ids.add(cell.id)
                unique_cells.append(cell)
        return unique_cells

    def _assign_cells_to_clusters(
        self, clusters: List[Cluster], min_overlap: float = 0.2
    ) -> List[Cluster]:
        """Assign cells to best overlapping cluster."""
        for cluster in clusters:
            cluster.cells = []

        for cell in self.cells:
            if not cell.text.strip():
                continue

            best_overlap = min_overlap
            best_cluster = None

            for cluster in clusters:
                if cell.bbox.area() <= 0:
                    continue

                overlap = cell.bbox.intersection_area_with(cluster.bbox)
                overlap_ratio = overlap / cell.bbox.area()

                if overlap_ratio > best_overlap:
                    best_overlap = overlap_ratio
                    best_cluster = cluster

            if best_cluster is not None:
                best_cluster.cells.append(cell)

        # Deduplicate cells in each cluster after assignment
        for cluster in clusters:
            cluster.cells = self._deduplicate_cells(cluster.cells)

        return clusters

    def _find_unassigned_cells(self, clusters: List[Cluster]) -> List[Cell]:
        """Find cells not assigned to any cluster."""
        assigned = {cell.id for cluster in clusters for cell in cluster.cells}
        return [
            cell for cell in self.cells if cell.id not in assigned and cell.text.strip()
        ]

    def _adjust_cluster_bboxes(self, clusters: List[Cluster]) -> List[Cluster]:
        """Adjust cluster bounding boxes to contain their cells."""
        for cluster in clusters:
            if not cluster.cells:
                continue

            cells_bbox = BoundingBox(
                l=min(cell.bbox.l for cell in cluster.cells),
                t=min(cell.bbox.t for cell in cluster.cells),
                r=max(cell.bbox.r for cell in cluster.cells),
                b=max(cell.bbox.b for cell in cluster.cells),
            )

            if cluster.label == DocItemLabel.TABLE:
                # For tables, take union of current bbox and cells bbox
                cluster.bbox = BoundingBox(
                    l=min(cluster.bbox.l, cells_bbox.l),
                    t=min(cluster.bbox.t, cells_bbox.t),
                    r=max(cluster.bbox.r, cells_bbox.r),
                    b=max(cluster.bbox.b, cells_bbox.b),
                )
            else:
                cluster.bbox = cells_bbox

        return clusters

    def _sort_cells(self, cells: List[Cell]) -> List[Cell]:
        """Sort cells in native reading order."""
        return sorted(cells, key=lambda c: (c.id))

    def _sort_clusters(
        self, clusters: List[Cluster], mode: str = "id"
    ) -> List[Cluster]:
        """Sort clusters in reading order (top-to-bottom, left-to-right)."""
        if mode == "id":  # sort in the order the cells are printed in the PDF.
            return sorted(
                clusters,
                key=lambda cluster: (
                    (
                        min(cell.id for cell in cluster.cells)
                        if cluster.cells
                        else sys.maxsize
                    ),
                    cluster.bbox.t,
                    cluster.bbox.l,
                ),
            )
        elif mode == "tblr":  # Sort top-to-bottom, then left-to-right ("row first")
            return sorted(
                clusters, key=lambda cluster: (cluster.bbox.t, cluster.bbox.l)
            )
        elif mode == "lrtb":  # Sort left-to-right, then top-to-bottom ("column first")
            return sorted(
                clusters, key=lambda cluster: (cluster.bbox.l, cluster.bbox.t)
            )
        else:
            return clusters

```
</content>
</file_53>

<file_54>
<path>utils/ocr_utils.py</path>
<content>
```python
def map_tesseract_script(script: str) -> str:
    r""" """
    if script == "Katakana" or script == "Hiragana":
        script = "Japanese"
    elif script == "Han":
        script = "HanS"
    elif script == "Korean":
        script = "Hangul"
    return script

```
</content>
</file_54>

<file_55>
<path>utils/profiling.py</path>
<content>
```python
import time
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

import numpy as np
from pydantic import BaseModel

from docling.datamodel.settings import settings

if TYPE_CHECKING:
    from docling.datamodel.document import ConversionResult


class ProfilingScope(str, Enum):
    PAGE = "page"
    DOCUMENT = "document"


class ProfilingItem(BaseModel):
    scope: ProfilingScope
    count: int = 0
    times: List[float] = []
    start_timestamps: List[datetime] = []

    def avg(self) -> float:
        return np.average(self.times)  # type: ignore

    def std(self) -> float:
        return np.std(self.times)  # type: ignore

    def mean(self) -> float:
        return np.mean(self.times)  # type: ignore

    def percentile(self, perc: float) -> float:
        return np.percentile(self.times, perc)  # type: ignore


class TimeRecorder:
    def __init__(
        self,
        conv_res: "ConversionResult",
        key: str,
        scope: ProfilingScope = ProfilingScope.PAGE,
    ):
        if settings.debug.profile_pipeline_timings:
            if key not in conv_res.timings.keys():
                conv_res.timings[key] = ProfilingItem(scope=scope)
            self.conv_res = conv_res
            self.key = key

    def __enter__(self):
        if settings.debug.profile_pipeline_timings:
            self.start = time.monotonic()
            self.conv_res.timings[self.key].start_timestamps.append(datetime.utcnow())
        return self

    def __exit__(self, *args):
        if settings.debug.profile_pipeline_timings:
            elapsed = time.monotonic() - self.start
            self.conv_res.timings[self.key].times.append(elapsed)
            self.conv_res.timings[self.key].count += 1

```
</content>
</file_55>

<file_56>
<path>utils/utils.py</path>
<content>
```python
import hashlib
from io import BytesIO
from itertools import islice
from pathlib import Path
from typing import List, Union


def chunkify(iterator, chunk_size):
    """Yield successive chunks of chunk_size from the iterable."""
    if isinstance(iterator, List):
        iterator = iter(iterator)
    for first in iterator:  # Take the first element from the iterator
        yield [first] + list(islice(iterator, chunk_size - 1))


def create_file_hash(path_or_stream: Union[BytesIO, Path]) -> str:
    """Create a stable page_hash of the path_or_stream of a file"""

    block_size = 65536
    hasher = hashlib.sha256()

    def _hash_buf(binary_stream):
        buf = binary_stream.read(block_size)  # read and page_hash in chunks
        while len(buf) > 0:
            hasher.update(buf)
            buf = binary_stream.read(block_size)

    if isinstance(path_or_stream, Path):
        with path_or_stream.open("rb") as afile:
            _hash_buf(afile)
    elif isinstance(path_or_stream, BytesIO):
        _hash_buf(path_or_stream)

    return hasher.hexdigest()


def create_hash(string: str):
    hasher = hashlib.sha256()
    hasher.update(string.encode("utf-8"))

    return hasher.hexdigest()

```
</content>
</file_56>

<file_57>
<path>utils/visualization.py</path>
<content>
```python
from docling_core.types.doc import DocItemLabel
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont

from docling.datamodel.base_models import Cluster


def draw_clusters(
    image: Image.Image, clusters: list[Cluster], scale_x: float, scale_y: float
) -> None:
    """
    Draw clusters on an image
    """
    draw = ImageDraw.Draw(image, "RGBA")
    # Create a smaller font for the labels
    font: ImageFont.ImageFont | FreeTypeFont
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        # Fallback to default font if arial is not available
        font = ImageFont.load_default()
    for c_tl in clusters:
        all_clusters = [c_tl, *c_tl.children]
        for c in all_clusters:
            # Draw cells first (underneath)
            cell_color = (0, 0, 0, 40)  # Transparent black for cells
            for tc in c.cells:
                cx0, cy0, cx1, cy1 = tc.bbox.as_tuple()
                cx0 *= scale_x
                cx1 *= scale_x
                cy0 *= scale_x
                cy1 *= scale_y

                draw.rectangle(
                    [(cx0, cy0), (cx1, cy1)],
                    outline=None,
                    fill=cell_color,
                )
            # Draw cluster rectangle
            x0, y0, x1, y1 = c.bbox.as_tuple()
            x0 *= scale_x
            x1 *= scale_x
            y0 *= scale_x
            y1 *= scale_y

            cluster_fill_color = (*list(DocItemLabel.get_color(c.label)), 70)
            cluster_outline_color = (
                *list(DocItemLabel.get_color(c.label)),
                255,
            )
            draw.rectangle(
                [(x0, y0), (x1, y1)],
                outline=cluster_outline_color,
                fill=cluster_fill_color,
            )
            # Add label name and confidence
            label_text = f"{c.label.name} ({c.confidence:.2f})"
            # Create semi-transparent background for text
            text_bbox = draw.textbbox((x0, y0), label_text, font=font)
            text_bg_padding = 2
            draw.rectangle(
                [
                    (
                        text_bbox[0] - text_bg_padding,
                        text_bbox[1] - text_bg_padding,
                    ),
                    (
                        text_bbox[2] + text_bg_padding,
                        text_bbox[3] + text_bg_padding,
                    ),
                ],
                fill=(255, 255, 255, 180),  # Semi-transparent white
            )
            # Draw text
            draw.text(
                (x0, y0),
                label_text,
                fill=(0, 0, 0, 255),  # Solid black
                font=font,
            )

```
</content>
</file_57>
