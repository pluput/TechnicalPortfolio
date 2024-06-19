"""Build static HTML site from directory of HTML templates and plain files."""
import shutil
import os
import json
import sys
import pathlib
import click
import jinja2


@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option('-o', '--output', "output", type=click.Path(),
              help='Output directory.')
@click.option('-v', '--verbose', "verbose", is_flag=True,
              help='Print more output.')
def main(input_dir, output, verbose):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)

    # catch error if not able to load config.json or find file
    try:
        with open(input_dir/'config.json', encoding="utf8") as file:
            configurations = json.load(file)
    except FileNotFoundError:
        print("File ", input_dir/'config.json', " not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error loading config.json file")
        sys.exit(1)

    # catch error if not able to load template environment with jinja2
    try:
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(input_dir/'templates')),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )
    except jinja2.TemplateError as error:
        print("Error loading template directory",
              str(input_dir/'templates'), ":", error)
        sys.exit(1)

    # make the output directory (output_dir) and exit if exists
    if output:
        output_dir = pathlib.Path(output)
    else:
        output_dir = input_dir/'html'

    if pathlib.Path(output_dir).exists():
        sys.exit("Output Directory Already Exists!")
    else:
        os.makedirs(output_dir)

    # add the static directory (static_dir) or not if does not exist
    static_dir = input_dir/'static'
    if pathlib.Path(static_dir).exists():
        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
        if verbose:
            print("Copied ", static_dir, " -> ", output_dir)

    # create template for each configuration and write it to output file
    for i in configurations:
        template = template_env.get_template((i['template']))
        url = i['url'].lstrip("/")
        if not pathlib.Path(output_dir/url).exists():
            os.makedirs(output_dir/url)
        output_file = output_dir/url/'index.html'
        with open(output_file, "w", encoding="utf8") as write_output:
            write_output.write(template.render(i['context']))
            if verbose:
                print("Rendered index.html -> ", output_file)


if __name__ == "__main__":
    main()
