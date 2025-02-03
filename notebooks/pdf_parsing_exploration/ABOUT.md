# Background

We explored a variety of opensource options for PDF parsing. Here are my notes, consider making a blog post about them.

# MacOS Testing
Testing on a 2019 Macbook Pro intel chipset.
- TODO: Dump full specs here
- Notebook: macos-exploration.ipynb
- Used UV package manager to get a sense of it


## Installation
- Challenges installing pytorch recent versions.
    - this made it impossible to install marker pdf and docling
- finnicky on the mack intel and using UV was a MESS


## py-zerox
- py-zerox worked well but the llm image analysis ran into signifigant rate limiting with the newer models
    - openai was the best in this case with gpt4-mini
    - sonnet did well when not limited
- RECOMMENDATIONS
    - try this with a local deepseek instance which has no rate limits
    - make a separate blog about setting this up
- OVERALL: good approach but requires api calls to LLM and tokens/rate limits

## pymupdf4llm

- worked out of the box
- decent reaults without rate limiting or other challegnes
- didnt do image analysis very well


  