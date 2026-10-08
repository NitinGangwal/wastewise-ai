# WasteWise AI

Snap. Scan. Segregate. Take a photo of any waste and get an instant classification
and disposal guide.

## What it does
- Detects up to 5 waste items in a single photo (upload or live camera)
- Classifies each item: Wet, Dry, Hazardous, E-waste, Sanitary
- Shows recyclability, single-use plastic flag and step-by-step disposal advice
- Warns when an item needs special handling (batteries, electronics)

## Open-source AI
- Gemma 4 (open-weight) through the Gemini API
- Gemma 3 running fully offline on-device through Ollama
Switch between the two from the sidebar.

## Run it
1. Install Python and Ollama (https://ollama.com), then run: ollama pull gemma3:4b
2. pip install -r requirements.txt
3. python -m streamlit run wastewise.py
4. In the sidebar choose an engine. For Gemma 4, enter a Gemini API key
   (free from https://aistudio.google.com/apikey).

## Tech stack
Python, Streamlit, Gemma 4, Gemma 3, Ollama, Pillow

## License
MIT
