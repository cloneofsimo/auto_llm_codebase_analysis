# Automate Massive Codebase Analysis with Language Model

<p align="center">
  <img src="chimp.webp" alt="Chimp" width="400">
</p>

Ever had to go over all the codebase and analyze everything one-by-one? Ever wanted to "read over all of it really fast" and get "high level picture" per folder? This short tiny codebase does exactly that, hope to make your codebase-analysis time shorter.

This will recursively generate...

* High-level summary of the codebase
* Highlights of the codebase
* Pythonic Pseudocode
* Import Relationships

# Installation & Use

Install sglang and run server.

```bash
pip install sglang
python -m sglang.launch_server --model-path "Qwen/Qwen1.5-72B-Chat" --tp 4 --port 8080
```


Run it via

```bash
convert.py CODEBASE_DIR OUTPUT_DIR --port 8080
```


# Example Output:

The [following](EXAMPLE_GEN.md) is example output from analysis of DeepSpeed codebase.

