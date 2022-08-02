import shutil
import subprocess
import copy
from typing import Tuple
import numpy as np
from pathlib import Path
import utils.config_latex as config_latex
import regex as re


def process_environment(data: str, search_pattern: str, env_type: str, ignore_pos: list = None) -> Tuple[list, str]:
    """Process LaTeX environment."""

    try:
        start_pos = re.search(r"\\begin\{document\}", data).end()
    except AttributeError:
        start_pos = 0
    if env_type == 'inline':
        start_pos = 0
    vertices_ptrs = []
    ignore_pos = ignore_pos or []
    regex = re.compile(search_pattern)
    start_pattern = False
    if ").*?" in search_pattern and env_type != 'display':
        start_pattern = search_pattern[9:search_pattern.find(").*?")].replace("\\{", "{")
    end_pattern = False
    if env_type == 'inline' or env_type == 'footnote':
        end_pattern = '$'
    if search_pattern[search_pattern.find('.*?(?=') + 6:-1] == '\\}':
        end_pattern = '}'
    while start_pos <= len(data):
        pattern = regex.search(data, pos=start_pos)
        # if found a pattern
        if pattern:
            # get start end position
            start, end = pattern.span()
            if (env_type == 'display_lyx' or env_type == 'inline_lyx') and data[start - 3:start - 2] == '\\':
                start_pos = start + 1
                continue
            if (env_type == 'display_lyx' or env_type == 'inline_lyx') and data[end - 1:end] == '\\':
                end_pattern_found = False
                while not end_pattern_found:
                    end += 2
                    if env_type == 'inline_lyx':
                        end_new = data[end:].find('\\)')
                    else:
                        end_new = data[end:].find('\\]')
                    end += end_new
                    if data[end - 1:end] != '\\':
                        end_pattern_found = True
            if env_type == 'caption2':
                if end - start < 30:
                    start = end + 2
                    end = start + data[start:].find('}')
                start += 1

            # check that no open brackets and $ exists
            while end_pattern:
                open_brackets = len(
                    [match for match in re.finditer('{', data[start:end]) if data[start + match.span()[0] - 1] != '\\'])
                closed_brackets = len(
                    [match for match in re.finditer('}', data[start:end]) if data[start + match.span()[0] - 1] != '\\'])
                dollar_signs = len([match for match in re.finditer('\$', data[start:end]) if
                                    data[start + match.span()[0] - 1] != '\\'])
                if open_brackets > closed_brackets or dollar_signs % 2 != 0:
                    end += 1
                    new_end = data[end:].find(end_pattern)
                    if new_end == -1:
                        break
                    if end_pattern == '$':
                        new_end += 1
                    end += new_end
                else:
                    break
            if env_type == 'display':
                start -= 2
                end += 2
            found = pattern.group()
            # make further content checks
            skip = config_latex.ignore_content(found, env_type)
            # check if $ is a $ sign instead of the inline env
            if (env_type == 'inline' or env_type == 'display') and not skip:
                # fixes $ signs in latex code
                if data[start - 1:start + 1] == '\\$' and data[start - 2:start + 1] != '\\\\$':
                    start_pos = start + 2
                    continue
            # adds word before _123
            if 'inline' in env_type:
                temp = copy.deepcopy(data[start:end])
                temp = temp.replace('$', '').replace(" ", "").replace("{", '').replace("}", "")
                if len(temp) >= 2 and temp[0] == '_' and data[start - 1] != ' ':
                    word_before = data[start - 10:start].split()[-1]
                    start -= len(word_before)

            # check ignore positions
            end_ignore_pos = False
            for pos in ignore_pos:
                if pos[1] >= start >= pos[0]:
                    skip = True
                    end_ignore_pos = pos[1]
                    if start == end_ignore_pos:
                        end_ignore_pos = False
                    break
            if env_type == 'figure2':
                start -= 1
            # check if definition of latex function
            if start_pattern:
                before = data[start - 15 - len(start_pattern):start - len(start_pattern)]
                before = before.replace(" ", "")
                if """\\newcommand{""" in before or """\\renewcommand{""" in before or """\\def""" in before:
                    skip = True
            # if skip make no coloring
            if skip:
                if end_ignore_pos:
                    start_pos = end_ignore_pos
                elif found == '':
                    start_pos = end + 1
                else:
                    start_pos = end
                continue
            else:
                vertices_ptrs.append((start, end))
                start_pos = end
                if 'footnote' in env_type and found == '' or start == end:
                    start_pos = end + 1
                if env_type == 'display':
                    start_pos += 2
        else:
            break
    return vertices_ptrs


def color_latex_code(data):
    # copy
    old_latex = copy.deepcopy(data)
    new_latex = []

    # modify header
    for index, row in enumerate(old_latex.split("\n")):
        if row.startswith("%"):
            row = '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
            new_latex.append(row)
            continue
        if '%' in row:
            temp_i = row.find('%')
            if row[temp_i - 1] != "\\":
                row = row[:temp_i]
                if all([characters in [" "] for characters in row]):
                    continue
        if "\\def\\thefootnote" in row:
            continue
        if '\\providecommand{\\LyX}' in row or '\\newcommand{\\LyX}' in row:
            lyx = True
        if "documentclass" in row:
            temp_i = row.find(']{')
            if temp_i > 0:
                temp_i += 2
                # row = f"{row[:temp_i]}article{row[-1]}"
            new_latex.append(row)
            new_latex.append(config_latex.LATEX_NO_COLOR)
        elif '\\usepackage[dvips]{graphicx}' in row:
            new_latex.append('\\usepackage{graphicx}')
        elif '\\usepackage{hyperref}' in row:
            new_latex.append('\\usepackage[hidelinks]{hyperref}')
        elif "documentstyle" in row:
            return "old_latex_version"
        else:
            new_latex.append(row)
    new_latex = "\n".join(new_latex)

    # colorize all non math text
    ignore_pos = get_ignore_positions(new_latex)
    color_patterns_non_math = {}
    for search_element in ["\\begin ", "\\end "]:
        new_latex = new_latex.replace(search_element, search_element[:-1])
    for key, value in config_latex.color_patterns.items():
        if 'inline' not in key and 'display' not in key:
            color_patterns_non_math[key] = value
    for key in color_patterns_non_math.keys():
        color_positions = process_environment(new_latex, config_latex.color_patterns[key], str(key), ignore_pos[key])
        new_latex = color_it(new_latex, {key: color_positions})

    # colorize display math formulas
    ignore_pos = get_ignore_positions(new_latex)
    color_patterns_math = {}
    for key, value in config_latex.color_patterns.items():
        if 'inline' in key or 'display' in key:
            color_patterns_math[key] = value
    color_positions = {key: process_environment(new_latex, config_latex.color_patterns[key], str(key), ignore_pos[key])
                       for key in color_patterns_math.keys()}
    color_positions = combine_color_positions(color_positions)
    new_latex = color_it(new_latex, color_positions)
    return new_latex


def combine_color_positions(color_positions):
    for key in color_positions.keys():
        if not color_positions[key]:
            continue
        while True:
            start = -1
            for ci, c in enumerate(color_positions[key]):
                if c[0] <= start:
                    color_positions[key][ci - 1] = (min(color_positions[key][ci - 1][0], color_positions[key][ci][0]),
                                                    max(color_positions[key][ci - 1][1], color_positions[key][ci][1]))
                    color_positions[key].pop(ci)
                    break
                start = c[1]
            if ci == len(color_positions[key]) - 1:
                break
    return color_positions


def get_ignore_positions(new_latex):
    ignore_positions = {}
    for key in config_latex.ignore_patterns.keys():
        ignore_pos = {k: find_ignore_pos(new_latex, config_latex.ignore_patterns[key][k])
                      for k in config_latex.ignore_patterns[key].keys()}
        if ", " in key:
            key = key.split(", ")
        else:
            key = [key]
        for k in key:
            if k not in ignore_positions:
                ignore_positions[k] = {}
            for kk in ignore_pos.keys():
                ignore_positions[k][kk] = ignore_pos[kk]
    for key in ignore_positions:
        if 'bea' in ignore_positions[key]:
            for pos_i, pos in enumerate(ignore_positions[key]['bea']):
                if new_latex[pos[0]:pos[1]].find('\\beq') > -1:
                    ignore_positions[key]['bea'][pos_i] = (pos[0], pos[0] + new_latex[pos[0]:pos[1]].find('\\beq'))
    ignore_pos = {key: [] for key in config_latex.color_patterns.keys()}
    for key in ignore_positions.keys():
        for v in ignore_positions[key].values():
            ignore_pos[key] += v
    return ignore_pos


def find_ignore_pos(data: str, search_pattern: str) -> Tuple[list, str]:
    """Process LaTeX environment."""
    vertices_ptrs = []
    start_pos = 0
    regex = re.compile(search_pattern)
    end_pattern = f"(?s)(?={search_pattern[search_pattern.find('.*?(?=') + 6:]}"
    if search_pattern == r"(?s)(?<=\$\$).*?(?=\$\$)":
        end_pattern == r"(?s)(?=\$\$)"
    while start_pos <= len(data):
        pattern = regex.search(data, pos=start_pos)
        # if found a pattern
        if pattern:
            # get start end position
            start, end = pattern.span()
            # check that no open brackets and $ exists
            while end_pattern:
                open_brackets = len([match for match in re.finditer('{', data[start:end]) if
                                     data[start + match.span()[0] - 1] != '\\'])
                closed_brackets = len([match for match in re.finditer('}', data[start:end]) if
                                       data[start + match.span()[0] - 1] != '\\'])
                dollar_signs = len([match for match in re.finditer('\$', data[start:end]) if
                                    data[start + match.span()[0] - 1] != '\\'])
                if open_brackets > closed_brackets or dollar_signs % 2 != 0:
                    new_end = re.search(end_pattern, data, pos=end + 1)
                    if new_end:
                        end = new_end.span()[0]
                    else:
                        break
                else:
                    break
            if start == end:
                start_pos = end + 1
                continue
            found = data[start:end]
            if '\\begin{document}' in found:
                start_pos = start + 1
                continue
            vertices_ptrs.append((start, end))
            start_pos = end
        else:
            break
    return vertices_ptrs


def color_it(data, color_positions):
    start_pos = 0
    result = ""
    while start_pos < len(data):
        color_positions = {key: value for key, value in color_positions.items() if value}
        if color_positions:
            key = list(color_positions.keys())[np.argmin([value[0][0] for key, value in color_positions.items()])]
            start = color_positions[key][0][0]
            end = color_positions[key][0][1]
            if not 'inline' in key:
                if 'start_correction' in config_latex.color[key]:
                    start += config_latex.color[key]['start_correction']
                if 'end_correction' in config_latex.color[key]:
                    end += config_latex.color[key]['end_correction']
            if key == 'inline_lyx':
                start -= 2
                end += 2
            if key == 'figure3':
                end += data[start:].find('}') - 1
                if '}' in data[end - 1:end]:
                    end -= 1
            head = data[start_pos:start]
            found = data[start:end]
            if 'inline' in key:
                result += f"{head}{config_latex.color['inline']['start']}{found}{config_latex.color['inline']['end']}"
            else:
                result += f"{head}{config_latex.color[key]['start']}{found}{config_latex.color[key]['end']}"
            start_pos = end
            color_positions[key].pop(0)

            for k in color_positions.keys():
                rerun = True
                while rerun:
                    rerun = False
                    if color_positions[k] and color_positions[k][0][0] < start_pos:
                        color_positions[k].pop(0)
                        rerun = True
        else:
            result += f"{data[start_pos:]}"
            start_pos = len(data)
    return result


def color_with_regex(main_tex: Path, config):
    """Process Latex source code and set color for math environments."""

    try:
        data = main_tex.read_text()
    except UnicodeDecodeError:
        shutil.rmtree(main_tex.parent)
        return 'Error'
    # NOTE: Make a black and white version
    vanilla_data = color_latex_code(data, True, config)
    # remove old latex versions
    if vanilla_data == 'old_latex_version':
        shutil.rmtree(main_tex.parent)
        return 'old_latex_version'
    vanilla_out = main_tex.parent / f"vanilla_{main_tex.name}"
    vanilla_out.write_text(vanilla_data)

    colored_data = color_latex_code(data, False, config)
    colored_out = main_tex.parent / f"colored_{main_tex.name}"
    colored_out.write_text(colored_data)
    return 'done'


def compile_pdf(source_dir: Path):
    """Compile source directory."""
    if source_dir is None:
        return False

    if source_dir.is_file():
        source_dir = source_dir.parent

    latexmk = subprocess.Popen(["latexmk", "-pdfdvi", "-interaction=nonstopmode", "-quiet", "-f"], cwd=source_dir,
                               stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        latexmk.wait(timeout=60)
        return True
    except subprocess.TimeoutExpired:
        latexmk.kill()
        return False
