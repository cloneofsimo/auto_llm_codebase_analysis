import json
import os
from pathlib import Path

import click
from sglang import (RuntimeEndpoint, assistant, function, gen,
                    set_default_backend, system, user)

set_default_backend(RuntimeEndpoint("http://localhost:10000"))


def highlight(file_content):
    @function
    def _call_sglang_highlight(s, prompt):
        s += system(
            "You are a helpful assistant specialized in highlighting key features of code."
        )
        s += user(prompt)
        s += assistant()
        s += f"There are 5 key features I can highlight.\n"
        for i in range(5):
            s += f"\n{i + 1}."
            s += gen(f"gen_{i}", stop="\n", max_tokens=512)

    state = _call_sglang_highlight.run(
        prompt=f"Highlight the key features of this code:\n\n{file_content}. What would you say is the key thing to look for for this code?"
    )
    for m in state.messages():
        print(m["role"], ":", m["content"])
    return state.text().split("There are 5 key features I can highlight.")[-1]


def overall_summarize(file_content):
    @function
    def _call_sglang_overall_summarize(s, prompt):
        s += system(
            "You are a helpful assistant specialized in providing overall summaries of codebases."
        )
        s += user(prompt)
        s += "1. List all the major, important methods and functions, and rate their importance. it has to be in form of -NAME : what it is, -Rating"
        s += "2. Describe what this file is all about.\n"
        s += assistant()
        s += f"Sure. There are multiple methods and classes.\n"
        for i in range(5):
            s += f"\n\n* `"
            s += gen(f"answer_{i}", stop="`")
            s += "`:"
            s += gen(f"answer_{i}_1", stop=["Rating", "*"])
            s += " Rating (out of 5):"
            s += gen(f"score", regex=r"[0-5]{1}")

            # s += "\nRating (Out of 10):"
            # s += gen(f"Rating_{i}", stop = '\n')
        s += gen(f"final", max_tokens=1024)

    state = _call_sglang_overall_summarize.run(
        prompt=f"Provide an overall summary of this codebase:\n\n{file_content}"
    )
    ret = state.text().split(f"Sure. There are multiple methods and classes.\n")[-1]
    return ret


def high_level_pseudocode(file_content):
    @function
    def _call_sglang_high_level_pseudocode(s, prompt):
        s += system(
            "You are a helpful assistant specialized in generating high-level pseudocode."
        )
        s += user(prompt)
        s += "1. List all the major, important methods and functions, and rate their importance.\n"
        s += "2. Describe what this file is all about.\n"
        s += assistant()
        s += f"Sure. Here is the pythonic pseudocode that overviews the file you described.\n"
        s += "```python\n"
        s += gen("long_answer", max_tokens=2048, stop="```")

    state = _call_sglang_high_level_pseudocode.run(
        prompt=f"Generate high-level pseudocode for this code:\n\n{file_content}"
    )
    for m in state.messages():
        print(m["role"], ":", m["content"])

    ret = state.text().split("```python")[-1]
    return ret


def analyze_import_relationships(file_content):
    import_lines = [
        line
        for line in file_content.split("\n")
        if line.startswith("import") or line.startswith("from")
    ]
    if import_lines:
        return "Imports found:\n" + "\n".join(import_lines)
    else:
        return "No imports found."


def write_markdown_file(path, content):
    with open(path, "w", encoding="utf-8") as md_file:
        md_file.write(content)




def analyze_file_and_generate_json(file_path, output_directory, global_codebase_path):
    # this will analyze single file -> convert to json.

    content = file_path.read_text(encoding="utf-8")
    relative_path = str(file_path.relative_to(global_codebase_path))

    content = f"# python file {relative_path}\n\n{content}"
    analyses = {
        "highlights": highlight(content),
        "overall_summary": overall_summarize(content),
        "pseudocode": high_level_pseudocode(content),
        "import_relationships": analyze_import_relationships(content),
    }
    relative_path = file_path.relative_to(global_codebase_path)
    output_file_path = output_directory / relative_path.with_suffix(".json")
    output_md_path = output_directory / relative_path.with_suffix(".md")

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

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


def analyze_directory_and_generate_overall_json(
    this_directory_path, output_directory, global_codebase_path
):
    all_summaries = []
    # stage 1. we will read & generate analysis for all files first.

    for root, _, files in os.walk(this_directory_path):
        for file in files:
            if not file.endswith(".json"):
                file_path = Path(root, file)
                analyze_file_and_generate_json(
                    file_path, output_directory, global_codebase_path
                )
                relative_file_path = file_path.relative_to(this_directory_path)
                json_file_path = output_directory / relative_file_path.with_suffix(
                    ".json"
                )
                with json_file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_summaries.append(
                        f" \n\n{ relative_file_path }\n\n { data[ 'overall_summary' ] }"
                    )

    overall_summary = "".join(all_summaries)
    overall_summary = overall_summarize(overall_summary)

    # overall_data = {"overall_summary": overall_summary}
    relative_path = Path(this_directory_path).relative_to(global_codebase_path)
    output_md_path = output_directory / relative_path / "_overall.md"
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    with output_md_path.open("w", encoding="utf-8") as f:
        f.write(overall_summary)


@click.command()
@click.argument("codebase_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_directory", type=click.Path(file_okay=False))
@click.argument("port", type=int)
def main(codebase_dir, output_directory, port):
    codebase_dir = Path(codebase_dir)
    output_directory = Path(output_directory)
    set_default_backend(RuntimeEndpoint(f"http://localhost:{port}"))

    analyze_directory_and_generate_overall_json(
        codebase_dir, output_directory, codebase_dir
    )
    click.echo(f"Analysis complete. Output is saved in {output_directory}")


if __name__ == "__main__":
    main()
