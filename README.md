# System for extracting figures from photos of pages

## Origin

I have learned a lot of biology using flash cards. Learning biology means learning not only schemas and pure text knowledge, but also how something looks like.
My vademecuum doesn't have e-book version, so to create flash cards with images I had to:
* Make photos of book pages
* Send them to PC
* **Rotate and cropp**
* Paste them into flashcards

This process takes a lot of idle time during which I don't learn much. So I decided to automate some parts of it - Rotating and cropping figures from photos of book pages.

## How to run
*Install Python 3.11
1. Create .venv and activate it
2. `pip install -r requirements.txt'
3. Look at poc.ipynb
4. Run script to process whole folder
```
python script/run_for_folder.py -i <input-folder> -o <output-folder>
```

## Files schema

```
Obrazki do fiszek/
├── README.md                           # Project documentation and overview
├── requirements.txt                    # Python dependencies and versions
├── poc.ipynb                           # Proof of concept Jupyter notebook
├── data/                               # Sample and test images
├── run_for_folder.py                   # Main script to process entire folder
└── src/                                # Core source code
    ├── system.py                       # Main system orchestration
    └── components/                     # Modular components
        ├── bounding_box.py             # Bounding box detection and manipulation
        ├── figure_extractor.py         # Core figure extraction logic
        ├── filename_generator.py       # File naming and organization
        ├── image_size_reducer.py       # Image resizing and optimization
        └── save_handler.py             # File saving and output management
```

### Key Dependencies

The system relies on several key Python packages:
- **Azure AI Document Intelligence** - For document analysis and figure detection
- **Pillow (PIL)** - For image processing and manipulation
- **NumPy** - For numerical operations
- **OpenAI** - For AI-powered enhancements
- **Azure Core & Identity** - For Azure service authentication

### Usage

The main entry point is `scripts/run_for_folder.py`, which processes entire folder of page images, extracts figures and saves in output directory. 

### Ideas & TODO
* ~~Try LangSAM to extract figures~~
    * It usually marks whole page as figure. Describing how figures looks like (e.g. "Two ovals connected with two horizontal arrows") improves results, but:
        * Generating figures descriptions (via LLMs) generates costs and makes system more buggy and more non-deterministic  
        * Idk how to handle detecting captions
* ~~Try YOLO-E to extract figures~~
    * YOLO-E works well for "naturally detectable things" (e.g. cats, dogs, laptops), but "figures in book" is kind of "fuzzy thing" with no strict description. This makes YOLO-E bad choice for this project
* Adjust way to extend figures by paragraphs (threshold is maybe to large)
* Make DB to track real-use detections accuracy
* Add MLFlow add try to upgrade the system 

