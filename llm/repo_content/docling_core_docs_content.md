<file_1>
<path>DoclingDocument.json</path>
<content>
```json
{
  "$defs": {
    "BoundingBox": {
      "description": "BoundingBox.",
      "properties": {
        "l": {
          "title": "L",
          "type": "number"
        },
        "t": {
          "title": "T",
          "type": "number"
        },
        "r": {
          "title": "R",
          "type": "number"
        },
        "b": {
          "title": "B",
          "type": "number"
        },
        "coord_origin": {
          "$ref": "#/$defs/CoordOrigin",
          "default": "TOPLEFT"
        }
      },
      "required": [
        "l",
        "t",
        "r",
        "b"
      ],
      "title": "BoundingBox",
      "type": "object"
    },
    "ChartBar": {
      "description": "Represents a bar in a bar chart.\n\nAttributes:\n    label (str): The label for the bar.\n    values (float): The value associated with the bar.",
      "properties": {
        "label": {
          "title": "Label",
          "type": "string"
        },
        "values": {
          "title": "Values",
          "type": "number"
        }
      },
      "required": [
        "label",
        "values"
      ],
      "title": "ChartBar",
      "type": "object"
    },
    "ChartLine": {
      "description": "Represents a line in a line chart.\n\nAttributes:\n    label (str): The label for the line.\n    values (List[Tuple[float, float]]): A list of (x, y) coordinate pairs\n        representing the line's data points.",
      "properties": {
        "label": {
          "title": "Label",
          "type": "string"
        },
        "values": {
          "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [
              {
                "type": "number"
              },
              {
                "type": "number"
              }
            ],
            "type": "array"
          },
          "title": "Values",
          "type": "array"
        }
      },
      "required": [
        "label",
        "values"
      ],
      "title": "ChartLine",
      "type": "object"
    },
    "ChartPoint": {
      "description": "Represents a point in a scatter chart.\n\nAttributes:\n    value (Tuple[float, float]): A (x, y) coordinate pair representing a point in a\n        chart.",
      "properties": {
        "value": {
          "maxItems": 2,
          "minItems": 2,
          "prefixItems": [
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ],
          "title": "Value",
          "type": "array"
        }
      },
      "required": [
        "value"
      ],
      "title": "ChartPoint",
      "type": "object"
    },
    "ChartSlice": {
      "description": "Represents a slice in a pie chart.\n\nAttributes:\n    label (str): The label for the slice.\n    value (float): The value represented by the slice.",
      "properties": {
        "label": {
          "title": "Label",
          "type": "string"
        },
        "value": {
          "title": "Value",
          "type": "number"
        }
      },
      "required": [
        "label",
        "value"
      ],
      "title": "ChartSlice",
      "type": "object"
    },
    "ChartStackedBar": {
      "description": "Represents a stacked bar in a stacked bar chart.\n\nAttributes:\n    label (List[str]): The labels for the stacked bars. Multiple values are stored\n        in cases where the chart is \"double stacked,\" meaning bars are stacked both\n        horizontally and vertically.\n    values (List[Tuple[str, int]]): A list of values representing different segments\n        of the stacked bar along with their label.",
      "properties": {
        "label": {
          "items": {
            "type": "string"
          },
          "title": "Label",
          "type": "array"
        },
        "values": {
          "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [
              {
                "type": "string"
              },
              {
                "type": "integer"
              }
            ],
            "type": "array"
          },
          "title": "Values",
          "type": "array"
        }
      },
      "required": [
        "label",
        "values"
      ],
      "title": "ChartStackedBar",
      "type": "object"
    },
    "CodeItem": {
      "additionalProperties": false,
      "description": "CodeItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "const": "code",
          "default": "code",
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "orig": {
          "title": "Orig",
          "type": "string"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "code_language": {
          "$ref": "#/$defs/CodeLanguageLabel",
          "default": "unknown"
        }
      },
      "required": [
        "self_ref",
        "orig",
        "text"
      ],
      "title": "CodeItem",
      "type": "object"
    },
    "CodeLanguageLabel": {
      "description": "CodeLanguageLabel.",
      "enum": [
        "Ada",
        "Awk",
        "Bash",
        "bc",
        "C",
        "C#",
        "C++",
        "CMake",
        "COBOL",
        "CSS",
        "Ceylon",
        "Clojure",
        "Crystal",
        "Cuda",
        "Cython",
        "D",
        "Dart",
        "dc",
        "Dockerfile",
        "Elixir",
        "Erlang",
        "FORTRAN",
        "Forth",
        "Go",
        "HTML",
        "Haskell",
        "Haxe",
        "Java",
        "JavaScript",
        "Julia",
        "Kotlin",
        "Lisp",
        "Lua",
        "Matlab",
        "MoonScript",
        "Nim",
        "OCaml",
        "ObjectiveC",
        "Octave",
        "PHP",
        "Pascal",
        "Perl",
        "Prolog",
        "Python",
        "Racket",
        "Ruby",
        "Rust",
        "SML",
        "SQL",
        "Scala",
        "Scheme",
        "Swift",
        "TypeScript",
        "unknown",
        "VisualBasic",
        "XML",
        "YAML"
      ],
      "title": "CodeLanguageLabel",
      "type": "string"
    },
    "CoordOrigin": {
      "description": "CoordOrigin.",
      "enum": [
        "TOPLEFT",
        "BOTTOMLEFT"
      ],
      "title": "CoordOrigin",
      "type": "string"
    },
    "DocumentOrigin": {
      "description": "FileSource.",
      "properties": {
        "mimetype": {
          "title": "Mimetype",
          "type": "string"
        },
        "binary_hash": {
          "maximum": 18446744073709551615,
          "minimum": 0,
          "title": "Binary Hash",
          "type": "integer"
        },
        "filename": {
          "title": "Filename",
          "type": "string"
        },
        "uri": {
          "anyOf": [
            {
              "format": "uri",
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Uri"
        }
      },
      "required": [
        "mimetype",
        "binary_hash",
        "filename"
      ],
      "title": "DocumentOrigin",
      "type": "object"
    },
    "GroupItem": {
      "additionalProperties": false,
      "description": "GroupItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "name": {
          "default": "group",
          "title": "Name",
          "type": "string"
        },
        "label": {
          "$ref": "#/$defs/GroupLabel",
          "default": "unspecified"
        }
      },
      "required": [
        "self_ref"
      ],
      "title": "GroupItem",
      "type": "object"
    },
    "GroupLabel": {
      "description": "GroupLabel.",
      "enum": [
        "unspecified",
        "list",
        "ordered_list",
        "chapter",
        "section",
        "sheet",
        "slide",
        "form_area",
        "key_value_area",
        "comment_section"
      ],
      "title": "GroupLabel",
      "type": "string"
    },
    "ImageRef": {
      "description": "ImageRef.",
      "properties": {
        "mimetype": {
          "title": "Mimetype",
          "type": "string"
        },
        "dpi": {
          "title": "Dpi",
          "type": "integer"
        },
        "size": {
          "$ref": "#/$defs/Size"
        },
        "uri": {
          "anyOf": [
            {
              "format": "uri",
              "minLength": 1,
              "type": "string"
            },
            {
              "format": "path",
              "type": "string"
            }
          ],
          "title": "Uri"
        }
      },
      "required": [
        "mimetype",
        "dpi",
        "size",
        "uri"
      ],
      "title": "ImageRef",
      "type": "object"
    },
    "KeyValueItem": {
      "additionalProperties": false,
      "description": "KeyValueItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "const": "key_value_region",
          "default": "key_value_region",
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        }
      },
      "required": [
        "self_ref"
      ],
      "title": "KeyValueItem",
      "type": "object"
    },
    "ListItem": {
      "additionalProperties": false,
      "description": "SectionItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "const": "list_item",
          "default": "list_item",
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "orig": {
          "title": "Orig",
          "type": "string"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "enumerated": {
          "default": false,
          "title": "Enumerated",
          "type": "boolean"
        },
        "marker": {
          "default": "-",
          "title": "Marker",
          "type": "string"
        }
      },
      "required": [
        "self_ref",
        "orig",
        "text"
      ],
      "title": "ListItem",
      "type": "object"
    },
    "PageItem": {
      "description": "PageItem.",
      "properties": {
        "size": {
          "$ref": "#/$defs/Size"
        },
        "image": {
          "anyOf": [
            {
              "$ref": "#/$defs/ImageRef"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "page_no": {
          "title": "Page No",
          "type": "integer"
        }
      },
      "required": [
        "size",
        "page_no"
      ],
      "title": "PageItem",
      "type": "object"
    },
    "PictureBarChartData": {
      "description": "Represents data of a bar chart.\n\nAttributes:\n    kind (Literal[\"bar_chart_data\"]): The type of the chart.\n    x_axis_label (str): The label for the x-axis.\n    y_axis_label (str): The label for the y-axis.\n    bars (List[ChartBar]): A list of bars in the chart.",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "kind": {
          "const": "bar_chart_data",
          "default": "bar_chart_data",
          "title": "Kind",
          "type": "string"
        },
        "x_axis_label": {
          "title": "X Axis Label",
          "type": "string"
        },
        "y_axis_label": {
          "title": "Y Axis Label",
          "type": "string"
        },
        "bars": {
          "items": {
            "$ref": "#/$defs/ChartBar"
          },
          "title": "Bars",
          "type": "array"
        }
      },
      "required": [
        "title",
        "x_axis_label",
        "y_axis_label",
        "bars"
      ],
      "title": "PictureBarChartData",
      "type": "object"
    },
    "PictureClassificationClass": {
      "description": "PictureClassificationData.",
      "properties": {
        "class_name": {
          "title": "Class Name",
          "type": "string"
        },
        "confidence": {
          "title": "Confidence",
          "type": "number"
        }
      },
      "required": [
        "class_name",
        "confidence"
      ],
      "title": "PictureClassificationClass",
      "type": "object"
    },
    "PictureClassificationData": {
      "description": "PictureClassificationData.",
      "properties": {
        "kind": {
          "const": "classification",
          "default": "classification",
          "title": "Kind",
          "type": "string"
        },
        "provenance": {
          "title": "Provenance",
          "type": "string"
        },
        "predicted_classes": {
          "items": {
            "$ref": "#/$defs/PictureClassificationClass"
          },
          "title": "Predicted Classes",
          "type": "array"
        }
      },
      "required": [
        "provenance",
        "predicted_classes"
      ],
      "title": "PictureClassificationData",
      "type": "object"
    },
    "PictureDescriptionData": {
      "description": "PictureDescriptionData.",
      "properties": {
        "kind": {
          "const": "description",
          "default": "description",
          "title": "Kind",
          "type": "string"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "provenance": {
          "title": "Provenance",
          "type": "string"
        }
      },
      "required": [
        "text",
        "provenance"
      ],
      "title": "PictureDescriptionData",
      "type": "object"
    },
    "PictureItem": {
      "additionalProperties": false,
      "description": "PictureItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "const": "picture",
          "default": "picture",
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "captions": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Captions",
          "type": "array"
        },
        "references": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "References",
          "type": "array"
        },
        "footnotes": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Footnotes",
          "type": "array"
        },
        "image": {
          "anyOf": [
            {
              "$ref": "#/$defs/ImageRef"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "annotations": {
          "default": [],
          "items": {
            "discriminator": {
              "mapping": {
                "bar_chart_data": "#/$defs/PictureBarChartData",
                "classification": "#/$defs/PictureClassificationData",
                "description": "#/$defs/PictureDescriptionData",
                "line_chart_data": "#/$defs/PictureLineChartData",
                "misc": "#/$defs/PictureMiscData",
                "molecule_data": "#/$defs/PictureMoleculeData",
                "pie_chart_data": "#/$defs/PicturePieChartData",
                "scatter_chart_data": "#/$defs/PictureScatterChartData",
                "stacked_bar_chart_data": "#/$defs/PictureStackedBarChartData"
              },
              "propertyName": "kind"
            },
            "oneOf": [
              {
                "$ref": "#/$defs/PictureClassificationData"
              },
              {
                "$ref": "#/$defs/PictureDescriptionData"
              },
              {
                "$ref": "#/$defs/PictureMoleculeData"
              },
              {
                "$ref": "#/$defs/PictureMiscData"
              },
              {
                "$ref": "#/$defs/PictureLineChartData"
              },
              {
                "$ref": "#/$defs/PictureBarChartData"
              },
              {
                "$ref": "#/$defs/PictureStackedBarChartData"
              },
              {
                "$ref": "#/$defs/PicturePieChartData"
              },
              {
                "$ref": "#/$defs/PictureScatterChartData"
              }
            ]
          },
          "title": "Annotations",
          "type": "array"
        }
      },
      "required": [
        "self_ref"
      ],
      "title": "PictureItem",
      "type": "object"
    },
    "PictureLineChartData": {
      "description": "Represents data of a line chart.\n\nAttributes:\n    kind (Literal[\"line_chart_data\"]): The type of the chart.\n    x_axis_label (str): The label for the x-axis.\n    y_axis_label (str): The label for the y-axis.\n    lines (List[ChartLine]): A list of lines in the chart.",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "kind": {
          "const": "line_chart_data",
          "default": "line_chart_data",
          "title": "Kind",
          "type": "string"
        },
        "x_axis_label": {
          "title": "X Axis Label",
          "type": "string"
        },
        "y_axis_label": {
          "title": "Y Axis Label",
          "type": "string"
        },
        "lines": {
          "items": {
            "$ref": "#/$defs/ChartLine"
          },
          "title": "Lines",
          "type": "array"
        }
      },
      "required": [
        "title",
        "x_axis_label",
        "y_axis_label",
        "lines"
      ],
      "title": "PictureLineChartData",
      "type": "object"
    },
    "PictureMiscData": {
      "description": "PictureMiscData.",
      "properties": {
        "kind": {
          "const": "misc",
          "default": "misc",
          "title": "Kind",
          "type": "string"
        },
        "content": {
          "title": "Content",
          "type": "object"
        }
      },
      "required": [
        "content"
      ],
      "title": "PictureMiscData",
      "type": "object"
    },
    "PictureMoleculeData": {
      "description": "PictureMoleculeData.",
      "properties": {
        "kind": {
          "const": "molecule_data",
          "default": "molecule_data",
          "title": "Kind",
          "type": "string"
        },
        "smi": {
          "title": "Smi",
          "type": "string"
        },
        "confidence": {
          "title": "Confidence",
          "type": "number"
        },
        "class_name": {
          "title": "Class Name",
          "type": "string"
        },
        "segmentation": {
          "items": {
            "maxItems": 2,
            "minItems": 2,
            "prefixItems": [
              {
                "type": "number"
              },
              {
                "type": "number"
              }
            ],
            "type": "array"
          },
          "title": "Segmentation",
          "type": "array"
        },
        "provenance": {
          "title": "Provenance",
          "type": "string"
        }
      },
      "required": [
        "smi",
        "confidence",
        "class_name",
        "segmentation",
        "provenance"
      ],
      "title": "PictureMoleculeData",
      "type": "object"
    },
    "PicturePieChartData": {
      "description": "Represents data of a pie chart.\n\nAttributes:\n    kind (Literal[\"pie_chart_data\"]): The type of the chart.\n    slices (List[ChartSlice]): A list of slices in the pie chart.",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "kind": {
          "const": "pie_chart_data",
          "default": "pie_chart_data",
          "title": "Kind",
          "type": "string"
        },
        "slices": {
          "items": {
            "$ref": "#/$defs/ChartSlice"
          },
          "title": "Slices",
          "type": "array"
        }
      },
      "required": [
        "title",
        "slices"
      ],
      "title": "PicturePieChartData",
      "type": "object"
    },
    "PictureScatterChartData": {
      "description": "Represents data of a scatter chart.\n\nAttributes:\n    kind (Literal[\"scatter_chart_data\"]): The type of the chart.\n    x_axis_label (str): The label for the x-axis.\n    y_axis_label (str): The label for the y-axis.\n    points (List[ChartPoint]): A list of points in the scatter chart.",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "kind": {
          "const": "scatter_chart_data",
          "default": "scatter_chart_data",
          "title": "Kind",
          "type": "string"
        },
        "x_axis_label": {
          "title": "X Axis Label",
          "type": "string"
        },
        "y_axis_label": {
          "title": "Y Axis Label",
          "type": "string"
        },
        "points": {
          "items": {
            "$ref": "#/$defs/ChartPoint"
          },
          "title": "Points",
          "type": "array"
        }
      },
      "required": [
        "title",
        "x_axis_label",
        "y_axis_label",
        "points"
      ],
      "title": "PictureScatterChartData",
      "type": "object"
    },
    "PictureStackedBarChartData": {
      "description": "Represents data of a stacked bar chart.\n\nAttributes:\n    kind (Literal[\"stacked_bar_chart_data\"]): The type of the chart.\n    x_axis_label (str): The label for the x-axis.\n    y_axis_label (str): The label for the y-axis.\n    stacked_bars (List[ChartStackedBar]): A list of stacked bars in the chart.",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "kind": {
          "const": "stacked_bar_chart_data",
          "default": "stacked_bar_chart_data",
          "title": "Kind",
          "type": "string"
        },
        "x_axis_label": {
          "title": "X Axis Label",
          "type": "string"
        },
        "y_axis_label": {
          "title": "Y Axis Label",
          "type": "string"
        },
        "stacked_bars": {
          "items": {
            "$ref": "#/$defs/ChartStackedBar"
          },
          "title": "Stacked Bars",
          "type": "array"
        }
      },
      "required": [
        "title",
        "x_axis_label",
        "y_axis_label",
        "stacked_bars"
      ],
      "title": "PictureStackedBarChartData",
      "type": "object"
    },
    "ProvenanceItem": {
      "description": "ProvenanceItem.",
      "properties": {
        "page_no": {
          "title": "Page No",
          "type": "integer"
        },
        "bbox": {
          "$ref": "#/$defs/BoundingBox"
        },
        "charspan": {
          "maxItems": 2,
          "minItems": 2,
          "prefixItems": [
            {
              "type": "integer"
            },
            {
              "type": "integer"
            }
          ],
          "title": "Charspan",
          "type": "array"
        }
      },
      "required": [
        "page_no",
        "bbox",
        "charspan"
      ],
      "title": "ProvenanceItem",
      "type": "object"
    },
    "RefItem": {
      "description": "RefItem.",
      "properties": {
        "$ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "$Ref",
          "type": "string"
        }
      },
      "required": [
        "$ref"
      ],
      "title": "RefItem",
      "type": "object"
    },
    "SectionHeaderItem": {
      "additionalProperties": false,
      "description": "SectionItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "const": "section_header",
          "default": "section_header",
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "orig": {
          "title": "Orig",
          "type": "string"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "level": {
          "default": 1,
          "maximum": 100,
          "minimum": 1,
          "title": "Level",
          "type": "integer"
        }
      },
      "required": [
        "self_ref",
        "orig",
        "text"
      ],
      "title": "SectionHeaderItem",
      "type": "object"
    },
    "Size": {
      "description": "Size.",
      "properties": {
        "width": {
          "default": 0.0,
          "title": "Width",
          "type": "number"
        },
        "height": {
          "default": 0.0,
          "title": "Height",
          "type": "number"
        }
      },
      "title": "Size",
      "type": "object"
    },
    "TableCell": {
      "description": "TableCell.",
      "properties": {
        "bbox": {
          "anyOf": [
            {
              "$ref": "#/$defs/BoundingBox"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "row_span": {
          "default": 1,
          "title": "Row Span",
          "type": "integer"
        },
        "col_span": {
          "default": 1,
          "title": "Col Span",
          "type": "integer"
        },
        "start_row_offset_idx": {
          "title": "Start Row Offset Idx",
          "type": "integer"
        },
        "end_row_offset_idx": {
          "title": "End Row Offset Idx",
          "type": "integer"
        },
        "start_col_offset_idx": {
          "title": "Start Col Offset Idx",
          "type": "integer"
        },
        "end_col_offset_idx": {
          "title": "End Col Offset Idx",
          "type": "integer"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "column_header": {
          "default": false,
          "title": "Column Header",
          "type": "boolean"
        },
        "row_header": {
          "default": false,
          "title": "Row Header",
          "type": "boolean"
        },
        "row_section": {
          "default": false,
          "title": "Row Section",
          "type": "boolean"
        }
      },
      "required": [
        "start_row_offset_idx",
        "end_row_offset_idx",
        "start_col_offset_idx",
        "end_col_offset_idx",
        "text"
      ],
      "title": "TableCell",
      "type": "object"
    },
    "TableData": {
      "description": "BaseTableData.",
      "properties": {
        "table_cells": {
          "default": [],
          "items": {
            "$ref": "#/$defs/TableCell"
          },
          "title": "Table Cells",
          "type": "array"
        },
        "num_rows": {
          "default": 0,
          "title": "Num Rows",
          "type": "integer"
        },
        "num_cols": {
          "default": 0,
          "title": "Num Cols",
          "type": "integer"
        }
      },
      "title": "TableData",
      "type": "object"
    },
    "TableItem": {
      "additionalProperties": false,
      "description": "TableItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "default": "table",
          "enum": [
            "document_index",
            "table"
          ],
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "captions": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Captions",
          "type": "array"
        },
        "references": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "References",
          "type": "array"
        },
        "footnotes": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Footnotes",
          "type": "array"
        },
        "image": {
          "anyOf": [
            {
              "$ref": "#/$defs/ImageRef"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "data": {
          "$ref": "#/$defs/TableData"
        }
      },
      "required": [
        "self_ref",
        "data"
      ],
      "title": "TableItem",
      "type": "object"
    },
    "TextItem": {
      "additionalProperties": false,
      "description": "TextItem.",
      "properties": {
        "self_ref": {
          "pattern": "^#(?:/([\\w-]+)(?:/(\\d+))?)?$",
          "title": "Self Ref",
          "type": "string"
        },
        "parent": {
          "anyOf": [
            {
              "$ref": "#/$defs/RefItem"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "children": {
          "default": [],
          "items": {
            "$ref": "#/$defs/RefItem"
          },
          "title": "Children",
          "type": "array"
        },
        "label": {
          "enum": [
            "caption",
            "checkbox_selected",
            "checkbox_unselected",
            "footnote",
            "formula",
            "page_footer",
            "page_header",
            "paragraph",
            "reference",
            "text",
            "title"
          ],
          "title": "Label",
          "type": "string"
        },
        "prov": {
          "default": [],
          "items": {
            "$ref": "#/$defs/ProvenanceItem"
          },
          "title": "Prov",
          "type": "array"
        },
        "orig": {
          "title": "Orig",
          "type": "string"
        },
        "text": {
          "title": "Text",
          "type": "string"
        }
      },
      "required": [
        "self_ref",
        "label",
        "orig",
        "text"
      ],
      "title": "TextItem",
      "type": "object"
    }
  },
  "description": "DoclingDocument.",
  "properties": {
    "schema_name": {
      "const": "DoclingDocument",
      "default": "DoclingDocument",
      "title": "Schema Name",
      "type": "string"
    },
    "version": {
      "default": "1.0.0",
      "pattern": "^(?P<major>0|[1-9]\\d*)\\.(?P<minor>0|[1-9]\\d*)\\.(?P<patch>0|[1-9]\\d*)(?:-(?P<prerelease>(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$",
      "title": "Version",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "origin": {
      "anyOf": [
        {
          "$ref": "#/$defs/DocumentOrigin"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "furniture": {
      "$ref": "#/$defs/GroupItem",
      "default": {
        "self_ref": "#/furniture",
        "parent": null,
        "children": [],
        "name": "_root_",
        "label": "unspecified"
      }
    },
    "body": {
      "$ref": "#/$defs/GroupItem",
      "default": {
        "self_ref": "#/body",
        "parent": null,
        "children": [],
        "name": "_root_",
        "label": "unspecified"
      }
    },
    "groups": {
      "default": [],
      "items": {
        "$ref": "#/$defs/GroupItem"
      },
      "title": "Groups",
      "type": "array"
    },
    "texts": {
      "default": [],
      "items": {
        "anyOf": [
          {
            "$ref": "#/$defs/SectionHeaderItem"
          },
          {
            "$ref": "#/$defs/ListItem"
          },
          {
            "$ref": "#/$defs/TextItem"
          },
          {
            "$ref": "#/$defs/CodeItem"
          }
        ]
      },
      "title": "Texts",
      "type": "array"
    },
    "pictures": {
      "default": [],
      "items": {
        "$ref": "#/$defs/PictureItem"
      },
      "title": "Pictures",
      "type": "array"
    },
    "tables": {
      "default": [],
      "items": {
        "$ref": "#/$defs/TableItem"
      },
      "title": "Tables",
      "type": "array"
    },
    "key_value_items": {
      "default": [],
      "items": {
        "$ref": "#/$defs/KeyValueItem"
      },
      "title": "Key Value Items",
      "type": "array"
    },
    "pages": {
      "additionalProperties": {
        "$ref": "#/$defs/PageItem"
      },
      "default": {},
      "title": "Pages",
      "type": "object"
    }
  },
  "required": [
    "name"
  ],
  "title": "DoclingDocument",
  "type": "object"
}
```
</content>
</file_1>

<file_2>
<path>Generic.json</path>
<content>
```json
{
  "$defs": {
    "FileInfoObject": {
      "description": "Filing information for any data object to be stored in a Docling database.",
      "properties": {
        "filename": {
          "description": "The name of a persistent object that created this data object",
          "title": "Filename",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "filename-prov": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The provenance of this data object, e.g. an archive file, a URL, or any other repository.",
          "title": "Filename-Prov",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "document-hash": {
          "description": "A unique identifier of this data object within a collection of a Docling database",
          "title": "Document-Hash",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "filename",
        "document-hash"
      ],
      "title": "FileInfoObject",
      "type": "object"
    }
  },
  "description": "A representation of a generic document.",
  "properties": {
    "_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "A short description or summary of the document.",
      "title": "Name",
      "x-es-type": "text"
    },
    "file-info": {
      "$ref": "#/$defs/FileInfoObject",
      "description": "Minimal identification information of the document within a collection.",
      "title": "Document information"
    }
  },
  "required": [
    "file-info"
  ],
  "title": "Generic",
  "type": "object"
}
```
</content>
</file_2>

<file_3>
<path>Record.json</path>
<content>
```json
{
  "$defs": {
    "Acquisition": {
      "additionalProperties": false,
      "description": "Information on how the data was obtained.",
      "properties": {
        "type": {
          "description": "The method to obtain the data.",
          "enum": [
            "API",
            "FTP",
            "Download",
            "Link",
            "Web scraping/Crawling",
            "Other"
          ],
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "date": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A string representation of the acquisition datetime in ISO 8601 format.",
          "title": "Date"
        },
        "link": {
          "anyOf": [
            {
              "format": "uri",
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Link to the data source of this document.",
          "title": "Link",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "size": {
          "anyOf": [
            {
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Size in bytes of the raw document from the data source.",
          "title": "Size",
          "x-es-type": "long"
        }
      },
      "required": [
        "type"
      ],
      "title": "Acquisition",
      "type": "object"
    },
    "Attribute": {
      "additionalProperties": false,
      "description": "Attribute model that describes a list of characteristics.",
      "properties": {
        "conf": {
          "description": "The confidence level of this attribute characteristics.",
          "maximum": 1.0,
          "minimum": 0.0,
          "title": "Confidence",
          "type": "number",
          "x-es-type": "float"
        },
        "prov": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/ProvenanceItem"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The sources of this attribute characteristics.",
          "title": "Provenance"
        },
        "predicates": {
          "description": "A list of characteristics (type, value, and name).",
          "items": {
            "$ref": "#/$defs/Predicate"
          },
          "title": "Predicates",
          "type": "array"
        }
      },
      "required": [
        "conf",
        "predicates"
      ],
      "title": "Attribute",
      "type": "object"
    },
    "BooleanValue": {
      "additionalProperties": false,
      "description": "Model for boolean values.",
      "properties": {
        "value": {
          "title": "Value",
          "type": "boolean",
          "x-es-type": "boolean"
        }
      },
      "required": [
        "value"
      ],
      "title": "BooleanValue",
      "type": "object"
    },
    "CollectionRecordInfo": {
      "additionalProperties": false,
      "description": "Information of a collection of type Record.",
      "properties": {
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Name of the collection.",
          "title": "Name",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "type": {
          "const": "Record",
          "description": "The collection type.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "version": {
          "anyOf": [
            {
              "pattern": "^(?P<major>0|[1-9]\\d*)\\.(?P<minor>0|[1-9]\\d*)\\.(?P<patch>0|[1-9]\\d*)(?:-(?P<prerelease>(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The version of this collection model.",
          "title": "Version",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "alias": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A list of tags (aliases) for the collection.",
          "title": "Alias",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "type"
      ],
      "title": "CollectionRecordInfo",
      "type": "object"
    },
    "DatetimeValue": {
      "additionalProperties": false,
      "description": "Model for datetime values.",
      "properties": {
        "value": {
          "format": "date-time",
          "title": "Value",
          "type": "string"
        }
      },
      "required": [
        "value"
      ],
      "title": "DatetimeValue",
      "type": "object"
    },
    "FileInfoObject": {
      "description": "Filing information for any data object to be stored in a Docling database.",
      "properties": {
        "filename": {
          "description": "The name of a persistent object that created this data object",
          "title": "Filename",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "filename-prov": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The provenance of this data object, e.g. an archive file, a URL, or any other repository.",
          "title": "Filename-Prov",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "document-hash": {
          "description": "A unique identifier of this data object within a collection of a Docling database",
          "title": "Document-Hash",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "filename",
        "document-hash"
      ],
      "title": "FileInfoObject",
      "type": "object"
    },
    "GeopointValue": {
      "additionalProperties": false,
      "description": "A representation of a geopoint (longitude and latitude coordinates).",
      "properties": {
        "value": {
          "items": {
            "type": "number"
          },
          "maxItems": 2,
          "minItems": 2,
          "title": "Value",
          "type": "array",
          "x-es-type": "geo_point"
        },
        "conf": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Conf",
          "x-es-type": "float"
        }
      },
      "required": [
        "value"
      ],
      "title": "GeopointValue",
      "type": "object"
    },
    "Identifier": {
      "additionalProperties": false,
      "description": "Unique identifier of a Docling data object.",
      "properties": {
        "type": {
          "description": "A string representing a collection or database that contains this data object.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "value": {
          "description": "The identifier value of the data object within a collection or database.",
          "title": "Value",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "_name": {
          "description": "A unique identifier of the data object across Docling, consisting of the concatenation of type and value in lower case, separated by hash (#).",
          "pattern": "^.+#.+$",
          "title": "_Name",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "type",
        "value",
        "_name"
      ],
      "title": "Identifier",
      "type": "object"
    },
    "Log": {
      "additionalProperties": false,
      "description": "Log entry to describe an ETL task on a document.",
      "properties": {
        "task": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "An identifier of this task. It may be used to identify this task from other tasks of the same agent and type.",
          "title": "Task",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "agent": {
          "description": "The Docling agent that performed the task, e.g., CCS or CXS.",
          "title": "Agent",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "type": {
          "description": "A task category.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "comment": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A description of the task or any comments in natural language.",
          "title": "Comment"
        },
        "date": {
          "description": "A string representation of the task execution datetime in ISO 8601 format.",
          "format": "date-time",
          "title": "Date",
          "type": "string"
        }
      },
      "required": [
        "agent",
        "type",
        "date"
      ],
      "title": "Log",
      "type": "object"
    },
    "NominalValue": {
      "additionalProperties": false,
      "description": "Model for nominal (categorical) values.",
      "properties": {
        "value": {
          "title": "Value",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "value"
      ],
      "title": "NominalValue",
      "type": "object"
    },
    "NumericalValue": {
      "additionalProperties": false,
      "description": "Model for numerical values.",
      "properties": {
        "min": {
          "title": "Min",
          "type": "number",
          "x-es-type": "float"
        },
        "max": {
          "title": "Max",
          "type": "number",
          "x-es-type": "float"
        },
        "val": {
          "title": "Val",
          "type": "number",
          "x-es-type": "float"
        },
        "err": {
          "title": "Err",
          "type": "number",
          "x-es-type": "float"
        },
        "unit": {
          "title": "Unit",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "min",
        "max",
        "val",
        "err",
        "unit"
      ],
      "title": "NumericalValue",
      "type": "object"
    },
    "Predicate": {
      "additionalProperties": false,
      "description": "Model for a predicate.",
      "properties": {
        "key": {
          "$ref": "#/$defs/PredicateKey"
        },
        "value": {
          "$ref": "#/$defs/PredicateValue"
        },
        "numerical_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/NumericalValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "numerical_value_si": {
          "anyOf": [
            {
              "$ref": "#/$defs/NumericalValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "nominal_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/NominalValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "text_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/TextValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "boolean_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/BooleanValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "datetime_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/DatetimeValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "geopoint_value": {
          "anyOf": [
            {
              "$ref": "#/$defs/GeopointValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "key",
        "value"
      ],
      "title": "Predicate",
      "type": "object"
    },
    "PredicateKey": {
      "additionalProperties": false,
      "description": "Model for the key (unique identifier) of a predicate.",
      "properties": {
        "name": {
          "description": "Name of the predicate key.",
          "title": "Name",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "type": {
          "description": "Type of predicate key.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "name",
        "type"
      ],
      "title": "PredicateKey",
      "type": "object"
    },
    "PredicateValue": {
      "additionalProperties": false,
      "description": "Model for the value of a predicate.",
      "properties": {
        "name": {
          "description": "Name of the predicate value (actual value).",
          "title": "Name",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "type": {
          "description": "Type of predicate value.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "name",
        "type"
      ],
      "title": "PredicateValue",
      "type": "object"
    },
    "ProvenanceItem": {
      "additionalProperties": false,
      "description": "A representation of an object provenance.",
      "properties": {
        "type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Any string representing the type of provenance, e.g. `sentence`, `table`, or `doi`.",
          "title": "The provenance type",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A text representing the evidence of the provenance, e.g. the sentence text or the content of a table cell",
          "title": "Evidence of the provenance",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "reference": {
          "anyOf": [
            {
              "$ref": "#/$defs/Identifier"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Reference to another object, e.g. record, statement, URL, or any other object that identifies the provenance",
          "title": "Reference to the provenance object"
        },
        "path": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A path that locates the evidence within the provenance object identified by the `reference` field using a JSON pointer notation, e.g., `#/main-text/5` to locate the `main-text` paragraph at index 5",
          "title": "The location of the provenance within the referenced object",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "span": {
          "anyOf": [
            {
              "items": {
                "type": "integer"
              },
              "maxItems": 2,
              "minItems": 2,
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "location of the item in the text/table referenced by the `path`, e.g., `[34, 67]`",
          "title": "The location of the item in the text/table"
        }
      },
      "title": "ProvenanceItem",
      "type": "object"
    },
    "RecordDescription": {
      "description": "Additional record metadata, including optional collection-specific fields.",
      "properties": {
        "logs": {
          "description": "Logs that describe the ETL tasks applied to this record.",
          "items": {
            "$ref": "#/$defs/Log"
          },
          "title": "Logs",
          "type": "array"
        },
        "publication_date": {
          "anyOf": [
            {
              "format": "date-time",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The date that best represents the last publication time of a record.",
          "title": "Publication date"
        },
        "collection": {
          "anyOf": [
            {
              "$ref": "#/$defs/CollectionRecordInfo"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The collection information of this record."
        },
        "acquisition": {
          "anyOf": [
            {
              "$ref": "#/$defs/Acquisition"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Information on how the document was obtained, for data governance purposes."
        }
      },
      "required": [
        "logs"
      ],
      "title": "RecordDescription",
      "type": "object"
    },
    "S3Reference": {
      "description": "References an s3 resource.",
      "properties": {
        "__ref_s3_data": {
          "examples": [
            "#/_s3_data/figures/0"
          ],
          "title": "Ref S3 Data",
          "type": "string"
        }
      },
      "required": [
        "__ref_s3_data"
      ],
      "title": "S3Reference",
      "type": "object"
    },
    "Subject": {
      "additionalProperties": false,
      "description": "A representation of a subject.",
      "properties": {
        "display_name": {
          "description": "Name of the subject in natural language. It can be used for end-user applications to display a human-readable name. For instance, `B(2) Mg(1)` for `MgB2` or `International Business Machines` for `IBM`",
          "title": "Display Name",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "display_image": {
          "anyOf": [
            {
              "$ref": "#/$defs/S3Reference"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Image representing the subject. It can be used for end-user applications.For example, the chemical structure drawing of a compound or the eight bar IBM logo for IBM.",
          "title": "Display Image",
          "x-es-suppress": true
        },
        "type": {
          "description": "Main subject type. For instance, `material`, `material-class`, `material-device`, `company`, or `person`.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "names": {
          "description": "List of given names for this subject. They may not be unique across different subjects.",
          "items": {
            "$ref": "#/$defs/SubjectNameIdentifier"
          },
          "title": "Names",
          "type": "array"
        },
        "identifiers": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/Identifier"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "List of unique identifiers in database. For instance, the `PubChem ID` of a record in the PubChem database.",
          "title": "Identifiers"
        },
        "labels": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "List of labels or categories for this subject.",
          "title": "Labels",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "display_name",
        "type",
        "names"
      ],
      "title": "Subject",
      "type": "object"
    },
    "SubjectNameIdentifier": {
      "additionalProperties": false,
      "description": "Identifier of subject names.",
      "properties": {
        "type": {
          "description": "A string representing a collection or database that contains this data object.",
          "title": "Type",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "value": {
          "description": "The identifier value of the data object within a collection or database.",
          "title": "Value",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        },
        "_name": {
          "description": "A unique identifier of the data object across Docling, consisting of the concatenation of type and value in lower case, separated by hash (#).",
          "pattern": "^.+#.+$",
          "title": "_Name",
          "type": "string",
          "x-es-ignore_above": 8191,
          "x-es-type": "keyword"
        }
      },
      "required": [
        "type",
        "value",
        "_name"
      ],
      "title": "SubjectNameIdentifier",
      "type": "object"
    },
    "TextValue": {
      "additionalProperties": false,
      "description": "Model for textual values.",
      "properties": {
        "value": {
          "title": "Value",
          "type": "string",
          "x-es-type": "text"
        }
      },
      "required": [
        "value"
      ],
      "title": "TextValue",
      "type": "object"
    }
  },
  "description": "A representation of a structured record in an database.",
  "properties": {
    "conf": {
      "description": "This value represents a score to the data item. Items originating from  databases will typically have a score 1.0, while items resulting from  an NLP model may have a value between 0.0 and 1.0.",
      "maximum": 1.0,
      "minimum": 0.0,
      "title": "The confidence of the evidence",
      "type": "number",
      "x-es-type": "float"
    },
    "prov": {
      "description": "A list of provenance items.",
      "items": {
        "$ref": "#/$defs/ProvenanceItem"
      },
      "title": "Provenance",
      "type": "array"
    },
    "file-info": {
      "$ref": "#/$defs/FileInfoObject"
    },
    "description": {
      "$ref": "#/$defs/RecordDescription"
    },
    "subject": {
      "$ref": "#/$defs/Subject"
    },
    "attributes": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/Attribute"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Attributes"
    },
    "_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "A short description or summary of the record.",
      "title": "Name",
      "x-es-type": "text"
    },
    "identifiers": {
      "anyOf": [
        {
          "items": {
            "$ref": "#/$defs/Identifier"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "A list of unique identifiers of this record in a database.",
      "title": "Identifiers"
    }
  },
  "required": [
    "conf",
    "prov",
    "file-info",
    "description",
    "subject"
  ],
  "title": "Record",
  "type": "object"
}
```
</content>
</file_3>
