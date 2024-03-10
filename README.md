# Automate Codebase analysis.

Install sglang and run server.

```bash
pip install sglang
python -m sglang.launch_server --model-path deepseek-ai/deepseek-coder-6.7b-instruct --tp 4
```


Run it via

```bash
convert.py CODEBASE_DIR OUTPUT_DIR --port 8080
```