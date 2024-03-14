import json
import os
from pathlib import Path

import click
from sglang import (
    RuntimeEndpoint,
    assistant,
    function,
    gen,
    set_default_backend,
    system,
    user,
)


import json
import os
from pathlib import Path


def multi_highlight(file_contents):
    @function
    def _call_sglang_highlight(s, prompt):
        s += system(
            "You are a helpful assistant specialized in highlighting key features of code."
        )
        s += user(prompt)
        s += assistant(f"There are 5 key features I can highlight.\n")

        for i in range(5):
            s += f"\n{i + 1}."
            s += gen(f"gen_{i}", stop=["\n"], max_tokens=512)

    args = [
        {
            "prompt": f"Highlight the key features of this code:\n\n{file_content}. What would you say is the key thing to look for for this code?"
        }
        for file_content in file_contents
    ]

    rets = _call_sglang_highlight.run_batch(
        args, temperature=0, max_new_tokens=1024, num_threads=64, progress_bar=True
    )

    return [
        state.text().split("There are 5 key features I can highlight.")[-1]
        for state in rets
    ]


def multi_overall_summarize(file_contents):
    @function
    def _call_sglang_overall_summarize(s, prompt):
        s += system(
            "You are a helpful assistant specialized in providing overall summaries of codebases."
        )
        s += user(prompt)
        s += "1. List all the major, important methods and functions, and rate their importance. it has to be in form of \n* `function_or_class_or_class_method`: EXPLANATION. Importance : **[IMPORTANCE]**\nFor example,\n* `default_inference_config`: Provides a default configuration for DeepSpeed inference. Importance : **[High]**\n\n* `_LRScheduler` `DeepSpeedOptimizerCallable`, `DeepSpeedSchedulerCallable`: Class and function types for handling optimizers and learning rate schedulers with DeepSpeed. Importance : **[Medium]**\n\n* `cli_main`: Wraps `main` for a command-line interface. Importance : **[Low]**\n\n"
        s += "2. Describe what this file is all about.\n"
        s += assistant(f"Sure. There are multiple methods and classes.\n")
        for i in range(5):
            s += f"\n"
            s += gen(f"answer_{i}", regex=r"\* `([^`]+)`:")
            s += gen(f"answer_{i}_2", stop=["\n"])

        s += gen(f"final", max_tokens=1024)

    args = [
        {"prompt": f"Provide an overall summary of this codebase:\n\n{file_content}"}
        for file_content in file_contents
    ]
    rets = _call_sglang_overall_summarize.run_batch(
        args, temperature=0, max_new_tokens=1024, num_threads=64, progress_bar=True
    )
    return [
        state.text().split("Sure. There are multiple methods and classes.\n")[-1]
        for state in rets
    ]


def multi_high_level_pseudocode(file_contents):
    @function
    def _call_sglang_high_level_pseudocode(s, prompt):
        s += system(
            "You are a helpful assistant specialized in generating high-level pythonic pseudocode."
        )
        s += user(prompt)
        s += "Rewrite above high-level logic in pythonic pseudocode with comments. Be very abstract and informative."
        s += assistant(
            f"Sure. Here is the pythonic pseudocode that overviews the file you described.\n"
        )
        s += "```python\n"
        s += gen("long_answer", max_tokens=2048, stop=["```"])

    args = [
        {"prompt": f"Generate high-level pseudocode for this code:\n\n{file_content}"}
        for file_content in file_contents
    ]
    rets = _call_sglang_high_level_pseudocode.run_batch(
        args, temperature=0, max_new_tokens=2048, num_threads=64, progress_bar=True
    )
    return [state.text().split("```python")[-1] for state in rets]


def single_analyze_import_relationships(file_content):
    import_lines = [
        line
        for line in file_content.split("\n")
        if line.startswith("import") or line.startswith("from")
    ]
    if import_lines:
        return "Imports found:\n" + "\n".join(import_lines)
    else:
        return "No imports found."


def multi_analyze_import_relationships(file_contents):
    return [
        single_analyze_import_relationships(file_content)
        for file_content in file_contents
    ]


def analyze_files_and_generate_json_batch(
    file_paths, output_directory, global_codebase_path
):
    contents = []
    relative_paths = []

    # Prepare content and relative paths for batch processing
    for file_path in file_paths:
        content = file_path.read_text(encoding="utf-8")
        relative_path = str(file_path.relative_to(global_codebase_path))
        content_with_header = f"# python file {relative_path}\n\n{content}"
        contents.append(content_with_header)
        relative_paths.append(relative_path)

    # Batch process analyses
    highlights = multi_highlight(contents)
    overall_summaries = multi_overall_summarize(contents)
    pseudocodes = multi_high_level_pseudocode(contents)
    import_relationships = multi_analyze_import_relationships(contents)

    # Process each file's analysis and save to output
    for i, file_path in enumerate(file_paths):
        output_file_path = output_directory / Path(relative_paths[i]).with_suffix(
            ".json"
        )
        output_md_path = output_directory / Path(relative_paths[i]).with_suffix(".md")
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        analyses = {
            "highlights": highlights[i],
            "overall_summary": overall_summaries[i],
            "pseudocode": pseudocodes[i],
            "import_relationships": import_relationships[i],
        }

        with output_file_path.open("w", encoding="utf-8") as f:
            json.dump(analyses, f, indent=4)

        with output_md_path.open("w", encoding="utf-8") as f:
            f.write("\n\n### Summary\n\n")
            f.write(analyses["overall_summary"].strip())
            f.write("\n\n### Highlights\n\n")
            f.write(analyses["highlights"].strip())
            f.write(
                f"\n\n### Pythonic Pseudocode\n\n```python\n{analyses['pseudocode'].strip()}\n```"
            )
            f.write("\n\n\n### import Relationships\n\n")
            f.write(analyses["import_relationships"].strip())


def analyze_directory_and_generate_overall_json_batch(
    this_directory_path, output_directory, global_codebase_path
):
    file_paths = []

    for root, _, files in os.walk(this_directory_path):
        for file in files:
            if not file.endswith(".json"):
                file_path = Path(root, file)
                file_paths.append(file_path)

    if file_paths:
        analyze_files_and_generate_json_batch(
            file_paths, output_directory, global_codebase_path
        )


@click.command()
@click.argument("codebase_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_directory", type=click.Path(file_okay=False))
@click.option("--port", type=int)
def main(codebase_dir, output_directory, port):
    codebase_dir = Path(codebase_dir)
    output_directory = Path(output_directory)
    set_default_backend(RuntimeEndpoint(f"http://localhost:{port}"))

    analyze_directory_and_generate_overall_json_batch(
        codebase_dir, output_directory, codebase_dir
    )
    click.echo(f"Analysis complete. Output is saved in {output_directory}")


if __name__ == "__main__":
    main()
