<file_1>
<path>__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Main package."""

```
</content>
</file_1>

<file_2>
<path>cli/__init__.py</path>
<content>
```python
"""CLI package."""

```
</content>
</file_2>

<file_3>
<path>cli/view.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""CLI for docling viewer."""
import importlib
import tempfile
import webbrowser
from pathlib import Path
from typing import Annotated, Optional

import typer

from docling_core.types.doc import DoclingDocument
from docling_core.types.doc.base import ImageRefMode
from docling_core.utils.file import resolve_source_to_path

app = typer.Typer(
    name="Docling",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)


def version_callback(value: bool):
    """Callback for version inspection."""
    if value:
        docling_core_version = importlib.metadata.version("docling-core")
        print(f"Docling Core version: {docling_core_version}")
        raise typer.Exit()


@app.command(no_args_is_help=True)
def view(
    source: Annotated[
        str,
        typer.Argument(
            ...,
            metavar="source",
            help="Docling JSON file to view.",
        ),
    ],
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version information.",
        ),
    ] = None,
):
    """Display a Docling JSON file on the default browser."""
    path = resolve_source_to_path(source=source)
    doc = DoclingDocument.load_from_json(filename=path)
    target_path = Path(tempfile.mkdtemp()) / "out.html"
    html_output = doc.export_to_html(image_mode=ImageRefMode.EMBEDDED)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    webbrowser.open(url=f"file://{target_path.absolute().resolve()}")


click_app = typer.main.get_command(app)

if __name__ == "__main__":
    app()

```
</content>
</file_3>

<file_4>
<path>py.typed</path>
<content>

[Content not displayed - Non-plaintext file]
</content>
</file_4>

<file_5>
<path>resources/schemas/doc/ANN.json</path>
<content>
```json
{
  "$schema": "http://json-schema.org/schema#",
  "definitions": {
    "annot+pred": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "cells",
          "clusters",
          "tables",
          "source"
        ],
        "properties": {
          "cells": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "id",
                "rawcell_id",
                "label"
              ],
              "properties": {
                "id": {
                  "type": "integer"
                },
                "rawcell_id": {
                  "type": "integer"
                },
                "label": {
                  "type": "string"
                }
              }
            }
          },
          "clusters": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "model",
                "type",
                "bbox",
                "cell_ids",
                "merged",
                "id"
              ],
              "properties": {
                "model": {
                  "type": "string"
                },
                "type": {
                  "type": "string"
                },
                "bbox": {
                  "type": "array",
                  "minItems": 4,
                  "maxItems": 4,
                  "items": {
                    "type": "number"
                  }
                },
                "cell_ids": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                },
                "merged": {
                  "type": "boolean"
                },
                "id": {
                  "type": "integer"
                }
              }
            }
          },
          "tables": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "cell_id",
                "label",
                "rows",
                "cols"
              ],
              "properties": {
                "cell_id": {
                  "type": "integer"
                },
                "label": {
                  "type": "string"
                },
                "rows": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                },
                "cols": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          },
          "source": {
            "type": "object",
            "required": [
              "type",
              "info",
              "timestamp"
            ],
            "properties": {
              "type": {
                "type": "string"
              },
              "timestamp": {
                "type": "number"
              },
              "info": {
                "type": "object",
                "required": [
                  "display_name",
                  "model_name",
                  "model_class",
                  "model_version",
                  "model_id"
                ],
                "properties": {
                  "display_name": {
                    "type": "string"
                  },
                  "model_name": {
                    "type": "string"
                  },
                  "model_class": {
                    "type": "string"
                  },
                  "model_version": {
                    "type": "string"
                  },
                  "model_id": {
                    "type": "string"
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "properties": {
    "annotations": {
      "$ref": "#/definitions/annot+pred"
    },
    "predictions": {
      "$ref": "#/definitions/annot+pred"
    },
    "reports": {
      "type": "array"
    }
  },
  "minProperties": 1,
  "type": "object"
}
```
</content>
</file_5>

<file_6>
<path>resources/schemas/doc/DOC.json</path>
<content>
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "_type": {
      "type": "string"
    },
    "bitmaps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "bounding-box": {
            "type": "object",
            "properties": {
              "max": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              },
              "min": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              }
            }
          },
          "image-id": {
            "type": "string"
          },
          "prov": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "bbox": {
                  "type": "array",
                  "items": {
                    "type": "number"
                  }
                },
                "page": {
                  "type": "integer"
                },
                "span": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          },
          "type": {
            "type": "string"
          }
        }
      }
    },
    "description": {
      "type": "object",
      "properties": {
        "abstract": {
          "type": "string"
        },
        "affiliations": {
          "type": "string"
        },
        "authors": {
          "type": "string"
        },
        "title": {
          "type": "string"
        }
      }
    },
    "equations": {
      "type": "array"
    },
    "figures": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "bounding-box": {
            "type": "object",
            "properties": {
              "max": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              },
              "min": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              }
            }
          },
          "image-id": {
            "type": "string"
          },
          "model": {
            "type": "string"
          },
          "prov": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "bbox": {
                  "type": "array",
                  "items": {
                    "type": "number"
                  }
                },
                "page": {
                  "type": "integer"
                },
                "span": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          },
          "type": {
            "type": "string"
          }
        }
      }
    },
    "file-info": {
      "type": "object",
      "properties": {
        "#-pages": {
          "type": "integer"
        },
        "document-hash": {
          "type": "string"
        },
        "filename": {
          "type": "string"
        },
        "page-hashes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "hash": {
                "type": "string"
              },
              "model": {
                "type": "string"
              },
              "page": {
                "type": "integer"
              }
            }
          }
        },
        "description": {
          "type": "object",
          "properties": {
            "keywords": {
              "type": "string"
            }
          }
        },
        "collection-name": {
          "type": "string"
        }
      }
    },
    "footnotes": {
      "type": "array"
    },
    "main-text": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "font": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "prov": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "bbox": {
                  "type": "array",
                  "items": {
                    "type": "number"
                  }
                },
                "page": {
                  "type": "integer"
                },
                "span": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          },
          "text": {
            "type": "string"
          },
          "type": {
            "type": "string"
          }
        }
      }
    },
    "tables": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "#-cols": {
            "type": "integer"
          },
          "#-rows": {
            "type": "integer"
          },
          "bounding-box": {
            "type": "object",
            "properties": {
              "max": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              },
              "min": {
                "type": "array",
                "items": {
                  "type": "number"
                }
              }
            }
          },
          "data": {
            "type": "array",
            "items": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "model": {
            "type": "string"
          },
          "prov": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "bbox": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                },
                "page": {
                  "type": "integer"
                },
                "span": {
                  "type": "array",
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          },
          "text": {
            "type": "string"
          },
          "type": {
            "type": "string"
          }
        }
      }
    }
  }
}

```
</content>
</file_6>

<file_7>
<path>resources/schemas/doc/OCR-output.json</path>
<content>
```json
{
  "$schema": "http://json-schema.org/schema#",
  "type": "object",
  "required": [
    "_meta",
    "info",
    "dimension",
    "words",
    "cells",
    "boxes",
    "paths"
  ],
  "properties": {
    "_meta": {
      "type": "object",
      "required": [
        "page",
        "coords-order",
        "coords-origin"
      ],
      "properties": {
        "page": {
          "type": "object",
          "required": [
            "width",
            "height"
          ],
          "properties": {
            "width": {
              "type": "number"
            },
            "height": {
              "type": "number"
            }
          }
        },
        "coords-order": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "coords-origin": {
          "type": "string"
        }
      }
    },
    "info": {
      "type": "object"
    },
    "dimension": {
      "type": "object",
      "required": [
        "width",
        "height"
      ],
      "properties": {
        "width": {
          "type": "number"
        },
        "height": {
          "type": "number"
        }
      }
    },
    "words": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "confidence",
          "bbox",
          "content"
        ],
        "properties": {
          "confidence": {
            "type": "number"
          },
          "bbox": {
            "type": "array",
            "item": {
              "type": "number"
            }
          },
          "content": {
            "type": "string"
          }
        }
      }
    },
    "cells": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "confidence",
          "bbox",
          "content"
        ],
        "properties": {
          "confidence": {
            "type": "number"
          },
          "bbox": {
            "type": "array",
            "item": {
              "type": "number"
            }
          },
          "content": {
            "type": "string"
          }
        }
      }
    },
    "boxes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "confidence",
          "bbox",
          "content"
        ],
        "properties": {
          "confidence": {
            "type": "number"
          },
          "bbox": {
            "type": "array",
            "item": {
              "type": "number"
            }
          },
          "content": {
            "type": "string"
          }
        }
      }
    },
    "paths": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "x",
          "y"
        ],
        "properties": {
          "x": {
            "type": "array",
            "items": {
              "type": "number"
            }
          },
          "y": {
            "type": "array",
            "items": {
              "type": "number"
            }
          }
        }
      }
    }
  }
}
```
</content>
</file_7>

<file_8>
<path>resources/schemas/doc/RAW.json</path>
<content>
```json
{
  "$schema": "http://json-schema.org/schema#",
  "type": "object",
  "required": [
    "info",
    "pages"
  ],
  "properties": {
    "info": {},
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "height",
          "width",
          "dimensions",
          "cells",
          "paths",
          "images",
          "fonts"
        ],
        "properties": {
          "height": {
            "type": "number"
          },
          "width": {
            "type": "number"
          },
          "dimensions": {
            "type": "object"
          },
          "cells": {
            "type": "array",
            "items": {
              "type": "object",
              "required": [
                "SEE_cell",
                "SEE_confidence",
                "angle",
                "box",
                "content",
                "enumeration",
                "font"
              ],
              "properties": {
                "SEE_cell": {
                  "type": "boolean"
                },
                "SEE_confidence": {
                  "type": "number"
                },
                "angle": {
                  "type": "number"
                },
                "box": {
                  "type": "object",
                  "required": [
                    "baseline",
                    "device"
                  ],
                  "properties": {
                    "baseline": {
                      "type": "array",
                      "minItems": 4,
                      "maxItems": 4,
                      "items": {
                        "type": "number"
                      }
                    },
                    "device": {
                      "type": "array",
                      "minItems": 4,
                      "maxItems": 4,
                      "items": {
                        "type": "number"
                      }
                    }
                  }
                },
                "content": {
                  "type": "object",
                  "required": [
                    "rnormalized"
                  ],
                  "properties": {
                    "rnormalized": {
                      "type": "string"
                    }
                  }
                },
                "enumeration": {
                  "type": "object",
                  "required": [
                    "match",
                    "type"
                  ],
                  "properties": {
                    "match": {
                      "type": "integer"
                    },
                    "type": {
                      "type": "integer"
                    }
                  }
                },
                "font": {
                  "type": "object",
                  "required": [
                    "color",
                    "name",
                    "size"
                  ],
                  "properties": {
                    "color": {
                      "type": "array",
                      "minItems": 3,
                      "maxItems": 4,
                      "items": {
                        "type": "number"
                      }
                    },
                    "name": {
                      "type": "string"
                    },
                    "size": {
                      "type": "number"
                    }
                  }
                }
              }
            }
          },
          "paths": {
            "type": "array",
            "items": {}
          },
          "vertical-lines": {
            "type": "array",
            "items": {}
          },
          "horizontal-lines": {
            "type": "array",
            "items": {}
          },
          "images": {
            "type": "array",
            "items": {}
          },
          "fonts": {
            "type": "array",
            "items": {}
          }
        }
      }
    }
  }
}
```
</content>
</file_8>

<file_9>
<path>resources/schemas/generated/ccs_document_schema.json</path>
<content>
```json
{
  "title": "ExportedCCSDocument",
  "type": "object",
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "type": {
      "title": "Type",
      "default": "pdf-document",
      "x-es": {
        "type": "keyword",
        "ignore_above": 8191
      },
      "type": "string"
    },
    "description": {
      "$ref": "#/definitions/CCSDocumentDescription"
    },
    "file-info": {
      "$ref": "#/definitions/CCSFileInfoObject"
    },
    "main-text": {
      "title": "Main-Text",
      "type": "array",
      "items": {
        "anyOf": [
          {
            "$ref": "#/definitions/Ref"
          },
          {
            "$ref": "#/definitions/RecursiveList"
          },
          {
            "$ref": "#/definitions/BaseText"
          }
        ]
      }
    },
    "figures": {
      "title": "Figures",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BaseCell"
      }
    },
    "tables": {
      "title": "Tables",
      "type": "array",
      "items": {
        "$ref": "#/definitions/Table"
      }
    },
    "bitmaps": {
      "title": "Bitmaps",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BitmapObject"
      }
    },
    "equations": {
      "title": "Equations",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BaseCell"
      }
    },
    "footnotes": {
      "title": "Footnotes",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BaseText"
      }
    },
    "page-dimensions": {
      "title": "Page-Dimensions",
      "type": "array",
      "items": {
        "$ref": "#/definitions/PageDimensions"
      }
    },
    "page-footers": {
      "title": "Page-Footers",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BaseText"
      }
    },
    "page-headers": {
      "title": "Page-Headers",
      "type": "array",
      "items": {
        "$ref": "#/definitions/BaseText"
      }
    },
    "_s3_data": {
      "$ref": "#/definitions/S3Data"
    }
  },
  "required": [
    "name",
    "description",
    "file-info",
    "main-text"
  ],
  "definitions": {
    "Affiliation": {
      "title": "Affiliation",
      "type": "object",
      "properties": {
        "name": {
          "title": "Name",
          "x-es": {
            "fields": {
              "lower": {
                "normalizer": "lowercase_asciifolding",
                "type": "keyword"
              },
              "keyword": {
                "type": "keyword"
              }
            },
            "type": "keyword"
          },
          "type": "string"
        },
        "id": {
          "title": "Id",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "source": {
          "title": "Source",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        }
      },
      "required": [
        "name",
        "id",
        "source"
      ]
    },
    "Author": {
      "title": "Author",
      "type": "object",
      "properties": {
        "name": {
          "title": "Name",
          "x-es": {
            "fields": {
              "lower": {
                "normalizer": "lowercase_asciifolding",
                "type": "keyword"
              },
              "keyword": {
                "type": "keyword"
              }
            },
            "type": "keyword"
          },
          "type": "string"
        },
        "id": {
          "title": "Id",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "source": {
          "title": "Source",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "affiliations": {
          "title": "Affiliations",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Affiliation"
          }
        }
      },
      "required": [
        "name",
        "id",
        "source",
        "affiliations"
      ]
    },
    "Identifier": {
      "title": "Identifier",
      "type": "object",
      "properties": {
        "type": {
          "title": "Type",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "value": {
          "title": "Value",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "_name": {
          "title": " Name",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        }
      },
      "required": [
        "type",
        "value",
        "_name"
      ]
    },
    "Log": {
      "title": "Log",
      "type": "object",
      "properties": {
        "agent": {
          "title": "Agent",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "type": {
          "title": "Type",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "comment": {
          "title": "Comment",
          "type": "string"
        },
        "date": {
          "title": "Date",
          "x-es": {
            "type": "date"
          },
          "type": "string",
          "format": "date-time"
        }
      },
      "required": [
        "agent",
        "type",
        "comment",
        "date"
      ]
    },
    "CCSDocumentDescription": {
      "title": "CCSDocumentDescription",
      "type": "object",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "abstract": {
          "title": "Abstract",
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "authors": {
          "title": "Authors",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Author"
          }
        },
        "affiliations": {
          "title": "Affiliations",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Affiliation"
          }
        },
        "subjects": {
          "title": "Subjects",
          "x-es": {
            "fields": {
              "keyword": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "keywords": {
          "title": "Keywords",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "publication_date": {
          "title": "Publication Date",
          "x-es": {
            "type": "date"
          },
          "type": "string",
          "format": "date-time"
        },
        "languages": {
          "title": "Languages",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "publishers": {
          "title": "Publishers",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "url_refs": {
          "title": "Url Refs",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "references": {
          "title": "References",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Identifier"
          }
        },
        "advanced": {
          "title": "Advanced",
          "additionalProperties": {},
          "properties": {},
          "type": "object"
        },
        "analytics": {
          "title": "Analytics",
          "additionalProperties": {},
          "properties": {},
          "type": "object"
        },
        "logs": {
          "title": "Logs",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Log"
          }
        }
      },
      "required": [
        "title",
        "abstract",
        "authors",
        "affiliations",
        "subjects",
        "keywords",
        "publication_date",
        "languages",
        "publishers",
        "url_refs",
        "references",
        "advanced",
        "analytics",
        "logs"
      ]
    },
    "CCSFileInfoDescription": {
      "title": "CCSFileInfoDescription",
      "type": "object",
      "properties": {
        "author": {
          "title": "Author",
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "keywords": {
          "title": "Keywords",
          "type": "string"
        },
        "subject": {
          "title": "Subject",
          "type": "string"
        },
        "title": {
          "title": "Title",
          "type": "string"
        }
      }
    },
    "PageReference": {
      "title": "PageReference",
      "type": "object",
      "properties": {
        "hash": {
          "title": "Hash",
          "type": "string"
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "page": {
          "title": "Page",
          "type": "integer"
        }
      },
      "required": [
        "hash",
        "model",
        "page"
      ]
    },
    "CCSFileInfoObject": {
      "title": "CCSFileInfoObject",
      "type": "object",
      "properties": {
        "filename": {
          "title": "Filename",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "#-pages": {
          "title": "#-Pages",
          "type": "integer"
        },
        "document-hash": {
          "title": "Document-Hash",
          "type": "string"
        },
        "collection-name": {
          "title": "Collection-Name",
          "type": "string"
        },
        "description": {
          "$ref": "#/definitions/CCSFileInfoDescription"
        },
        "page-hashes": {
          "title": "Page-Hashes",
          "type": "array",
          "items": {
            "$ref": "#/definitions/PageReference"
          }
        },
        "filename-prov": {
          "title": "Filename-Prov",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        }
      },
      "required": [
        "filename",
        "#-pages",
        "document-hash",
        "collection-name",
        "description",
        "page-hashes",
        "filename-prov"
      ]
    },
    "Ref": {
      "title": "Ref",
      "type": "object",
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "type": "string"
        },
        "__ref": {
          "title": "  Ref",
          "type": "string"
        }
      },
      "required": [
        "name",
        "type",
        "__ref"
      ]
    },
    "Prov": {
      "title": "Prov",
      "type": "object",
      "properties": {
        "bbox": {
          "title": "Bbox",
          "type": "array",
          "items": [
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ]
        },
        "page": {
          "title": "Page",
          "type": "integer"
        },
        "span": {
          "title": "Span",
          "type": "array",
          "items": [
            {
              "type": "integer"
            },
            {
              "type": "integer"
            }
          ]
        }
      },
      "required": [
        "bbox",
        "page",
        "span"
      ]
    },
    "ListItem": {
      "title": "ListItem",
      "type": "object",
      "properties": {
        "text": {
          "title": "Text",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "name": {
          "title": "Name",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "font": {
          "title": "Font",
          "type": "string"
        },
        "prov": {
          "title": "Prov",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Prov"
          }
        },
        "identifier": {
          "title": "Identifier",
          "type": "string"
        }
      },
      "required": [
        "text",
        "type",
        "identifier"
      ]
    },
    "RecursiveList": {
      "title": "RecursiveList",
      "type": "object",
      "properties": {
        "data": {
          "title": "Data",
          "type": "array",
          "items": {
            "anyOf": [
              {
                "$ref": "#/definitions/ListItem"
              },
              {
                "$ref": "#/definitions/RecursiveList"
              }
            ]
          }
        },
        "name": {
          "title": "Name",
          "type": "string"
        },
        "prov": {
          "title": "Prov",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Prov"
          }
        },
        "type": {
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "data",
        "type"
      ]
    },
    "BaseText": {
      "title": "BaseText",
      "type": "object",
      "properties": {
        "text": {
          "title": "Text",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "name": {
          "title": "Name",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        },
        "font": {
          "title": "Font",
          "type": "string"
        },
        "prov": {
          "title": "Prov",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Prov"
          }
        }
      },
      "required": [
        "text",
        "type"
      ]
    },
    "BoundingBoxContainer": {
      "title": "BoundingBoxContainer",
      "type": "object",
      "properties": {
        "min": {
          "title": "Min",
          "type": "array",
          "items": [
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ]
        },
        "max": {
          "title": "Max",
          "type": "array",
          "items": [
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ]
        }
      },
      "required": [
        "min",
        "max"
      ]
    },
    "CellsContainer": {
      "title": "CellsContainer",
      "type": "object",
      "properties": {
        "data": {
          "title": "Data",
          "type": "array",
          "items": {
            "type": "array",
            "items": [
              {
                "type": "number"
              },
              {
                "type": "number"
              },
              {
                "type": "number"
              },
              {
                "type": "number"
              },
              {
                "type": "string"
              },
              {
                "type": "string"
              }
            ]
          }
        },
        "header": {
          "title": "Header",
          "default": [
            "x0",
            "y0",
            "x1",
            "y1",
            "font",
            "text"
          ],
          "type": "array",
          "items": [
            {
              "enum": [
                "x0"
              ],
              "type": "string"
            },
            {
              "enum": [
                "y0"
              ],
              "type": "string"
            },
            {
              "enum": [
                "x1"
              ],
              "type": "string"
            },
            {
              "enum": [
                "y1"
              ],
              "type": "string"
            },
            {
              "enum": [
                "font"
              ],
              "type": "string"
            },
            {
              "enum": [
                "text"
              ],
              "type": "string"
            }
          ]
        }
      },
      "required": [
        "data"
      ]
    },
    "BaseCell": {
      "title": "BaseCell",
      "type": "object",
      "properties": {
        "bounding-box": {
          "$ref": "#/definitions/BoundingBoxContainer"
        },
        "cells": {
          "$ref": "#/definitions/CellsContainer"
        },
        "prov": {
          "title": "Prov",
          "type": "array",
          "items": {
            "$ref": "#/definitions/Prov"
          }
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        }
      },
      "required": [
        "bounding-box",
        "cells",
        "text",
        "type"
      ]
    },
    "TableCell": {
      "title": "TableCell",
      "type": "object",
      "properties": {
        "bbox": {
          "title": "Bbox",
          "type": "array",
          "items": [
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            },
            {
              "type": "number"
            }
          ]
        },
        "spans": {
          "title": "Spans",
          "type": "array",
          "items": {
            "type": "array",
            "items": [
              {
                "type": "integer"
              },
              {
                "type": "integer"
              }
            ]
          }
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "text",
        "type"
      ]
    },
    "Table": {
      "title": "Table",
      "type": "object",
      "properties": {
        "num_cols": {
          "title": "Num Cols",
          "type": "integer"
        },
        "num_rows": {
          "title": "Num Rows",
          "type": "integer"
        },
        "bounding_box": {
          "$ref": "#/definitions/BoundingBoxContainer"
        },
        "cells": {
          "$ref": "#/definitions/CellsContainer"
        },
        "data": {
          "title": "Data",
          "type": "array",
          "items": {
            "type": "array",
            "items": {
              "$ref": "#/definitions/TableCell"
            }
          }
        },
        "model": {
          "title": "Model",
          "type": "string"
        },
        "prov": {
          "$ref": "#/definitions/Prov"
        },
        "text": {
          "title": "Text",
          "type": "string"
        },
        "type": {
          "title": "Type",
          "type": "string"
        }
      },
      "required": [
        "num_cols",
        "num_rows",
        "data",
        "text",
        "type"
      ]
    },
    "BitmapObject": {
      "title": "BitmapObject",
      "type": "object",
      "properties": {
        "type": {
          "title": "Type",
          "type": "string"
        },
        "bounding_box": {
          "$ref": "#/definitions/BoundingBoxContainer"
        },
        "prov": {
          "$ref": "#/definitions/Prov"
        }
      },
      "required": [
        "type",
        "bounding_box",
        "prov"
      ]
    },
    "PageDimensions": {
      "title": "PageDimensions",
      "type": "object",
      "properties": {
        "height": {
          "title": "Height",
          "type": "number"
        },
        "page": {
          "title": "Page",
          "type": "integer"
        },
        "width": {
          "title": "Width",
          "type": "number"
        }
      },
      "required": [
        "height",
        "page",
        "width"
      ]
    },
    "S3Resource": {
      "title": "S3Resource",
      "type": "object",
      "properties": {
        "mime": {
          "title": "Mime",
          "type": "string"
        },
        "path": {
          "title": "Path",
          "type": "string"
        },
        "page": {
          "title": "Page",
          "type": "integer"
        }
      },
      "required": [
        "mime",
        "path"
      ]
    },
    "S3Data": {
      "title": "S3Data",
      "type": "object",
      "properties": {
        "pdf_document": {
          "title": "Pdf Document",
          "type": "array",
          "items": {
            "$ref": "#/definitions/S3Resource"
          }
        },
        "pdf_pages": {
          "title": "Pdf Pages",
          "type": "array",
          "items": {
            "$ref": "#/definitions/S3Resource"
          }
        }
      }
    }
  }
}
```
</content>
</file_9>

<file_10>
<path>resources/schemas/generated/minimal_document_schema_flat.json</path>
<content>
```json
{
  "title": "MinimalDocument",
  "type": "object",
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "type": {
      "title": "Type",
      "default": "document",
      "type": "string"
    },
    "description": {
      "title": "CCSDocumentDescription",
      "type": "object",
      "properties": {
        "title": {
          "title": "Title",
          "type": "string"
        },
        "abstract": {
          "title": "Abstract",
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "authors": {
          "title": "Authors",
          "type": "array",
          "items": {
            "title": "Author",
            "type": "object",
            "properties": {
              "name": {
                "title": "Name",
                "x-es": {
                  "fields": {
                    "lower": {
                      "normalizer": "lowercase_asciifolding",
                      "type": "keyword"
                    },
                    "keyword": {
                      "type": "keyword"
                    }
                  },
                  "type": "keyword"
                },
                "type": "string"
              },
              "id": {
                "title": "Id",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "source": {
                "title": "Source",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "affiliations": {
                "title": "Affiliations",
                "type": "array",
                "items": {
                  "title": "Affiliation",
                  "type": "object",
                  "properties": {
                    "name": {
                      "title": "Name",
                      "x-es": {
                        "fields": {
                          "lower": {
                            "normalizer": "lowercase_asciifolding",
                            "type": "keyword"
                          },
                          "keyword": {
                            "type": "keyword"
                          }
                        },
                        "type": "keyword"
                      },
                      "type": "string"
                    },
                    "id": {
                      "title": "Id",
                      "x-es": {
                        "type": "keyword",
                        "ignore_above": 8191
                      },
                      "type": "string"
                    },
                    "source": {
                      "title": "Source",
                      "x-es": {
                        "type": "keyword",
                        "ignore_above": 8191
                      },
                      "type": "string"
                    }
                  },
                  "required": [
                    "name",
                    "id",
                    "source"
                  ]
                }
              }
            },
            "required": [
              "name",
              "id",
              "source",
              "affiliations"
            ]
          }
        },
        "affiliations": {
          "title": "Affiliations",
          "type": "array",
          "items": {
            "title": "Affiliation",
            "type": "object",
            "properties": {
              "name": {
                "title": "Name",
                "x-es": {
                  "fields": {
                    "lower": {
                      "normalizer": "lowercase_asciifolding",
                      "type": "keyword"
                    },
                    "keyword": {
                      "type": "keyword"
                    }
                  },
                  "type": "keyword"
                },
                "type": "string"
              },
              "id": {
                "title": "Id",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "source": {
                "title": "Source",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              }
            },
            "required": [
              "name",
              "id",
              "source"
            ]
          }
        },
        "subjects": {
          "title": "Subjects",
          "x-es": {
            "fields": {
              "keyword": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "keywords": {
          "title": "Keywords",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "publication_date": {
          "title": "Publication Date",
          "x-es": {
            "type": "date"
          },
          "type": "string",
          "format": "date-time"
        },
        "languages": {
          "title": "Languages",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "publishers": {
          "title": "Publishers",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "url_refs": {
          "title": "Url Refs",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "references": {
          "title": "References",
          "type": "array",
          "items": {
            "title": "Identifier",
            "type": "object",
            "properties": {
              "type": {
                "title": "Type",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "value": {
                "title": "Value",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "_name": {
                "title": " Name",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              }
            },
            "required": [
              "type",
              "value",
              "_name"
            ]
          }
        },
        "advanced": {
          "title": "Advanced",
          "additionalProperties": {},
          "properties": {},
          "type": "object"
        },
        "analytics": {
          "title": "Analytics",
          "additionalProperties": {},
          "properties": {},
          "type": "object"
        },
        "logs": {
          "title": "Logs",
          "type": "array",
          "items": {
            "title": "Log",
            "type": "object",
            "properties": {
              "agent": {
                "title": "Agent",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "type": {
                "title": "Type",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "comment": {
                "title": "Comment",
                "type": "string"
              },
              "date": {
                "title": "Date",
                "x-es": {
                  "type": "date"
                },
                "type": "string",
                "format": "date-time"
              }
            },
            "required": [
              "agent",
              "type",
              "comment",
              "date"
            ]
          }
        }
      },
      "required": [
        "title",
        "abstract",
        "authors",
        "affiliations",
        "subjects",
        "keywords",
        "publication_date",
        "languages",
        "publishers",
        "url_refs",
        "references",
        "advanced",
        "analytics",
        "logs"
      ]
    },
    "file-info": {
      "title": "FileInfoObject",
      "type": "object",
      "properties": {
        "filename": {
          "title": "Filename",
          "x-es": {
            "type": "keyword",
            "ignore_above": 8191
          },
          "type": "string"
        }
      },
      "required": [
        "filename"
      ]
    },
    "main-text": {
      "title": "Main-Text",
      "type": "array",
      "items": {
        "anyOf": [
          {
            "title": "Ref",
            "type": "object",
            "properties": {
              "name": {
                "title": "Name",
                "type": "string"
              },
              "type": {
                "title": "Type",
                "type": "string"
              },
              "__ref": {
                "title": "  Ref",
                "type": "string"
              }
            },
            "required": [
              "name",
              "type",
              "__ref"
            ]
          },
          {
            "title": "BaseList",
            "type": "object",
            "properties": {
              "data": {
                "title": "Data",
                "type": "array",
                "items": {
                  "title": "ListItem",
                  "type": "object",
                  "properties": {
                    "text": {
                      "title": "Text",
                      "type": "string"
                    },
                    "type": {
                      "title": "Type",
                      "x-es": {
                        "type": "keyword",
                        "ignore_above": 8191
                      },
                      "type": "string"
                    },
                    "name": {
                      "title": "Name",
                      "x-es": {
                        "type": "keyword",
                        "ignore_above": 8191
                      },
                      "type": "string"
                    },
                    "font": {
                      "title": "Font",
                      "type": "string"
                    },
                    "prov": {
                      "title": "Prov",
                      "type": "array",
                      "items": {
                        "title": "Prov",
                        "type": "object",
                        "properties": {
                          "bbox": {
                            "title": "Bbox",
                            "type": "array",
                            "items": [
                              {
                                "type": "number"
                              },
                              {
                                "type": "number"
                              },
                              {
                                "type": "number"
                              },
                              {
                                "type": "number"
                              }
                            ]
                          },
                          "page": {
                            "title": "Page",
                            "type": "integer"
                          },
                          "span": {
                            "title": "Span",
                            "type": "array",
                            "items": [
                              {
                                "type": "integer"
                              },
                              {
                                "type": "integer"
                              }
                            ]
                          }
                        },
                        "required": [
                          "bbox",
                          "page",
                          "span"
                        ]
                      }
                    },
                    "identifier": {
                      "title": "Identifier",
                      "type": "string"
                    }
                  },
                  "required": [
                    "text",
                    "type",
                    "identifier"
                  ]
                }
              },
              "name": {
                "title": "Name",
                "type": "string"
              },
              "prov": {
                "title": "Prov",
                "type": "array",
                "items": {
                  "title": "Prov",
                  "type": "object",
                  "properties": {
                    "bbox": {
                      "title": "Bbox",
                      "type": "array",
                      "items": [
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        }
                      ]
                    },
                    "page": {
                      "title": "Page",
                      "type": "integer"
                    },
                    "span": {
                      "title": "Span",
                      "type": "array",
                      "items": [
                        {
                          "type": "integer"
                        },
                        {
                          "type": "integer"
                        }
                      ]
                    }
                  },
                  "required": [
                    "bbox",
                    "page",
                    "span"
                  ]
                }
              },
              "type": {
                "title": "Type",
                "type": "string"
              }
            },
            "required": [
              "data",
              "type"
            ]
          },
          {
            "title": "BaseText",
            "type": "object",
            "properties": {
              "text": {
                "title": "Text",
                "type": "string"
              },
              "type": {
                "title": "Type",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "name": {
                "title": "Name",
                "x-es": {
                  "type": "keyword",
                  "ignore_above": 8191
                },
                "type": "string"
              },
              "font": {
                "title": "Font",
                "type": "string"
              },
              "prov": {
                "title": "Prov",
                "type": "array",
                "items": {
                  "title": "Prov",
                  "type": "object",
                  "properties": {
                    "bbox": {
                      "title": "Bbox",
                      "type": "array",
                      "items": [
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        },
                        {
                          "type": "number"
                        }
                      ]
                    },
                    "page": {
                      "title": "Page",
                      "type": "integer"
                    },
                    "span": {
                      "title": "Span",
                      "type": "array",
                      "items": [
                        {
                          "type": "integer"
                        },
                        {
                          "type": "integer"
                        }
                      ]
                    }
                  },
                  "required": [
                    "bbox",
                    "page",
                    "span"
                  ]
                }
              }
            },
            "required": [
              "text",
              "type"
            ]
          }
        ]
      }
    },
    "figures": {
      "title": "Figures",
      "type": "array",
      "items": {
        "title": "BaseCell",
        "type": "object",
        "properties": {
          "bounding-box": {
            "title": "BoundingBoxContainer",
            "type": "object",
            "properties": {
              "min": {
                "title": "Min",
                "type": "array",
                "items": [
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  }
                ]
              },
              "max": {
                "title": "Max",
                "type": "array",
                "items": [
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  }
                ]
              }
            },
            "required": [
              "min",
              "max"
            ]
          },
          "cells": {
            "title": "CellsContainer",
            "type": "object",
            "properties": {
              "data": {
                "title": "Data",
                "type": "array",
                "items": {
                  "type": "array",
                  "items": [
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    }
                  ]
                }
              },
              "header": {
                "title": "Header",
                "default": [
                  "x0",
                  "y0",
                  "x1",
                  "y1",
                  "font",
                  "text"
                ],
                "type": "array",
                "items": [
                  {
                    "enum": [
                      "x0"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "y0"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "x1"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "y1"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "font"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "text"
                    ],
                    "type": "string"
                  }
                ]
              }
            },
            "required": [
              "data"
            ]
          },
          "prov": {
            "title": "Prov",
            "type": "array",
            "items": {
              "title": "Prov",
              "type": "object",
              "properties": {
                "bbox": {
                  "title": "Bbox",
                  "type": "array",
                  "items": [
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    }
                  ]
                },
                "page": {
                  "title": "Page",
                  "type": "integer"
                },
                "span": {
                  "title": "Span",
                  "type": "array",
                  "items": [
                    {
                      "type": "integer"
                    },
                    {
                      "type": "integer"
                    }
                  ]
                }
              },
              "required": [
                "bbox",
                "page",
                "span"
              ]
            }
          },
          "text": {
            "title": "Text",
            "type": "string"
          },
          "type": {
            "title": "Type",
            "x-es": {
              "type": "keyword",
              "ignore_above": 8191
            },
            "type": "string"
          }
        },
        "required": [
          "bounding-box",
          "cells",
          "text",
          "type"
        ]
      }
    },
    "tables": {
      "title": "Tables",
      "type": "array",
      "items": {
        "title": "Table",
        "type": "object",
        "properties": {
          "num_cols": {
            "title": "Num Cols",
            "type": "integer"
          },
          "num_rows": {
            "title": "Num Rows",
            "type": "integer"
          },
          "bounding_box": {
            "title": "BoundingBoxContainer",
            "type": "object",
            "properties": {
              "min": {
                "title": "Min",
                "type": "array",
                "items": [
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  }
                ]
              },
              "max": {
                "title": "Max",
                "type": "array",
                "items": [
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  }
                ]
              }
            },
            "required": [
              "min",
              "max"
            ]
          },
          "cells": {
            "title": "CellsContainer",
            "type": "object",
            "properties": {
              "data": {
                "title": "Data",
                "type": "array",
                "items": {
                  "type": "array",
                  "items": [
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "number"
                    },
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    }
                  ]
                }
              },
              "header": {
                "title": "Header",
                "default": [
                  "x0",
                  "y0",
                  "x1",
                  "y1",
                  "font",
                  "text"
                ],
                "type": "array",
                "items": [
                  {
                    "enum": [
                      "x0"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "y0"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "x1"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "y1"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "font"
                    ],
                    "type": "string"
                  },
                  {
                    "enum": [
                      "text"
                    ],
                    "type": "string"
                  }
                ]
              }
            },
            "required": [
              "data"
            ]
          },
          "data": {
            "title": "Data",
            "type": "array",
            "items": {
              "type": "array",
              "items": {
                "title": "TableCell",
                "type": "object",
                "properties": {
                  "bbox": {
                    "title": "Bbox",
                    "type": "array",
                    "items": [
                      {
                        "type": "number"
                      },
                      {
                        "type": "number"
                      },
                      {
                        "type": "number"
                      },
                      {
                        "type": "number"
                      }
                    ]
                  },
                  "spans": {
                    "title": "Spans",
                    "type": "array",
                    "items": {
                      "type": "array",
                      "items": [
                        {
                          "type": "integer"
                        },
                        {
                          "type": "integer"
                        }
                      ]
                    }
                  },
                  "text": {
                    "title": "Text",
                    "type": "string"
                  },
                  "type": {
                    "title": "Type",
                    "type": "string"
                  }
                },
                "required": [
                  "text",
                  "type"
                ]
              }
            }
          },
          "model": {
            "title": "Model",
            "type": "string"
          },
          "prov": {
            "title": "Prov",
            "type": "object",
            "properties": {
              "bbox": {
                "title": "Bbox",
                "type": "array",
                "items": [
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "number"
                  }
                ]
              },
              "page": {
                "title": "Page",
                "type": "integer"
              },
              "span": {
                "title": "Span",
                "type": "array",
                "items": [
                  {
                    "type": "integer"
                  },
                  {
                    "type": "integer"
                  }
                ]
              }
            },
            "required": [
              "bbox",
              "page",
              "span"
            ]
          },
          "text": {
            "title": "Text",
            "type": "string"
          },
          "type": {
            "title": "Type",
            "type": "string"
          }
        },
        "required": [
          "num_cols",
          "num_rows",
          "data",
          "text",
          "type"
        ]
      }
    }
  },
  "required": [
    "name",
    "description",
    "file-info",
    "main-text"
  ]
}
```
</content>
</file_10>

<file_11>
<path>resources/schemas/search/search_doc_mapping.json</path>
<content>
```json
{
  "mappings": {
    "dynamic": false,
    "_size": {
      "enabled": true
    },
    "_meta": {
      "$ref": "ccs:schemas#/Document"
    },
    "properties": {
      "description": {
        "type": "object",
        "properties": {
          "abstract": {
            "type": "text"
          },
          "affiliations": {
            "type": "keyword"
          },
          "authors": {
            "type": "keyword"
          },
          "title": {
            "type": "text"
          }
        }
      },
      "figures": {
        "type": "object",
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "type": "keyword"
          },
          "prov": {
            "type": "object",
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "file-info": {
        "type": "object",
        "properties": {
          "filename": {
            "type": "text"
          }
        }
      },
      "main-text": {
        "type": "object",
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "type": "keyword"
          },
          "name": {
            "type": "keyword"
          },
          "prov": {
            "type": "object",
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "_name": {
        "type": "keyword"
      },
      "tables": {
        "type": "object",
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "type": "keyword"
          },
          "prov": {
            "type": "object",
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "type": {
        "type": "keyword"
      }
    }
  }
}

```
</content>
</file_11>

<file_12>
<path>resources/schemas/search/search_doc_mapping_v2.json</path>
<content>
```json
{
  "settings": {
    "analysis": {
      "normalizer": {
        "lowercase_asciifolding": {
          "type": "custom",
          "filter": [
            "lowercase",
            "asciifolding"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": false,
    "_size": {
      "enabled": true
    },
    "_meta": {
      "version": "1.0",
      "$ref": "ccs:schemas#/Document"
    },
    "properties": {
      "_name": {
        "type": "text"
      },
      "identifiers": {
        "properties": {
          "_name": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "type": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "value": {
            "ignore_above": 8191,
            "type": "keyword"
          }
        }
      },
      "description": {
        "properties": {
          "abstract": {
            "type": "text"
          },
          "affiliations": {
            "properties": {
              "name": {
                "type": "text",
                "fields": {
                  "lower": {
                    "normalizer": "lowercase_asciifolding",
                    "type": "keyword"
                  },
                  "keyword": {
                    "type": "keyword"
                  }
                }
              },
              "id": {
                "ignore_above": 8191,
                "type": "keyword"
              },
              "source": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          },
          "authors": {
            "properties": {
              "name": {
                "type": "text",
                "fields": {
                  "lower": {
                    "normalizer": "lowercase_asciifolding",
                    "type": "keyword"
                  },
                  "keyword": {
                    "type": "keyword"
                  }
                }
              },
              "affiliations": {
                "properties": {
                  "name": {
                    "type": "text",
                    "fields": {
                      "lower": {
                        "normalizer": "lowercase_asciifolding",
                        "type": "keyword"
                      },
                      "keyword": {
                        "type": "keyword"
                      }
                    }
                  },
                  "id": {
                    "ignore_above": 8191,
                    "type": "keyword"
                  },
                  "source": {
                    "ignore_above": 8191,
                    "type": "keyword"
                  }
                }
              }
            }
          },
          "title": {
            "type": "text"
          },
          "subjects": {
            "type": "text",
            "fields": {
              "keyword": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          },
          "publication_date": {
            "type": "date"
          },
          "languages": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "publishers": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "url_refs": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "references": {
            "properties": {
              "_name": {
                "ignore_above": 8191,
                "type": "keyword"
              },
              "type": {
                "ignore_above": 8191,
                "type": "keyword"
              },
              "value": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          },
          "logs": {
            "properties": {
              "date": {
                "type": "date"
              },
              "agent": {
                "ignore_above": 8191,
                "type": "keyword"
              },
              "comment": {
                "type": "text"
              },
              "type": {
                "ignore_above": 8191,
                "type": "keyword"
              }
            }
          }
        }
      },
      "figures": {
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "prov": {
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "file-info": {
        "properties": {
          "filename-prov": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "filename": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "document-hash": {
            "ignore_above": 8191,
            "type": "keyword"
          }
        }
      },
      "main-text": {
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "name": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "prov": {
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "tables": {
        "properties": {
          "text": {
            "type": "text"
          },
          "type": {
            "ignore_above": 8191,
            "type": "keyword"
          },
          "prov": {
            "properties": {
              "page": {
                "type": "integer"
              }
            }
          }
        }
      },
      "type": {
        "ignore_above": 8191,
        "type": "keyword"
      }
    }
  }
}

```
</content>
</file_12>

<file_13>
<path>search/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models and utility functions for search database mappings."""

```
</content>
</file_13>

<file_14>
<path>search/json_schema_to_search_mapper.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Methods to convert a JSON Schema into a search database schema."""
import re
from copy import deepcopy
from typing import Any, Optional, Pattern, Tuple, TypedDict

from jsonref import replace_refs


class SearchIndexDefinition(TypedDict):
    """Data type for an index basic definition (settings and mappings)."""

    settings: dict
    mappings: dict


class JsonSchemaToSearchMapper:
    """Map a JSON Schema to an search database schema.

    The generated database schema is a mapping describing the fields from the
    JSON Schema and how they should be indexed in a Lucene index of a search database.

    Potential issues:
    - Tuples may not be converted properly (e.g., Tuple[float,float,float,str,str])
    - Method `_remove_keys` may lead to wrong results if a field is named `properties`.
    """

    def __init__(
        self,
        settings_extra: Optional[dict] = None,
        mappings_extra: Optional[dict] = None,
    ):
        """Create an instance of the mapper with default settings."""
        self.settings = {
            "analysis": {
                # Create a normalizer for lowercase ascii folding,
                # this is used in keyword fields
                "normalizer": {
                    "lowercase_asciifolding": {
                        "type": "custom",
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            }
        }

        self.settings_extra = settings_extra
        self.mappings_extra = mappings_extra

        self._re_es_flag = re.compile(r"^(?:x-es-)(.*)")

        self._rm_keys = (
            "description",
            "required",
            "title",
            "additionalProperties",
            "format",
            "enum",
            "pattern",
            "$comment",
            "default",
            "minItems",
            "maxItems",
            "minimum",
            "maximum",
            "minLength",
            "maxLength",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "$defs",
            "const",
        )

        self._suppress_key = "x-es-suppress"

        self._type_format_mappings: dict[tuple[str, str], str] = {
            ("string", "date-time"): "date",
        }

        self._type_mappings = {
            "number": "double",
            "string": "text",
        }

        self._types_to_remove = ("object",)

    def get_index_definition(self, schema: dict) -> SearchIndexDefinition:
        """Generates a search database schema from a JSON Schema.

        The search database schema consists of the sections `settings` and `mappings`,
        which define the fields, their data types, and other specifications to index
        JSON documents into a Lucene index.
        """
        mapping = deepcopy(schema)

        mapping = self._suppress(mapping, self._suppress_key)

        mapping = replace_refs(mapping)

        mapping = self._merge_unions(mapping)

        mapping = self._clean_types(mapping)

        mapping = self._collapse_arrays(mapping)

        mapping = self._remove_keys(mapping, self._rm_keys)

        mapping = self._translate_keys_re(mapping)

        mapping = self._clean(mapping)

        mapping.pop("definitions", None)

        result = SearchIndexDefinition(
            settings=self.settings,
            mappings=mapping,
        )

        if self.mappings_extra:
            result["mappings"] = {**result["mappings"], **self.mappings_extra}

        if self.settings_extra:
            result["settings"] = {**result["settings"], **self.settings_extra}

        return result

    def _merge_unions(self, doc: dict) -> dict:
        """Merge objects of type anyOf, allOf, or oneOf (options).

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.

        Returns:
            A transformation of a JSON schema by merging option fields.
        """

        def _clean(value: Any) -> Any:
            if isinstance(value, list):
                return [_clean(v) for v in value]

            if isinstance(value, dict):
                union: list = []
                merged_union: dict = {}

                for k, v in value.items():
                    if k in ("oneOf", "allOf", "anyOf"):
                        union.extend(v)
                    else:
                        merged_union[k] = v

                if not union:
                    return {k: _clean(v) for k, v in value.items()}

                for u in union:
                    if not isinstance(u, dict):
                        continue

                    for k, v in u.items():
                        if k == "type" and v == "null":  # null values are irrelevant
                            continue
                        elif not isinstance(v, dict) or k not in merged_union:
                            merged_union[k] = _clean(v)
                        elif isinstance(v, dict) and k in merged_union:
                            merged_union[k] = _clean({**merged_union[k], **v})

                return merged_union

            return value

        return _clean(doc)

    def _clean_types(self, doc: dict) -> dict:
        """Clean field types originated from a JSON schema to obtain search mappings.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.

        Returns:
            A transformation of a JSON schema by merging option fields.
        """

        def _clean(value: Any) -> Any:
            if isinstance(value, list):
                return [_clean(v) for v in value]

            if isinstance(value, dict):
                if isinstance(value.get("type"), str):
                    t: str = value["type"]

                    # Tuples
                    if t == "array" and isinstance(value.get("items"), list):
                        items: list = value["items"]

                        if items:
                            value["items"] = value["items"][0]
                        else:
                            value["items"] = {}

                    # Unwanted types, such as 'object'
                    if t in self._types_to_remove:
                        value.pop("type", None)

                    # Map formats
                    f: str = value.get("format", "")
                    if (t, f) in self._type_format_mappings:
                        value["type"] = self._type_format_mappings[(t, f)]
                        value.pop("format", None)

                    # Map types, such as 'string' to 'text'
                    elif t in self._type_mappings:
                        value["type"] = self._type_mappings[t]

                return {k: _clean(v) for k, v in value.items()}

            return value

        return _clean(doc)

    @staticmethod
    def _collapse_arrays(doc: dict) -> dict:
        """Collapse arrays from a JSON schema to match a search database mappings.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.

        Returns:
            A transformation of a JSON schema by collapsing arrays.
        """

        def __collapse(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (__collapse(v) for v in d_)]

            if isinstance(d_, dict):
                if "type" in d_ and d_["type"] == "array" and "items" in d_:
                    collapsed = __collapse(d_["items"])

                    d_ = deepcopy(d_)
                    d_.pop("items", None)
                    d_.pop("type", None)

                    merged = {**d_, **collapsed}

                    return merged

                return {k: __collapse(v) for k, v in d_.items()}

            return d_

        return __collapse(doc)

    @staticmethod
    def _suppress(doc: dict, suppress_key: str) -> dict:
        """Remove a key from a JSON schema to match a search database mappings.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.
            key: The name of a field to be removed from the `doc`.

        Returns:
            A transformation of a JSON schema by removing the field `suppress_key`.
        """

        def __suppress(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (__suppress(v) for v in d_)]

            if isinstance(d_, dict):
                if suppress_key in d_ and d_[suppress_key] is True:
                    return {}
                else:
                    return {
                        k: v for k, v in ((k, __suppress(v)) for k, v in d_.items())
                    }
            return d_

        return __suppress(doc)

    @staticmethod
    def _remove_keys(doc: dict, keys: Tuple[str, ...]) -> dict:
        """Remove keys from a JSON schema to match a search database mappings.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.
            keys: Fields to be removed from the `doc`.

        Returns:
            A transformation of a JSON schema by removing the fields in `keys`.
        """

        def __remove(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (__remove(v) for v in d_)]

            if isinstance(d_, dict):
                result = {}
                for k, v in d_.items():
                    if k == "properties" and isinstance(v, dict):
                        # All properties must be included, they are not to be removed,
                        # even if they have a name of a key that's to be removed.
                        result[k] = {p_k: __remove(p_v) for p_k, p_v in v.items()}
                    elif k not in keys:
                        result[k] = __remove(v)

                return result

            return d_

        return __remove(doc)

    @staticmethod
    def _remove_keys_re(doc: dict, regx: Pattern) -> dict:
        """Remove keys from a JSON schema to match a search database mappings.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.
            keys: A pattern defining the fields to be removed from the `doc`.

        Returns:
            A transformation of a JSON schema by removing fields with a name pattern.
        """

        def __remove(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (__remove(v) for v in d_)]

            if isinstance(d_, dict):
                return {
                    k: v
                    for k, v in (
                        (k, __remove(v)) for k, v in d_.items() if not regx.match(k)
                    )
                }

            return d_

        return __remove(doc)

    def _translate_keys_re(self, doc: dict) -> dict:
        """Translate marked keys from a JSON schema to match a search database mappings.

        The keys to be translated should have a name that matches the pattern defined
        by this class patter, for instance, a name starting with `x-es-`.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.

        Returns:
            A transformation of a JSON schema towards a search database mappings.
        """

        def __translate(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (__translate(v) for v in d_)]

            if isinstance(d_, dict):
                new_dict = {}
                for k, v in d_.items():
                    new_dict[k] = __translate(v)

                delkeys = []
                for k in list(new_dict.keys()):
                    k_ = self._re_es_flag.sub(r"\1", k)
                    if k_ != k:
                        new_dict[k_] = new_dict[k]
                        delkeys.append(k)

                for k in delkeys:
                    new_dict.pop(k, None)

                return new_dict

            return d_

        return __translate(doc)

    @staticmethod
    def _clean(doc: dict) -> dict:
        """Recursively remove empty lists, dicts, strings, or None elements from a dict.

        Args:
            doc: A JSON schema or a transformation towards a search database mappings.

        Returns:
            A transformation of a JSON schema by removing empty objects.
        """

        def _empty(x) -> bool:
            return x is None or x == {} or x == [] or x == ""

        def _clean(d_: Any) -> Any:
            if isinstance(d_, list):
                return [v for v in (_clean(v) for v in d_) if not _empty(v)]

            if isinstance(d_, dict):
                return {
                    k: v
                    for k, v in ((k, _clean(v)) for k, v in d_.items())
                    if not _empty(v)
                }

            return d_

        return _clean(doc)

```
</content>
</file_14>

<file_15>
<path>search/mapping.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Methods to define fields in an index mapping of a search database."""
from typing import Any, Optional


def es_field(
    *,
    type: Optional[str] = None,
    ignore_above: Optional[int] = None,
    term_vector: Optional[str] = None,
    **kwargs: Any,
):
    """Create x-es kwargs to be passed to a `pydantic.Field` via unpacking."""
    all_kwargs = {**kwargs}

    if type is not None:
        all_kwargs["type"] = type

    if ignore_above is not None:
        all_kwargs["ignore_above"] = ignore_above

    if term_vector is not None:
        all_kwargs["term_vector"] = term_vector

    return {f"x-es-{k}": v for k, v in all_kwargs.items()}

```
</content>
</file_15>

<file_16>
<path>search/meta.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models and methods to define the metadata fields in database index mappings."""
from pathlib import Path
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, StrictStr, ValidationInfo, field_validator

from docling_core.search.package import Package
from docling_core.types.base import CollectionTypeEnum, StrictDateTime, UniqueList
from docling_core.utils.alias import AliasModel

ClassificationT = TypeVar("ClassificationT", bound=str)
DomainT = TypeVar("DomainT", bound=str)


class S3Path(BaseModel, extra="forbid"):
    """The path details within a cloud object storage for CCS-parsed files."""

    bucket: StrictStr
    prefix: StrictStr
    infix: StrictStr

    def __hash__(self):
        """Return the hash value for this S3Path object."""
        return hash((type(self),) + tuple(self.__dict__.values()))


class S3CcsData(BaseModel, extra="forbid"):
    """The access details to a cloud object storage for CCS-parsed files."""

    endpoint: StrictStr
    paths: UniqueList[S3Path] = Field(min_length=1)


class DocumentLicense(BaseModel, extra="forbid"):
    """Document license for a search database index within the index mappings."""

    code: Optional[list[StrictStr]] = None
    text: Optional[list[StrictStr]] = None


class Meta(AliasModel, Generic[ClassificationT, DomainT], extra="forbid"):
    """Metadata of a search database index within the index mappings."""

    aliases: Optional[list[StrictStr]] = None
    created: StrictDateTime
    description: Optional[StrictStr] = None
    source: StrictStr
    storage: Optional[StrictStr] = None
    display_name: Optional[StrictStr] = None
    type: CollectionTypeEnum
    classification: Optional[list[ClassificationT]] = None
    version: UniqueList[Package] = Field(min_length=1)
    license: Optional[StrictStr] = None
    filename: Optional[Path] = None
    domain: Optional[list[DomainT]] = None
    reference: Optional[StrictStr] = Field(default=None, alias="$ref")
    ccs_s3_data: Optional[S3CcsData] = None
    document_license: Optional[DocumentLicense] = None
    index_key: Optional[StrictStr] = None
    project_key: Optional[StrictStr] = None

    @field_validator("reference")
    @classmethod
    def reference_for_document(cls, v, info: ValidationInfo):
        """Validate the reference field for indexes of type Document."""
        if "type" in info.data and info.data["type"] == "Document":
            if v and v != "ccs:schemas#/Document":
                raise ValueError("wrong reference value for Document type")
            else:
                return "ccs:schemas#/Document"
        else:
            return v

    @field_validator("version")
    @classmethod
    def version_has_schema(cls, v):
        """Validate that the docling-core library is always set in version field."""
        docling_core = [item for item in v if item.name == "docling-core"]
        if not docling_core:
            raise ValueError(
                "the version should include at least a valid docling-core package"
            )
        elif len(docling_core) > 1:
            raise ValueError(
                "the version must not include more than 1 docling-core package"
            )
        else:
            return v

```
</content>
</file_16>

<file_17>
<path>search/package.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models and methods to define a package model."""

import importlib.metadata
import re
from typing import Final

from pydantic import BaseModel, StrictStr, StringConstraints
from typing_extensions import Annotated

VERSION_PATTERN: Final = (
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+"
    r"(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class Package(BaseModel, extra="forbid"):
    """Representation of a software package.

    The version needs to comply with Semantic Versioning 2.0.0.
    """

    name: StrictStr = "docling-core"
    version: Annotated[str, StringConstraints(strict=True, pattern=VERSION_PATTERN)] = (
        importlib.metadata.version("docling-core")
    )

    def __hash__(self):
        """Return the hash value for this S3Path object."""
        return hash((type(self),) + tuple(self.__dict__.values()))

    def get_major(self):
        """Get the major version of this package."""
        return re.match(VERSION_PATTERN, self.version)["major"]

    def get_minor(self):
        """Get the major version of this package."""
        return re.match(VERSION_PATTERN, self.version)["minor"]

    def get_patch(self):
        """Get the major version of this package."""
        return re.match(VERSION_PATTERN, self.version)["patch"]

    def get_pre_release(self):
        """Get the pre-release version of this package."""
        return re.match(VERSION_PATTERN, self.version)["prerelease"]

    def get_build_metadata(self):
        """Get the build metadata version of this package."""
        return re.match(VERSION_PATTERN, self.version)["buildmetadata"]

```
</content>
</file_17>

<file_18>
<path>transforms/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Data transformations package."""

```
</content>
</file_18>

<file_19>
<path>transforms/chunker/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the chunker types."""

from docling_core.transforms.chunker.base import BaseChunk, BaseChunker, BaseMeta
from docling_core.transforms.chunker.hierarchical_chunker import (
    DocChunk,
    DocMeta,
    HierarchicalChunker,
)

```
</content>
</file_19>

<file_20>
<path>transforms/chunker/base.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define base classes for chunking."""
import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Iterator

from pydantic import BaseModel

from docling_core.types.doc import DoclingDocument as DLDocument

DFLT_DELIM = "\n"


class BaseMeta(BaseModel):
    """Chunk metadata base class."""

    excluded_embed: ClassVar[list[str]] = []
    excluded_llm: ClassVar[list[str]] = []

    def export_json_dict(self) -> dict[str, Any]:
        """Helper method for exporting non-None keys to JSON mode.

        Returns:
            dict[str, Any]: The exported dictionary.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class BaseChunk(BaseModel):
    """Chunk base class."""

    text: str
    meta: BaseMeta

    def export_json_dict(self) -> dict[str, Any]:
        """Helper method for exporting non-None keys to JSON mode.

        Returns:
            dict[str, Any]: The exported dictionary.
        """
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class BaseChunker(BaseModel, ABC):
    """Chunker base class."""

    delim: str = DFLT_DELIM

    @abstractmethod
    def chunk(self, dl_doc: DLDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        """Chunk the provided document.

        Args:
            dl_doc (DLDocument): document to chunk

        Raises:
            NotImplementedError: in this abstract implementation

        Yields:
            Iterator[BaseChunk]: iterator over extracted chunks
        """
        raise NotImplementedError()

    def serialize(self, chunk: BaseChunk) -> str:
        """Serialize the given chunk. This base implementation is embedding-targeted.

        Args:
            chunk: chunk to serialize

        Returns:
            str: the serialized form of the chunk
        """
        meta = chunk.meta.export_json_dict()

        items = []
        for k in meta:
            if k not in chunk.meta.excluded_embed:
                if isinstance(meta[k], list):
                    items.append(
                        self.delim.join(
                            [
                                d if isinstance(d, str) else json.dumps(d)
                                for d in meta[k]
                            ]
                        )
                    )
                else:
                    items.append(json.dumps(meta[k]))
        items.append(chunk.text)

        return self.delim.join(items)

```
</content>
</file_20>

<file_21>
<path>transforms/chunker/hierarchical_chunker.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Chunker implementation leveraging the document structure."""

from __future__ import annotations

import logging
import re
from typing import Any, ClassVar, Final, Iterator, Literal, Optional

from pandas import DataFrame
from pydantic import Field, StringConstraints, field_validator
from typing_extensions import Annotated

from docling_core.search.package import VERSION_PATTERN
from docling_core.transforms.chunker import BaseChunk, BaseChunker, BaseMeta
from docling_core.types import DoclingDocument as DLDocument
from docling_core.types.doc.document import (
    DocItem,
    DocumentOrigin,
    LevelNumber,
    ListItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
)
from docling_core.types.doc.labels import DocItemLabel

_VERSION: Final = "1.0.0"

_KEY_SCHEMA_NAME = "schema_name"
_KEY_VERSION = "version"
_KEY_DOC_ITEMS = "doc_items"
_KEY_HEADINGS = "headings"
_KEY_CAPTIONS = "captions"
_KEY_ORIGIN = "origin"

_logger = logging.getLogger(__name__)


class DocMeta(BaseMeta):
    """Data model for Hierarchical Chunker chunk metadata."""

    schema_name: Literal["docling_core.transforms.chunker.DocMeta"] = Field(
        default="docling_core.transforms.chunker.DocMeta",
        alias=_KEY_SCHEMA_NAME,
    )
    version: Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)] = (
        Field(
            default=_VERSION,
            alias=_KEY_VERSION,
        )
    )
    doc_items: list[DocItem] = Field(
        alias=_KEY_DOC_ITEMS,
        min_length=1,
    )
    headings: Optional[list[str]] = Field(
        default=None,
        alias=_KEY_HEADINGS,
        min_length=1,
    )
    captions: Optional[list[str]] = Field(
        default=None,
        alias=_KEY_CAPTIONS,
        min_length=1,
    )
    origin: Optional[DocumentOrigin] = Field(
        default=None,
        alias=_KEY_ORIGIN,
    )

    excluded_embed: ClassVar[list[str]] = [
        _KEY_SCHEMA_NAME,
        _KEY_VERSION,
        _KEY_DOC_ITEMS,
        _KEY_ORIGIN,
    ]
    excluded_llm: ClassVar[list[str]] = [
        _KEY_SCHEMA_NAME,
        _KEY_VERSION,
        _KEY_DOC_ITEMS,
        _KEY_ORIGIN,
    ]

    @field_validator(_KEY_VERSION)
    @classmethod
    def check_version_is_compatible(cls, v: str) -> str:
        """Check if this meta item version is compatible with current version."""
        current_match = re.match(VERSION_PATTERN, _VERSION)
        doc_match = re.match(VERSION_PATTERN, v)
        if (
            doc_match is None
            or current_match is None
            or doc_match["major"] != current_match["major"]
            or doc_match["minor"] > current_match["minor"]
        ):
            raise ValueError(f"incompatible version {v} with schema version {_VERSION}")
        else:
            return _VERSION


class DocChunk(BaseChunk):
    """Data model for document chunks."""

    meta: DocMeta


class HierarchicalChunker(BaseChunker):
    r"""Chunker implementation leveraging the document layout.

    Args:
        merge_list_items (bool): Whether to merge successive list items.
            Defaults to True.
        delim (str): Delimiter to use for merging text. Defaults to "\n".
    """

    merge_list_items: bool = True

    @classmethod
    def _triplet_serialize(cls, table_df: DataFrame) -> str:

        # copy header as first row and shift all rows by one
        table_df.loc[-1] = table_df.columns  # type: ignore[call-overload]
        table_df.index = table_df.index + 1
        table_df = table_df.sort_index()

        rows = [str(item).strip() for item in table_df.iloc[:, 0].to_list()]
        cols = [str(item).strip() for item in table_df.iloc[0, :].to_list()]

        nrows = table_df.shape[0]
        ncols = table_df.shape[1]
        texts = [
            f"{rows[i]}, {cols[j]} = {str(table_df.iloc[i, j]).strip()}"
            for i in range(1, nrows)
            for j in range(1, ncols)
        ]
        output_text = ". ".join(texts)

        return output_text

    def chunk(self, dl_doc: DLDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        r"""Chunk the provided document.

        Args:
            dl_doc (DLDocument): document to chunk

        Yields:
            Iterator[Chunk]: iterator over extracted chunks
        """
        heading_by_level: dict[LevelNumber, str] = {}
        list_items: list[TextItem] = []
        for item, level in dl_doc.iterate_items():
            captions = None
            if isinstance(item, DocItem):

                # first handle any merging needed
                if self.merge_list_items:
                    if isinstance(
                        item, ListItem
                    ) or (  # TODO remove when all captured as ListItem:
                        isinstance(item, TextItem)
                        and item.label == DocItemLabel.LIST_ITEM
                    ):
                        list_items.append(item)
                        continue
                    elif list_items:  # need to yield
                        yield DocChunk(
                            text=self.delim.join([i.text for i in list_items]),
                            meta=DocMeta(
                                doc_items=list_items,
                                headings=[
                                    heading_by_level[k]
                                    for k in sorted(heading_by_level)
                                ]
                                or None,
                                origin=dl_doc.origin,
                            ),
                        )
                        list_items = []  # reset

                if isinstance(item, SectionHeaderItem) or (
                    isinstance(item, TextItem)
                    and item.label in [DocItemLabel.SECTION_HEADER, DocItemLabel.TITLE]
                ):
                    level = (
                        item.level
                        if isinstance(item, SectionHeaderItem)
                        else (0 if item.label == DocItemLabel.TITLE else 1)
                    )
                    heading_by_level[level] = item.text

                    # remove headings of higher level as they just went out of scope
                    keys_to_del = [k for k in heading_by_level if k > level]
                    for k in keys_to_del:
                        heading_by_level.pop(k, None)
                    continue

                if isinstance(item, TextItem) or (
                    (not self.merge_list_items) and isinstance(item, ListItem)
                ):
                    text = item.text
                elif isinstance(item, TableItem):
                    table_df = item.export_to_dataframe()
                    if table_df.shape[0] < 1 or table_df.shape[1] < 2:
                        # at least two cols needed, as first column contains row headers
                        continue
                    text = self._triplet_serialize(table_df=table_df)
                    captions = [
                        c.text for c in [r.resolve(dl_doc) for r in item.captions]
                    ] or None
                else:
                    continue
                c = DocChunk(
                    text=text,
                    meta=DocMeta(
                        doc_items=[item],
                        headings=[heading_by_level[k] for k in sorted(heading_by_level)]
                        or None,
                        captions=captions,
                        origin=dl_doc.origin,
                    ),
                )
                yield c

        if self.merge_list_items and list_items:  # need to yield
            yield DocChunk(
                text=self.delim.join([i.text for i in list_items]),
                meta=DocMeta(
                    doc_items=list_items,
                    headings=[heading_by_level[k] for k in sorted(heading_by_level)]
                    or None,
                    origin=dl_doc.origin,
                ),
            )

```
</content>
</file_21>

<file_22>
<path>transforms/chunker/hybrid_chunker.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Hybrid chunker implementation leveraging both doc structure & token awareness."""

import warnings
from typing import Any, Iterable, Iterator, Optional, Union

from pydantic import BaseModel, ConfigDict, PositiveInt, TypeAdapter, model_validator
from typing_extensions import Self

try:
    import semchunk
    from transformers import AutoTokenizer, PreTrainedTokenizerBase
except ImportError:
    raise RuntimeError(
        "Module requires 'chunking' extra; to install, run: "
        "`pip install 'docling-core[chunking]'`"
    )

from docling_core.transforms.chunker import (
    BaseChunk,
    BaseChunker,
    DocChunk,
    DocMeta,
    HierarchicalChunker,
)
from docling_core.types import DoclingDocument
from docling_core.types.doc.document import TextItem


class HybridChunker(BaseChunker):
    r"""Chunker doing tokenization-aware refinements on top of document layout chunking.

    Args:
        tokenizer: The tokenizer to use; either instantiated object or name or path of
            respective pretrained model
        max_tokens: The maximum number of tokens per chunk. If not set, limit is
            resolved from the tokenizer
        merge_peers: Whether to merge undersized chunks sharing same relevant metadata
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tokenizer: Union[PreTrainedTokenizerBase, str] = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    max_tokens: int = None  # type: ignore[assignment]
    merge_peers: bool = True

    _inner_chunker: HierarchicalChunker = HierarchicalChunker()

    @model_validator(mode="after")
    def _patch_tokenizer_and_max_tokens(self) -> Self:
        self._tokenizer = (
            self.tokenizer
            if isinstance(self.tokenizer, PreTrainedTokenizerBase)
            else AutoTokenizer.from_pretrained(self.tokenizer)
        )
        if self.max_tokens is None:
            self.max_tokens = TypeAdapter(PositiveInt).validate_python(
                self._tokenizer.model_max_length
            )
        return self

    def _count_text_tokens(self, text: Optional[Union[str, list[str]]]):
        if text is None:
            return 0
        elif isinstance(text, list):
            total = 0
            for t in text:
                total += self._count_text_tokens(t)
            return total
        return len(self._tokenizer.tokenize(text, max_length=None))

    class _ChunkLengthInfo(BaseModel):
        total_len: int
        text_len: int
        other_len: int

    def _count_chunk_tokens(self, doc_chunk: DocChunk):
        ser_txt = self.serialize(chunk=doc_chunk)
        return len(self._tokenizer.tokenize(text=ser_txt, max_length=None))

    def _doc_chunk_length(self, doc_chunk: DocChunk):
        text_length = self._count_text_tokens(doc_chunk.text)
        total = self._count_chunk_tokens(doc_chunk=doc_chunk)
        return self._ChunkLengthInfo(
            total_len=total,
            text_len=text_length,
            other_len=total - text_length,
        )

    def _make_chunk_from_doc_items(
        self, doc_chunk: DocChunk, window_start: int, window_end: int
    ):
        doc_items = doc_chunk.meta.doc_items[window_start : window_end + 1]
        meta = DocMeta(
            doc_items=doc_items,
            headings=doc_chunk.meta.headings,
            captions=doc_chunk.meta.captions,
            origin=doc_chunk.meta.origin,
        )
        window_text = (
            doc_chunk.text
            if len(doc_chunk.meta.doc_items) == 1
            else self.delim.join(
                [
                    doc_item.text
                    for doc_item in doc_items
                    if isinstance(doc_item, TextItem)
                ]
            )
        )
        new_chunk = DocChunk(text=window_text, meta=meta)
        return new_chunk

    def _split_by_doc_items(self, doc_chunk: DocChunk) -> list[DocChunk]:
        chunks = []
        window_start = 0
        window_end = 0  # an inclusive index
        num_items = len(doc_chunk.meta.doc_items)
        while window_end < num_items:
            new_chunk = self._make_chunk_from_doc_items(
                doc_chunk=doc_chunk,
                window_start=window_start,
                window_end=window_end,
            )
            if self._count_chunk_tokens(doc_chunk=new_chunk) <= self.max_tokens:
                if window_end < num_items - 1:
                    window_end += 1
                    # Still room left to add more to this chunk AND still at least one
                    # item left
                    continue
                else:
                    # All the items in the window fit into the chunk and there are no
                    # other items left
                    window_end = num_items  # signalizing the last loop
            elif window_start == window_end:
                # Only one item in the window and it doesn't fit into the chunk. So
                # we'll just make it a chunk for now and it will get split in the
                # plain text splitter.
                window_end += 1
                window_start = window_end
            else:
                # Multiple items in the window but they don't fit into the chunk.
                # However, the existing items must have fit or we wouldn't have
                # gotten here. So we put everything but the last item into the chunk
                # and then start a new window INCLUDING the current window end.
                new_chunk = self._make_chunk_from_doc_items(
                    doc_chunk=doc_chunk,
                    window_start=window_start,
                    window_end=window_end - 1,
                )
                window_start = window_end
            chunks.append(new_chunk)
        return chunks

    def _split_using_plain_text(
        self,
        doc_chunk: DocChunk,
    ) -> list[DocChunk]:
        lengths = self._doc_chunk_length(doc_chunk)
        if lengths.total_len <= self.max_tokens:
            return [DocChunk(**doc_chunk.export_json_dict())]
        else:
            # How much room is there for text after subtracting out the headers and
            # captions:
            available_length = self.max_tokens - lengths.other_len
            sem_chunker = semchunk.chunkerify(
                self._tokenizer, chunk_size=available_length
            )
            if available_length <= 0:
                warnings.warn(
                    f"Headers and captions for this chunk are longer than the total amount of size for the chunk, chunk will be ignored: {doc_chunk.text=}"  # noqa
                )
                return []
            text = doc_chunk.text
            segments = sem_chunker.chunk(text)
            chunks = [DocChunk(text=s, meta=doc_chunk.meta) for s in segments]
            return chunks

    def _merge_chunks_with_matching_metadata(self, chunks: list[DocChunk]):
        output_chunks = []
        window_start = 0
        window_end = 0  # an inclusive index
        num_chunks = len(chunks)
        while window_end < num_chunks:
            chunk = chunks[window_end]
            headings_and_captions = (chunk.meta.headings, chunk.meta.captions)
            ready_to_append = False
            if window_start == window_end:
                current_headings_and_captions = headings_and_captions
                window_end += 1
                first_chunk_of_window = chunk
            else:
                chks = chunks[window_start : window_end + 1]
                doc_items = [it for chk in chks for it in chk.meta.doc_items]
                candidate = DocChunk(
                    text=self.delim.join([chk.text for chk in chks]),
                    meta=DocMeta(
                        doc_items=doc_items,
                        headings=current_headings_and_captions[0],
                        captions=current_headings_and_captions[1],
                        origin=chunk.meta.origin,
                    ),
                )
                if (
                    headings_and_captions == current_headings_and_captions
                    and self._count_chunk_tokens(doc_chunk=candidate) <= self.max_tokens
                ):
                    # there is room to include the new chunk so add it to the window and
                    # continue
                    window_end += 1
                    new_chunk = candidate
                else:
                    ready_to_append = True
            if ready_to_append or window_end == num_chunks:
                # no more room OR the start of new metadata.  Either way, end the block
                # and use the current window_end as the start of a new block
                if window_start + 1 == window_end:
                    # just one chunk so use it as is
                    output_chunks.append(first_chunk_of_window)
                else:
                    output_chunks.append(new_chunk)
                # no need to reset window_text, etc. because that will be reset in the
                # next iteration in the if window_start == window_end block
                window_start = window_end

        return output_chunks

    def chunk(self, dl_doc: DoclingDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        r"""Chunk the provided document.

        Args:
            dl_doc (DLDocument): document to chunk

        Yields:
            Iterator[Chunk]: iterator over extracted chunks
        """
        res: Iterable[DocChunk]
        res = self._inner_chunker.chunk(dl_doc=dl_doc, **kwargs)  # type: ignore
        res = [x for c in res for x in self._split_by_doc_items(c)]
        res = [x for c in res for x in self._split_using_plain_text(c)]
        if self.merge_peers:
            res = self._merge_chunks_with_matching_metadata(res)
        return iter(res)

```
</content>
</file_22>

<file_23>
<path>types/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the main types."""

from docling_core.types.doc.document import DoclingDocument
from docling_core.types.gen.generic import Generic
from docling_core.types.rec.record import Record

```
</content>
</file_23>

<file_24>
<path>types/base.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define common models across types."""
from datetime import datetime, timezone
from enum import Enum
from typing import Final, Generic, Hashable, List, Literal, Optional, TypeVar

from pydantic import (
    AfterValidator,
    AnyUrl,
    BaseModel,
    Field,
    PlainSerializer,
    StrictStr,
    StringConstraints,
    ValidationInfo,
    WrapValidator,
    field_validator,
)
from pydantic.types import NonNegativeInt
from typing_extensions import Annotated

from docling_core.search.mapping import es_field
from docling_core.search.package import VERSION_PATTERN
from docling_core.utils.alias import AliasModel
from docling_core.utils.validators import validate_datetime, validate_unique_list

# (subset of) JSON Pointer URI fragment id format, e.g. "#/main-text/84":
_JSON_POINTER_REGEX: Final[str] = r"^#(?:/([\w-]+)(?:/(\d+))?)?$"

LanguageT = TypeVar("LanguageT", bound=str)
IdentifierTypeT = TypeVar("IdentifierTypeT", bound=str)
DescriptionAdvancedT = TypeVar("DescriptionAdvancedT", bound=BaseModel)
DescriptionAnalyticsT = TypeVar("DescriptionAnalyticsT", bound=BaseModel)
SubjectTypeT = TypeVar("SubjectTypeT", bound=str)
SubjectNameTypeT = TypeVar("SubjectNameTypeT", bound=str)
PredicateValueTypeT = TypeVar("PredicateValueTypeT", bound=str)
PredicateKeyNameT = TypeVar("PredicateKeyNameT", bound=str)
PredicateKeyTypeT = TypeVar("PredicateKeyTypeT", bound=str)
ProvenanceTypeT = TypeVar("ProvenanceTypeT", bound=str)
CollectionNameTypeT = TypeVar("CollectionNameTypeT", bound=str)
Coordinates = Annotated[
    list[float],
    Field(min_length=2, max_length=2, json_schema_extra=es_field(type="geo_point")),
]
T = TypeVar("T", bound=Hashable)

UniqueList = Annotated[
    List[T],
    AfterValidator(validate_unique_list),
    Field(json_schema_extra={"uniqueItems": True}),
]

StrictDateTime = Annotated[
    datetime,
    WrapValidator(validate_datetime),
    PlainSerializer(
        lambda x: x.astimezone(tz=timezone.utc).isoformat(), return_type=str
    ),
]

ACQUISITION_TYPE = Literal[
    "API", "FTP", "Download", "Link", "Web scraping/Crawling", "Other"
]


class Identifier(AliasModel, Generic[IdentifierTypeT], extra="forbid"):
    """Unique identifier of a Docling data object."""

    type_: IdentifierTypeT = Field(
        alias="type",
        description=(
            "A string representing a collection or database that contains this "
            "data object."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    value: StrictStr = Field(
        description=(
            "The identifier value of the data object within a collection or database."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    name: str = Field(
        alias="_name",
        title="_Name",
        description=(
            "A unique identifier of the data object across Docling, consisting of "
            "the concatenation of type and value in lower case, separated by hash "
            "(#)."
        ),
        pattern=r"^.+#.+$",
        strict=True,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

    @field_validator("name")
    @classmethod
    def name_from_type_value(cls, v, info: ValidationInfo):
        """Validate the reference field for indexes of type Document."""
        if (
            "type_" in info.data
            and "value" in info.data
            and v != f"{info.data['type_'].lower()}#{info.data['value'].lower()}"
        ):
            raise ValueError(
                "the _name field must be the concatenation of type and value in lower "
                "case, separated by hash (#)"
            )
        return v


class Log(AliasModel, extra="forbid"):
    """Log entry to describe an ETL task on a document."""

    task: Optional[StrictStr] = Field(
        default=None,
        description=(
            "An identifier of this task. It may be used to identify this task from "
            "other tasks of the same agent and type."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    agent: StrictStr = Field(
        description="The Docling agent that performed the task, e.g., CCS or CXS.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    type_: StrictStr = Field(
        alias="type",
        description="A task category.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    comment: Optional[StrictStr] = Field(
        default=None,
        description="A description of the task or any comments in natural language.",
    )
    date: StrictDateTime = Field(
        description=(
            "A string representation of the task execution datetime in ISO 8601 format."
        )
    )


class FileInfoObject(AliasModel):
    """Filing information for any data object to be stored in a Docling database."""

    filename: StrictStr = Field(
        description="The name of a persistent object that created this data object",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    fileprov: Optional[StrictStr] = Field(
        default=None,
        description=(
            "The provenance of this data object, e.g. an archive file, a URL, or any"
            " other repository."
        ),
        alias="filename-prov",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    document_hash: StrictStr = Field(
        description=(
            "A unique identifier of this data object within a collection of a "
            "Docling database"
        ),
        alias="document-hash",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )


class CollectionTypeEnum(str, Enum):
    """Enumeration of valid Docling collection types."""

    generic = "Generic"
    document = "Document"
    record = "Record"


CollectionTypeT = TypeVar("CollectionTypeT", bound=CollectionTypeEnum)


class CollectionInfo(
    BaseModel, Generic[CollectionNameTypeT, CollectionTypeT], extra="forbid"
):
    """Information of a collection."""

    name: Optional[CollectionNameTypeT] = Field(
        default=None,
        description="Name of the collection.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    type: CollectionTypeT = Field(
        ...,
        description="The collection type.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    version: Optional[
        Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)]
    ] = Field(
        default=None,
        description="The version of this collection model.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    alias: Optional[list[StrictStr]] = Field(
        default=None,
        description="A list of tags (aliases) for the collection.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )


class CollectionDocumentInfo(
    CollectionInfo[CollectionNameTypeT, Literal[CollectionTypeEnum.document]],
    Generic[CollectionNameTypeT],
    extra="forbid",
):
    """Information of a collection of type Document."""


class CollectionRecordInfo(
    CollectionInfo[CollectionNameTypeT, Literal[CollectionTypeEnum.record]],
    Generic[CollectionNameTypeT],
    extra="forbid",
):
    """Information of a collection of type Record."""


class Acquisition(BaseModel, extra="forbid"):
    """Information on how the data was obtained."""

    type: ACQUISITION_TYPE = Field(
        description="The method to obtain the data.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    date: Optional[StrictDateTime] = Field(
        default=None,
        description=(
            "A string representation of the acquisition datetime in ISO 8601 format."
        ),
    )
    link: Optional[AnyUrl] = Field(
        default=None,
        description="Link to the data source of this document.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    size: Optional[NonNegativeInt] = Field(
        default=None,
        description="Size in bytes of the raw document from the data source.",
        json_schema_extra=es_field(type="long"),
    )

```
</content>
</file_24>

<file_25>
<path>types/doc/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models defined by the Document type."""

from .base import BoundingBox, CoordOrigin, ImageRefMode, Size
from .document import (
    CodeItem,
    DocItem,
    DoclingDocument,
    DocumentOrigin,
    FloatingItem,
    GroupItem,
    ImageRef,
    KeyValueItem,
    NodeItem,
    PageItem,
    PictureClassificationClass,
    PictureClassificationData,
    PictureDataType,
    PictureItem,
    ProvenanceItem,
    RefItem,
    SectionHeaderItem,
    TableCell,
    TableData,
    TableItem,
    TextItem,
)
from .labels import DocItemLabel, GroupLabel, TableCellLabel

```
</content>
</file_25>

<file_26>
<path>types/doc/base.py</path>
<content>
```python
"""Models for the base data types."""

from enum import Enum
from typing import Tuple

from pydantic import BaseModel


class ImageRefMode(str, Enum):
    """ImageRefMode."""

    PLACEHOLDER = "placeholder"  # just a place-holder
    EMBEDDED = "embedded"  # embed the image as a base64
    REFERENCED = "referenced"  # reference the image via uri


class CoordOrigin(str, Enum):
    """CoordOrigin."""

    TOPLEFT = "TOPLEFT"
    BOTTOMLEFT = "BOTTOMLEFT"


class Size(BaseModel):
    """Size."""

    width: float = 0.0
    height: float = 0.0

    def as_tuple(self):
        """as_tuple."""
        return (self.width, self.height)


class BoundingBox(BaseModel):
    """BoundingBox."""

    l: float  # left
    t: float  # top
    r: float  # right
    b: float  # bottom

    coord_origin: CoordOrigin = CoordOrigin.TOPLEFT

    @property
    def width(self):
        """width."""
        return self.r - self.l

    @property
    def height(self):
        """height."""
        return abs(self.t - self.b)

    def resize_by_scale(self, x_scale: float, y_scale: float):
        """resize_by_scale."""
        return BoundingBox(
            l=self.l * x_scale,
            r=self.r * x_scale,
            t=self.t * y_scale,
            b=self.b * y_scale,
            coord_origin=self.coord_origin,
        )

    def scale_to_size(self, old_size: Size, new_size: Size):
        """scale_to_size."""
        return self.resize_by_scale(
            x_scale=new_size.width / old_size.width,
            y_scale=new_size.height / old_size.height,
        )

    # same as before, but using the implementation above
    def scaled(self, scale: float):
        """scaled."""
        return self.resize_by_scale(x_scale=scale, y_scale=scale)

    # same as before, but using the implementation above
    def normalized(self, page_size: Size):
        """normalized."""
        return self.scale_to_size(
            old_size=page_size, new_size=Size(height=1.0, width=1.0)
        )

    def expand_by_scale(self, x_scale: float, y_scale: float) -> "BoundingBox":
        """expand_to_size."""
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return BoundingBox(
                l=self.l - self.width * x_scale,
                r=self.r + self.width * x_scale,
                t=self.t - self.height * y_scale,
                b=self.b + self.height * y_scale,
                coord_origin=self.coord_origin,
            )
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return BoundingBox(
                l=self.l - self.width * x_scale,
                r=self.r + self.width * x_scale,
                t=self.t + self.height * y_scale,
                b=self.b - self.height * y_scale,
                coord_origin=self.coord_origin,
            )

    def as_tuple(self) -> Tuple[float, float, float, float]:
        """as_tuple."""
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return (self.l, self.t, self.r, self.b)
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return (self.l, self.b, self.r, self.t)

    @classmethod
    def from_tuple(cls, coord: Tuple[float, ...], origin: CoordOrigin):
        """from_tuple.

        :param coord: Tuple[float:
        :param ...]:
        :param origin: CoordOrigin:

        """
        if origin == CoordOrigin.TOPLEFT:
            l, t, r, b = coord[0], coord[1], coord[2], coord[3]
            if r < l:
                l, r = r, l
            if b < t:
                b, t = t, b

            return BoundingBox(l=l, t=t, r=r, b=b, coord_origin=origin)
        elif origin == CoordOrigin.BOTTOMLEFT:
            l, b, r, t = coord[0], coord[1], coord[2], coord[3]
            if r < l:
                l, r = r, l
            if b > t:
                b, t = t, b

            return BoundingBox(l=l, t=t, r=r, b=b, coord_origin=origin)

    def area(self) -> float:
        """area."""
        return abs(self.r - self.l) * abs(self.b - self.t)

    def intersection_area_with(self, other: "BoundingBox") -> float:
        """Calculate the intersection area with another bounding box."""
        if self.coord_origin != other.coord_origin:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        # Calculate intersection coordinates
        left = max(self.l, other.l)
        right = min(self.r, other.r)

        if self.coord_origin == CoordOrigin.TOPLEFT:
            bottom = max(self.t, other.t)
            top = min(self.b, other.b)
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            top = min(self.t, other.t)
            bottom = max(self.b, other.b)

        # Calculate intersection dimensions
        width = right - left
        height = top - bottom

        # If the bounding boxes do not overlap, width or height will be negative
        if width <= 0 or height <= 0:
            return 0.0

        return width * height

    def intersection_over_union(
        self, other: "BoundingBox", eps: float = 1.0e-6
    ) -> float:
        """intersection_over_union."""
        intersection_area = self.intersection_area_with(other=other)

        union_area = (
            abs(self.l - self.r) * abs(self.t - self.b)
            + abs(other.l - other.r) * abs(other.t - other.b)
            - intersection_area
        )

        return intersection_area / (union_area + eps)

    def intersection_over_self(
        self, other: "BoundingBox", eps: float = 1.0e-6
    ) -> float:
        """intersection_over_self."""
        intersection_area = self.intersection_area_with(other=other)
        return intersection_area / self.area()

    def to_bottom_left_origin(self, page_height: float) -> "BoundingBox":
        """to_bottom_left_origin.

        :param page_height:

        """
        if self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return self.model_copy()
        elif self.coord_origin == CoordOrigin.TOPLEFT:
            return BoundingBox(
                l=self.l,
                r=self.r,
                t=page_height - self.t,
                b=page_height - self.b,
                coord_origin=CoordOrigin.BOTTOMLEFT,
            )

    def to_top_left_origin(self, page_height: float) -> "BoundingBox":
        """to_top_left_origin.

        :param page_height:

        """
        if self.coord_origin == CoordOrigin.TOPLEFT:
            return self.model_copy()
        elif self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return BoundingBox(
                l=self.l,
                r=self.r,
                t=page_height - self.t,  # self.b
                b=page_height - self.b,  # self.t
                coord_origin=CoordOrigin.TOPLEFT,
            )

    def overlaps(self, other: "BoundingBox") -> bool:
        """overlaps."""
        return self.overlaps_horizontally(other=other) and self.overlaps_vertically(
            other=other
        )

    def overlaps_horizontally(self, other: "BoundingBox") -> bool:
        """Check if two bounding boxes overlap horizontally."""
        return not (self.r <= other.l or other.r <= self.l)

    def overlaps_vertically(self, other: "BoundingBox") -> bool:
        """Check if two bounding boxes overlap vertically."""
        if self.coord_origin != other.coord_origin:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        # Normalize coordinates if needed
        if self.coord_origin == CoordOrigin.BOTTOMLEFT:
            return not (self.t <= other.b or other.t <= self.b)
        elif self.coord_origin == CoordOrigin.TOPLEFT:
            return not (self.b <= other.t or other.b <= self.t)

    def overlaps_vertically_with_iou(self, other: "BoundingBox", iou: float) -> bool:
        """overlaps_y_with_iou."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):

            if self.overlaps_vertically(other=other):

                u0 = min(self.b, other.b)
                u1 = max(self.t, other.t)

                i0 = max(self.b, other.b)
                i1 = min(self.t, other.t)

                iou_ = float(i1 - i0) / float(u1 - u0)
                return (iou_) > iou

            return False

        elif (
            self.coord_origin == CoordOrigin.TOPLEFT
            and other.coord_origin == CoordOrigin.TOPLEFT
        ):
            if self.overlaps_vertically(other=other):
                u0 = min(self.t, other.t)
                u1 = max(self.b, other.b)

                i0 = max(self.t, other.t)
                i1 = min(self.b, other.b)

                iou_ = float(i1 - i0) / float(u1 - u0)
                return (iou_) > iou

            return False
        else:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        return False

    def is_left_of(self, other: "BoundingBox") -> bool:
        """is_left_of."""
        return self.l < other.l

    def is_strictly_left_of(self, other: "BoundingBox", eps: float = 0.001) -> bool:
        """is_strictly_left_of."""
        return (self.r + eps) < other.l

    def is_above(self, other: "BoundingBox") -> bool:
        """is_above."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            return self.t > other.t

        elif (
            self.coord_origin == CoordOrigin.TOPLEFT
            and other.coord_origin == CoordOrigin.TOPLEFT
        ):
            return self.t < other.t

        else:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        return False

    def is_strictly_above(self, other: "BoundingBox", eps: float = 1.0e-3) -> bool:
        """is_strictly_above."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and other.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            return (self.b + eps) > other.t

        elif (
            self.coord_origin == CoordOrigin.TOPLEFT
            and other.coord_origin == CoordOrigin.TOPLEFT
        ):
            return (self.b + eps) < other.t

        else:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        return False

    def is_horizontally_connected(
        self, elem_i: "BoundingBox", elem_j: "BoundingBox"
    ) -> bool:
        """is_horizontally_connected."""
        if (
            self.coord_origin == CoordOrigin.BOTTOMLEFT
            and elem_i.coord_origin == CoordOrigin.BOTTOMLEFT
            and elem_j.coord_origin == CoordOrigin.BOTTOMLEFT
        ):
            min_ij = min(elem_i.b, elem_j.b)
            max_ij = max(elem_i.t, elem_j.t)

            if self.b < max_ij and min_ij < self.t:  # overlap_y
                return False

            if self.l < elem_i.r and elem_j.l < self.r:
                return True

            return False

        elif (
            self.coord_origin == CoordOrigin.TOPLEFT
            and elem_i.coord_origin == CoordOrigin.TOPLEFT
            and elem_j.coord_origin == CoordOrigin.TOPLEFT
        ):
            min_ij = min(elem_i.t, elem_j.t)
            max_ij = max(elem_i.b, elem_j.b)

            if self.t < max_ij and min_ij < self.b:  # overlap_y
                return False

            if self.l < elem_i.r and elem_j.l < self.r:
                return True

            return False

        else:
            raise ValueError("BoundingBoxes have different CoordOrigin")

        return False

```
</content>
</file_26>

<file_27>
<path>types/doc/document.py</path>
<content>
```python
"""Models for the Docling Document data type."""

import base64
import copy
import hashlib
import html
import json
import logging
import mimetypes
import os
import re
import sys
import textwrap
import typing
import warnings
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Final, List, Literal, Optional, Tuple, Union
from urllib.parse import quote, unquote
from xml.etree.cElementTree import SubElement, tostring
from xml.sax.saxutils import unescape

import latex2mathml.converter
import latex2mathml.exceptions
import pandas as pd
import yaml
from PIL import Image as PILImage
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)
from tabulate import tabulate
from typing_extensions import Annotated, Self

from docling_core.search.package import VERSION_PATTERN
from docling_core.types.base import _JSON_POINTER_REGEX
from docling_core.types.doc import BoundingBox, Size
from docling_core.types.doc.base import ImageRefMode
from docling_core.types.doc.labels import CodeLanguageLabel, DocItemLabel, GroupLabel
from docling_core.types.doc.tokens import DocumentToken, TableToken
from docling_core.types.doc.utils import relative_path

_logger = logging.getLogger(__name__)

Uint64 = typing.Annotated[int, Field(ge=0, le=(2**64 - 1))]
LevelNumber = typing.Annotated[int, Field(ge=1, le=100)]
CURRENT_VERSION: Final = "1.0.0"

DEFAULT_EXPORT_LABELS = {
    DocItemLabel.TITLE,
    DocItemLabel.DOCUMENT_INDEX,
    DocItemLabel.SECTION_HEADER,
    DocItemLabel.PARAGRAPH,
    DocItemLabel.TABLE,
    DocItemLabel.PICTURE,
    DocItemLabel.FORMULA,
    DocItemLabel.CHECKBOX_UNSELECTED,
    DocItemLabel.CHECKBOX_SELECTED,
    DocItemLabel.TEXT,
    DocItemLabel.LIST_ITEM,
    DocItemLabel.CODE,
    DocItemLabel.REFERENCE,
}


class BasePictureData(BaseModel):
    """BasePictureData."""

    kind: str


class PictureClassificationClass(BaseModel):
    """PictureClassificationData."""

    class_name: str
    confidence: float


class PictureClassificationData(BasePictureData):
    """PictureClassificationData."""

    kind: Literal["classification"] = "classification"
    provenance: str
    predicted_classes: List[PictureClassificationClass]


class PictureDescriptionData(BasePictureData):
    """PictureDescriptionData."""

    kind: Literal["description"] = "description"
    text: str
    provenance: str


class PictureMoleculeData(BaseModel):
    """PictureMoleculeData."""

    kind: Literal["molecule_data"] = "molecule_data"

    smi: str
    confidence: float
    class_name: str
    segmentation: List[Tuple[float, float]]
    provenance: str


class PictureMiscData(BaseModel):
    """PictureMiscData."""

    kind: Literal["misc"] = "misc"
    content: Dict[str, Any]


class ChartLine(BaseModel):
    """Represents a line in a line chart.

    Attributes:
        label (str): The label for the line.
        values (List[Tuple[float, float]]): A list of (x, y) coordinate pairs
            representing the line's data points.
    """

    label: str
    values: List[Tuple[float, float]]


class ChartBar(BaseModel):
    """Represents a bar in a bar chart.

    Attributes:
        label (str): The label for the bar.
        values (float): The value associated with the bar.
    """

    label: str
    values: float


class ChartStackedBar(BaseModel):
    """Represents a stacked bar in a stacked bar chart.

    Attributes:
        label (List[str]): The labels for the stacked bars. Multiple values are stored
            in cases where the chart is "double stacked," meaning bars are stacked both
            horizontally and vertically.
        values (List[Tuple[str, int]]): A list of values representing different segments
            of the stacked bar along with their label.
    """

    label: List[str]
    values: List[Tuple[str, int]]


class ChartSlice(BaseModel):
    """Represents a slice in a pie chart.

    Attributes:
        label (str): The label for the slice.
        value (float): The value represented by the slice.
    """

    label: str
    value: float


class ChartPoint(BaseModel):
    """Represents a point in a scatter chart.

    Attributes:
        value (Tuple[float, float]): A (x, y) coordinate pair representing a point in a
            chart.
    """

    value: Tuple[float, float]


class PictureChartData(BaseModel):
    """Base class for picture chart data.

    Attributes:
        title (str): The title of the chart.
    """

    title: str


class PictureLineChartData(PictureChartData):
    """Represents data of a line chart.

    Attributes:
        kind (Literal["line_chart_data"]): The type of the chart.
        x_axis_label (str): The label for the x-axis.
        y_axis_label (str): The label for the y-axis.
        lines (List[ChartLine]): A list of lines in the chart.
    """

    kind: Literal["line_chart_data"] = "line_chart_data"
    x_axis_label: str
    y_axis_label: str
    lines: List[ChartLine]


class PictureBarChartData(PictureChartData):
    """Represents data of a bar chart.

    Attributes:
        kind (Literal["bar_chart_data"]): The type of the chart.
        x_axis_label (str): The label for the x-axis.
        y_axis_label (str): The label for the y-axis.
        bars (List[ChartBar]): A list of bars in the chart.
    """

    kind: Literal["bar_chart_data"] = "bar_chart_data"
    x_axis_label: str
    y_axis_label: str
    bars: List[ChartBar]


class PictureStackedBarChartData(PictureChartData):
    """Represents data of a stacked bar chart.

    Attributes:
        kind (Literal["stacked_bar_chart_data"]): The type of the chart.
        x_axis_label (str): The label for the x-axis.
        y_axis_label (str): The label for the y-axis.
        stacked_bars (List[ChartStackedBar]): A list of stacked bars in the chart.
    """

    kind: Literal["stacked_bar_chart_data"] = "stacked_bar_chart_data"
    x_axis_label: str
    y_axis_label: str
    stacked_bars: List[ChartStackedBar]


class PicturePieChartData(PictureChartData):
    """Represents data of a pie chart.

    Attributes:
        kind (Literal["pie_chart_data"]): The type of the chart.
        slices (List[ChartSlice]): A list of slices in the pie chart.
    """

    kind: Literal["pie_chart_data"] = "pie_chart_data"
    slices: List[ChartSlice]


class PictureScatterChartData(PictureChartData):
    """Represents data of a scatter chart.

    Attributes:
        kind (Literal["scatter_chart_data"]): The type of the chart.
        x_axis_label (str): The label for the x-axis.
        y_axis_label (str): The label for the y-axis.
        points (List[ChartPoint]): A list of points in the scatter chart.
    """

    kind: Literal["scatter_chart_data"] = "scatter_chart_data"
    x_axis_label: str
    y_axis_label: str
    points: List[ChartPoint]


PictureDataType = Annotated[
    Union[
        PictureClassificationData,
        PictureDescriptionData,
        PictureMoleculeData,
        PictureMiscData,
        PictureLineChartData,
        PictureBarChartData,
        PictureStackedBarChartData,
        PicturePieChartData,
        PictureScatterChartData,
    ],
    Field(discriminator="kind"),
]


class TableCell(BaseModel):
    """TableCell."""

    bbox: Optional[BoundingBox] = None
    row_span: int = 1
    col_span: int = 1
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    text: str
    column_header: bool = False
    row_header: bool = False
    row_section: bool = False

    @model_validator(mode="before")
    @classmethod
    def from_dict_format(cls, data: Any) -> Any:
        """from_dict_format."""
        if isinstance(data, Dict):
            # Check if this is a native BoundingBox or a bbox from docling-ibm-models
            if (
                # "bbox" not in data
                # or data["bbox"] is None
                # or isinstance(data["bbox"], BoundingBox)
                "text"
                in data
            ):
                return data
            text = data["bbox"].get("token", "")
            if not len(text):
                text_cells = data.pop("text_cell_bboxes", None)
                if text_cells:
                    for el in text_cells:
                        text += el["token"] + " "

                text = text.strip()
            data["text"] = text

        return data


class TableData(BaseModel):  # TBD
    """BaseTableData."""

    table_cells: List[TableCell] = []
    num_rows: int = 0
    num_cols: int = 0

    @computed_field  # type: ignore
    @property
    def grid(
        self,
    ) -> List[List[TableCell]]:
        """grid."""
        # Initialise empty table data grid (only empty cells)
        table_data = [
            [
                TableCell(
                    text="",
                    start_row_offset_idx=i,
                    end_row_offset_idx=i + 1,
                    start_col_offset_idx=j,
                    end_col_offset_idx=j + 1,
                )
                for j in range(self.num_cols)
            ]
            for i in range(self.num_rows)
        ]

        # Overwrite cells in table data for which there is actual cell content.
        for cell in self.table_cells:
            for i in range(
                min(cell.start_row_offset_idx, self.num_rows),
                min(cell.end_row_offset_idx, self.num_rows),
            ):
                for j in range(
                    min(cell.start_col_offset_idx, self.num_cols),
                    min(cell.end_col_offset_idx, self.num_cols),
                ):
                    table_data[i][j] = cell

        return table_data


class DocumentOrigin(BaseModel):
    """FileSource."""

    mimetype: str  # the mimetype of the original file
    binary_hash: Uint64  # the binary hash of the original file.
    # TODO: Change to be Uint64 and provide utility method to generate

    filename: str  # The name of the original file, including extension, without path.
    # Could stem from filesystem, source URI, Content-Disposition header, ...

    uri: Optional[AnyUrl] = (
        None  # any possible reference to a source file,
        # from any file handler protocol (e.g. https://, file://, s3://)
    )

    _extra_mimetypes: typing.ClassVar[List[str]] = [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
        "application/vnd.openxmlformats-officedocument.presentationml.template",
        "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/asciidoc",
        "text/markdown",
    ]

    @field_validator("binary_hash", mode="before")
    @classmethod
    def parse_hex_string(cls, value):
        """parse_hex_string."""
        if isinstance(value, str):
            try:
                # Convert hex string to an integer
                hash_int = Uint64(value, 16)
                # Mask to fit within 64 bits (unsigned)
                return (
                    hash_int & 0xFFFFFFFFFFFFFFFF
                )  # TODO be sure it doesn't clip uint64 max
            except ValueError:
                raise ValueError(f"Invalid sha256 hexdigest: {value}")
        return value  # If already an int, return it as is.

    @field_validator("mimetype")
    @classmethod
    def validate_mimetype(cls, v):
        """validate_mimetype."""
        # Check if the provided MIME type is valid using mimetypes module
        if v not in mimetypes.types_map.values() and v not in cls._extra_mimetypes:
            raise ValueError(f"'{v}' is not a valid MIME type")
        return v


class RefItem(BaseModel):
    """RefItem."""

    cref: str = Field(alias="$ref", pattern=_JSON_POINTER_REGEX)

    # This method makes RefItem compatible with DocItem
    def get_ref(self):
        """get_ref."""
        return self

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def resolve(self, doc: "DoclingDocument"):
        """resolve."""
        path_components = self.cref.split("/")
        if (num_comps := len(path_components)) == 3:
            _, path, index_str = path_components
            index = int(index_str)
            obj = doc.__getattribute__(path)[index]
        elif num_comps == 2:
            _, path = path_components
            obj = doc.__getattribute__(path)
        else:
            raise RuntimeError(f"Unsupported number of path components: {num_comps}")
        return obj


class ImageRef(BaseModel):
    """ImageRef."""

    mimetype: str
    dpi: int
    size: Size
    uri: Union[AnyUrl, Path] = Field(union_mode="left_to_right")
    _pil: Optional[PILImage.Image] = None

    @property
    def pil_image(self) -> Optional[PILImage.Image]:
        """Return the PIL Image."""
        if self._pil is not None:
            return self._pil

        if isinstance(self.uri, AnyUrl):
            if self.uri.scheme == "data":
                encoded_img = str(self.uri).split(",")[1]
                decoded_img = base64.b64decode(encoded_img)
                self._pil = PILImage.open(BytesIO(decoded_img))
            elif self.uri.scheme == "file":
                self._pil = PILImage.open(unquote(str(self.uri.path)))
            # else: Handle http request or other protocols...
        elif isinstance(self.uri, Path):
            self._pil = PILImage.open(self.uri)

        return self._pil

    @field_validator("mimetype")
    @classmethod
    def validate_mimetype(cls, v):
        """validate_mimetype."""
        # Check if the provided MIME type is valid using mimetypes module
        if v not in mimetypes.types_map.values():
            raise ValueError(f"'{v}' is not a valid MIME type")
        return v

    @classmethod
    def from_pil(cls, image: PILImage.Image, dpi: int) -> Self:
        """Construct ImageRef from a PIL Image."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        img_uri = f"data:image/png;base64,{img_str}"
        return cls(
            mimetype="image/png",
            dpi=dpi,
            size=Size(width=image.width, height=image.height),
            uri=img_uri,
            _pil=image,
        )


class ProvenanceItem(BaseModel):
    """ProvenanceItem."""

    page_no: int
    bbox: BoundingBox
    charspan: Tuple[int, int]


class NodeItem(BaseModel):
    """NodeItem."""

    self_ref: str = Field(pattern=_JSON_POINTER_REGEX)
    parent: Optional[RefItem] = None
    children: List[RefItem] = []

    model_config = ConfigDict(extra="forbid")

    def get_ref(self):
        """get_ref."""
        return RefItem(cref=self.self_ref)


class GroupItem(NodeItem):  # Container type, can't be a leaf node
    """GroupItem."""

    name: str = (
        "group"  # Name of the group, e.g. "Introduction Chapter",
        # "Slide 5", "Navigation menu list", ...
    )
    label: GroupLabel = GroupLabel.UNSPECIFIED


class DocItem(
    NodeItem
):  # Base type for any element that carries content, can be a leaf node
    """DocItem."""

    label: DocItemLabel
    prov: List[ProvenanceItem] = []

    def get_location_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str,
        xsize: int = 100,
        ysize: int = 100,
        add_page_index: bool = True,
    ) -> str:
        """Get the location string for the BaseCell."""
        if not len(self.prov):
            return ""

        location = ""
        for prov in self.prov:
            page_w, page_h = doc.pages[prov.page_no].size.as_tuple()

            page_i = -1
            if add_page_index:
                page_i = prov.page_no

            loc_str = DocumentToken.get_location(
                bbox=prov.bbox.to_bottom_left_origin(page_h).as_tuple(),
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                page_i=page_i,
            )
            location += f"{loc_str}{new_line}"

        return location

    def get_image(self, doc: "DoclingDocument") -> Optional[PILImage.Image]:
        """Returns the image of this DocItem.

        The function returns None if this DocItem has no valid provenance or
        if a valid image of the page containing this DocItem is not available
        in doc.
        """
        if not len(self.prov):
            return None

        page = doc.pages.get(self.prov[0].page_no)
        if page is None or page.size is None or page.image is None:
            return None

        page_image = page.image.pil_image
        if not page_image:
            return None
        crop_bbox = (
            self.prov[0]
            .bbox.to_top_left_origin(page_height=page.size.height)
            .scale_to_size(old_size=page.size, new_size=page.image.size)
            # .scaled(scale=page_image.height / page.size.height)
        )
        return page_image.crop(crop_bbox.as_tuple())


class TextItem(DocItem):
    """TextItem."""

    label: typing.Literal[
        DocItemLabel.CAPTION,
        DocItemLabel.CHECKBOX_SELECTED,
        DocItemLabel.CHECKBOX_UNSELECTED,
        DocItemLabel.FOOTNOTE,
        DocItemLabel.FORMULA,
        DocItemLabel.PAGE_FOOTER,
        DocItemLabel.PAGE_HEADER,
        DocItemLabel.PARAGRAPH,
        DocItemLabel.REFERENCE,
        DocItemLabel.TEXT,
        DocItemLabel.TITLE,
    ]

    orig: str  # untreated representation
    text: str  # sanitized representation

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
    ):
        r"""Export text element to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)

        """
        body = f"<{self.label.value}>"

        # TODO: This must be done through an explicit mapping.
        # assert DocumentToken.is_known_token(
        #    body
        # ), f"failed DocumentToken.is_known_token({body})"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line="",
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_content and self.text is not None:
            body += self.text.strip()

        body += f"</{self.label.value}>{new_line}"

        return body


class CodeItem(TextItem):
    """CodeItem."""

    label: typing.Literal[DocItemLabel.CODE] = (
        DocItemLabel.CODE  # type: ignore[assignment]
    )
    code_language: CodeLanguageLabel = CodeLanguageLabel.UNKNOWN


class SectionHeaderItem(TextItem):
    """SectionItem."""

    label: typing.Literal[DocItemLabel.SECTION_HEADER] = (
        DocItemLabel.SECTION_HEADER  # type: ignore[assignment]
    )
    level: LevelNumber = 1

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
    ):
        r"""Export text element to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)

        """
        body = f"<{self.label.value}_level_{self.level}>"

        # TODO: This must be done through an explicit mapping.
        # assert DocumentToken.is_known_token(
        #    body
        # ), f"failed DocumentToken.is_known_token({body})"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line="",
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_content and self.text is not None:
            body += self.text.strip()

        body += f"</{self.label.value}_level_{self.level}>{new_line}"

        return body


class ListItem(TextItem):
    """SectionItem."""

    label: typing.Literal[DocItemLabel.LIST_ITEM] = (
        DocItemLabel.LIST_ITEM  # type: ignore[assignment]
    )
    enumerated: bool = False
    marker: str = "-"  # The bullet or number symbol that prefixes this list item


class FloatingItem(DocItem):
    """FloatingItem."""

    captions: List[RefItem] = []
    references: List[RefItem] = []
    footnotes: List[RefItem] = []
    image: Optional[ImageRef] = None

    def caption_text(self, doc: "DoclingDocument") -> str:
        """Computes the caption as a single text."""
        text = ""
        for cap in self.captions:
            text += cap.resolve(doc).text
        return text

    def get_image(self, doc: "DoclingDocument") -> Optional[PILImage.Image]:
        """Returns the image corresponding to this FloatingItem.

        This function returns the PIL image from self.image if one is available.
        Otherwise, it uses DocItem.get_image to get an image of this FloatingItem.

        In particular, when self.image is None, the function returns None if this
        FloatingItem has no valid provenance or the doc does not contain a valid image
        for the required page.
        """
        if self.image is not None:
            return self.image.pil_image
        return super().get_image(doc=doc)


class PictureItem(FloatingItem):
    """PictureItem."""

    label: typing.Literal[DocItemLabel.PICTURE] = DocItemLabel.PICTURE

    annotations: List[PictureDataType] = []

    # Convert the image to Base64
    def _image_to_base64(self, pil_image, format="PNG"):
        """Base64 representation of the image."""
        buffered = BytesIO()
        pil_image.save(buffered, format=format)  # Save the image to the byte stream
        img_bytes = buffered.getvalue()  # Get the byte data
        img_base64 = base64.b64encode(img_bytes).decode(
            "utf-8"
        )  # Encode to Base64 and decode to string
        return img_base64

    def _image_to_hexhash(self) -> Optional[str]:
        """Hexash from the image."""
        if self.image is not None and self.image._pil is not None:
            # Convert the image to raw bytes
            image_bytes = self.image._pil.tobytes()

            # Create a hash object (e.g., SHA-256)
            hasher = hashlib.sha256()

            # Feed the image bytes into the hash object
            hasher.update(image_bytes)

            # Get the hexadecimal representation of the hash
            return hasher.hexdigest()

        return None

    def export_to_markdown(
        self,
        doc: "DoclingDocument",
        add_caption: bool = True,
        image_mode: ImageRefMode = ImageRefMode.EMBEDDED,
        image_placeholder: str = "<!-- image -->",
    ) -> str:
        """Export picture to Markdown format."""
        default_response = "\n" + image_placeholder + "\n"
        error_response = (
            "\n<!-- 🖼️❌ Image not available. "
            "Please use `PdfPipelineOptions(generate_picture_images=True)`"
            " --> \n"
        )

        if image_mode == ImageRefMode.PLACEHOLDER:
            return default_response

        elif image_mode == ImageRefMode.EMBEDDED:

            # short-cut: we already have the image in base64
            if (
                isinstance(self.image, ImageRef)
                and isinstance(self.image.uri, AnyUrl)
                and self.image.uri.scheme == "data"
            ):
                text = f"\n![Image]({self.image.uri})\n"
                return text

            # get the self.image._pil or crop it out of the page-image
            img = self.get_image(doc)

            if img is not None:
                imgb64 = self._image_to_base64(img)
                text = f"\n![Image](data:image/png;base64,{imgb64})\n"

                return text
            else:
                return error_response

        elif image_mode == ImageRefMode.REFERENCED:
            if not isinstance(self.image, ImageRef) or (
                isinstance(self.image.uri, AnyUrl) and self.image.uri.scheme == "data"
            ):
                return default_response

            text = f"\n![Image]({quote(str(self.image.uri))})\n"
            return text

        else:
            return default_response

    def export_to_html(
        self,
        doc: "DoclingDocument",
        add_caption: bool = True,
        image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER,
    ) -> str:
        """Export picture to HTML format."""
        text = ""
        if add_caption and len(self.captions):
            text = self.caption_text(doc)

        caption_text = ""
        if len(text) > 0:
            caption_text = f"<figcaption>{text}</figcaption>"

        default_response = f"<figure>{caption_text}</figure>"

        if image_mode == ImageRefMode.PLACEHOLDER:
            return default_response

        elif image_mode == ImageRefMode.EMBEDDED:
            # short-cut: we already have the image in base64
            if (
                isinstance(self.image, ImageRef)
                and isinstance(self.image.uri, AnyUrl)
                and self.image.uri.scheme == "data"
            ):
                img_text = f'<img src="{self.image.uri}">'
                return f"<figure>{caption_text}{img_text}</figure>"

            # get the self.image._pil or crop it out of the page-image
            img = self.get_image(doc)

            if img is not None:
                imgb64 = self._image_to_base64(img)
                img_text = f'<img src="data:image/png;base64,{imgb64}">'

                return f"<figure>{caption_text}{img_text}</figure>"
            else:
                return default_response

        elif image_mode == ImageRefMode.REFERENCED:

            if not isinstance(self.image, ImageRef) or (
                isinstance(self.image.uri, AnyUrl) and self.image.uri.scheme == "data"
            ):
                return default_response

            img_text = f'<img src="{quote(str(self.image.uri))}">'
            return f"<figure>{caption_text}{img_text}</figure>"

        else:
            return default_response

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,  # not used at the moment
        add_page_index: bool = True,
    ):
        r"""Export picture to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_caption: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param # not used at the momentadd_page_index: bool:  (Default value = True)

        """
        body = f"{DocumentToken.BEG_FIGURE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line=new_line,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and len(self.captions):
            text = self.caption_text(doc)

            if len(text):
                body += f"{DocumentToken.BEG_CAPTION.value}"
                body += f"{text.strip()}"
                body += f"{DocumentToken.END_CAPTION.value}"
                body += f"{new_line}"

        body += f"{DocumentToken.END_FIGURE.value}{new_line}"

        return body


class TableItem(FloatingItem):
    """TableItem."""

    data: TableData
    label: typing.Literal[
        DocItemLabel.DOCUMENT_INDEX,
        DocItemLabel.TABLE,
    ] = DocItemLabel.TABLE

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export the table as a Pandas DataFrame."""
        if self.data.num_rows == 0 or self.data.num_cols == 0:
            return pd.DataFrame()

        # Count how many rows are column headers
        num_headers = 0
        for i, row in enumerate(self.data.grid):
            if len(row) == 0:
                raise RuntimeError(
                    f"Invalid table. {len(row)=} but {self.data.num_cols=}."
                )

            any_header = False
            for cell in row:
                if cell.column_header:
                    any_header = True
                    break

            if any_header:
                num_headers += 1
            else:
                break

        # Create the column names from all col_headers
        columns: Optional[List[str]] = None
        if num_headers > 0:
            columns = ["" for _ in range(self.data.num_cols)]
            for i in range(num_headers):
                for j, cell in enumerate(self.data.grid[i]):
                    col_name = cell.text
                    if columns[j] != "":
                        col_name = f".{col_name}"
                    columns[j] += col_name

        # Create table data
        table_data = [
            [cell.text for cell in row] for row in self.data.grid[num_headers:]
        ]

        # Create DataFrame
        df = pd.DataFrame(table_data, columns=columns)

        return df

    def export_to_markdown(self) -> str:
        """Export the table as markdown."""
        table = []
        for row in self.data.grid:
            tmp = []
            for col in row:

                # make sure that md tables are not broken
                # due to newline chars in the text
                text = col.text
                text = text.replace("\n", " ")
                tmp.append(text)

            table.append(tmp)

        md_table = ""
        if len(table) > 1 and len(table[0]) > 0:
            try:
                md_table = tabulate(table[1:], headers=table[0], tablefmt="github")
            except ValueError:
                md_table = tabulate(
                    table[1:],
                    headers=table[0],
                    tablefmt="github",
                    disable_numparse=True,
                )
        return md_table

    def export_to_html(
        self, doc: Optional["DoclingDocument"] = None, add_caption: bool = True
    ) -> str:
        """Export the table as html."""
        if doc is None:
            warnings.warn(
                "The `doc` argument will be mandatory in a future version. "
                "It must be provided to include a caption.",
                DeprecationWarning,
            )

        nrows = self.data.num_rows
        ncols = self.data.num_cols

        text = ""
        if doc is not None and add_caption and len(self.captions):
            text = html.escape(self.caption_text(doc))

        if len(self.data.table_cells) == 0:
            return ""

        body = ""

        for i in range(nrows):
            body += "<tr>"
            for j in range(ncols):
                cell: TableCell = self.data.grid[i][j]

                rowspan, rowstart = (
                    cell.row_span,
                    cell.start_row_offset_idx,
                )
                colspan, colstart = (
                    cell.col_span,
                    cell.start_col_offset_idx,
                )

                if rowstart != i:
                    continue
                if colstart != j:
                    continue

                content = html.escape(cell.text.strip())
                celltag = "td"
                if cell.column_header:
                    celltag = "th"

                opening_tag = f"{celltag}"
                if rowspan > 1:
                    opening_tag += f' rowspan="{rowspan}"'
                if colspan > 1:
                    opening_tag += f' colspan="{colspan}"'

                body += f"<{opening_tag}>{content}</{celltag}>"
            body += "</tr>"

        if len(text) > 0 and len(body) > 0:
            body = f"<table><caption>{text}</caption><tbody>{body}</tbody></table>"
        elif len(text) == 0 and len(body) > 0:
            body = f"<table><tbody>{body}</tbody></table>"
        elif len(text) > 0 and len(body) == 0:
            body = f"<table><caption>{text}</caption></table>"
        else:
            body = "<table></table>"

        return body

    def export_to_otsl(
        self,
        doc: "DoclingDocument",
        add_cell_location: bool = True,
        add_cell_text: bool = True,
        xsize: int = 100,
        ysize: int = 100,
    ) -> str:
        """Export the table as OTSL."""
        # Possible OTSL tokens...
        #
        # Empty and full cells:
        # "ecel", "fcel"
        #
        # Cell spans (horisontal, vertical, 2d):
        # "lcel", "ucel", "xcel"
        #
        # New line:
        # "nl"
        #
        # Headers (column, row, section row):
        # "ched", "rhed", "srow"

        body = []
        nrows = self.data.num_rows
        ncols = self.data.num_cols
        if len(self.data.table_cells) == 0:
            return ""

        page_no = 0
        if len(self.prov) > 0:
            page_no = self.prov[0].page_no

        for i in range(nrows):
            for j in range(ncols):
                cell: TableCell = self.data.grid[i][j]
                content = cell.text.strip()
                rowspan, rowstart = (
                    cell.row_span,
                    cell.start_row_offset_idx,
                )
                colspan, colstart = (
                    cell.col_span,
                    cell.start_col_offset_idx,
                )

                if len(doc.pages.keys()):
                    page_w, page_h = doc.pages[page_no].size.as_tuple()
                cell_loc = ""
                if cell.bbox is not None:
                    cell_loc = DocumentToken.get_location(
                        bbox=cell.bbox.to_bottom_left_origin(page_h).as_tuple(),
                        page_w=page_w,
                        page_h=page_h,
                        xsize=xsize,
                        ysize=ysize,
                        page_i=page_no,
                    )

                if rowstart == i and colstart == j:
                    if len(content) > 0:
                        if cell.column_header:
                            body.append(str(TableToken.OTSL_CHED.value))
                        elif cell.row_header:
                            body.append(str(TableToken.OTSL_RHED.value))
                        elif cell.row_section:
                            body.append(str(TableToken.OTSL_SROW.value))
                        else:
                            body.append(str(TableToken.OTSL_FCEL.value))
                        if add_cell_location:
                            body.append(str(cell_loc))
                        if add_cell_text:
                            body.append(str(content))
                    else:
                        body.append(str(TableToken.OTSL_ECEL.value))
                else:
                    add_cross_cell = False
                    if rowstart != i:
                        if colspan == 1:
                            body.append(str(TableToken.OTSL_UCEL.value))
                        else:
                            add_cross_cell = True
                    if colstart != j:
                        if rowspan == 1:
                            body.append(str(TableToken.OTSL_LCEL.value))
                        else:
                            add_cross_cell = True
                    if add_cross_cell:
                        body.append(str(TableToken.OTSL_XCEL.value))
            body.append(str(TableToken.OTSL_NL.value))
            body_str = "".join(body)
        return body_str

    def export_to_document_tokens(
        self,
        doc: "DoclingDocument",
        new_line: str = "\n",
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,
        add_cell_location: bool = True,
        add_cell_label: bool = True,
        add_cell_text: bool = True,
        add_page_index: bool = True,
    ):
        r"""Export table to document tokens format.

        :param doc: "DoclingDocument":
        :param new_line: str:  (Default value = "\n")
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_caption: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_cell_location: bool:  (Default value = True)
        :param add_cell_label: bool:  (Default value = True)
        :param add_cell_text: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)

        """
        body = f"{DocumentToken.BEG_TABLE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                doc=doc,
                new_line=new_line,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and len(self.captions):
            text = self.caption_text(doc)

            if len(text):
                body += f"{DocumentToken.BEG_CAPTION.value}"
                body += f"{text.strip()}"
                body += f"{DocumentToken.END_CAPTION.value}"
                body += f"{new_line}"

        if add_content and len(self.data.table_cells) > 0:
            for i, row in enumerate(self.data.grid):
                body += f"<row_{i}>"
                for j, col in enumerate(row):

                    text = ""
                    if add_cell_text:
                        text = col.text.strip()

                    cell_loc = ""
                    if (
                        col.bbox is not None
                        and add_cell_location
                        and add_page_index
                        and len(self.prov) > 0
                    ):
                        page_w, page_h = doc.pages[self.prov[0].page_no].size.as_tuple()
                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox.to_bottom_left_origin(page_h).as_tuple(),
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=self.prov[0].page_no,
                        )
                    elif (
                        col.bbox is not None
                        and add_cell_location
                        and not add_page_index
                        and len(self.prov) > 0
                    ):
                        page_w, page_h = doc.pages[self.prov[0].page_no].size.as_tuple()

                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox.to_bottom_left_origin(page_h).as_tuple(),
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=-1,
                        )

                    cell_label = ""
                    if add_cell_label:
                        if col.column_header:
                            cell_label = "<col_header>"
                        elif col.row_header:
                            cell_label = "<row_header>"
                        elif col.row_section:
                            cell_label = "<row_section>"
                        else:
                            cell_label = "<body>"

                    body += f"<col_{j}>{cell_loc}{cell_label}{text}</col_{j}>"

                body += f"</row_{i}>{new_line}"

        body += f"{DocumentToken.END_TABLE.value}{new_line}"

        return body


class KeyValueItem(DocItem):
    """KeyValueItem."""

    label: typing.Literal[DocItemLabel.KEY_VALUE_REGION] = DocItemLabel.KEY_VALUE_REGION


ContentItem = Annotated[
    Union[
        TextItem,
        SectionHeaderItem,
        ListItem,
        CodeItem,
        PictureItem,
        TableItem,
        KeyValueItem,
    ],
    Field(discriminator="label"),
]


class PageItem(BaseModel):
    """PageItem."""

    # A page carries separate root items for furniture and body,
    # only referencing items on the page
    size: Size
    image: Optional[ImageRef] = None
    page_no: int


class DoclingDocument(BaseModel):
    """DoclingDocument."""

    _HTML_DEFAULT_HEAD: str = r"""<head>
    <link rel="icon" type="image/png"
    href="https://ds4sd.github.io/docling/assets/logo.png"/>
    <meta charset="UTF-8">
    <title>
    Powered by Docling
    </title>
    <style>
    html {
    background-color: LightGray;
    }
    body {
    margin: 0 auto;
    width:800px;
    padding: 30px;
    background-color: White;
    font-family: Arial, sans-serif;
    box-shadow: 10px 10px 10px grey;
    }
    figure{
    display: block;
    width: 100%;
    margin: 0px;
    margin-top: 10px;
    margin-bottom: 10px;
    }
    img {
    display: block;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    max-width: 640px;
    max-height: 640px;
    }
    table {
    min-width:500px;
    background-color: White;
    border-collapse: collapse;
    cell-padding: 5px;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    }
    th, td {
    border: 1px solid black;
    padding: 8px;
    }
    th {
    font-weight: bold;
    }
    table tr:nth-child(even) td{
    background-color: LightGray;
    }
    math annotation {
    display: none;
    }
    .formula-not-decoded {
    background: repeating-linear-gradient(
    45deg, /* Angle of the stripes */
    LightGray, /* First color */
    LightGray 10px, /* Length of the first color */
    White 10px, /* Second color */
    White 20px /* Length of the second color */
    );
    margin: 0;
    text-align: center;
    }
    </style>
    </head>"""

    schema_name: typing.Literal["DoclingDocument"] = "DoclingDocument"
    version: Annotated[str, StringConstraints(pattern=VERSION_PATTERN, strict=True)] = (
        CURRENT_VERSION
    )
    name: str  # The working name of this document, without extensions
    # (could be taken from originating doc, or just "Untitled 1")
    origin: Optional[DocumentOrigin] = (
        None  # DoclingDocuments may specify an origin (converted to DoclingDocument).
        # This is optional, e.g. a DoclingDocument could also be entirely
        # generated from synthetic data.
    )

    furniture: GroupItem = GroupItem(
        name="_root_", self_ref="#/furniture"
    )  # List[RefItem] = []
    body: GroupItem = GroupItem(name="_root_", self_ref="#/body")  # List[RefItem] = []

    groups: List[GroupItem] = []
    texts: List[Union[SectionHeaderItem, ListItem, TextItem, CodeItem]] = []
    pictures: List[PictureItem] = []
    tables: List[TableItem] = []
    key_value_items: List[KeyValueItem] = []

    pages: Dict[int, PageItem] = {}  # empty as default

    def add_group(
        self,
        label: Optional[GroupLabel] = None,
        name: Optional[str] = None,
        parent: Optional[NodeItem] = None,
    ) -> GroupItem:
        """add_group.

        :param label: Optional[GroupLabel]:  (Default value = None)
        :param name: Optional[str]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        group_index = len(self.groups)
        cref = f"#/groups/{group_index}"

        group = GroupItem(self_ref=cref, parent=parent.get_ref())
        if name is not None:
            group.name = name
        if label is not None:
            group.label = label

        self.groups.append(group)
        parent.children.append(RefItem(cref=cref))

        return group

    def add_list_item(
        self,
        text: str,
        enumerated: bool = False,
        marker: Optional[str] = None,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_list_item.

        :param label: str:
        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)

        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        marker = marker or "-"

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        list_item = ListItem(
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
            enumerated=enumerated,
            marker=marker,
        )
        if prov:
            list_item.prov.append(prov)

        self.texts.append(list_item)
        parent.children.append(RefItem(cref=cref))

        return list_item

    def add_text(
        self,
        label: DocItemLabel,
        text: str,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_text.

        :param label: str:
        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)

        """
        # Catch a few cases that are in principle allowed
        # but that will create confusion down the road
        if label in [DocItemLabel.TITLE]:
            return self.add_title(text=text, orig=orig, prov=prov, parent=parent)

        elif label in [DocItemLabel.LIST_ITEM]:
            return self.add_list_item(text=text, orig=orig, prov=prov, parent=parent)

        elif label in [DocItemLabel.SECTION_HEADER]:
            return self.add_heading(text=text, orig=orig, prov=prov, parent=parent)

        elif label in [DocItemLabel.CODE]:
            return self.add_code(text=text, orig=orig, prov=prov, parent=parent)

        else:

            if not parent:
                parent = self.body

            if not orig:
                orig = text

            text_index = len(self.texts)
            cref = f"#/texts/{text_index}"
            text_item = TextItem(
                label=label,
                text=text,
                orig=orig,
                self_ref=cref,
                parent=parent.get_ref(),
            )
            if prov:
                text_item.prov.append(prov)

            self.texts.append(text_item)
            parent.children.append(RefItem(cref=cref))

            return text_item

    def add_table(
        self,
        data: TableData,
        caption: Optional[Union[TextItem, RefItem]] = None,  # This is not cool yet.
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
        label: DocItemLabel = DocItemLabel.TABLE,
    ):
        """add_table.

        :param data: TableData:
        :param caption: Optional[Union[TextItem, RefItem]]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)
        :param label: DocItemLabel:  (Default value = DocItemLabel.TABLE)

        """
        if not parent:
            parent = self.body

        table_index = len(self.tables)
        cref = f"#/tables/{table_index}"

        tbl_item = TableItem(
            label=label, data=data, self_ref=cref, parent=parent.get_ref()
        )
        if prov:
            tbl_item.prov.append(prov)
        if caption:
            tbl_item.captions.append(caption.get_ref())

        self.tables.append(tbl_item)
        parent.children.append(RefItem(cref=cref))

        return tbl_item

    def add_picture(
        self,
        annotations: List[PictureDataType] = [],
        image: Optional[ImageRef] = None,
        caption: Optional[Union[TextItem, RefItem]] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_picture.

        :param data: List[PictureData]: (Default value = [])
        :param caption: Optional[Union[TextItem:
        :param RefItem]]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)
        """
        if not parent:
            parent = self.body

        picture_index = len(self.pictures)
        cref = f"#/pictures/{picture_index}"

        fig_item = PictureItem(
            label=DocItemLabel.PICTURE,
            annotations=annotations,
            image=image,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            fig_item.prov.append(prov)
        if caption:
            fig_item.captions.append(caption.get_ref())

        self.pictures.append(fig_item)
        parent.children.append(RefItem(cref=cref))

        return fig_item

    def add_title(
        self,
        text: str,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_title.

        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)
        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        text_item = TextItem(
            label=DocItemLabel.TITLE,
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            text_item.prov.append(prov)

        self.texts.append(text_item)
        parent.children.append(RefItem(cref=cref))

        return text_item

    def add_code(
        self,
        text: str,
        code_language: Optional[CodeLanguageLabel] = None,
        orig: Optional[str] = None,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_code.

        :param text: str:
        :param code_language: Optional[str]: (Default value = None)
        :param orig: Optional[str]:  (Default value = None)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)
        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        code_item = CodeItem(
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if code_language:
            code_item.code_language = code_language
        if prov:
            code_item.prov.append(prov)

        self.texts.append(code_item)
        parent.children.append(RefItem(cref=cref))

        return code_item

    def add_heading(
        self,
        text: str,
        orig: Optional[str] = None,
        level: LevelNumber = 1,
        prov: Optional[ProvenanceItem] = None,
        parent: Optional[NodeItem] = None,
    ):
        """add_heading.

        :param label: DocItemLabel:
        :param text: str:
        :param orig: Optional[str]:  (Default value = None)
        :param level: LevelNumber:  (Default value = 1)
        :param prov: Optional[ProvenanceItem]:  (Default value = None)
        :param parent: Optional[NodeItem]:  (Default value = None)
        """
        if not parent:
            parent = self.body

        if not orig:
            orig = text

        text_index = len(self.texts)
        cref = f"#/texts/{text_index}"
        section_header_item = SectionHeaderItem(
            level=level,
            text=text,
            orig=orig,
            self_ref=cref,
            parent=parent.get_ref(),
        )
        if prov:
            section_header_item.prov.append(prov)

        self.texts.append(section_header_item)
        parent.children.append(RefItem(cref=cref))

        return section_header_item

    def num_pages(self):
        """num_pages."""
        return len(self.pages.values())

    def validate_tree(self, root) -> bool:
        """validate_tree."""
        res = []
        for child_ref in root.children:
            child = child_ref.resolve(self)
            if child.parent.resolve(self) != root:
                return False
            res.append(self.validate_tree(child))

        return all(res) or len(res) == 0

    def iterate_items(
        self,
        root: Optional[NodeItem] = None,
        with_groups: bool = False,
        traverse_pictures: bool = False,
        page_no: Optional[int] = None,
        _level: int = 0,  # fixed parameter, carries through the node nesting level
    ) -> typing.Iterable[Tuple[NodeItem, int]]:  # tuple of node and level
        """iterate_elements.

        :param root: Optional[NodeItem]:  (Default value = None)
        :param with_groups: bool:  (Default value = False)
        :param traverse_pictures: bool:  (Default value = False)
        :param page_no: Optional[int]:  (Default value = None)
        :param _level:  (Default value = 0)
        :param # fixed parameter:
        :param carries through the node nesting level:
        """
        if not root:
            root = self.body

        # Yield non-group items or group items when with_groups=True
        if not isinstance(root, GroupItem) or with_groups:
            if isinstance(root, DocItem):
                if page_no is None or any(
                    prov.page_no == page_no for prov in root.prov
                ):
                    yield root, _level
            else:
                yield root, _level

        # Handle picture traversal - only traverse children if requested
        if isinstance(root, PictureItem) and not traverse_pictures:
            return

        # Traverse children
        for child_ref in root.children:
            child = child_ref.resolve(self)
            if isinstance(child, NodeItem):
                yield from self.iterate_items(
                    child,
                    with_groups=with_groups,
                    traverse_pictures=traverse_pictures,
                    page_no=page_no,
                    _level=_level + 1,
                )

    def _clear_picture_pil_cache(self):
        """Clear cache storage of all images."""
        for item, level in self.iterate_items(with_groups=False):
            if isinstance(item, PictureItem):
                if item.image is not None and item.image._pil is not None:
                    item.image._pil.close()

    def _list_images_on_disk(self) -> List[Path]:
        """List all images on disk."""
        result: List[Path] = []

        for item, level in self.iterate_items(with_groups=False):
            if isinstance(item, PictureItem):
                if item.image is not None:
                    if (
                        isinstance(item.image.uri, AnyUrl)
                        and item.image.uri.scheme == "file"
                        and item.image.uri.path is not None
                    ):
                        local_path = Path(unquote(item.image.uri.path))
                        result.append(local_path)
                    elif isinstance(item.image.uri, Path):
                        result.append(item.image.uri)

        return result

    def _with_embedded_pictures(self) -> "DoclingDocument":
        """Document with embedded images.

        Creates a copy of this document where all pictures referenced
        through a file URI are turned into base64 embedded form.
        """
        result: DoclingDocument = copy.deepcopy(self)

        for ix, (item, level) in enumerate(result.iterate_items(with_groups=True)):
            if isinstance(item, PictureItem):

                if item.image is not None:
                    if (
                        isinstance(item.image.uri, AnyUrl)
                        and item.image.uri.scheme == "file"
                    ):
                        assert isinstance(item.image.uri.path, str)
                        tmp_image = PILImage.open(str(unquote(item.image.uri.path)))
                        item.image = ImageRef.from_pil(tmp_image, dpi=item.image.dpi)

                    elif isinstance(item.image.uri, Path):
                        tmp_image = PILImage.open(str(item.image.uri))
                        item.image = ImageRef.from_pil(tmp_image, dpi=item.image.dpi)

        return result

    def _with_pictures_refs(
        self, image_dir: Path, reference_path: Optional[Path] = None
    ) -> "DoclingDocument":
        """Document with images as refs.

        Creates a copy of this document where all picture data is
        saved to image_dir and referenced through file URIs.
        """
        result: DoclingDocument = copy.deepcopy(self)

        img_count = 0
        image_dir.mkdir(parents=True, exist_ok=True)

        if image_dir.is_dir():
            for item, level in result.iterate_items(with_groups=False):
                if isinstance(item, PictureItem):

                    if (
                        item.image is not None
                        and isinstance(item.image.uri, AnyUrl)
                        and item.image.uri.scheme == "data"
                        and item.image.pil_image is not None
                    ):
                        img = item.image.pil_image

                        hexhash = item._image_to_hexhash()

                        # loc_path = image_dir / f"image_{img_count:06}.png"
                        if hexhash is not None:
                            loc_path = image_dir / f"image_{img_count:06}_{hexhash}.png"

                            img.save(loc_path)
                            if reference_path is not None:
                                obj_path = relative_path(
                                    reference_path.resolve(), loc_path.resolve()
                                )
                            else:
                                obj_path = loc_path

                            item.image.uri = Path(obj_path)

                        # if item.image._pil is not None:
                        #    item.image._pil.close()

                    img_count += 1

        return result

    def print_element_tree(self):
        """Print_element_tree."""
        for ix, (item, level) in enumerate(self.iterate_items(with_groups=True)):
            if isinstance(item, GroupItem):
                print(" " * level, f"{ix}: {item.label.value} with name={item.name}")
            elif isinstance(item, DocItem):
                print(" " * level, f"{ix}: {item.label.value}")

    def export_to_element_tree(self) -> str:
        """Export_to_element_tree."""
        texts = []
        for ix, (item, level) in enumerate(self.iterate_items(with_groups=True)):
            if isinstance(item, GroupItem):
                texts.append(
                    " " * level + f"{ix}: {item.label.value} with name={item.name}"
                )
            elif isinstance(item, DocItem):
                texts.append(" " * level + f"{ix}: {item.label.value}")

        return "\n".join(texts)

    def save_as_json(
        self,
        filename: Path,
        artifacts_dir: Optional[Path] = None,
        image_mode: ImageRefMode = ImageRefMode.EMBEDDED,
        indent: int = 2,
    ):
        """Save as json."""
        artifacts_dir, reference_path = self._get_output_paths(filename, artifacts_dir)

        if image_mode == ImageRefMode.REFERENCED:
            os.makedirs(artifacts_dir, exist_ok=True)

        new_doc = self._make_copy_with_refmode(
            artifacts_dir, image_mode, reference_path=reference_path
        )

        out = new_doc.export_to_dict()
        with open(filename, "w", encoding="utf-8") as fw:
            json.dump(out, fw, indent=indent)

    @classmethod
    def load_from_json(cls, filename: Path) -> "DoclingDocument":
        """load_from_json.

        :param filename: The filename to load a saved DoclingDocument from a .json.
        :type filename: Path

        :returns: The loaded DoclingDocument.
        :rtype: DoclingDocument

        """
        with open(filename, "r", encoding="utf-8") as f:
            return cls.model_validate_json(f.read())

    def save_as_yaml(
        self,
        filename: Path,
        artifacts_dir: Optional[Path] = None,
        image_mode: ImageRefMode = ImageRefMode.EMBEDDED,
        default_flow_style: bool = False,
    ):
        """Save as yaml."""
        artifacts_dir, reference_path = self._get_output_paths(filename, artifacts_dir)

        if image_mode == ImageRefMode.REFERENCED:
            os.makedirs(artifacts_dir, exist_ok=True)

        new_doc = self._make_copy_with_refmode(
            artifacts_dir, image_mode, reference_path=reference_path
        )

        out = new_doc.export_to_dict()
        with open(filename, "w", encoding="utf-8") as fw:
            yaml.dump(out, fw, default_flow_style=default_flow_style)

    def export_to_dict(
        self,
        mode: str = "json",
        by_alias: bool = True,
        exclude_none: bool = True,
    ) -> Dict:
        """Export to dict."""
        out = self.model_dump(mode=mode, by_alias=by_alias, exclude_none=exclude_none)

        return out

    def save_as_markdown(
        self,
        filename: Path,
        artifacts_dir: Optional[Path] = None,
        delim: str = "\n",
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        strict_text: bool = False,
        escaping_underscores: bool = True,
        image_placeholder: str = "<!-- image -->",
        image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER,
        indent: int = 4,
        text_width: int = -1,
        page_no: Optional[int] = None,
    ):
        """Save to markdown."""
        artifacts_dir, reference_path = self._get_output_paths(filename, artifacts_dir)

        if image_mode == ImageRefMode.REFERENCED:
            os.makedirs(artifacts_dir, exist_ok=True)

        new_doc = self._make_copy_with_refmode(
            artifacts_dir, image_mode, reference_path=reference_path
        )

        md_out = new_doc.export_to_markdown(
            delim=delim,
            from_element=from_element,
            to_element=to_element,
            labels=labels,
            strict_text=strict_text,
            escaping_underscores=escaping_underscores,
            image_placeholder=image_placeholder,
            image_mode=image_mode,
            indent=indent,
            text_width=text_width,
            page_no=page_no,
        )

        with open(filename, "w", encoding="utf-8") as fw:
            fw.write(md_out)

    def export_to_markdown(  # noqa: C901
        self,
        delim: str = "\n",
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        strict_text: bool = False,
        escaping_underscores: bool = True,
        image_placeholder: str = "<!-- image -->",
        image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER,
        indent: int = 4,
        text_width: int = -1,
        page_no: Optional[int] = None,
    ) -> str:
        r"""Serialize to Markdown.

        Operates on a slice of the document's body as defined through arguments
        from_element and to_element; defaulting to the whole document.

        :param delim: Delimiter to use when concatenating the various
                Markdown parts. (Default value = "\n").
        :type delim: str = "\n"
        :param from_element: Body slicing start index (inclusive).
                (Default value = 0).
        :type from_element: int = 0
        :param to_element: Body slicing stop index
                (exclusive). (Default value = maxint).
        :type to_element: int = sys.maxsize
        :param labels: The set of document labels to include in the export.
        :type labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS
        :param strict_text: bool: Whether to only include the text content
            of the document. (Default value = False).
        :type strict_text: bool = False
        :param escaping_underscores: bool: Whether to escape underscores in the
            text content of the document. (Default value = True).
        :type escaping_underscores: bool = True
        :param image_placeholder: The placeholder to include to position
            images in the markdown. (Default value = "\<!-- image --\>").
        :type image_placeholder: str = "<!-- image -->"
        :param image_mode: The mode to use for including images in the
            markdown. (Default value = ImageRefMode.PLACEHOLDER).
        :type image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER
        :param indent: The indent in spaces of the nested lists.
            (Default value = 4).
        :type indent: int = 4
        :returns: The exported Markdown representation.
        :rtype: str
        """
        mdtexts: list[str] = []
        list_nesting_level = 0  # Track the current list nesting level
        previous_level = 0  # Track the previous item's level
        in_list = False  # Track if we're currently processing list items

        # Our export markdown doesn't contain any emphasis styling:
        # Bold, Italic, or Bold-Italic
        # Hence, any underscore that we print into Markdown is coming from document text
        # That means we need to escape it, to properly reflect content in the markdown
        # However, we need to preserve underscores in image URLs
        # to maintain their validity
        # For example: ![image](path/to_image.png) should remain unchanged
        def _escape_underscores(text):
            """Escape underscores but leave them intact in the URL.."""
            # Firstly, identify all the URL patterns.
            url_pattern = r"!\[.*?\]\((.*?)\)"
            # Matches both inline ($...$) and block ($$...$$) LaTeX equations:
            latex_pattern = r"\$\$?(?:\\.|[^$\\])*\$\$?"
            combined_pattern = f"({url_pattern})|({latex_pattern})"

            parts = []
            last_end = 0

            for match in re.finditer(combined_pattern, text):
                # Text to add before the URL (needs to be escaped)
                before_url = text[last_end : match.start()]
                parts.append(re.sub(r"(?<!\\)_", r"\_", before_url))

                # Add the full URL part (do not escape)
                parts.append(match.group(0))
                last_end = match.end()

            # Add the final part of the text (which needs to be escaped)
            if last_end < len(text):
                parts.append(re.sub(r"(?<!\\)_", r"\_", text[last_end:]))

            return "".join(parts)

        def _append_text(text: str, do_escape_html=True, do_escape_underscores=True):
            if do_escape_underscores and escaping_underscores:
                text = _escape_underscores(text)
            if do_escape_html:
                text = html.escape(text, quote=False)
            mdtexts.append(text)

        for ix, (item, level) in enumerate(
            self.iterate_items(self.body, with_groups=True, page_no=page_no)
        ):
            # If we've moved to a lower level, we're exiting one or more groups
            if level < previous_level:
                # Calculate how many levels we've exited
                level_difference = previous_level - level
                # Decrement list_nesting_level for each list group we've exited
                list_nesting_level = max(0, list_nesting_level - level_difference)

            previous_level = level  # Update previous_level for next iteration

            if ix < from_element or to_element <= ix:
                continue  # skip as many items as you want

            if (isinstance(item, DocItem)) and (item.label not in labels):
                continue  # skip any label that is not whitelisted

            # Handle newlines between different types of content
            if (
                len(mdtexts) > 0
                and not isinstance(item, (ListItem, GroupItem))
                and in_list
            ):
                mdtexts[-1] += "\n"
                in_list = False

            if isinstance(item, GroupItem) and item.label in [
                GroupLabel.LIST,
                GroupLabel.ORDERED_LIST,
            ]:

                if list_nesting_level == 0:  # Check if we're on the top level.
                    # In that case a new list starts directly after another list.
                    mdtexts.append("\n")  # Add a blank line

                # Increment list nesting level when entering a new list
                list_nesting_level += 1
                in_list = True
                continue

            elif isinstance(item, GroupItem):
                continue

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.TITLE]:
                in_list = False
                marker = "" if strict_text else "#"
                text = f"{marker} {item.text}"
                _append_text(text.strip() + "\n")

            elif (
                isinstance(item, TextItem)
                and item.label in [DocItemLabel.SECTION_HEADER]
            ) or isinstance(item, SectionHeaderItem):
                in_list = False
                marker = ""
                if not strict_text:
                    marker = "#" * level
                    if len(marker) < 2:
                        marker = "##"
                text = f"{marker} {item.text}\n"
                _append_text(text.strip() + "\n")

            elif isinstance(item, CodeItem) and item.label in labels:
                in_list = False
                text = f"```\n{item.text}\n```\n"
                _append_text(text, do_escape_underscores=False, do_escape_html=False)

            elif isinstance(item, ListItem) and item.label in [DocItemLabel.LIST_ITEM]:
                in_list = True
                # Calculate indent based on list_nesting_level
                # -1 because level 1 needs no indent
                list_indent = " " * (indent * (list_nesting_level - 1))

                marker = ""
                if strict_text:
                    marker = ""
                elif item.enumerated:
                    marker = item.marker
                else:
                    marker = "-"  # Markdown needs only dash as item marker.

                text = f"{list_indent}{marker} {item.text}"
                _append_text(text)

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.FORMULA]:
                in_list = False
                if item.text != "":
                    _append_text(
                        f"$${item.text}$$\n",
                        do_escape_underscores=False,
                        do_escape_html=False,
                    )
                elif item.orig != "":
                    _append_text(
                        "<!-- formula-not-decoded -->\n",
                        do_escape_underscores=False,
                        do_escape_html=False,
                    )

            elif isinstance(item, TextItem) and item.label in labels:
                in_list = False
                if len(item.text) and text_width > 0:
                    text = item.text
                    wrapped_text = textwrap.fill(text, width=text_width)
                    _append_text(wrapped_text + "\n")
                elif len(item.text):
                    text = f"{item.text}\n"
                    _append_text(text)

            elif isinstance(item, TableItem) and not strict_text:
                in_list = False
                _append_text(item.caption_text(self))
                md_table = item.export_to_markdown()
                _append_text("\n" + md_table + "\n")

            elif isinstance(item, PictureItem) and not strict_text:
                in_list = False
                _append_text(item.caption_text(self))

                line = item.export_to_markdown(
                    doc=self,
                    image_placeholder=image_placeholder,
                    image_mode=image_mode,
                )

                _append_text(line, do_escape_html=False, do_escape_underscores=False)

            elif isinstance(item, DocItem) and item.label in labels:
                in_list = False
                text = "<!-- missing-text -->"
                _append_text(text, do_escape_html=False, do_escape_underscores=False)

        mdtext = (delim.join(mdtexts)).strip()
        mdtext = re.sub(
            r"\n\n\n+", "\n\n", mdtext
        )  # remove cases of double or more empty lines.

        return mdtext

    def export_to_text(  # noqa: C901
        self,
        delim: str = "\n\n",
        from_element: int = 0,
        to_element: int = 1000000,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
    ) -> str:
        """export_to_text."""
        return self.export_to_markdown(
            delim,
            from_element,
            to_element,
            labels,
            strict_text=True,
            escaping_underscores=False,
            image_placeholder="",
        )

    def save_as_html(
        self,
        filename: Path,
        artifacts_dir: Optional[Path] = None,
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER,
        formula_to_mathml: bool = True,
        page_no: Optional[int] = None,
        html_lang: str = "en",
        html_head: str = _HTML_DEFAULT_HEAD,
    ):
        """Save to HTML."""
        artifacts_dir, reference_path = self._get_output_paths(filename, artifacts_dir)

        if image_mode == ImageRefMode.REFERENCED:
            os.makedirs(artifacts_dir, exist_ok=True)

        new_doc = self._make_copy_with_refmode(
            artifacts_dir, image_mode, reference_path=reference_path
        )

        html_out = new_doc.export_to_html(
            from_element=from_element,
            to_element=to_element,
            labels=labels,
            image_mode=image_mode,
            formula_to_mathml=formula_to_mathml,
            page_no=page_no,
            html_lang=html_lang,
            html_head=html_head,
        )

        with open(filename, "w", encoding="utf-8") as fw:
            fw.write(html_out)

    def _get_output_paths(
        self, filename: Path, artifacts_dir: Optional[Path] = None
    ) -> Tuple[Path, Optional[Path]]:
        if artifacts_dir is None:
            # Remove the extension and add '_pictures'
            artifacts_dir = filename.with_suffix("")
            artifacts_dir = artifacts_dir.with_name(artifacts_dir.name + "_artifacts")
        if artifacts_dir.is_absolute():
            reference_path = None
        else:
            reference_path = filename.parent
        return artifacts_dir, reference_path

    def _make_copy_with_refmode(
        self,
        artifacts_dir: Path,
        image_mode: ImageRefMode,
        reference_path: Optional[Path] = None,
    ):
        new_doc = None
        if image_mode == ImageRefMode.PLACEHOLDER:
            new_doc = self
        elif image_mode == ImageRefMode.REFERENCED:
            new_doc = self._with_pictures_refs(
                image_dir=artifacts_dir, reference_path=reference_path
            )
        elif image_mode == ImageRefMode.EMBEDDED:
            new_doc = self._with_embedded_pictures()
        else:
            raise ValueError("Unsupported ImageRefMode")
        return new_doc

    def export_to_html(  # noqa: C901
        self,
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        image_mode: ImageRefMode = ImageRefMode.PLACEHOLDER,
        formula_to_mathml: bool = True,
        page_no: Optional[int] = None,
        html_lang: str = "en",
        html_head: str = _HTML_DEFAULT_HEAD,
    ) -> str:
        r"""Serialize to HTML."""

        def close_lists(
            curr_level: int,
            prev_level: int,
            in_ordered_list: List[bool],
            html_texts: list[str],
        ):

            if len(in_ordered_list) == 0:
                return (in_ordered_list, html_texts)

            while curr_level < prev_level and len(in_ordered_list) > 0:
                if in_ordered_list[-1]:
                    html_texts.append("</ol>")
                else:
                    html_texts.append("</ul>")

                prev_level -= 1
                in_ordered_list.pop()  # = in_ordered_list[:-1]

            return (in_ordered_list, html_texts)

        head_lines = ["<!DOCTYPE html>", f'<html lang="{html_lang}">', html_head]
        html_texts: list[str] = []

        prev_level = 0  # Track the previous item's level

        in_ordered_list: List[bool] = []  # False

        def _prepare_tag_content(
            text: str, do_escape_html=True, do_replace_newline=True
        ) -> str:
            if do_escape_html:
                text = html.escape(text, quote=False)
            if do_replace_newline:
                text = text.replace("\n", "<br>")
            return text

        for ix, (item, curr_level) in enumerate(
            self.iterate_items(self.body, with_groups=True, page_no=page_no)
        ):
            # If we've moved to a lower level, we're exiting one or more groups
            if curr_level < prev_level and len(in_ordered_list) > 0:
                # Calculate how many levels we've exited
                # level_difference = previous_level - level
                # Decrement list_nesting_level for each list group we've exited
                # list_nesting_level = max(0, list_nesting_level - level_difference)

                in_ordered_list, html_texts = close_lists(
                    curr_level=curr_level,
                    prev_level=prev_level,
                    in_ordered_list=in_ordered_list,
                    html_texts=html_texts,
                )

            prev_level = curr_level  # Update previous_level for next iteration

            if ix < from_element or to_element <= ix:
                continue  # skip as many items as you want

            if (isinstance(item, DocItem)) and (item.label not in labels):
                continue  # skip any label that is not whitelisted

            if isinstance(item, GroupItem) and item.label in [
                GroupLabel.ORDERED_LIST,
            ]:

                text = "<ol>"
                html_texts.append(text)

                # Increment list nesting level when entering a new list
                in_ordered_list.append(True)

            elif isinstance(item, GroupItem) and item.label in [
                GroupLabel.LIST,
            ]:

                text = "<ul>"
                html_texts.append(text)

                # Increment list nesting level when entering a new list
                in_ordered_list.append(False)

            elif isinstance(item, GroupItem):
                continue

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.TITLE]:

                text = f"<h1>{_prepare_tag_content(item.text)}</h1>"
                html_texts.append(text)

            elif isinstance(item, SectionHeaderItem):

                section_level: int = min(item.level + 1, 6)

                text = (
                    f"<h{(section_level)}>"
                    f"{_prepare_tag_content(item.text)}</h{(section_level)}>"
                )
                html_texts.append(text)

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.FORMULA]:

                math_formula = _prepare_tag_content(
                    item.text, do_escape_html=False, do_replace_newline=False
                )
                text = ""

                def _image_fallback(item: TextItem):
                    item_image = item.get_image(doc=self)
                    if item_image is not None:
                        img_ref = ImageRef.from_pil(item_image, dpi=72)
                        return (
                            "<figure>"
                            f'<img src="{img_ref.uri}" alt="{item.orig}" />'
                            "</figure>"
                        )

                # If the formula is not processed correcty, use its image
                if (
                    item.text == ""
                    and item.orig != ""
                    and image_mode == ImageRefMode.EMBEDDED
                    and len(item.prov) > 0
                ):
                    text = _image_fallback(item)

                # Building a math equation in MathML format
                # ref https://www.w3.org/TR/wai-aria-1.1/#math
                elif formula_to_mathml:
                    try:
                        mathml_element = latex2mathml.converter.convert_to_element(
                            math_formula, display="block"
                        )
                        annotation = SubElement(
                            mathml_element, "annotation", dict(encoding="TeX")
                        )
                        annotation.text = math_formula
                        mathml = unescape(tostring(mathml_element, encoding="unicode"))
                        text = f"<div>{mathml}</div>"
                    except Exception as err:
                        _logger.warning(
                            "Malformed formula cannot be rendered. "
                            f"Error {err.__class__.__name__}, formula={math_formula}"
                        )
                        if image_mode == ImageRefMode.EMBEDDED and len(item.prov) > 0:
                            text = _image_fallback(item)
                        else:
                            text = f"<pre>{math_formula}</pre>"

                elif math_formula != "":
                    text = f"<pre>{math_formula}</pre>"

                if text != "":
                    html_texts.append(text)
                else:
                    html_texts.append(
                        '<div class="formula-not-decoded">Formula not decoded</div>'
                    )

            elif isinstance(item, ListItem):

                text = f"<li>{_prepare_tag_content(item.text)}</li>"
                html_texts.append(text)

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.LIST_ITEM]:

                text = f"<li>{_prepare_tag_content(item.text)}</li>"
                html_texts.append(text)

            elif isinstance(item, CodeItem):
                code_text = _prepare_tag_content(
                    item.text, do_escape_html=False, do_replace_newline=False
                )
                text = f"<pre><code>{code_text}</code></pre>"
                html_texts.append(text)

            elif isinstance(item, TextItem):

                text = f"<p>{_prepare_tag_content(item.text)}</p>"
                html_texts.append(text)
            elif isinstance(item, TableItem):

                text = item.export_to_html(doc=self, add_caption=True)
                html_texts.append(text)

            elif isinstance(item, PictureItem):

                html_texts.append(
                    item.export_to_html(
                        doc=self, add_caption=True, image_mode=image_mode
                    )
                )

            elif isinstance(item, DocItem) and item.label in labels:
                continue

        html_texts.append("</html>")

        lines = []
        lines.extend(head_lines)
        lines.extend(html_texts)

        delim = "\n"
        html_text = (delim.join(lines)).strip()

        return html_text

    def save_as_document_tokens(
        self,
        filename: Path,
        delim: str = "\n\n",
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
        # table specific flags
        add_table_cell_location: bool = False,
        add_table_cell_label: bool = True,
        add_table_cell_text: bool = True,
        # specifics
        page_no: Optional[int] = None,
        with_groups: bool = True,
    ):
        r"""Save the document content to a DocumentToken format."""
        out = self.export_to_document_tokens(
            delim=delim,
            from_element=from_element,
            to_element=to_element,
            labels=labels,
            xsize=xsize,
            ysize=ysize,
            add_location=add_location,
            add_content=add_content,
            add_page_index=add_page_index,
            # table specific flags
            add_table_cell_location=add_table_cell_location,
            add_table_cell_label=add_table_cell_label,
            add_table_cell_text=add_table_cell_text,
            # specifics
            page_no=page_no,
            with_groups=with_groups,
        )

        with open(filename, "w", encoding="utf-8") as fw:
            fw.write(out)

    def export_to_document_tokens(
        self,
        delim: str = "\n",
        from_element: int = 0,
        to_element: int = sys.maxsize,
        labels: set[DocItemLabel] = DEFAULT_EXPORT_LABELS,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
        # table specific flags
        add_table_cell_location: bool = False,
        add_table_cell_label: bool = True,
        add_table_cell_text: bool = True,
        # specifics
        page_no: Optional[int] = None,
        with_groups: bool = True,
        newline: bool = True,
    ) -> str:
        r"""Exports the document content to a DocumentToken format.

        Operates on a slice of the document's body as defined through arguments
        from_element and to_element; defaulting to the whole main_text.

        :param delim: str:  (Default value = "\n\n")
        :param from_element: int:  (Default value = 0)
        :param to_element: Optional[int]:  (Default value = None)
        :param labels: set[DocItemLabel]
        :param xsize: int:  (Default value = 100)
        :param ysize: int:  (Default value = 100)
        :param add_location: bool:  (Default value = True)
        :param add_content: bool:  (Default value = True)
        :param add_page_index: bool:  (Default value = True)
        :param # table specific flagsadd_table_cell_location: bool
        :param add_table_cell_label: bool:  (Default value = True)
        :param add_table_cell_text: bool:  (Default value = True)
        :returns: The content of the document formatted as a DocTags string.
        :rtype: str
        """

        def close_lists(
            curr_level: int,
            prev_level: int,
            in_ordered_list: List[bool],
            result: str,
            delim: str,
        ):

            if len(in_ordered_list) == 0:
                return (in_ordered_list, result)

            while curr_level < prev_level and len(in_ordered_list) > 0:
                if in_ordered_list[-1]:
                    result += f"</ordered_list>{delim}"
                else:
                    result += f"</unordered_list>{delim}"

                prev_level -= 1
                in_ordered_list.pop()  # = in_ordered_list[:-1]

            return (in_ordered_list, result)

        if newline:
            delim = "\n"
        else:
            delim = ""

        prev_level = 0  # Track the previous item's level

        in_ordered_list: List[bool] = []  # False

        result = f"{DocumentToken.BEG_DOCUMENT.value}{delim}"

        for ix, (item, curr_level) in enumerate(
            self.iterate_items(self.body, with_groups=True)
        ):

            # If we've moved to a lower level, we're exiting one or more groups
            if curr_level < prev_level and len(in_ordered_list) > 0:
                # Calculate how many levels we've exited
                # level_difference = previous_level - level
                # Decrement list_nesting_level for each list group we've exited
                # list_nesting_level = max(0, list_nesting_level - level_difference)

                in_ordered_list, result = close_lists(
                    curr_level=curr_level,
                    prev_level=prev_level,
                    in_ordered_list=in_ordered_list,
                    result=result,
                    delim=delim,
                )

            prev_level = curr_level  # Update previous_level for next iteration

            if ix < from_element or to_element <= ix:
                continue  # skip as many items as you want

            if (isinstance(item, DocItem)) and (item.label not in labels):
                continue  # skip any label that is not whitelisted

            if isinstance(item, GroupItem) and item.label in [
                GroupLabel.ORDERED_LIST,
            ]:

                result += f"<ordered_list>{delim}"
                in_ordered_list.append(True)

            elif isinstance(item, GroupItem) and item.label in [
                GroupLabel.LIST,
            ]:

                result += f"<unordered_list>{delim}"
                in_ordered_list.append(False)

            elif isinstance(item, SectionHeaderItem):

                result += item.export_to_document_tokens(
                    doc=self,
                    new_line=delim,
                    xsize=xsize,
                    ysize=ysize,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )
            elif isinstance(item, CodeItem) and (item.label in labels):

                result += item.export_to_document_tokens(
                    doc=self,
                    new_line=delim,
                    xsize=xsize,
                    ysize=ysize,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )

            elif isinstance(item, TextItem) and (item.label in labels):

                result += item.export_to_document_tokens(
                    doc=self,
                    new_line=delim,
                    xsize=xsize,
                    ysize=ysize,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )

            elif isinstance(item, TableItem) and (item.label in labels):

                result += item.export_to_document_tokens(
                    doc=self,
                    new_line=delim,
                    xsize=xsize,
                    ysize=ysize,
                    add_caption=True,
                    add_location=add_location,
                    add_content=add_content,
                    add_cell_location=add_table_cell_location,
                    add_cell_label=add_table_cell_label,
                    add_cell_text=add_table_cell_text,
                    add_page_index=add_page_index,
                )

            elif isinstance(item, PictureItem) and (item.label in labels):

                result += item.export_to_document_tokens(
                    doc=self,
                    new_line=delim,
                    xsize=xsize,
                    ysize=ysize,
                    add_caption=True,
                    add_location=add_location,
                    add_content=add_content,
                    add_page_index=add_page_index,
                )

        result += DocumentToken.END_DOCUMENT.value

        return result

    def _export_to_indented_text(
        self, indent="  ", max_text_len: int = -1, explicit_tables: bool = False
    ):
        """Export the document to indented text to expose hierarchy."""
        result = []

        def get_text(text: str, max_text_len: int):

            middle = " ... "

            if max_text_len == -1:
                return text
            elif len(text) < max_text_len + len(middle):
                return text
            else:
                tbeg = int((max_text_len - len(middle)) / 2)
                tend = int(max_text_len - tbeg)

                return text[0:tbeg] + middle + text[-tend:]

        for i, (item, level) in enumerate(self.iterate_items(with_groups=True)):
            if isinstance(item, GroupItem):
                result.append(
                    indent * level
                    + f"item-{i} at level {level}: {item.label}: group {item.name}"
                )

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.TITLE]:
                text = get_text(text=item.text, max_text_len=max_text_len)

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}: {text}"
                )

            elif isinstance(item, SectionHeaderItem):
                text = get_text(text=item.text, max_text_len=max_text_len)

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}: {text}"
                )

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.CODE]:
                text = get_text(text=item.text, max_text_len=max_text_len)

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}: {text}"
                )

            elif isinstance(item, ListItem) and item.label in [DocItemLabel.LIST_ITEM]:
                text = get_text(text=item.text, max_text_len=max_text_len)

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}: {text}"
                )

            elif isinstance(item, TextItem):
                text = get_text(text=item.text, max_text_len=max_text_len)

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}: {text}"
                )

            elif isinstance(item, TableItem):

                result.append(
                    indent * level
                    + f"item-{i} at level {level}: {item.label} with "
                    + f"[{item.data.num_rows}x{item.data.num_cols}]"
                )

                for _ in item.captions:
                    caption = _.resolve(self)
                    result.append(
                        indent * (level + 1)
                        + f"item-{i} at level {level + 1}: {caption.label}: "
                        + f"{caption.text}"
                    )

                if explicit_tables:
                    grid: list[list[str]] = []
                    for i, row in enumerate(item.data.grid):
                        grid.append([])
                        for j, cell in enumerate(row):
                            if j < 10:
                                text = get_text(text=cell.text, max_text_len=16)
                                grid[-1].append(text)

                    result.append("\n" + tabulate(grid) + "\n")

            elif isinstance(item, PictureItem):

                result.append(
                    indent * level + f"item-{i} at level {level}: {item.label}"
                )

                for _ in item.captions:
                    caption = _.resolve(self)
                    result.append(
                        indent * (level + 1)
                        + f"item-{i} at level {level + 1}: {caption.label}: "
                        + f"{caption.text}"
                    )

            elif isinstance(item, DocItem):
                result.append(
                    indent * (level + 1)
                    + f"item-{i} at level {level}: {item.label}: ignored"
                )

        return "\n".join(result)

    def add_page(
        self, page_no: int, size: Size, image: Optional[ImageRef] = None
    ) -> PageItem:
        """add_page.

        :param page_no: int:
        :param size: Size:

        """
        pitem = PageItem(page_no=page_no, size=size, image=image)

        self.pages[page_no] = pitem
        return pitem

    @field_validator("version")
    @classmethod
    def check_version_is_compatible(cls, v: str) -> str:
        """Check if this document version is compatible with current version."""
        current_match = re.match(VERSION_PATTERN, CURRENT_VERSION)
        doc_match = re.match(VERSION_PATTERN, v)
        if (
            doc_match is None
            or current_match is None
            or doc_match["major"] != current_match["major"]
            or doc_match["minor"] > current_match["minor"]
        ):
            raise ValueError(
                f"incompatible version {v} with schema version {CURRENT_VERSION}"
            )
        else:
            return CURRENT_VERSION

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def validate_document(cls, d: "DoclingDocument"):
        """validate_document."""
        if not d.validate_tree(d.body) or not d.validate_tree(d.furniture):
            raise ValueError("Document hierachy is inconsistent.")

        return d

```
</content>
</file_27>

<file_28>
<path>types/doc/labels.py</path>
<content>
```python
"""Models for the labels types."""

from enum import Enum
from typing import Tuple


class DocItemLabel(str, Enum):
    """DocItemLabel."""

    CAPTION = "caption"
    FOOTNOTE = "footnote"
    FORMULA = "formula"
    LIST_ITEM = "list_item"
    PAGE_FOOTER = "page_footer"
    PAGE_HEADER = "page_header"
    PICTURE = "picture"
    SECTION_HEADER = "section_header"
    TABLE = "table"
    TEXT = "text"
    TITLE = "title"
    DOCUMENT_INDEX = "document_index"
    CODE = "code"
    CHECKBOX_SELECTED = "checkbox_selected"
    CHECKBOX_UNSELECTED = "checkbox_unselected"
    FORM = "form"
    KEY_VALUE_REGION = "key_value_region"

    # Additional labels for markup-based formats (e.g. HTML, Word)
    PARAGRAPH = "paragraph"
    REFERENCE = "reference"

    def __str__(self):
        """Get string value."""
        return str(self.value)

    @staticmethod
    def get_color(label: "DocItemLabel") -> Tuple[int, int, int]:
        """Return the RGB color associated with a given label."""
        color_map = {
            DocItemLabel.CAPTION: (255, 204, 153),
            DocItemLabel.FOOTNOTE: (200, 200, 255),
            DocItemLabel.FORMULA: (192, 192, 192),
            DocItemLabel.LIST_ITEM: (153, 153, 255),
            DocItemLabel.PAGE_FOOTER: (204, 255, 204),
            DocItemLabel.PAGE_HEADER: (204, 255, 204),
            DocItemLabel.PICTURE: (255, 204, 164),
            DocItemLabel.SECTION_HEADER: (255, 153, 153),
            DocItemLabel.TABLE: (255, 204, 204),
            DocItemLabel.TEXT: (255, 255, 153),
            DocItemLabel.TITLE: (255, 153, 153),
            DocItemLabel.DOCUMENT_INDEX: (220, 220, 220),
            DocItemLabel.CODE: (125, 125, 125),
            DocItemLabel.CHECKBOX_SELECTED: (255, 182, 193),
            DocItemLabel.CHECKBOX_UNSELECTED: (255, 182, 193),
            DocItemLabel.FORM: (200, 255, 255),
            DocItemLabel.KEY_VALUE_REGION: (183, 65, 14),
            DocItemLabel.PARAGRAPH: (255, 255, 153),
            DocItemLabel.REFERENCE: (176, 224, 230),
        }
        return color_map[label]


class GroupLabel(str, Enum):
    """GroupLabel."""

    UNSPECIFIED = "unspecified"
    LIST = (
        "list"  # group label for list container (not the list-items) (e.g. HTML <ul/>)
    )
    ORDERED_LIST = "ordered_list"  # List with enumeration (e.g. HTML <ol/>)
    CHAPTER = "chapter"
    SECTION = "section"
    SHEET = "sheet"
    SLIDE = "slide"
    FORM_AREA = "form_area"
    KEY_VALUE_AREA = "key_value_area"
    COMMENT_SECTION = "comment_section"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class PictureClassificationLabel(str, Enum):
    """PictureClassificationLabel."""

    OTHER = "other"

    # If more than one picture is grouped together, it
    # is generally not possible to assign a label
    PICTURE_GROUP = "picture_group"

    # General
    PIE_CHART = "pie_chart"
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    FLOW_CHART = "flow_chart"
    SCATTER_CHART = "scatter_chart"
    HEATMAP = "heatmap"
    REMOTE_SENSING = "remote_sensing"

    NATURAL_IMAGE = "natural_image"

    # Chemistry
    MOLECULAR_STRUCTURE = "chemistry_molecular_structure"
    MARKUSH_STRUCTURE = "chemistry_markush_structure"

    # Company
    ICON = "icon"
    LOGO = "logo"
    SIGNATURE = "signature"
    STAMP = "stamp"
    QR_CODE = "qr_code"
    BAR_CODE = "bat_code"
    SCREENSHOT = "screenshot"

    # Geology/Geography
    GEOGRAPHIC_MAP = "map"
    STRATIGRAPHIC_CHART = "stratigraphic_chart"

    # Engineering
    CAD_DRAWING = "cad_drawing"
    ELECTRICAL_DIAGRAM = "electrical_diagram"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class TableCellLabel(str, Enum):
    """TableCellLabel."""

    COLUMN_HEADER = "col_header"
    ROW_HEADER = "row_header"
    ROW_SECTION = "row_section"
    BODY = "body"

    def __str__(self):
        """Get string value."""
        return str(self.value)


class CodeLanguageLabel(str, Enum):
    """CodeLanguageLabel."""

    ADA = "Ada"
    AWK = "Awk"
    BASH = "Bash"
    BC = "bc"
    C = "C"
    C_SHARP = "C#"
    C_PLUS_PLUS = "C++"
    CMAKE = "CMake"
    COBOL = "COBOL"
    CSS = "CSS"
    CEYLON = "Ceylon"
    CLOJURE = "Clojure"
    CRYSTAL = "Crystal"
    CUDA = "Cuda"
    CYTHON = "Cython"
    D = "D"
    DART = "Dart"
    DC = "dc"
    DOCKERFILE = "Dockerfile"
    ELIXIR = "Elixir"
    ERLANG = "Erlang"
    FORTRAN = "FORTRAN"
    FORTH = "Forth"
    GO = "Go"
    HTML = "HTML"
    HASKELL = "Haskell"
    HAXE = "Haxe"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    JULIA = "Julia"
    KOTLIN = "Kotlin"
    LISP = "Lisp"
    LUA = "Lua"
    MATLAB = "Matlab"
    MOONSCRIPT = "MoonScript"
    NIM = "Nim"
    OCAML = "OCaml"
    OBJECTIVEC = "ObjectiveC"
    OCTAVE = "Octave"
    PHP = "PHP"
    PASCAL = "Pascal"
    PERL = "Perl"
    PROLOG = "Prolog"
    PYTHON = "Python"
    RACKET = "Racket"
    RUBY = "Ruby"
    RUST = "Rust"
    SML = "SML"
    SQL = "SQL"
    SCALA = "Scala"
    SCHEME = "Scheme"
    SWIFT = "Swift"
    TYPESCRIPT = "TypeScript"
    UNKNOWN = "unknown"
    VISUALBASIC = "VisualBasic"
    XML = "XML"
    YAML = "YAML"

    def __str__(self):
        """Get string value."""
        return str(self.value)

```
</content>
</file_28>

<file_29>
<path>types/doc/tokens.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Tokens used in the docling document model."""

from enum import Enum
from typing import Tuple


class TableToken(Enum):
    """Class to represent an LLM friendly representation of a Table."""

    CELL_LABEL_COLUMN_HEADER = "<column_header>"
    CELL_LABEL_ROW_HEADER = "<row_header>"
    CELL_LABEL_SECTION_HEADERE = "<section_header>"
    CELL_LABEL_DATA = "<data>"

    OTSL_ECEL = "<ecel>"  # empty cell
    OTSL_FCEL = "<fcel>"  # cell with content
    OTSL_LCEL = "<lcel>"  # left looking cell,
    OTSL_UCEL = "<ucel>"  # up looking cell,
    OTSL_XCEL = "<xcel>"  # 2d extension cell (cross cell),
    OTSL_NL = "<nl>"  # new line,
    OTSL_CHED = "<ched>"  # - column header cell,
    OTSL_RHED = "<rhed>"  # - row header cell,
    OTSL_SROW = "<srow>"  # - section row cell

    @classmethod
    def get_special_tokens(cls):
        """Function to get all special document tokens."""
        special_tokens = [token.value for token in cls]
        return special_tokens

    @staticmethod
    def is_known_token(label):
        """Function to check if label is in tokens."""
        return label in TableToken.get_special_tokens()


class DocumentToken(Enum):
    """Class to represent an LLM friendly representation of a Document."""

    BEG_DOCUMENT = "<document>"
    END_DOCUMENT = "</document>"

    BEG_TITLE = "<title>"
    END_TITLE = "</title>"

    BEG_ABSTRACT = "<abstract>"
    END_ABSTRACT = "</abstract>"

    BEG_DOI = "<doi>"
    END_DOI = "</doi>"
    BEG_DATE = "<date>"
    END_DATE = "</date>"

    BEG_AUTHORS = "<authors>"
    END_AUTHORS = "</authors>"
    BEG_AUTHOR = "<author>"
    END_AUTHOR = "</author>"

    BEG_AFFILIATIONS = "<affiliations>"
    END_AFFILIATIONS = "</affiliations>"
    BEG_AFFILIATION = "<affiliation>"
    END_AFFILIATION = "</affiliation>"

    BEG_HEADER = "<section-header>"
    END_HEADER = "</section-header>"
    BEG_TEXT = "<text>"
    END_TEXT = "</text>"
    BEG_PARAGRAPH = "<paragraph>"
    END_PARAGRAPH = "</paragraph>"
    BEG_TABLE = "<table>"
    END_TABLE = "</table>"
    BEG_FIGURE = "<figure>"
    END_FIGURE = "</figure>"
    BEG_CAPTION = "<caption>"
    END_CAPTION = "</caption>"
    BEG_EQUATION = "<equation>"
    END_EQUATION = "</equation>"
    BEG_LIST = "<list>"
    END_LIST = "</list>"
    BEG_LISTITEM = "<list-item>"
    END_LISTITEM = "</list-item>"

    BEG_LOCATION = "<location>"
    END_LOCATION = "</location>"
    BEG_GROUP = "<group>"
    END_GROUP = "</group>"

    @classmethod
    def get_special_tokens(
        cls,
        max_rows: int = 100,
        max_cols: int = 100,
        max_pages: int = 1000,
        page_dimension: Tuple[int, int] = (100, 100),
    ):
        """Function to get all special document tokens."""
        special_tokens = [token.value for token in cls]

        # Adding dynamically generated row and col tokens
        for i in range(0, max_rows + 1):
            special_tokens += [f"<row_{i}>", f"</row_{i}>"]

        for i in range(0, max_cols + 1):
            special_tokens += [f"<col_{i}>", f"</col_{i}>"]

        for i in range(6):
            special_tokens += [f"<section-header-{i}>", f"</section-header-{i}>"]

        # FIXME: this is synonym of section header
        for i in range(6):
            special_tokens += [f"<subtitle-level-{i}>", f"</subtitle-level-{i}>"]

        # Adding dynamically generated page-tokens
        for i in range(0, max_pages + 1):
            special_tokens.append(f"<page_{i}>")
            special_tokens.append(f"</page_{i}>")

        # Adding dynamically generated location-tokens
        for i in range(0, max(page_dimension[0] + 1, page_dimension[1] + 1)):
            special_tokens.append(f"<loc_{i}>")

        return special_tokens

    @staticmethod
    def is_known_token(label):
        """Function to check if label is in tokens."""
        return label in DocumentToken.get_special_tokens()

    @staticmethod
    def get_row_token(row: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<row_{row}>"
        else:
            return f"</row_{row}>"

    @staticmethod
    def get_col_token(col: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<col_{col}>"
        else:
            return f"</col_{col}>"

    @staticmethod
    def get_page_token(page: int):
        """Function to get page tokens."""
        return f"<page_{page}>"

    @staticmethod
    def get_location_token(val: float, rnorm: int = 100):
        """Function to get location tokens."""
        val_ = round(rnorm * val)

        if val_ < 0:
            return "<loc_0>"

        if val_ > rnorm:
            return f"<loc_{rnorm}>"

        return f"<loc_{val_}>"

    @staticmethod
    def get_location(
        bbox: tuple[float, float, float, float],
        page_w: float,
        page_h: float,
        xsize: int = 100,
        ysize: int = 100,
        page_i: int = -1,
    ):
        """Get the location string give bbox and page-dim."""
        assert bbox[0] <= bbox[2], f"bbox[0]<=bbox[2] => {bbox[0]}<={bbox[2]}"
        assert bbox[1] <= bbox[3], f"bbox[1]<=bbox[3] => {bbox[1]}<={bbox[3]}"

        x0 = bbox[0] / page_w
        y0 = bbox[1] / page_h
        x1 = bbox[2] / page_w
        y1 = bbox[3] / page_h

        page_tok = ""
        if page_i != -1:
            page_tok = DocumentToken.get_page_token(page=page_i)

        x0_tok = DocumentToken.get_location_token(val=min(x0, x1), rnorm=xsize)
        y0_tok = DocumentToken.get_location_token(val=min(y0, y1), rnorm=ysize)
        x1_tok = DocumentToken.get_location_token(val=max(x0, x1), rnorm=xsize)
        y1_tok = DocumentToken.get_location_token(val=max(y0, y1), rnorm=ysize)

        loc_str = f"{DocumentToken.BEG_LOCATION.value}"
        loc_str += f"{page_tok}{x0_tok}{y0_tok}{x1_tok}{y1_tok}"
        loc_str += f"{DocumentToken.END_LOCATION.value}"

        return loc_str

```
</content>
</file_29>

<file_30>
<path>types/doc/utils.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Utils for document types."""

from pathlib import Path


def relative_path(src: Path, target: Path) -> Path:
    """Compute the relative path from `src` to `target`.

    Args:
        src (str | Path): The source directory or file path (must be absolute).
        target (str | Path): The target directory or file path (must be absolute).

    Returns:
        Path: The relative path from `src` to `target`.

    Raises:
        ValueError: If either `src` or `target` is not an absolute path.
    """
    src = Path(src).resolve()
    target = Path(target).resolve()

    # Ensure both paths are absolute
    if not src.is_absolute():
        raise ValueError(f"The source path must be absolute: {src}")
    if not target.is_absolute():
        raise ValueError(f"The target path must be absolute: {target}")

    # Find the common ancestor
    common_parts = []
    for src_part, target_part in zip(src.parts, target.parts):
        if src_part == target_part:
            common_parts.append(src_part)
        else:
            break

    # Determine the path to go up from src to the common ancestor
    up_segments = [".."] * (len(src.parts) - len(common_parts))

    # Add the path from the common ancestor to the target
    down_segments = target.parts[len(common_parts) :]

    # Combine and return the result
    return Path(*up_segments, *down_segments)

```
</content>
</file_30>

<file_31>
<path>types/gen/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models defined by the Generic type."""

```
</content>
</file_31>

<file_32>
<path>types/gen/generic.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define a generic Docling type."""

from typing import Optional

from pydantic import Field, StrictStr

from docling_core.search.mapping import es_field
from docling_core.types.base import FileInfoObject
from docling_core.utils.alias import AliasModel


class Generic(AliasModel):
    """A representation of a generic document."""

    name: Optional[StrictStr] = Field(
        default=None,
        description="A short description or summary of the document.",
        alias="_name",
        json_schema_extra=es_field(type="text"),
    )

    file_info: FileInfoObject = Field(
        title="Document information",
        description=(
            "Minimal identification information of the document within a collection."
        ),
        alias="file-info",
    )

```
</content>
</file_32>

<file_33>
<path>types/io/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models for io."""

from io import BytesIO

from pydantic import BaseModel, ConfigDict


class DocumentStream(BaseModel):
    """Wrapper class for a bytes stream with a filename."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    stream: BytesIO

```
</content>
</file_33>

<file_34>
<path>types/legacy_doc/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models defined by the Document type."""

```
</content>
</file_34>

<file_35>
<path>types/legacy_doc/base.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define common models across CCS objects."""
from typing import Annotated, List, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, PositiveInt, StrictStr

from docling_core.search.mapping import es_field
from docling_core.types.legacy_doc.tokens import DocumentToken
from docling_core.utils.alias import AliasModel

CellData = tuple[float, float, float, float, str, str]

CellHeader = tuple[
    Literal["x0"],
    Literal["y0"],
    Literal["x1"],
    Literal["y1"],
    Literal["font"],
    Literal["text"],
]

BoundingBox = Annotated[list[float], Field(min_length=4, max_length=4)]

Span = Annotated[list[int], Field(min_length=2, max_length=2)]


class CellsContainer(BaseModel):
    """Cell container."""

    data: Optional[list[CellData]] = None
    header: CellHeader = ("x0", "y0", "x1", "y1", "font", "text")


class S3Resource(BaseModel):
    """Resource in a cloud object storage."""

    mime: str
    path: str
    page: Optional[PositiveInt] = None


class S3Data(AliasModel):
    """Data object in a cloud object storage."""

    pdf_document: Optional[list[S3Resource]] = Field(default=None, alias="pdf-document")
    pdf_pages: Optional[list[S3Resource]] = Field(default=None, alias="pdf-pages")
    pdf_images: Optional[list[S3Resource]] = Field(default=None, alias="pdf-images")
    json_document: Optional[S3Resource] = Field(default=None, alias="json-document")
    json_meta: Optional[S3Resource] = Field(default=None, alias="json-meta")
    glm_json_document: Optional[S3Resource] = Field(
        default=None, alias="glm-json-document"
    )
    figures: Optional[list[S3Resource]] = None


class S3Reference(AliasModel):
    """References an s3 resource."""

    ref_s3_data: StrictStr = Field(
        alias="__ref_s3_data", examples=["#/_s3_data/figures/0"]
    )


class Prov(AliasModel):
    """Provenance."""

    bbox: BoundingBox
    page: PositiveInt
    span: Span
    ref_s3_data: Optional[StrictStr] = Field(
        default=None, alias="__ref_s3_data", json_schema_extra=es_field(suppress=True)
    )


class BoundingBoxContainer(BaseModel):
    """Bounding box container."""

    min: BoundingBox
    max: BoundingBox


class BitmapObject(AliasModel):
    """Bitmap object."""

    obj_type: str = Field(alias="type")
    bounding_box: BoundingBoxContainer = Field(
        json_schema_extra=es_field(suppress=True)
    )
    prov: Prov


class PageDimensions(BaseModel):
    """Page dimensions."""

    height: float
    page: PositiveInt
    width: float


class TableCell(AliasModel):
    """Table cell."""

    bbox: Optional[BoundingBox] = None
    spans: Optional[list[Span]] = None
    text: str = Field(json_schema_extra=es_field(term_vector="with_positions_offsets"))
    obj_type: str = Field(alias="type")


class GlmTableCell(TableCell):
    """Glm Table cell."""

    col: Optional[int] = Field(default=None, json_schema_extra=es_field(suppress=True))
    col_header: bool = Field(
        default=False, alias="col-header", json_schema_extra=es_field(suppress=True)
    )
    col_span: Optional[Span] = Field(
        default=None, alias="col-span", json_schema_extra=es_field(suppress=True)
    )
    row: Optional[int] = Field(default=None, json_schema_extra=es_field(suppress=True))
    row_header: bool = Field(
        default=False, alias="row-header", json_schema_extra=es_field(suppress=True)
    )
    row_span: Optional[Span] = Field(
        default=None, alias="row-span", json_schema_extra=es_field(suppress=True)
    )


class BaseCell(AliasModel):
    """Base cell."""

    prov: Optional[list[Prov]] = None
    text: Optional[str] = Field(
        default=None, json_schema_extra=es_field(term_vector="with_positions_offsets")
    )
    obj_type: str = Field(
        alias="type", json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    payload: Optional[dict] = None

    def get_location_tokens(
        self,
        new_line: str,
        page_w: float,
        page_h: float,
        xsize: int = 100,
        ysize: int = 100,
        add_page_index: bool = True,
    ) -> str:
        """Get the location string for the BaseCell."""
        if self.prov is None:
            return ""

        location = ""
        for prov in self.prov:

            page_i = -1
            if add_page_index:
                page_i = prov.page

            loc_str = DocumentToken.get_location(
                bbox=prov.bbox,
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                page_i=page_i,
            )
            location += f"{loc_str}{new_line}"

        return location


class Table(BaseCell):
    """Table."""

    num_cols: int = Field(alias="#-cols")
    num_rows: int = Field(alias="#-rows")
    data: Optional[list[list[Union[GlmTableCell, TableCell]]]] = None
    model: Optional[str] = None

    # FIXME: we need to check why we have bounding_box (this should be in prov)
    bounding_box: Optional[BoundingBoxContainer] = Field(
        default=None, alias="bounding-box", json_schema_extra=es_field(suppress=True)
    )

    def _get_tablecell_span(self, cell: TableCell, ix: int):
        if cell.spans is None:
            span = set()
        else:
            span = set([s[ix] for s in cell.spans])
        if len(span) == 0:
            return 1, None, None
        return len(span), min(span), max(span)

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export the table as a Pandas DataFrame."""
        if self.data is None or self.num_rows == 0 or self.num_cols == 0:
            return pd.DataFrame()

        # Count how many rows are column headers
        num_headers = 0
        for i, row in enumerate(self.data):
            if len(row) == 0:
                raise RuntimeError(f"Invalid table. {len(row)=} but {self.num_cols=}.")

            any_header = False
            for cell in row:
                if cell.obj_type == "col_header":
                    any_header = True
                    break

            if any_header:
                num_headers += 1
            else:
                break

        # Create the column names from all col_headers
        columns: Optional[List[str]] = None
        if num_headers > 0:
            columns = ["" for _ in range(self.num_cols)]
            for i in range(num_headers):
                for j, cell in enumerate(self.data[i]):
                    col_name = cell.text
                    if columns[j] != "":
                        col_name = f".{col_name}"
                    columns[j] += col_name

        # Create table data
        table_data = [[cell.text for cell in row] for row in self.data[num_headers:]]

        # Create DataFrame
        df = pd.DataFrame(table_data, columns=columns)

        return df

    def export_to_html(self) -> str:
        """Export the table as html."""
        body = ""
        nrows = self.num_rows
        ncols = self.num_cols

        if self.data is None:
            return ""
        for i in range(nrows):
            body += "<tr>"
            for j in range(ncols):
                cell: TableCell = self.data[i][j]

                rowspan, rowstart, rowend = self._get_tablecell_span(cell, 0)
                colspan, colstart, colend = self._get_tablecell_span(cell, 1)

                if rowstart is not None and rowstart != i:
                    continue
                if colstart is not None and colstart != j:
                    continue

                if rowstart is None:
                    rowstart = i
                if colstart is None:
                    colstart = j

                content = cell.text.strip()
                label = cell.obj_type
                celltag = "td"
                if label in ["row_header", "row_multi_header", "row_title"]:
                    pass
                elif label in ["col_header", "col_multi_header"]:
                    celltag = "th"

                opening_tag = f"{celltag}"
                if rowspan > 1:
                    opening_tag += f' rowspan="{rowspan}"'
                if colspan > 1:
                    opening_tag += f' colspan="{colspan}"'

                body += f"<{opening_tag}>{content}</{celltag}>"
            body += "</tr>"
        body = f"<table>{body}</table>"

        return body

    def export_to_document_tokens(
        self,
        new_line: str = "\n",
        page_w: float = 0.0,
        page_h: float = 0.0,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,
        add_cell_location: bool = True,
        add_cell_label: bool = True,
        add_cell_text: bool = True,
        add_page_index: bool = True,
    ):
        """Export table to document tokens format."""
        body = f"{DocumentToken.BEG_TABLE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                new_line=new_line,
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and self.text is not None and len(self.text) > 0:
            body += f"{DocumentToken.BEG_CAPTION.value}"
            body += f"{self.text.strip()}"
            body += f"{DocumentToken.END_CAPTION.value}"
            body += f"{new_line}"

        if add_content and self.data is not None and len(self.data) > 0:
            for i, row in enumerate(self.data):
                body += f"<row_{i}>"
                for j, col in enumerate(row):

                    text = ""
                    if add_cell_text:
                        text = col.text.strip()

                    cell_loc = ""
                    if (
                        col.bbox is not None
                        and add_cell_location
                        and add_page_index
                        and self.prov is not None
                        and len(self.prov) > 0
                    ):
                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox,
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=self.prov[0].page,
                        )
                    elif (
                        col.bbox is not None
                        and add_cell_location
                        and not add_page_index
                    ):
                        cell_loc = DocumentToken.get_location(
                            bbox=col.bbox,
                            page_w=page_w,
                            page_h=page_h,
                            xsize=xsize,
                            ysize=ysize,
                            page_i=-1,
                        )

                    cell_label = ""
                    if (
                        add_cell_label
                        and col.obj_type is not None
                        and len(col.obj_type) > 0
                    ):
                        cell_label = f"<{col.obj_type}>"

                    body += f"<col_{j}>{cell_loc}{cell_label}{text}</col_{j}>"

                body += f"</row_{i}>{new_line}"

        body += f"{DocumentToken.END_TABLE.value}{new_line}"

        return body


# FIXME: let's add some figure specific data-types later
class Figure(BaseCell):
    """Figure."""

    # FIXME: we need to check why we have bounding_box (this should be in prov)
    bounding_box: Optional[BoundingBoxContainer] = Field(
        default=None, alias="bounding-box", json_schema_extra=es_field(suppress=True)
    )

    def export_to_document_tokens(
        self,
        new_line: str = "\n",
        page_w: float = 0.0,
        page_h: float = 0.0,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_caption: bool = True,
        add_content: bool = True,  # not used at the moment
        add_page_index: bool = True,
    ):
        """Export figure to document tokens format."""
        body = f"{DocumentToken.BEG_FIGURE.value}{new_line}"

        if add_location:
            body += self.get_location_tokens(
                new_line=new_line,
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_caption and self.text is not None and len(self.text) > 0:
            body += f"{DocumentToken.BEG_CAPTION.value}"
            body += f"{self.text.strip()}"
            body += f"{DocumentToken.END_CAPTION.value}"
            body += f"{new_line}"

        body += f"{DocumentToken.END_FIGURE.value}{new_line}"

        return body


class BaseText(BaseCell):
    """Base model for text objects."""

    # FIXME: do we need these ???
    name: Optional[StrictStr] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    font: Optional[str] = None

    def export_to_document_tokens(
        self,
        new_line: str = "\n",
        page_w: float = 0.0,
        page_h: float = 0.0,
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
    ):
        """Export text element to document tokens format."""
        body = f"<{self.obj_type}>"

        assert DocumentToken.is_known_token(
            body
        ), f"failed DocumentToken.is_known_token({body})"

        if add_location:
            body += self.get_location_tokens(
                new_line="",
                page_w=page_w,
                page_h=page_h,
                xsize=xsize,
                ysize=ysize,
                add_page_index=add_page_index,
            )

        if add_content and self.text is not None:
            body += self.text.strip()

        body += f"</{self.obj_type}>{new_line}"

        return body


class ListItem(BaseText):
    """List item."""

    identifier: str


class Ref(AliasModel):
    """Reference."""

    name: str
    obj_type: str = Field(alias="type")
    ref: str = Field(alias="$ref")


class PageReference(BaseModel):
    """Page reference."""

    hash: str = Field(json_schema_extra=es_field(type="keyword", ignore_above=8191))
    model: str = Field(json_schema_extra=es_field(suppress=True))
    page: PositiveInt = Field(json_schema_extra=es_field(type="short"))

```
</content>
</file_35>

<file_36>
<path>types/legacy_doc/doc_ann.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models for annotations and predictions in CCS."""
from typing import Any

from pydantic import BaseModel

from docling_core.types.legacy_doc.base import BoundingBox

AnnotationReport = Any  # TODO


class Cell(BaseModel):
    """Cell."""

    id: int
    rawcell_id: int
    label: str


class Cluster(BaseModel):
    """Cluster."""

    model: str
    type: str
    bbox: BoundingBox
    cell_ids: list[int]
    merged: bool
    id: int


class Table(BaseModel):
    """Table."""

    cell_id: int
    label: str
    rows: list[int]
    cols: list[int]


class Info(BaseModel):
    """Info."""

    display_name: str
    model_name: str
    model_class: str
    model_version: str
    model_id: str


class Source(BaseModel):
    """Source."""

    type: str
    timestamp: float
    info: Info


class AnnotPredItem(BaseModel):
    """Annotation or prediction item."""

    cells: list[Cell]
    clusters: list[Cluster]
    tables: list[Table]
    source: Source


class Annotation(BaseModel):
    """Annotations."""

    annotations: list[AnnotPredItem]
    predictions: list[AnnotPredItem]
    reports: list[AnnotationReport]

```
</content>
</file_36>

<file_37>
<path>types/legacy_doc/doc_ocr.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models for CCS objects with OCR."""
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from docling_core.types.legacy_doc.base import BoundingBox
from docling_core.utils.alias import AliasModel

CoordsOrder = Literal["x1", "y1", "x2", "y2"]

CoordsOrigin = Literal["top-left"]  # TODO

Info = Dict[str, Any]  # TODO


class Page(BaseModel):
    """Page."""

    width: float
    height: float


class Meta(AliasModel):
    """Meta."""

    page: Page
    coords_order: List[CoordsOrder] = Field(..., alias="coords-order")
    coords_origin: CoordsOrigin = Field(..., alias="coords-origin")


class Dimension(BaseModel):
    """Dimension."""

    width: float
    height: float


class Word(BaseModel):
    """Word."""

    confidence: float
    bbox: BoundingBox
    content: str


class Cell(BaseModel):
    """Cell."""

    confidence: float
    bbox: BoundingBox
    content: str


class Box(BaseModel):
    """Box."""

    confidence: float
    bbox: BoundingBox
    content: str


class Path(BaseModel):
    """Path."""

    x: List[float]
    y: List[float]


class OcrOutput(AliasModel):
    """OCR output."""

    meta: Meta = Field(..., alias="_meta")
    info: Info
    dimension: Dimension
    words: List[Word]
    cells: List[Cell]
    boxes: List[Box]
    paths: List[Path]

```
</content>
</file_37>

<file_38>
<path>types/legacy_doc/doc_raw.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models for CCS objects in raw format."""
from typing import Any, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from docling_core.types.legacy_doc.base import BoundingBox
from docling_core.utils.alias import AliasModel

FontDifferences = dict[str, Any]
NamedWidths = dict[str, Any]
IgnoredCell = Any


class Box(BaseModel):
    """Box."""

    baseline: BoundingBox
    device: BoundingBox


class Content(BaseModel):
    """Content."""

    rnormalized: str


class Enumeration(BaseModel):
    """Enumeration."""

    match: int
    type: int


class Font(BaseModel):
    """Font."""

    color: Annotated[List[float], Field(min_length=3, max_length=4)]
    name: str
    size: float


class Cell(AliasModel):
    """Cell."""

    see_cell: bool = Field(..., alias="SEE_cell")
    see_confidence: float = Field(..., alias="SEE_confidence")
    angle: float
    box: Box
    content: Content
    enumeration: Enumeration
    font: Font


class PageDimensions(BaseModel):
    """PageDimensions."""

    bbox: BoundingBox
    height: float
    width: float


class Path(AliasModel):
    """Path."""

    bbox: BoundingBox
    sub_paths: list[float] = Field(..., alias="sub-paths")
    type: str
    x_values: list[float] = Field(..., alias="x-values")
    y_values: list[float] = Field(..., alias="y-values")


class VerticalLine(BaseModel):
    """Vertical line."""

    y0: int
    y1: int
    x: int


class HorizontalLine(BaseModel):
    """Horizontal line."""

    x0: int
    x1: int
    y: int


class Image(BaseModel):
    """Image."""

    box: BoundingBox
    height: float
    width: float


class FontRange(BaseModel):
    """Font range."""

    first: int
    second: int


class FontCmap(BaseModel):
    """Font cmap."""

    cmap: dict[str, str]
    name: str
    range: FontRange
    type: int


class FontMetrics(AliasModel):
    """Font metrics."""

    stem_h: float = Field(..., alias="StemH")
    stem_v: float = Field(..., alias="StemV")
    ascent: float
    average_width: float = Field(..., alias="average-width")
    bbox: BoundingBox
    cap_height: float
    default_width: float = Field(..., alias="default-width")
    descent: float
    file: str
    italic_angle: float = Field(..., alias="italic-angle")
    max_width: float = Field(..., alias="max-width")
    missing_width: float = Field(..., alias="missing-width")
    name: str
    named_widths: NamedWidths = Field(..., alias="named-widths")
    weight: str
    widths: dict[str, float]
    x_height: float


class FontInfo(AliasModel):
    """Font info."""

    font_cmap: FontCmap = Field(..., alias="font-cmap")
    font_differences: FontDifferences = Field(..., alias="font-differences")
    font_metrics: FontMetrics = Field(..., alias="font-metrics")
    name: str
    internal_name: str = Field(..., alias="name (internal)")
    subtype: str


class Page(AliasModel):
    """Page."""

    height: float
    width: float
    dimensions: PageDimensions
    cells: list[Cell]
    paths: list[Path]
    vertical_lines: Optional[list[VerticalLine]] = Field(..., alias="vertical-lines")
    horizontal_lines: Optional[list[HorizontalLine]] = Field(
        ..., alias="horizontal-lines"
    )
    ignored_cells: list[IgnoredCell] = Field(..., alias="ignored-cells")
    images: list[Image]
    fonts: dict[str, FontInfo]


class Histograms(AliasModel):
    """Histogram."""

    mean_char_height: dict[str, float] = Field(..., alias="mean-char-height")
    mean_char_width: dict[str, float] = Field(..., alias="mean-char-width")
    number_of_chars: dict[str, int] = Field(..., alias="number-of-chars")


class PdfInfo(BaseModel):
    """PDF info."""

    histograms: Histograms
    styles: list[str]


class RawPdf(BaseModel):
    """Raw PDF."""

    info: PdfInfo
    pages: list[Page]

```
</content>
</file_38>

<file_39>
<path>types/legacy_doc/document.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Models for the Docling Document data type."""

from datetime import datetime
from typing import Dict, Generic, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    NonNegativeInt,
    StrictStr,
    model_validator,
)
from tabulate import tabulate

from docling_core.search.mapping import es_field
from docling_core.types.base import (
    Acquisition,
    CollectionDocumentInfo,
    CollectionNameTypeT,
    DescriptionAdvancedT,
    DescriptionAnalyticsT,
    FileInfoObject,
    Identifier,
    IdentifierTypeT,
    LanguageT,
    Log,
)
from docling_core.types.legacy_doc.base import (
    BaseCell,
    BaseText,
    BitmapObject,
    Figure,
    PageDimensions,
    PageReference,
    Ref,
    S3Data,
    Table,
)
from docling_core.types.legacy_doc.tokens import DocumentToken
from docling_core.utils.alias import AliasModel


class CCSFileInfoDescription(BaseModel, extra="forbid"):
    """File info description."""

    author: Optional[list[StrictStr]] = None
    keywords: Optional[str] = None
    subject: Optional[str] = None
    title: Optional[StrictStr] = None
    creation_date: Optional[str] = None  # datetime


class CCSFileInfoObject(FileInfoObject, extra="forbid"):
    """File info object."""

    num_pages: Optional[int] = Field(default=None, alias="#-pages")

    collection_name: Optional[str] = Field(
        default=None,
        alias="collection-name",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    description: Optional[CCSFileInfoDescription] = Field(
        default=None, json_schema_extra=es_field(suppress=True)
    )
    page_hashes: Optional[list[PageReference]] = Field(
        default=None, alias="page-hashes"
    )


class Affiliation(BaseModel, extra="forbid"):
    """Affiliation."""

    name: str = Field(
        ...,
        json_schema_extra=es_field(
            fields={
                "lower": {
                    "normalizer": "lowercase_asciifolding",
                    "type": "keyword",
                    "ignore_above": 8191,
                },
                "keyword": {"type": "keyword", "ignore_above": 8191},
            },
        ),
    )
    id: Optional[str] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    source: Optional[str] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )


class Author(BaseModel, extra="forbid"):
    """Author."""

    name: str = Field(
        ...,
        json_schema_extra=es_field(
            type="text",
            fields={
                "lower": {
                    "normalizer": "lowercase_asciifolding",
                    "type": "keyword",
                    "ignore_above": 8191,
                },
                "keyword": {"type": "keyword", "ignore_above": 8191},
            },
        ),
    )
    id: Optional[str] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    source: Optional[str] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    affiliations: Optional[list[Affiliation]] = None


class Publication(BaseModel, Generic[IdentifierTypeT], extra="forbid"):
    """Publication details of a journal or venue."""

    identifiers: Optional[list[Identifier[IdentifierTypeT]]] = Field(
        default=None,
        description="Unique identifiers of a publication venue.",
    )
    name: StrictStr = Field(
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
        description="Name of the publication.",
    )
    alternate_names: Optional[list[StrictStr]] = Field(
        default=None,
        json_schema_extra=es_field(type="text"),
        title="Alternate Names",
        description="Other names or abbreviations of this publication.",
    )
    type: Optional[list[StrictStr]] = Field(
        default=None,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
        description="Type of publication (journal article, conference, review,...).",
    )
    pages: Optional[StrictStr] = Field(
        default=None,
        json_schema_extra=es_field(type="text"),
        description="Page range in the publication.",
    )
    issue: Optional[StrictStr] = Field(
        default=None,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
        description="Publication issue (issue number).",
    )
    volume: Optional[StrictStr] = Field(
        default=None,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
        description="Publication volume.",
    )
    url: Optional[AnyHttpUrl] = Field(
        default=None,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
        description="URL on the publication site.",
    )


class DescriptionLicense(BaseModel, extra="forbid"):
    """Licence in document description."""

    code: Optional[StrictStr] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    text: Optional[StrictStr] = None


class CCSDocumentDescription(
    AliasModel,
    Generic[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ],
):
    """Description in document."""

    title: Optional[StrictStr] = None
    abstract: Optional[list[StrictStr]] = None
    authors: Optional[list[Author]] = None
    affiliations: Optional[list[Affiliation]] = None
    subjects: Optional[list[str]] = Field(
        default=None,
        json_schema_extra=es_field(
            fields={"keyword": {"ignore_above": 8191, "type": "keyword"}}
        ),
    )
    keywords: Optional[list[str]] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    publication_date: Optional[datetime] = None
    languages: Optional[list[LanguageT]] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    license_: Optional[DescriptionLicense] = Field(default=None, alias="license")
    publishers: Optional[list[StrictStr]] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    url_refs: Optional[list[str]] = Field(
        default=None, json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )
    references: Optional[list[Identifier[IdentifierTypeT]]] = None
    publication: Optional[list[Publication]] = Field(
        default=None, description="List of publication journals or venues."
    )
    reference_count: Optional[NonNegativeInt] = Field(
        default=None,
        title="Reference Count",
        description="Total number of documents referenced by this document.",
        json_schema_extra=es_field(type="integer"),
    )
    citation_count: Optional[NonNegativeInt] = Field(
        default=None,
        title="Citation Count",
        description=(
            "Total number of citations that this document has received (number "
            "of documents in whose bibliography this document appears)."
        ),
        json_schema_extra=es_field(type="integer"),
    )
    citation_date: Optional[datetime] = Field(
        default=None,
        title="Citation Count Date",
        description="Last update date of the citation count.",
    )
    advanced: Optional[DescriptionAdvancedT] = None
    analytics: Optional[DescriptionAnalyticsT] = None
    logs: list[Log]
    collection: Optional[CollectionDocumentInfo[CollectionNameTypeT]] = Field(
        default=None, description="The collection information of this document."
    )
    acquisition: Optional[Acquisition] = Field(
        default=None,
        description=(
            "Information on how the document was obtained, for data governance"
            " purposes."
        ),
    )


class MinimalDocument(
    AliasModel,
    Generic[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ],
):
    """Minimal model for a document."""

    name: StrictStr = Field(alias="_name")
    obj_type: Optional[StrictStr] = Field("document", alias="type")
    description: CCSDocumentDescription[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ]
    file_info: FileInfoObject = Field(alias="file-info")
    main_text: Optional[list[Union[Ref, BaseText]]] = Field(
        default=None, alias="main-text"
    )
    figures: Optional[list[Figure]] = None
    tables: Optional[list[Table]] = None


class CCSDocument(
    MinimalDocument,
    Generic[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ],
):
    """Model for a CCS-generated document."""

    obj_type: Optional[StrictStr] = Field("pdf-document", alias="type")
    bitmaps: Optional[list[BitmapObject]] = None
    equations: Optional[list[BaseCell]] = None
    footnotes: Optional[list[BaseText]] = None
    file_info: CCSFileInfoObject = Field(alias="file-info")
    main_text: Optional[list[Union[Ref, BaseText]]] = Field(
        default=None,
        alias="main-text",
    )
    page_dimensions: Optional[list[PageDimensions]] = Field(
        default=None, alias="page-dimensions"
    )
    page_footers: Optional[list[BaseText]] = Field(default=None, alias="page-footers")
    page_headers: Optional[list[BaseText]] = Field(default=None, alias="page-headers")
    s3_data: Optional[S3Data] = Field(default=None, alias="_s3_data")

    @model_validator(mode="before")
    @classmethod
    def from_dict(cls, data):
        """Validates and fixes the input data."""
        if not isinstance(data, dict):
            return data
        description_collection = data["description"].get("collection")
        if not description_collection:
            data["description"].setdefault("collection", {})

        data["description"]["collection"].setdefault("type", "Document")
        logs = data["description"].get("logs")
        if not logs:
            data["description"].setdefault("logs", [])

        abstract = data["description"].get("abstract")
        if abstract is not None and not isinstance(abstract, list):
            if isinstance(abstract, str):
                data["description"]["abstract"] = [abstract]
            else:
                data["description"].pop("abstract")

        for key in ["affiliations", "authors"]:
            descr = data["description"].get(key)
            if descr is not None and not isinstance(descr, list):
                if isinstance(descr, dict):
                    data["description"][key] = [descr]
                else:
                    data["description"].pop(key)

        if data.get("main-text"):
            for item in data["main-text"]:
                if ref := item.pop("__ref", None):
                    item["$ref"] = ref

        return data


class ExportedCCSDocument(
    MinimalDocument,
    Generic[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ],
):
    """Document model for Docling."""

    obj_type: Optional[StrictStr] = Field(
        "pdf-document",
        alias="type",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    bitmaps: Optional[list[BitmapObject]] = None
    equations: Optional[list[BaseCell]] = None
    footnotes: Optional[list[BaseText]] = None
    description: CCSDocumentDescription[
        DescriptionAdvancedT,
        DescriptionAnalyticsT,
        IdentifierTypeT,
        LanguageT,
        CollectionNameTypeT,
    ]
    file_info: CCSFileInfoObject = Field(alias="file-info")
    main_text: Optional[list[Union[Ref, BaseText]]] = Field(
        default=None, alias="main-text"
    )
    page_dimensions: Optional[list[PageDimensions]] = Field(
        default=None, alias="page-dimensions"
    )
    page_footers: Optional[list[BaseText]] = Field(default=None, alias="page-footers")
    page_headers: Optional[list[BaseText]] = Field(default=None, alias="page-headers")
    s3_data: Optional[S3Data] = Field(default=None, alias="_s3_data")
    identifiers: Optional[list[Identifier[IdentifierTypeT]]] = None

    @model_validator(mode="before")
    @classmethod
    def from_dict(cls, data):
        """Fix ref in main-text."""
        if not isinstance(data, dict):
            return data
        if data.get("main-text"):
            for item in data["main-text"]:
                if ref := item.pop("__ref", None):
                    item["$ref"] = ref

        return data

    def _resolve_ref(self, item: Ref) -> Optional[Union[BaseCell, BaseText]]:
        """Return the resolved reference.

        Resolved the Ref object within the document.
        If the object is not found, None is returned.
        """
        result: Optional[Union[BaseCell, BaseText]] = None

        # NOTE: currently only resolves refs explicitely, such that we can make
        # assumptions on ref parts
        if item.obj_type == "table" and self.tables:
            parts = item.ref.split("/")
            result = self.tables[int(parts[2])]
        elif item.obj_type == "figure" and self.figures:
            parts = item.ref.split("/")
            result = self.figures[int(parts[2])]
        elif item.obj_type == "equation" and self.equations:
            parts = item.ref.split("/")
            result = self.equations[int(parts[2])]
        elif item.obj_type == "footnote" and self.footnotes:
            parts = item.ref.split("/")
            result = self.footnotes[int(parts[2])]

        return result

    def get_map_to_page_dimensions(self):
        """Get a map from page-index (start at 1) to page-dim [width, height]."""
        pagedims = {}

        if self.page_dimensions is not None:
            for _ in self.page_dimensions:
                pagedims[_.page] = [_.width, _.height]

        return pagedims

    def export_to_dict(self) -> Dict:
        """export_to_dict."""
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)

    def export_to_markdown(  # noqa: C901
        self,
        delim: str = "\n\n",
        main_text_start: int = 0,
        main_text_stop: Optional[int] = None,
        main_text_labels: list[str] = [
            "title",
            "subtitle-level-1",
            "paragraph",
            "caption",
            "table",
            "figure",
        ],
        strict_text: bool = False,
        image_placeholder: str = "<!-- image -->",
    ) -> str:
        r"""Serialize to Markdown.

        Operates on a slice of the document's main_text as defined through arguments
        main_text_start and main_text_stop; defaulting to the whole main_text.

        Args:
            delim (str, optional): Delimiter to use when concatenating the various
                Markdown parts. Defaults to "\n\n".
            main_text_start (int, optional): Main-text slicing start index (inclusive).
                Defaults to 0.
            main_text_end (Optional[int], optional): Main-text slicing stop index
                (exclusive). Defaults to None.
            main_text_labels (list[str], optional): The labels to include in the
                markdown.
            strict_text (bool, optional): if true, the output will be only plain text
                without any markdown styling. Defaults to False.
            image_placeholder (str, optional): the placeholder to include to position
                images in the markdown. Defaults to a markdown comment "<!-- image -->".

        Returns:
            str: The exported Markdown representation.
        """
        has_title = False
        prev_text = ""
        md_texts: list[str] = []

        if self.main_text is not None:
            # collect all captions embedded in table and figure objects
            # to avoid repeating them
            embedded_captions = set()
            for orig_item in self.main_text[main_text_start:main_text_stop]:
                item = (
                    self._resolve_ref(orig_item)
                    if isinstance(orig_item, Ref)
                    else orig_item
                )
                if item is None:
                    continue

                if (
                    isinstance(item, (Table, Figure))
                    and item.text
                    and item.obj_type in main_text_labels
                ):
                    embedded_captions.add(item.text)

            # serialize document to markdown
            for orig_item in self.main_text[main_text_start:main_text_stop]:
                markdown_text = ""

                item = (
                    self._resolve_ref(orig_item)
                    if isinstance(orig_item, Ref)
                    else orig_item
                )
                if item is None:
                    continue

                item_type = item.obj_type
                if isinstance(item, BaseText) and item_type in main_text_labels:
                    text = item.text

                    # skip captions of they are embedded in the actual
                    # floating object
                    if item_type == "caption" and text in embedded_captions:
                        continue

                    # ignore repeated text
                    if prev_text == text or text is None:
                        continue
                    else:
                        prev_text = text

                    # first title match
                    if item_type == "title" and not has_title:
                        if strict_text:
                            markdown_text = f"{text}"
                        else:
                            markdown_text = f"# {text}"
                        has_title = True

                    # secondary titles
                    elif item_type in {"title", "subtitle-level-1"} or (
                        has_title and item_type == "title"
                    ):
                        if strict_text:
                            markdown_text = f"{text}"
                        else:
                            markdown_text = f"## {text}"

                    # normal text
                    else:
                        markdown_text = text

                elif (
                    isinstance(item, Table)
                    and (item.data or item.text)
                    and item_type in main_text_labels
                ):

                    md_table = ""
                    table = []
                    if item.data is not None:
                        for row in item.data:
                            tmp = []
                            for col in row:
                                tmp.append(col.text)
                            table.append(tmp)

                    if len(table) > 1 and len(table[0]) > 0:
                        try:
                            md_table = tabulate(
                                table[1:], headers=table[0], tablefmt="github"
                            )
                        except ValueError:
                            md_table = tabulate(
                                table[1:],
                                headers=table[0],
                                tablefmt="github",
                                disable_numparse=True,
                            )

                    markdown_text = ""
                    if item.text:
                        markdown_text = item.text
                    if not strict_text:
                        markdown_text += (
                            "\n\n" if len(markdown_text) > 0 else ""
                        ) + md_table

                elif isinstance(item, Figure) and item_type in main_text_labels:

                    markdown_text = ""
                    if item.text:
                        markdown_text = item.text
                    if not strict_text:
                        markdown_text += (
                            "\n" if len(markdown_text) > 0 else ""
                        ) + image_placeholder

                if markdown_text:
                    md_texts.append(markdown_text)

        result = delim.join(md_texts)
        return result

    def export_to_document_tokens(
        self,
        delim: str = "\n\n",
        main_text_start: int = 0,
        main_text_stop: Optional[int] = None,
        main_text_labels: list[str] = [
            "title",
            "subtitle-level-1",
            "paragraph",
            "caption",
            "table",
            "figure",
        ],
        xsize: int = 100,
        ysize: int = 100,
        add_location: bool = True,
        add_content: bool = True,
        add_page_index: bool = True,
        # table specific flags
        add_table_cell_location: bool = False,
        add_table_cell_label: bool = True,
        add_table_cell_text: bool = True,
    ) -> str:
        r"""Exports the document content to an DocumentToken format.

        Operates on a slice of the document's main_text as defined through arguments
        main_text_start and main_text_stop; defaulting to the whole main_text.

        Returns:
            str: The content of the document formatted as a DocTags string.
        """
        new_line = ""
        if delim:
            new_line = "\n"

        doctags = f"{DocumentToken.BEG_DOCUMENT.value}{new_line}"

        # pagedims = self.get_map_to_page_dimensions()

        if self.main_text is not None:
            for orig_item in self.main_text[main_text_start:main_text_stop]:

                item = (
                    self._resolve_ref(orig_item)
                    if isinstance(orig_item, Ref)
                    else orig_item
                )

                if item is None:
                    continue

                prov = item.prov

                page_i = -1
                page_w = 0.0
                page_h = 0.0

                if (
                    add_location
                    and self.page_dimensions is not None
                    and prov is not None
                    and len(prov) > 0
                ):

                    page_i = prov[0].page
                    page_dim = self.page_dimensions[page_i - 1]

                    page_w = float(page_dim.width)
                    page_h = float(page_dim.height)

                item_type = item.obj_type
                if isinstance(item, BaseText) and (item_type in main_text_labels):

                    doctags += item.export_to_document_tokens(
                        new_line=new_line,
                        page_w=page_w,
                        page_h=page_h,
                        xsize=xsize,
                        ysize=ysize,
                        add_location=add_location,
                        add_content=add_content,
                        add_page_index=add_page_index,
                    )

                elif isinstance(item, Table) and (item_type in main_text_labels):

                    doctags += item.export_to_document_tokens(
                        new_line=new_line,
                        page_w=page_w,
                        page_h=page_h,
                        xsize=xsize,
                        ysize=ysize,
                        add_caption=True,
                        add_location=add_location,
                        add_content=add_content,
                        add_cell_location=add_table_cell_location,
                        add_cell_label=add_table_cell_label,
                        add_cell_text=add_table_cell_text,
                        add_page_index=add_page_index,
                    )

                elif isinstance(item, Figure) and (item_type in main_text_labels):

                    doctags += item.export_to_document_tokens(
                        new_line=new_line,
                        page_w=page_w,
                        page_h=page_h,
                        xsize=xsize,
                        ysize=ysize,
                        add_caption=True,
                        add_location=add_location,
                        add_content=add_content,
                        add_page_index=add_page_index,
                    )

        doctags += DocumentToken.END_DOCUMENT.value

        return doctags

```
</content>
</file_39>

<file_40>
<path>types/legacy_doc/tokens.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Tokens used in the docling document model."""

from enum import Enum
from typing import Annotated, Tuple

from pydantic import Field


class TableToken(Enum):
    """Class to represent an LLM friendly representation of a Table."""

    CELL_LABEL_COLUMN_HEADER = "<column_header>"
    CELL_LABEL_ROW_HEADER = "<row_header>"
    CELL_LABEL_SECTION_HEADERE = "<section_header>"
    CELL_LABEL_DATA = "<data>"

    OTSL_ECEL = "<ecel>"  # empty cell
    OTSL_FCEL = "<fcel>"  # cell with content
    OTSL_LCEL = "<lcel>"  # left looking cell,
    OTSL_UCEL = "<ucel>"  # up looking cell,
    OTSL_XCEL = "<xcel>"  # 2d extension cell (cross cell),
    OTSL_NL = "<nl>"  # new line,
    OTSL_CHED = "<ched>"  # - column header cell,
    OTSL_RHED = "<rhed>"  # - row header cell,
    OTSL_SROW = "<srow>"  # - section row cell

    @classmethod
    def get_special_tokens(cls):
        """Function to get all special document tokens."""
        special_tokens = [token.value for token in cls]
        return special_tokens

    @staticmethod
    def is_known_token(label):
        """Function to check if label is in tokens."""
        return label in TableToken.get_special_tokens()


class DocumentToken(Enum):
    """Class to represent an LLM friendly representation of a Document."""

    BEG_DOCUMENT = "<document>"
    END_DOCUMENT = "</document>"

    BEG_TITLE = "<title>"
    END_TITLE = "</title>"

    BEG_ABSTRACT = "<abstract>"
    END_ABSTRACT = "</abstract>"

    BEG_DOI = "<doi>"
    END_DOI = "</doi>"
    BEG_DATE = "<date>"
    END_DATE = "</date>"

    BEG_AUTHORS = "<authors>"
    END_AUTHORS = "</authors>"
    BEG_AUTHOR = "<author>"
    END_AUTHOR = "</author>"

    BEG_AFFILIATIONS = "<affiliations>"
    END_AFFILIATIONS = "</affiliations>"
    BEG_AFFILIATION = "<affiliation>"
    END_AFFILIATION = "</affiliation>"

    BEG_HEADER = "<section-header>"
    END_HEADER = "</section-header>"
    BEG_TEXT = "<text>"
    END_TEXT = "</text>"
    BEG_PARAGRAPH = "<paragraph>"
    END_PARAGRAPH = "</paragraph>"
    BEG_TABLE = "<table>"
    END_TABLE = "</table>"
    BEG_FIGURE = "<figure>"
    END_FIGURE = "</figure>"
    BEG_CAPTION = "<caption>"
    END_CAPTION = "</caption>"
    BEG_EQUATION = "<equation>"
    END_EQUATION = "</equation>"
    BEG_LIST = "<list>"
    END_LIST = "</list>"
    BEG_LISTITEM = "<list-item>"
    END_LISTITEM = "</list-item>"

    BEG_LOCATION = "<location>"
    END_LOCATION = "</location>"
    BEG_GROUP = "<group>"
    END_GROUP = "</group>"

    @classmethod
    def get_special_tokens(
        cls,
        max_rows: int = 100,
        max_cols: int = 100,
        max_pages: int = 1000,
        page_dimension: Tuple[int, int] = (100, 100),
    ):
        """Function to get all special document tokens."""
        special_tokens = [token.value for token in cls]

        # Adding dynamically generated row and col tokens
        for i in range(0, max_rows + 1):
            special_tokens += [f"<row_{i}>", f"</row_{i}>"]

        for i in range(0, max_cols + 1):
            special_tokens += [f"<col_{i}>", f"</col_{i}>"]

        for i in range(6):
            special_tokens += [f"<section-header-{i}>", f"</section-header-{i}>"]

        # FIXME: this is synonym of section header
        for i in range(6):
            special_tokens += [f"<subtitle-level-{i}>", f"</subtitle-level-{i}>"]

        # Adding dynamically generated page-tokens
        for i in range(0, max_pages + 1):
            special_tokens.append(f"<page_{i}>")
            special_tokens.append(f"</page_{i}>")

        # Adding dynamically generated location-tokens
        for i in range(0, max(page_dimension[0] + 1, page_dimension[1] + 1)):
            special_tokens.append(f"<loc_{i}>")

        return special_tokens

    @staticmethod
    def is_known_token(label):
        """Function to check if label is in tokens."""
        return label in DocumentToken.get_special_tokens()

    @staticmethod
    def get_row_token(row: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<row_{row}>"
        else:
            return f"</row_{row}>"

    @staticmethod
    def get_col_token(col: int, beg=bool) -> str:
        """Function to get page tokens."""
        if beg:
            return f"<col_{col}>"
        else:
            return f"</col_{col}>"

    @staticmethod
    def get_page_token(page: int):
        """Function to get page tokens."""
        return f"<page_{page}>"

    @staticmethod
    def get_location_token(val: float, rnorm: int = 100):
        """Function to get location tokens."""
        val_ = round(rnorm * val)

        if val_ < 0:
            return "<loc_0>"

        if val_ > rnorm:
            return f"<loc_{rnorm}>"

        return f"<loc_{val_}>"

    @staticmethod
    def get_location(
        # bbox: Tuple[float, float, float, float],
        bbox: Annotated[list[float], Field(min_length=4, max_length=4)],
        page_w: float,
        page_h: float,
        xsize: int = 100,
        ysize: int = 100,
        page_i: int = -1,
    ):
        """Get the location string give bbox and page-dim."""
        assert bbox[0] <= bbox[2], f"bbox[0]<=bbox[2] => {bbox[0]}<={bbox[2]}"
        assert bbox[1] <= bbox[3], f"bbox[1]<=bbox[3] => {bbox[1]}<={bbox[3]}"

        x0 = bbox[0] / page_w
        y0 = bbox[1] / page_h
        x1 = bbox[2] / page_w
        y1 = bbox[3] / page_h

        page_tok = ""
        if page_i != -1:
            page_tok = DocumentToken.get_page_token(page=page_i)

        x0_tok = DocumentToken.get_location_token(val=min(x0, x1), rnorm=xsize)
        y0_tok = DocumentToken.get_location_token(val=min(y0, y1), rnorm=ysize)
        x1_tok = DocumentToken.get_location_token(val=max(x0, x1), rnorm=xsize)
        y1_tok = DocumentToken.get_location_token(val=max(y0, y1), rnorm=ysize)

        loc_str = f"{DocumentToken.BEG_LOCATION.value}"
        loc_str += f"{page_tok}{x0_tok}{y0_tok}{x1_tok}{y1_tok}"
        loc_str += f"{DocumentToken.END_LOCATION.value}"

        return loc_str

```
</content>
</file_40>

<file_41>
<path>types/nlp/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models defining NLP artifacts."""

```
</content>
</file_41>

<file_42>
<path>types/nlp/qa.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model for Q&A pairs."""
from typing import Generic, Optional

from pydantic import BaseModel, Field, StrictBool, StrictStr

from docling_core.search.mapping import es_field
from docling_core.types.base import DescriptionAdvancedT, StrictDateTime, UniqueList
from docling_core.types.nlp.qa_labels import QALabelling


class QAPair(BaseModel, Generic[DescriptionAdvancedT]):
    """A representation of a question-answering (QA) pair."""

    context: StrictStr = Field(
        description=(
            "A single string containing the context of the question enabling the"
            " presentation of the answer."
        )
    )
    question: StrictStr = Field(description="A question on the given context.")
    answer: StrictStr = Field(
        description="The answer to the question from the context."
    )
    short_answer: Optional[StrictStr] = Field(
        default=None, description="Alternative and concise answer."
    )
    retrieved_context: Optional[StrictBool] = Field(
        default=False,
        description="Whether the context was retrieved from the question.",
    )
    generated_question: Optional[StrictBool] = Field(
        default=False, description="Whether the question was generated by an AI model."
    )
    generated_answer: Optional[StrictBool] = Field(
        default=False, description="Whether the answer was generated by an AI model."
    )
    created: StrictDateTime = Field(
        description="Datetime when the QA pair was created ."
    )
    user: Optional[StrictStr] = Field(
        default=None,
        description=(
            "Unique identifier of the user that created or curated this QA pair."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    model: Optional[StrictStr] = Field(
        default=None,
        description="Unique identifier of the model used to generate this QA pair.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    paths: UniqueList[StrictStr] = Field(
        description=(
            "One or more references to a document that identify the provenance of the"
            " QA pair context."
        ),
        examples=[
            "badce7c84d0ba7ba0fb5e94492b0d91e2506a7cb48e4524ad572c546a35f768e#/"
            "main-text/4"
        ],
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    advanced: Optional[DescriptionAdvancedT] = Field(
        default=None,
        description="Document metadata to provide more details on the context.",
    )
    labels: Optional[QALabelling] = Field(
        default=None, description="QApair labelling axes."
    )

```
</content>
</file_42>

<file_43>
<path>types/nlp/qa_labels.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define models for labeling Q&A pairs."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

from docling_core.search.mapping import es_field

QAScopeLabel = Literal["corpus", "document", "out_of_scope"]
QAAlignmentLabel = Literal["aligned", "tangential", "misaligned"]
QACorrectnessLabel = Literal["entailed", "not_entailed"]
QACompletenessLabel = Literal["complete", "incomplete"]
QAInformationLabel = Literal[
    "fact_single",
    "fact_multi",
    "summary",
    "reasoning",
    "choice",
    "procedure",
    "opinion",
    "feedback",
]


class QALabelling(BaseModel, extra="forbid"):
    """Subclass to classify QA pair."""

    scope: Optional[QAScopeLabel] = Field(
        default=None,
        description="""Enumeration of QA scope types based on question only.
            - Corpus: question is asked on the entire corpus
                > Example: "What is the operating temperature of device X?"
            - Document: need to know the precise document before answering the question
                > Example: "What is its operating temperature?"
            - Out of scope: question is out of scope for the system
                > Example: "What is the volume of moon?" """,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    alignment: Optional[QAAlignmentLabel] = Field(
        default=None,
        description="""Enumeration of QA alignment types based on question-context pair.
            Given the following context: "Device X works between 2 and 20 degrees C"
            A question can be:
            - Aligned: the context has information that the question seeks
                > Example: "Can device X work at 10 degrees?"
            - Tangential: the context does not have the information directly
                            but the question is related to the context
                > Example: "Is device X safe?"
            - Misaligned: the question has nothing to do with the context
                > Example: "Why is device Y not working?" """,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    correctness: Optional[QACorrectnessLabel] = Field(
        default=None,
        description="""Enumeration of QA correctness types based on
            question-answer-context triplet.
            Given the following context: "Device X works between 2 and 20 degrees C"
            and the following question: "Can device X work at 10 degrees?"
            An answer can be:
            - Entailed: answer is entailed to both question and context
                > Example: "Yes, as it works between 2 and 20 degrees."
            - Not entailed: answer is not entailed to either question or context
                > Example: "Yes, device X can work at any temperature." """,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    completeness: Optional[QACompletenessLabel] = Field(
        default=None,
        description="""Enumeration of QA completeness types based on
            question-answer-context triplet.
            Given the following context: "A, B, C, and D met on Friday."
            and the following question: "Who was in the meeting?"
            An answer can be:
            - Complete: Answer contains all relevant information requested by a
                question that can be extracted from the associated ground-truth context
                > Example: "A, B, C, and D."
            - Incomplete: Answer does not contain the entire relevant information in
                the context
                > Example: "B and D" """,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    information: Optional[QAInformationLabel] = Field(
        default=None,
        description="""Enumeration of QA nature of information types based on question
            only.
            - Single fact: Answer should be a short phrase containing a numerical or
                textual fact
                > Example: "What is the boiling point of water?"
            - Multiple fact: Answer is a list of two or more facts (not necessarily in
                list format)
                > Example: "What is the minimum and maximum age of people working at
                IBM?"
            - Summary: Answer summarises a part of the context without any modification.
                > Example: "Briefly describe the temperature requirements for this
                device in a table"
            - Reasoning: Answer requires inferring information from the context that
                can be inferred but is not explicitly stated (e.g., operating
                temperature is given and the question asks if the device can operate at
                a particular temperature)
                > Example: "Why can I not operate this device under water?"
            - Multiple choice: Question provides a few choices implicitly or explicitly
                and the answer must be one of these choices. Includes yes/no questions
                > Example: "If I operate this device at 10 degrees, will it be in the
                green range or red?"
            - Procedure: Answer outlines the steps to do something. As opposed to a
                summary, the order of information matters here
                > Example: "How can I access part X of device Y?"
            - Opinion: The context provides several viewpoints and the question
                requests the opinion of the chatbot
                > Example: "Is device X better than Y?"
            - Feedback: The question is actually a feedback on the preceding generation
                within a session
                > Example: "Your summary was inadequate" """,
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

```
</content>
</file_43>

<file_44>
<path>types/rec/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for models defined by the Record type."""

```
</content>
</file_44>

<file_45>
<path>types/rec/attribute.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model Attribute."""
from typing import Generic, Optional

from pydantic import Field
from typing_extensions import Annotated

from docling_core.search.mapping import es_field
from docling_core.types.base import (
    IdentifierTypeT,
    PredicateKeyNameT,
    PredicateKeyTypeT,
    PredicateValueTypeT,
    ProvenanceTypeT,
)
from docling_core.types.rec.base import ProvenanceItem
from docling_core.types.rec.predicate import Predicate
from docling_core.utils.alias import AliasModel


class Attribute(
    AliasModel,
    Generic[
        IdentifierTypeT,
        PredicateValueTypeT,
        PredicateKeyNameT,
        PredicateKeyTypeT,
        ProvenanceTypeT,
    ],
    extra="forbid",
):
    """Attribute model that describes a list of characteristics."""

    conf: Annotated[float, Field(strict=True, ge=0.0, le=1.0, allow_inf_nan=False)] = (
        Field(
            ...,
            title="Confidence",
            description="The confidence level of this attribute characteristics.",
            json_schema_extra=es_field(type="float"),
        )
    )

    prov: Optional[list[ProvenanceItem[IdentifierTypeT, ProvenanceTypeT]]] = Field(
        default=None,
        title="Provenance",
        description="The sources of this attribute characteristics.",
    )

    predicates: list[
        Predicate[PredicateValueTypeT, PredicateKeyNameT, PredicateKeyTypeT]
    ] = Field(..., description="A list of characteristics (type, value, and name).")

```
</content>
</file_45>

<file_46>
<path>types/rec/base.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the base models for the Record type."""
from typing import Generic, List, Optional

from pydantic import Field, StrictInt, StrictStr
from typing_extensions import Annotated

from docling_core.search.mapping import es_field
from docling_core.types.base import Identifier, IdentifierTypeT, ProvenanceTypeT
from docling_core.utils.alias import AliasModel


class ProvenanceItem(
    AliasModel, Generic[IdentifierTypeT, ProvenanceTypeT], extra="forbid"
):
    """A representation of an object provenance."""

    type_: Optional[ProvenanceTypeT] = Field(
        default=None,
        alias="type",
        title="The provenance type",
        description=(
            "Any string representing the type of provenance, e.g. `sentence`, "
            "`table`, or `doi`."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

    text: Optional[StrictStr] = Field(
        default=None,
        title="Evidence of the provenance",
        description=(
            "A text representing the evidence of the provenance, e.g. the sentence "
            "text or the content of a table cell"
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

    reference: Optional[Identifier[IdentifierTypeT]] = Field(
        default=None,
        title="Reference to the provenance object",
        description=(
            "Reference to another object, e.g. record, statement, URL, or any other "
            "object that identifies the provenance"
        ),
    )

    path: Optional[StrictStr] = Field(
        default=None,
        title="The location of the provenance within the referenced object",
        description=(
            "A path that locates the evidence within the provenance object identified "
            "by the `reference` field using a JSON pointer notation, e.g., "
            "`#/main-text/5` to locate the `main-text` paragraph at index 5"
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

    span: Optional[Annotated[List[StrictInt], Field(min_length=2, max_length=2)]] = (
        Field(
            default=None,
            title="The location of the item in the text/table",
            description=(
                "location of the item in the text/table referenced by the `path`,"
                " e.g., `[34, 67]`"
            ),
        )
    )


class Provenance(AliasModel, Generic[IdentifierTypeT, ProvenanceTypeT]):
    """A representation of an evidence, as a list of provenance objects."""

    conf: Annotated[float, Field(strict=True, ge=0.0, le=1.0)] = Field(
        ...,
        title="The confidence of the evidence",
        description=(
            "This value represents a score to the data item. Items originating from "
            " databases will typically have a score 1.0, while items resulting from "
            " an NLP model may have a value between 0.0 and 1.0."
        ),
        json_schema_extra=es_field(type="float"),
    )
    prov: list[ProvenanceItem[IdentifierTypeT, ProvenanceTypeT]] = Field(
        title="Provenance", description="A list of provenance items."
    )

```
</content>
</file_46>

<file_47>
<path>types/rec/predicate.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model Predicate."""
from datetime import datetime
from typing import Annotated, Generic, Optional

from pydantic import (
    BaseModel,
    Field,
    StrictBool,
    StrictFloat,
    StrictStr,
    field_validator,
)

from docling_core.search.mapping import es_field
from docling_core.types.base import (
    Coordinates,
    PredicateKeyNameT,
    PredicateKeyTypeT,
    PredicateValueTypeT,
)
from docling_core.utils.alias import AliasModel


class NumericalValue(BaseModel, extra="forbid"):
    """Model for numerical values."""

    min: StrictFloat = Field(..., json_schema_extra=es_field(type="float"))
    max: StrictFloat = Field(..., json_schema_extra=es_field(type="float"))
    val: StrictFloat = Field(..., json_schema_extra=es_field(type="float"))
    err: StrictFloat = Field(..., json_schema_extra=es_field(type="float"))
    unit: StrictStr = Field(
        ..., json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )


class NominalValue(BaseModel, extra="forbid"):
    """Model for nominal (categorical) values."""

    value: StrictStr = Field(
        ..., json_schema_extra=es_field(type="keyword", ignore_above=8191)
    )


class TextValue(BaseModel, extra="forbid"):
    """Model for textual values."""

    value: StrictStr = Field(..., json_schema_extra=es_field(type="text"))


class BooleanValue(BaseModel, extra="forbid"):
    """Model for boolean values."""

    value: StrictBool = Field(..., json_schema_extra=es_field(type="boolean"))


class DatetimeValue(BaseModel, extra="forbid"):
    """Model for datetime values."""

    value: datetime


class GeopointValue(BaseModel, extra="forbid"):
    """A representation of a geopoint (longitude and latitude coordinates)."""

    value: Coordinates
    conf: Optional[Annotated[float, Field(strict=True, ge=0.0, le=1.0)]] = Field(
        default=None, json_schema_extra=es_field(type="float")
    )

    @field_validator("value")
    @classmethod
    def validate_coordinates(cls, v):
        """Validate the reference field for indexes of type Document."""
        if abs(v[0]) > 180:
            raise ValueError("invalid longitude")
        if abs(v[1]) > 90:
            raise ValueError("invalid latitude")
        return v


class PredicateKey(
    AliasModel, Generic[PredicateKeyNameT, PredicateKeyTypeT], extra="forbid"
):
    """Model for the key (unique identifier) of a predicate."""

    name: PredicateKeyNameT = Field(
        description="Name of the predicate key.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    type_: PredicateKeyTypeT = Field(
        alias="type",
        title="Type",
        description="Type of predicate key.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )


class PredicateValue(AliasModel, Generic[PredicateValueTypeT], extra="forbid"):
    """Model for the value of a predicate."""

    name: StrictStr = Field(
        description="Name of the predicate value (actual value).",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    type_: PredicateValueTypeT = Field(
        alias="type",
        description="Type of predicate value.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )


class Predicate(
    AliasModel,
    Generic[PredicateValueTypeT, PredicateKeyNameT, PredicateKeyTypeT],
    extra="forbid",
):
    """Model for a predicate."""

    key: PredicateKey[PredicateKeyNameT, PredicateKeyTypeT]
    value: PredicateValue[PredicateValueTypeT]

    numerical_value: Optional[NumericalValue] = None
    numerical_value_si: Optional[NumericalValue] = None
    nominal_value: Optional[NominalValue] = None
    text_value: Optional[TextValue] = None
    boolean_value: Optional[BooleanValue] = None
    datetime_value: Optional[DatetimeValue] = None
    geopoint_value: Optional[GeopointValue] = None

```
</content>
</file_47>

<file_48>
<path>types/rec/record.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model Record."""
from typing import Generic, Optional

from pydantic import BaseModel, Field, StrictStr

from docling_core.search.mapping import es_field
from docling_core.types.base import (
    Acquisition,
    CollectionNameTypeT,
    CollectionRecordInfo,
    FileInfoObject,
    Identifier,
    IdentifierTypeT,
    Log,
    PredicateKeyNameT,
    PredicateKeyTypeT,
    PredicateValueTypeT,
    StrictDateTime,
    SubjectNameTypeT,
    SubjectTypeT,
)
from docling_core.types.rec.attribute import Attribute
from docling_core.types.rec.base import Provenance, ProvenanceTypeT
from docling_core.types.rec.subject import Subject


class RecordDescription(BaseModel, Generic[CollectionNameTypeT]):
    """Additional record metadata, including optional collection-specific fields."""

    logs: list[Log] = Field(
        description="Logs that describe the ETL tasks applied to this record."
    )
    publication_date: Optional[StrictDateTime] = Field(
        default=None,
        title="Publication date",
        description=(
            "The date that best represents the last publication time of a record."
        ),
    )
    collection: Optional[CollectionRecordInfo[CollectionNameTypeT]] = Field(
        default=None, description="The collection information of this record."
    )
    acquisition: Optional[Acquisition] = Field(
        default=None,
        description=(
            "Information on how the document was obtained, for data governance"
            " purposes."
        ),
    )


class Record(
    Provenance,
    Generic[
        IdentifierTypeT,
        PredicateValueTypeT,
        PredicateKeyNameT,
        PredicateKeyTypeT,
        ProvenanceTypeT,
        SubjectTypeT,
        SubjectNameTypeT,
        CollectionNameTypeT,
    ],
):
    """A representation of a structured record in an database."""

    file_info: FileInfoObject = Field(alias="file-info")
    description: RecordDescription
    subject: Subject[IdentifierTypeT, SubjectTypeT, SubjectNameTypeT]
    attributes: Optional[
        list[
            Attribute[
                IdentifierTypeT,
                PredicateValueTypeT,
                PredicateKeyNameT,
                PredicateKeyTypeT,
                ProvenanceTypeT,
            ]
        ]
    ] = None
    name: Optional[StrictStr] = Field(
        default=None,
        description="A short description or summary of the record.",
        alias="_name",
        json_schema_extra=es_field(type="text"),
    )
    identifiers: Optional[list[Identifier[IdentifierTypeT]]] = Field(
        default=None,
        description="A list of unique identifiers of this record in a database.",
    )

```
</content>
</file_48>

<file_49>
<path>types/rec/statement.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model Statement."""
from enum import Enum
from typing import Generic

from pydantic import Field

from docling_core.types.base import (
    IdentifierTypeT,
    PredicateKeyNameT,
    PredicateKeyTypeT,
    PredicateValueTypeT,
    ProvenanceTypeT,
    SubjectNameTypeT,
    SubjectTypeT,
)
from docling_core.types.rec.attribute import Attribute
from docling_core.types.rec.subject import Subject


class StatementToken(Enum):
    """Class to represent an LLM friendly representation of statements."""

    BEG_STATEMENTS = "<statements>"
    END_STATEMENTS = "</statements>"

    BEG_STATEMENT = "<statement>"
    END_STATEMENT = "</statement>"

    BEG_PROV = "<prov>"
    END_PROV = "</prov>"

    BEG_SUBJECT = "<subject>"
    END_SUBJECT = "</subject>"

    BEG_PREDICATE = "<predicate>"
    END_PREDICATE = "</predicate>"

    BEG_PROPERTY = "<property>"
    END_PROPERTY = "</property>"

    BEG_VALUE = "<value>"
    END_VALUE = "</value>"

    BEG_UNIT = "<unit>"
    END_UNIT = "</unit>"

    @classmethod
    def get_special_tokens(cls):
        """Function to get all special statements tokens."""
        return [token.value for token in cls]


class Statement(
    Attribute,
    Generic[
        IdentifierTypeT,
        PredicateValueTypeT,
        PredicateKeyNameT,
        PredicateKeyTypeT,
        ProvenanceTypeT,
        SubjectTypeT,
        SubjectNameTypeT,
    ],
    extra="allow",
):
    """A representation of a statement on a subject."""

    subject: Subject[IdentifierTypeT, SubjectTypeT, SubjectNameTypeT] = Field(
        description="The subject (entity) of this statement."
    )

```
</content>
</file_49>

<file_50>
<path>types/rec/subject.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define the model Subject."""
from typing import Generic, Optional

from pydantic import Field, StrictStr

from docling_core.search.mapping import es_field
from docling_core.types.base import (
    Identifier,
    IdentifierTypeT,
    SubjectNameTypeT,
    SubjectTypeT,
)
from docling_core.types.legacy_doc.base import S3Reference
from docling_core.utils.alias import AliasModel


class SubjectNameIdentifier(Identifier[SubjectNameTypeT], Generic[SubjectNameTypeT]):
    """Identifier of subject names.""" ""


class Subject(
    AliasModel,
    Generic[IdentifierTypeT, SubjectTypeT, SubjectNameTypeT],
    extra="forbid",
):
    """A representation of a subject."""

    display_name: StrictStr = Field(
        title="Display Name",
        description=(
            "Name of the subject in natural language. It can be used for end-user "
            "applications to display a human-readable name. For instance, `B(2) Mg(1)` "
            "for `MgB2` or `International Business Machines` for `IBM`"
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    display_image: Optional[S3Reference] = Field(
        default=None,
        title="Display Image",
        description=(
            "Image representing the subject. It can be used for end-user applications."
            "For example, the chemical structure drawing of a compound "
            "or the eight bar IBM logo for IBM."
        ),
        json_schema_extra=es_field(suppress=True),
    )
    type_: SubjectTypeT = Field(
        alias="type",
        description=(
            "Main subject type. For instance, `material`, `material-class`, "
            "`material-device`, `company`, or `person`."
        ),
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )
    names: list[SubjectNameIdentifier[SubjectNameTypeT]] = Field(
        description=(
            "List of given names for this subject. They may not be unique across "
            "different subjects."
        )
    )
    identifiers: Optional[list[Identifier[IdentifierTypeT]]] = Field(
        default=None,
        description=(
            "List of unique identifiers in database. For instance, the `PubChem ID` "
            "of a record in the PubChem database."
        ),
    )
    labels: Optional[list[StrictStr]] = Field(
        default=None,
        description="List of labels or categories for this subject.",
        json_schema_extra=es_field(type="keyword", ignore_above=8191),
    )

```
</content>
</file_50>

<file_51>
<path>utils/__init__.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Package for modules to support data models."""

```
</content>
</file_51>

<file_52>
<path>utils/alias.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Define utility models and types related to field aliases."""
from pydantic import BaseModel, ConfigDict


class AliasModel(BaseModel):
    """Model for alias fields to ensure instantiation and serialization by alias."""

    model_config = ConfigDict(populate_by_name=True)

    def model_dump(self, **kwargs) -> dict:
        """Generate a dictionary representation of the model using field aliases."""
        if "by_alias" not in kwargs:
            kwargs = {**kwargs, "by_alias": True}

        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs) -> str:
        """Generate a JSON representation of the model using field aliases."""
        if "by_alias" not in kwargs:
            kwargs = {**kwargs, "by_alias": True}

        return super().model_dump_json(**kwargs)

```
</content>
</file_52>

<file_53>
<path>utils/file.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""File-related utilities."""

import importlib
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from pydantic import AnyHttpUrl, TypeAdapter, ValidationError
from typing_extensions import deprecated

from docling_core.types.doc.utils import relative_path  # noqa
from docling_core.types.io import DocumentStream


def resolve_remote_filename(
    http_url: AnyHttpUrl,
    response_headers: Dict[str, str],
    fallback_filename="file",
) -> str:
    """Resolves the filename from a remote url and its response headers.

    Args:
        source AnyHttpUrl: The source http url.
        response_headers Dict: Headers received while fetching the remote file.
        fallback_filename str: Filename to use in case none can be determined.

    Returns:
        str: The actual filename of the remote url.
    """
    fname = None
    # try to get filename from response header
    if cont_disp := response_headers.get("Content-Disposition"):
        for par in cont_disp.strip().split(";"):
            # currently only handling directive "filename" (not "*filename")
            if (split := par.split("=")) and split[0].strip() == "filename":
                fname = "=".join(split[1:]).strip().strip("'\"") or None
                break
    # otherwise, use name from URL:
    if fname is None:
        fname = Path(http_url.path or "").name or fallback_filename

    return fname


def resolve_source_to_stream(
    source: Union[Path, AnyHttpUrl, str], headers: Optional[Dict[str, str]] = None
) -> DocumentStream:
    """Resolves the source (URL, path) of a file to a binary stream.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.
        headers (Dict | None): Optional set of headers to use for fetching
            the remote URL.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        DocumentStream: The resolved file loaded as a stream.
    """
    try:
        http_url: AnyHttpUrl = TypeAdapter(AnyHttpUrl).validate_python(source)

        # make all header keys lower case
        _headers = headers or {}
        req_headers = {k.lower(): v for k, v in _headers.items()}
        # add user-agent is not set
        if "user-agent" not in req_headers:
            agent_name = f"docling-core/{importlib.metadata.version('docling-core')}"
            req_headers["user-agent"] = agent_name

        # fetch the page
        res = requests.get(http_url, stream=True, headers=req_headers)
        res.raise_for_status()
        fname = resolve_remote_filename(http_url=http_url, response_headers=res.headers)

        stream = BytesIO(res.content)
        doc_stream = DocumentStream(name=fname, stream=stream)
    except ValidationError:
        try:
            local_path = TypeAdapter(Path).validate_python(source)
            stream = BytesIO(local_path.read_bytes())
            doc_stream = DocumentStream(name=local_path.name, stream=stream)
        except ValidationError:
            raise ValueError(f"Unexpected source type encountered: {type(source)}")
    return doc_stream


def _resolve_source_to_path(
    source: Union[Path, AnyHttpUrl, str],
    headers: Optional[Dict[str, str]] = None,
    workdir: Optional[Path] = None,
) -> Path:
    doc_stream = resolve_source_to_stream(source=source, headers=headers)

    # use a temporary directory if not specified
    if workdir is None:
        workdir = Path(tempfile.mkdtemp())

    # create the parent workdir if it doesn't exist
    workdir.mkdir(exist_ok=True, parents=True)

    # save result to a local file
    local_path = workdir / doc_stream.name
    with local_path.open("wb") as f:
        f.write(doc_stream.stream.read())

    return local_path


def resolve_source_to_path(
    source: Union[Path, AnyHttpUrl, str],
    headers: Optional[Dict[str, str]] = None,
    workdir: Optional[Path] = None,
) -> Path:
    """Resolves the source (URL, path) of a file to a local file path.

    If a URL is provided, the content is first downloaded to a local file, located in
      the provided workdir or in a temporary directory if no workdir provided.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.
        headers (Dict | None): Optional set of headers to use for fetching
            the remote URL.
        workdir (Path | None): If set, the work directory where the file will
            be downloaded, otherwise a temp dir will be used.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        Path: The local file path.
    """
    return _resolve_source_to_path(
        source=source,
        headers=headers,
        workdir=workdir,
    )


@deprecated("Use `resolve_source_to_path()` or `resolve_source_to_stream()`  instead")
def resolve_file_source(
    source: Union[Path, AnyHttpUrl, str],
    headers: Optional[Dict[str, str]] = None,
) -> Path:
    """Resolves the source (URL, path) of a file to a local file path.

    If a URL is provided, the content is first downloaded to a temporary local file.

    Args:
        source (Path | AnyHttpUrl | str): The file input source. Can be a path or URL.
        headers (Dict | None): Optional set of headers to use for fetching
            the remote URL.

    Raises:
        ValueError: If source is of unexpected type.

    Returns:
        Path: The local file path.
    """
    return _resolve_source_to_path(
        source=source,
        headers=headers,
    )

```
</content>
</file_53>

<file_54>
<path>utils/generate_docs.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Generate documentation of Docling types as JSON schema.

Example:
    python docling_core/utils/generate_docs.py /tmp/docling_core_files
"""
import argparse
import json
import os
from argparse import BooleanOptionalAction
from pathlib import Path
from shutil import rmtree
from typing import Final

from docling_core.utils.generate_jsonschema import generate_json_schema

MODELS: Final = ["DoclingDocument", "Record", "Generic"]


def _prepare_directory(folder: str, clean: bool = False) -> None:
    """Create a directory or empty its content if it already exists.

    Args:
        folder: The name of the directory.
        clean: Whether any existing content in the directory should be removed.
    """
    if os.path.isdir(folder):
        if clean:
            for path in Path(folder).glob("**/*"):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    rmtree(path)
    else:
        os.makedirs(folder, exist_ok=True)


def generate_collection_jsonschema(folder: str):
    """Generate the JSON schema of Docling collections and export them to a folder.

    Args:
        folder: The name of the directory.
    """
    for item in MODELS:
        json_schema = generate_json_schema(item)
        with open(
            os.path.join(folder, f"{item}.json"), mode="w", encoding="utf8"
        ) as json_file:
            json.dump(json_schema, json_file, ensure_ascii=False, indent=2)


def main() -> None:
    """Generate the JSON Schema of Docling collections and export documentation."""
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "directory",
        help=(
            "Directory to generate files. If it exists, any existing content will be"
            " removed."
        ),
    )
    argparser.add_argument(
        "--clean",
        help="Whether any existing content in directory should be removed.",
        action=BooleanOptionalAction,
        dest="clean",
        default=False,
        required=False,
    )
    args = argparser.parse_args()

    _prepare_directory(args.directory, args.clean)

    generate_collection_jsonschema(args.directory)


if __name__ == "__main__":
    main()

```
</content>
</file_54>

<file_55>
<path>utils/generate_jsonschema.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Generate the JSON Schema of pydantic models and export them to files.

Example:
    python docling_core/utils/generate_jsonschema.py doc.document.TableCell

"""
import argparse
import json
from typing import Any, Union

from pydantic import BaseModel


def _import_class(class_reference: str) -> Any:
    components = class_reference.split(".")
    module_ref = ".".join(components[:-1])
    class_name = components[-1]
    mod = __import__(module_ref, fromlist=[class_name])
    class_type = getattr(mod, class_name)

    return class_type


def generate_json_schema(class_reference: str) -> Union[dict, None]:
    """Generate a jsonable dict of a model's schema from a data type.

    Args:
        class_reference: The reference to a class in 'docling_core.types'.

    Returns:
        A jsonable dict of the model's schema.
    """
    if not class_reference.startswith("docling_core.types."):
        class_reference = "docling_core.types." + class_reference
    class_type = _import_class(class_reference)
    if issubclass(class_type, BaseModel):
        return class_type.model_json_schema()
    else:
        return None


def main() -> None:
    """Print the JSON Schema of a model."""
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "class_ref", help="Class reference, e.g., doc.document.TableCell"
    )
    args = argparser.parse_args()

    json_schema = generate_json_schema(args.class_ref)
    print(
        json.dumps(json_schema, ensure_ascii=False, indent=2).encode("utf-8").decode()
    )


if __name__ == "__main__":
    main()

```
</content>
</file_55>

<file_56>
<path>utils/legacy.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Utilities for converting between legacy and new document format."""

import hashlib
import uuid
from pathlib import Path
from typing import Dict, Optional, Union

from docling_core.types.doc import (
    BoundingBox,
    CoordOrigin,
    DocItem,
    DocItemLabel,
    DoclingDocument,
    DocumentOrigin,
    PictureItem,
    ProvenanceItem,
    SectionHeaderItem,
    Size,
    TableCell,
    TableItem,
    TextItem,
)
from docling_core.types.doc.document import GroupItem, ListItem, TableData
from docling_core.types.doc.labels import GroupLabel
from docling_core.types.legacy_doc.base import (
    BaseCell,
    BaseText,
    Figure,
    GlmTableCell,
    PageDimensions,
    PageReference,
    Prov,
    Ref,
)
from docling_core.types.legacy_doc.base import Table as DsSchemaTable
from docling_core.types.legacy_doc.base import TableCell as DsTableCell
from docling_core.types.legacy_doc.document import (
    CCSDocumentDescription as DsDocumentDescription,
)
from docling_core.types.legacy_doc.document import CCSFileInfoObject as DsFileInfoObject
from docling_core.types.legacy_doc.document import ExportedCCSDocument as DsDocument


def _create_hash(string: str):
    hasher = hashlib.sha256()
    hasher.update(string.encode("utf-8"))

    return hasher.hexdigest()


def doc_item_label_to_legacy_type(label: DocItemLabel):
    """Convert the DocItemLabel to the legacy type."""
    _label_to_ds_type = {
        DocItemLabel.TITLE: "title",
        DocItemLabel.DOCUMENT_INDEX: "table-of-contents",
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
    }
    if label in _label_to_ds_type:
        return _label_to_ds_type[label]
    return label.value


def doc_item_label_to_legacy_name(label: DocItemLabel):
    """Convert the DocItemLabel to the legacy name."""
    _reverse_label_name_mapping = {
        DocItemLabel.CAPTION: "Caption",
        DocItemLabel.FOOTNOTE: "Footnote",
        DocItemLabel.FORMULA: "Formula",
        DocItemLabel.LIST_ITEM: "List-item",
        DocItemLabel.PAGE_FOOTER: "Page-footer",
        DocItemLabel.PAGE_HEADER: "Page-header",
        DocItemLabel.PICTURE: "Picture",
        DocItemLabel.SECTION_HEADER: "Section-header",
        DocItemLabel.TABLE: "Table",
        DocItemLabel.TEXT: "Text",
        DocItemLabel.TITLE: "Title",
        DocItemLabel.DOCUMENT_INDEX: "Document Index",
        DocItemLabel.CODE: "Code",
        DocItemLabel.CHECKBOX_SELECTED: "Checkbox-Selected",
        DocItemLabel.CHECKBOX_UNSELECTED: "Checkbox-Unselected",
        DocItemLabel.FORM: "Form",
        DocItemLabel.KEY_VALUE_REGION: "Key-Value Region",
        DocItemLabel.PARAGRAPH: "paragraph",
    }
    if label in _reverse_label_name_mapping:
        return _reverse_label_name_mapping[label]
    return label.value


def docling_document_to_legacy(doc: DoclingDocument, fallback_filaname: str = "file"):
    """Convert a DoclingDocument to the legacy format."""
    title = ""
    desc: DsDocumentDescription = DsDocumentDescription(logs=[])

    if doc.origin is not None:
        document_hash = _create_hash(str(doc.origin.binary_hash))
        filename = doc.origin.filename
    else:
        document_hash = _create_hash(str(uuid.uuid4()))
        filename = fallback_filaname

    page_hashes = [
        PageReference(
            hash=_create_hash(document_hash + ":" + str(p.page_no - 1)),
            page=p.page_no,
            model="default",
        )
        for p in doc.pages.values()
    ]

    file_info = DsFileInfoObject(
        filename=filename,
        document_hash=document_hash,
        num_pages=len(doc.pages),
        page_hashes=page_hashes,
    )

    main_text: list[Union[Ref, BaseText]] = []
    tables: list[DsSchemaTable] = []
    figures: list[Figure] = []
    equations: list[BaseCell] = []
    footnotes: list[BaseText] = []
    page_headers: list[BaseText] = []
    page_footers: list[BaseText] = []

    # TODO: populate page_headers page_footers from doc.furniture

    embedded_captions = set()
    for ix, (item, level) in enumerate(doc.iterate_items(doc.body)):

        if isinstance(item, (TableItem, PictureItem)) and len(item.captions) > 0:
            caption = item.caption_text(doc)
            if caption:
                embedded_captions.add(caption)

    for item, level in doc.iterate_items():
        if isinstance(item, DocItem):
            item_type = item.label

            if isinstance(item, (TextItem, ListItem, SectionHeaderItem)):

                if isinstance(item, ListItem) and item.marker:
                    text = f"{item.marker} {item.text}"
                else:
                    text = item.text

                # Can be empty.
                prov = [
                    Prov(
                        bbox=p.bbox.as_tuple(),
                        page=p.page_no,
                        span=[0, len(item.text)],
                    )
                    for p in item.prov
                ]
                main_text.append(
                    BaseText(
                        text=text,
                        obj_type=doc_item_label_to_legacy_type(item.label),
                        name=doc_item_label_to_legacy_name(item.label),
                        prov=prov,
                    )
                )

                # skip captions of they are embedded in the actual
                # floating object
                if item_type == DocItemLabel.CAPTION and text in embedded_captions:
                    continue

            elif isinstance(item, TableItem) and item.data:
                index = len(tables)
                ref_str = f"#/tables/{index}"
                main_text.append(
                    Ref(
                        name=doc_item_label_to_legacy_name(item.label),
                        obj_type=doc_item_label_to_legacy_type(item.label),
                        ref=ref_str,
                    ),
                )

                # Initialise empty table data grid (only empty cells)
                table_data = [
                    [
                        DsTableCell(
                            text="",
                            # bbox=[0,0,0,0],
                            spans=[[i, j]],
                            obj_type="body",
                        )
                        for j in range(item.data.num_cols)
                    ]
                    for i in range(item.data.num_rows)
                ]

                # Overwrite cells in table data for which there is actual cell content.
                for cell in item.data.table_cells:
                    for i in range(
                        min(cell.start_row_offset_idx, item.data.num_rows),
                        min(cell.end_row_offset_idx, item.data.num_rows),
                    ):
                        for j in range(
                            min(cell.start_col_offset_idx, item.data.num_cols),
                            min(cell.end_col_offset_idx, item.data.num_cols),
                        ):
                            celltype = "body"
                            if cell.column_header:
                                celltype = "col_header"
                            elif cell.row_header:
                                celltype = "row_header"
                            elif cell.row_section:
                                celltype = "row_section"

                            def _make_spans(cell: TableCell, table_item: TableItem):
                                for rspan in range(
                                    min(
                                        cell.start_row_offset_idx,
                                        table_item.data.num_rows,
                                    ),
                                    min(
                                        cell.end_row_offset_idx,
                                        table_item.data.num_rows,
                                    ),
                                ):
                                    for cspan in range(
                                        min(
                                            cell.start_col_offset_idx,
                                            table_item.data.num_cols,
                                        ),
                                        min(
                                            cell.end_col_offset_idx,
                                            table_item.data.num_cols,
                                        ),
                                    ):
                                        yield [rspan, cspan]

                            spans = list(_make_spans(cell, item))
                            table_data[i][j] = GlmTableCell(
                                text=cell.text,
                                bbox=(
                                    cell.bbox.as_tuple()
                                    if cell.bbox is not None
                                    else None
                                ),  # check if this is bottom-left
                                spans=spans,
                                obj_type=celltype,
                                col=j,
                                row=i,
                                row_header=cell.row_header,
                                row_section=cell.row_section,
                                col_header=cell.column_header,
                                row_span=[
                                    cell.start_row_offset_idx,
                                    cell.end_row_offset_idx,
                                ],
                                col_span=[
                                    cell.start_col_offset_idx,
                                    cell.end_col_offset_idx,
                                ],
                            )

                # Compute the caption
                caption = item.caption_text(doc)

                tables.append(
                    DsSchemaTable(
                        text=caption,
                        num_cols=item.data.num_cols,
                        num_rows=item.data.num_rows,
                        obj_type=doc_item_label_to_legacy_type(item.label),
                        data=table_data,
                        prov=[
                            Prov(
                                bbox=p.bbox.as_tuple(),
                                page=p.page_no,
                                span=[0, 0],
                            )
                            for p in item.prov
                        ],
                    )
                )

            elif isinstance(item, PictureItem):
                index = len(figures)
                ref_str = f"#/figures/{index}"
                main_text.append(
                    Ref(
                        name=doc_item_label_to_legacy_name(item.label),
                        obj_type=doc_item_label_to_legacy_type(item.label),
                        ref=ref_str,
                    ),
                )

                # Compute the caption
                caption = item.caption_text(doc)

                figures.append(
                    Figure(
                        prov=[
                            Prov(
                                bbox=p.bbox.as_tuple(),
                                page=p.page_no,
                                span=[0, len(caption)],
                            )
                            for p in item.prov
                        ],
                        obj_type=doc_item_label_to_legacy_type(item.label),
                        text=caption,
                        # data=[[]],
                    )
                )

    page_dimensions = [
        PageDimensions(page=p.page_no, height=p.size.height, width=p.size.width)
        for p in doc.pages.values()
    ]

    legacy_doc: DsDocument = DsDocument(
        name=title,
        description=desc,
        file_info=file_info,
        main_text=main_text,
        equations=equations,
        footnotes=footnotes,
        page_headers=page_headers,
        page_footers=page_footers,
        tables=tables,
        figures=figures,
        page_dimensions=page_dimensions,
    )

    return legacy_doc


def legacy_to_docling_document(legacy_doc: DsDocument) -> DoclingDocument:  # noqa: C901
    """Convert a legacy document to DoclingDocument.

    It is known that the following content will not be preserved in the transformation:
    - name of labels (upper vs lower case)
    - caption of figures are not in main-text anymore
    - s3_data removed
    - model metadata removed
    - logs removed
    - document hash cannot be preserved
    """

    def _transform_prov(item: BaseCell) -> Optional[ProvenanceItem]:
        """Create a new provenance from a legacy item."""
        prov: Optional[ProvenanceItem] = None
        if item.prov is not None and len(item.prov) > 0:
            prov = ProvenanceItem(
                page_no=int(item.prov[0].page),
                charspan=tuple(item.prov[0].span),
                bbox=BoundingBox.from_tuple(
                    tuple(item.prov[0].bbox), origin=CoordOrigin.BOTTOMLEFT
                ),
            )
        return prov

    origin = DocumentOrigin(
        mimetype="application/pdf",
        filename=legacy_doc.file_info.filename,
        binary_hash=legacy_doc.file_info.document_hash,
    )
    doc_name = Path(origin.filename).stem

    doc: DoclingDocument = DoclingDocument(name=doc_name, origin=origin)

    # define pages
    if legacy_doc.page_dimensions is not None:
        for page_dim in legacy_doc.page_dimensions:
            page_no = int(page_dim.page)
            size = Size(width=page_dim.width, height=page_dim.height)

            doc.add_page(page_no=page_no, size=size)

    # page headers
    if legacy_doc.page_headers is not None:
        for text_item in legacy_doc.page_headers:
            if text_item.text is None:
                continue
            prov = _transform_prov(text_item)
            doc.add_text(
                label=DocItemLabel.PAGE_HEADER,
                text=text_item.text,
                parent=doc.furniture,
            )

    # page footers
    if legacy_doc.page_footers is not None:
        for text_item in legacy_doc.page_footers:
            if text_item.text is None:
                continue
            prov = _transform_prov(text_item)
            doc.add_text(
                label=DocItemLabel.PAGE_FOOTER,
                text=text_item.text,
                parent=doc.furniture,
            )

    # footnotes
    if legacy_doc.footnotes is not None:
        for text_item in legacy_doc.footnotes:
            if text_item.text is None:
                continue
            prov = _transform_prov(text_item)
            doc.add_text(
                label=DocItemLabel.FOOTNOTE, text=text_item.text, parent=doc.furniture
            )

    # main-text content
    if legacy_doc.main_text is not None:
        item: Optional[Union[BaseCell, BaseText]]

        # collect all captions embedded in table and figure objects
        # to avoid repeating them
        embedded_captions: Dict[str, int] = {}
        for ix, orig_item in enumerate(legacy_doc.main_text):
            item = (
                legacy_doc._resolve_ref(orig_item)
                if isinstance(orig_item, Ref)
                else orig_item
            )
            if item is None:
                continue

            if isinstance(item, (DsSchemaTable, Figure)) and item.text:
                embedded_captions[item.text] = ix

        # build lookup from floating objects to their caption item
        floating_to_caption: Dict[int, BaseText] = {}
        for ix, orig_item in enumerate(legacy_doc.main_text):
            item = (
                legacy_doc._resolve_ref(orig_item)
                if isinstance(orig_item, Ref)
                else orig_item
            )
            if item is None:
                continue

            item_type = item.obj_type.lower()
            if (
                isinstance(item, BaseText)
                and (
                    item_type == "caption"
                    or (item.name is not None and item.name.lower() == "caption")
                )
                and item.text in embedded_captions
            ):
                floating_ix = embedded_captions[item.text]
                floating_to_caption[floating_ix] = item

        # main loop iteration
        current_list: Optional[GroupItem] = None
        for ix, orig_item in enumerate(legacy_doc.main_text):
            item = (
                legacy_doc._resolve_ref(orig_item)
                if isinstance(orig_item, Ref)
                else orig_item
            )
            if item is None:
                continue

            prov = _transform_prov(item)
            item_type = item.obj_type.lower()

            # if a group is needed, add it
            if isinstance(item, BaseText) and (
                item_type in "list-item-level-1" or item.name in {"list", "list-item"}
            ):
                if current_list is None:
                    current_list = doc.add_group(label=GroupLabel.LIST, name="list")
            else:
                current_list = None

            # add the document item in the document
            if isinstance(item, BaseText):
                text = item.text if item.text is not None else ""
                label_name = item.name if item.name is not None else "text"

                if item_type == "caption":
                    if text in embedded_captions:
                        # skip captions if they are embedded in the actual
                        # floating objects
                        continue
                    else:
                        # captions without a related object are inserted as text
                        doc.add_text(label=DocItemLabel.TEXT, text=text, prov=prov)

                # first title match
                if item_type == "title":
                    doc.add_title(text=text, prov=prov)

                # secondary titles
                elif item_type in {
                    "subtitle-level-1",
                }:
                    doc.add_heading(text=text, prov=prov)

                # list item
                elif item_type in "list-item-level-1" or label_name in {
                    "list",
                    "list-item",
                }:
                    # TODO: Infer if this is a numbered or a bullet list item
                    doc.add_list_item(
                        text=text, enumerated=False, prov=prov, parent=current_list
                    )

                # normal text
                else:
                    label = DocItemLabel.TEXT
                    normalized_label_name = label_name.replace("-", "_")
                    if normalized_label_name is not None:
                        try:
                            label = DocItemLabel(normalized_label_name)
                        except ValueError:
                            pass
                    doc.add_text(label=label, text=text, prov=prov)

            elif isinstance(item, DsSchemaTable):

                table_data = TableData(num_cols=item.num_cols, num_rows=item.num_rows)
                if item.data is not None:
                    seen_spans = set()
                    for row_ix, row in enumerate(item.data):
                        for col_ix, orig_cell_data in enumerate(row):

                            cell_bbox: Optional[BoundingBox] = (
                                BoundingBox.from_tuple(
                                    tuple(orig_cell_data.bbox),
                                    origin=CoordOrigin.BOTTOMLEFT,
                                )
                                if orig_cell_data.bbox is not None
                                else None
                            )
                            cell = TableCell(
                                start_row_offset_idx=row_ix,
                                end_row_offset_idx=row_ix + 1,
                                start_col_offset_idx=col_ix,
                                end_col_offset_idx=col_ix + 1,
                                text=orig_cell_data.text,
                                bbox=cell_bbox,
                                column_header=(orig_cell_data.obj_type == "col_header"),
                                row_header=(orig_cell_data.obj_type == "row_header"),
                                row_section=(orig_cell_data.obj_type == "row_section"),
                            )

                            if orig_cell_data.spans is not None:
                                # convert to a tuple of tuples for hashing
                                spans_tuple = tuple(
                                    tuple(span) for span in orig_cell_data.spans
                                )

                                # skip repeated spans
                                if spans_tuple in seen_spans:
                                    continue

                                seen_spans.add(spans_tuple)

                                cell.start_row_offset_idx = min(
                                    s[0] for s in spans_tuple
                                )
                                cell.end_row_offset_idx = (
                                    max(s[0] for s in spans_tuple) + 1
                                )
                                cell.start_col_offset_idx = min(
                                    s[1] for s in spans_tuple
                                )
                                cell.end_col_offset_idx = (
                                    max(s[1] for s in spans_tuple) + 1
                                )

                                cell.row_span = (
                                    cell.end_row_offset_idx - cell.start_row_offset_idx
                                )
                                cell.col_span = (
                                    cell.end_col_offset_idx - cell.start_col_offset_idx
                                )

                            table_data.table_cells.append(cell)

                new_item = doc.add_table(data=table_data, prov=prov)
                if (caption_item := floating_to_caption.get(ix)) is not None:
                    if caption_item.text is not None:
                        caption_prov = _transform_prov(caption_item)
                        caption = doc.add_text(
                            label=DocItemLabel.CAPTION,
                            text=caption_item.text,
                            prov=caption_prov,
                            parent=new_item,
                        )
                        new_item.captions.append(caption.get_ref())

            elif isinstance(item, Figure):
                new_item = doc.add_picture(prov=prov)
                if (caption_item := floating_to_caption.get(ix)) is not None:
                    if caption_item.text is not None:
                        caption_prov = _transform_prov(caption_item)
                        caption = doc.add_text(
                            label=DocItemLabel.CAPTION,
                            text=caption_item.text,
                            prov=caption_prov,
                            parent=new_item,
                        )
                        new_item.captions.append(caption.get_ref())

            # equations
            elif (
                isinstance(item, BaseCell)
                and item.text is not None
                and item_type in {"formula", "equation"}
            ):
                doc.add_text(label=DocItemLabel.FORMULA, text=item.text, prov=prov)

    return doc

```
</content>
</file_56>

<file_57>
<path>utils/validate.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Validation of Document-related files against their data schemas."""
import argparse
import json
import logging

from docling_core.utils.validators import (
    validate_ann_schema,
    validate_ocr_schema,
    validate_raw_schema,
)

logger = logging.getLogger("docling-core")


def parse_arguments():
    """Parse the arguments from the command line."""
    argparser = argparse.ArgumentParser(description="validate example-file with schema")

    argparser.add_argument(
        "-f", "--format", required=True, help="format of the file [RAW, ANN, OCR]"
    )

    argparser.add_argument(
        "-i", "--input-file", required=True, help="JSON filename to be validated"
    )

    pargs = argparser.parse_args()

    return pargs.format, pargs.input_file


def run():
    """Run the validation of a file containing a Document."""
    file_format, input_file = parse_arguments()

    with open(input_file, "r", encoding="utf-8") as fd:
        file_ = json.load(fd)

    result = (False, "Empty result")

    if file_format == "RAW":
        result = validate_raw_schema(file_)

    elif file_format == "ANN":
        result = validate_ann_schema(file_)

    elif file_format == "OCR":
        result = validate_ocr_schema(file_)

    else:
        logger.error("format of the file needs to `RAW`, `ANN` or `OCR`")

    if result[0]:
        logger.info("Done!")
    else:
        logger.error("invalid schema: {}".format(result[1]))


def main():
    """Set up the environment and run the validation of a Document."""
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    # logger.addHandler(ch)

    logging.basicConfig(handlers=[ch])
    run()


if __name__ == "__main__":
    main()

```
</content>
</file_57>

<file_58>
<path>utils/validators.py</path>
<content>
```python
#
# Copyright IBM Corp. 2024 - 2024
# SPDX-License-Identifier: MIT
#

"""Module for custom type validators."""
import json
import logging
from datetime import datetime
from importlib import resources
from typing import Hashable, TypeVar

import jsonschema
from pydantic_core import PydanticCustomError

logger = logging.getLogger("docling-core")

T = TypeVar("T", bound=Hashable)


def validate_schema(file_: dict, schema: dict) -> tuple[bool, str]:
    """Check wheter the workflow is properly formatted JSON and contains valid keys.

    Where possible, this also checks a few basic dependencies between properties, but
    this functionality is limited.
    """
    try:
        jsonschema.validate(file_, schema)
        return (True, "All good!")

    except jsonschema.ValidationError as err:
        return (False, err.message)


def validate_raw_schema(file_: dict) -> tuple[bool, str]:
    """Validate a RAW file."""
    logger.debug("validate RAW schema ... ")

    schema_txt = (
        resources.files("docling_core")
        .joinpath("resources/schemas/legacy_doc/RAW.json")
        .read_text("utf-8")
    )
    schema = json.loads(schema_txt)

    return validate_schema(file_, schema)


def validate_ann_schema(file_: dict) -> tuple[bool, str]:
    """Validate an annotated (ANN) file."""
    logger.debug("validate ANN schema ... ")

    schema_txt = (
        resources.files("docling_core")
        .joinpath("resources/schemas/legacy_doc/ANN.json")
        .read_text("utf-8")
    )
    schema = json.loads(schema_txt)

    return validate_schema(file_, schema)


def validate_ocr_schema(file_: dict) -> tuple[bool, str]:
    """Validate an OCR file."""
    logger.debug("validate OCR schema ... ")

    schema_txt = (
        resources.files("docling_core")
        .joinpath("resources/schemas/legacy_doc/OCR-output.json")
        .read_text("utf-8")
    )
    schema = json.loads(schema_txt)

    return validate_schema(file_, schema)


def validate_unique_list(v: list[T]) -> list[T]:
    """Validate that a list has unique values.

    Validator for list types, since pydantic V2 does not support the `unique_items`
    parameter from V1. More information on
    https://github.com/pydantic/pydantic-core/pull/820#issuecomment-1670475909

    Args:
        v: any list of hashable types

    Returns:
        The list, after checking for unique items.
    """
    if len(v) != len(set(v)):
        raise PydanticCustomError("unique_list", "List must be unique")
    return v


def validate_datetime(v, handler):
    """Validate that a value is a datetime or a non-numeric string."""
    if type(v) is datetime or (type(v) is str and not v.isnumeric()):
        return handler(v)
    else:
        raise ValueError("Value type must be a datetime or a non-numeric string")

```
</content>
</file_58>
