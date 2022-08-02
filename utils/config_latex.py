"""regrex search"""
import copy

color_patterns = {
    # double_dollar_only: r"(?<![\$])\$\$([^$]+)\$\$(?!\$)",
    "display": r"(?s)(?<=\$\$).*?(?=\$\$)",  # regrex for $$ ... $$
    'display_lyx': r"(?s)(?<=\\\[).*?(?=\\\])",  # for \[...\]
    "inline": r"(\${1,2})(?:(?!\1)[\s\S])*\1",  # regrex for $ ... $
    'inline_lyx': r"(?s)(?<=\\\().*?(?=\\\))",  # for lyx \( ... \),
    'inline_qed': r"\\qed",
    'section': r"(?s)(?<=\\section\{).*?(?=\})",  # for \section{...}
    'section2': r"(?s)(?<=\\section\*\{).*?(?=\})",
    'section3': r"(?s)(?<=\\resection\{).*?(?=\})",
    'section4': r"(?s)(?<=\\begin\{section\}\{).*?(?=\})",
    'subsection': r"(?s)(?<=\\subsection\{).*?(?=\})",  # for \subsection{...}
    'subsection2': r"(?s)(?<=\\subsection\*\{).*?(?=\})",
    'subsection3': r"(?s)(?<=\\begin\{subsection\}\{).*?(?=\})",
    'subsubsection': r"(?s)(?<=\\subsubsection\{).*?(?=\})",  # for \subsubsection{...}
    'subsubsection2': r"(?s)(?<=\\subsubsection\*\{).*?(?=\})",
    'subsubsection3': r"(?s)(?<=\\begin\{subsubsection\}\{).*?(?=\})",
    "figure": r"(?s)(?<=\\includegraphics\[).*?(?=\])",  # for \includegraphics[...]
    "figure2": r"(?s)(?<=\\includegraphics\{).*?(?=\})",
    "figure3": r"(?s)(?<=\\EPSFIGURE\[).*?(?=\])",  # for \EPSFIGURE[...],
    "figure4": r"(?s)(?<=\\epsfig\{).*?(?=\})",  # for \epsfig{...}
    "figure5": r"(?s)(?<=\\begin\{picture\}).*?(?=\\end\{picture\})",  # for \epsfig{...}
    "figure6": r"(?s)(?<=\\psfig\{).*?(?=\})",  # for \psfig{...}
    "figure7": r"(?s)(?<=\\epsfbox\{).*?(?=\})",  # for \epsfbox{...}
    "footnote": r"(\${1,2})(?:(?!\1)[\s\S])*\1",  # regrex for $ ... $
    "footnote2": r"(?s)(?<=\\renewcommand\{\\thefootnote\}\{).*?(?=\})",  # regrex for $ ... $
    "footnote3": r"(?s)(?<=\\footnote\{).*?(?=\})",
    "table": r"(?s)(?<=\\begin\{tabular\}).*?(?=\\end\{tabular\})",
    "table2": r"(?s)(?<=\\begin\{table\}).*?(?=\\end\{table\})",
    "table3": r"(?s)(?<=\\begin\{longtable\}).*?(?=\\end\{longtable\})",
    "caption": r"(?s)(?<=\\caption\{).*?(?=\})",
    "caption2": r"(?s)(?<=\parbox\{).*?(?=\})"
}

ignore_patterns = {
    #'tabular': r"(?s)(?<=\\begin\{tabular\}).*?(?=\\end\{tabular\})",  # regrex for \begin{tabular} ... \end{tabular}
    #'table': r"(?s)(?<=\\begin\{table\}).*?(?=\\end\{table\})",  # regrex for \begin{table} ... \end{table}
    #'item': r"(?s)(?<=\\item\[).*?(?=\])",  # regrex for \item[...]
    #  'figure': r"(?s)(?<=\\begin\{figure\}).*?(?=\\end\{figure\})",  # regrex for \begin{figure} ... \end{figure}
    'inline, inline_lyx, display, display_lyx': {'beq': r"(?s)(?<=\\beq).*?(?=\\eeq)",
                                                 'figure': r"(?s)(?<=\\begin\{picture\}).*?(?=\\end\{picture\})",
                                                 'tabular': r"(?s)(?<=\\begin\{tabular\}).*?(?=\\end\{tabular\})",
                                                 'longtable': r"(?s)(?<=\\begin\{longtable\}).*?(?=\\end\{longtable\})",
                                                 'defeqnarray': r"(?s)(?<=\\def\\eqnarray\{).*?(?=\})"},
    'inline, inline_lyx': {'equation': r"(?s)(?<=\\begin\{equation\}).*?(?=\\end\{equation\})",
                           'align': r"(?s)(?<=\\begin\{align\}).*?(?=\\end\{align\})",
                            'bea': r"(?s)(?<=\\bea).*?(?=\\eea)",
                            'bea{': r"(?s)(?<=\\bea\{).*?(?=\\eea)",
                            'be{': r"(?s)(?<=\\be\{).*?(?=\\ee)",
                           'bibitem': r"(?s)(?<=\\bibitem\[).*?(?=\])",
                           'ifcase': r"(?s)(?<=\\ifcase ).*?(?=\\fi)"},
    'table, table2, table3': {'align': r"(?s)(?<=\\begin\{align\}).*?(?=\\end\{align\})",
                              'beq': r"(?s)(?<=\\beq).*?(?=\\eeq)",
                        'bea': r"(?s)(?<=\\bea).*?(?=\\eea)",
                              'equation': r"(?s)(?<=\\begin\{equation\}).*?(?=\\end\{equation\})",
                                'display': r"(?s)(?<=\$\$).*?(?=\$\$)"},
    'display, display_lyx': {'figure': r"(?s)(?<=\\begin\{figure\}).*?(?=\\end\{figure\})"},
    'figure5': {'display': r"(?s)(?<=\$\$).*?(?=\$\$)"}

}


def ignore_content(content, env_type):
    if 'inline' in env_type:
        if content[:2] == '$$' and content[-2:] == '$$':
            return True
        if "\\ref{" in content:
            return True
        if "\\cite{" in content:
            return True
        if check_if_footnote(content):
            return True
        if content[0] == '(' and content[-1] == ')' and content[1:-1].isnumeric():
            return True
        if content[0] == '[' and content[-1] == ']' and content[1:-1].isnumeric():
            return True
        temp = copy.copy(content)
        temp = temp.replace(" ", "").replace('$', '').replace('{', '').replace('}', '')
        if temp == "\\bullet":
            return True
        if temp == "^\\prime":
            return True
        if temp[:8] == "^{\\rule{" and temp.find("}{") and temp[-2:] == "}}":
            return True
    if env_type == 'subsection' or env_type == 'section' or env_type == 'subsubsection':
        if content == '':
            return True
    if env_type == 'footnote':
        if check_if_footnote(content):
            return False
        temp = copy.copy(content)
        temp = temp.replace(" ", "").replace('$', '')
        if temp[:8] == "^{\\rule{" and temp.find("}{") and temp[-2:] == "}}":
            return False
        if "^" == content[1]:
            temp = content.replace(" ", "")
            if temp[2] == "{" and temp[-2] == "}" and temp[2:-2].find("}") == -1 and temp[2:-2].isnumeric():
                return False
        return True
    if env_type == 'footnote2':
        if "\\textcolor{footnote_color" in content:
            return True
    if env_type == 'display_lyx':
        if '\epsfxsize' in content or '\parbox' in content or '\epsfxsize' in content or '\epsfbox' in content:
            return True
    return False


def check_if_footnote(possible_footnote):
    possible_footnote = possible_footnote.replace("{", "").replace("}", "").replace(" ", "").replace("\\,", "").replace(",", "").replace("$", "").replace("\\strut", "").replace("\\!", "").replace("\\phantom", "").replace(".", "").replace("\\;", "")
    if len(possible_footnote) > 1 and (possible_footnote[0] == "^" and possible_footnote[1:].isnumeric() or possible_footnote[0] == "^" and len(possible_footnote) < 5):
        return True
    if possible_footnote == "^\\dagger":
        return True
    return False


"""color entries"""
color = {
    'display': {'start': "\\textcolor{display}{", 'end': "}"},
    'display_lyx': {'start': "\\textcolor{display}{", 'end': "}"},
    'inline': {'start': "\\textcolor{inline}{", 'end': "}"},
    'section': {'start': "\\textcolor{header1}{", 'end': "}", 'start_correction': -9},
    'section2': {'start': "\\textcolor{header1*}{", 'end': "}", 'start_correction': -10},
    'section3': {'start': "\\textcolor{header1}{", 'end': "}", 'start_correction': -11},
    'section4': {'start': "\\textcolor{header1}{", 'end': "}", 'start_correction': 0},
    'subsection': {'start': "\\textcolor{header2}{", 'end': "}", 'start_correction': -12},
    'subsection2': {'start': "\\textcolor{header2*}{", 'end': "}", 'start_correction': -13},
    'subsection3': {'start': "\\textcolor{header2}{", 'end': "}", 'start_correction': 0},
    'subsubsection': {'start': "\\textcolor{header3}{", 'end': "}", 'start_correction': -15},
    'subsubsection2': {'start': "\\textcolor{header3*}{", 'end': "}", 'start_correction': -16},
    'subsubsection3': {'start': "\\textcolor{header3}{", 'end': "}", 'start_correction': 0},
    'figure': {'start': "", 'end': ", cfbox=figure 1pt 0pt"},
    'figure2': {'start': "[cfbox=figure 1pt 0pt]", 'end': ""},
    'figure3': {'start': "", 'end': ", cfbox=figure 1pt 0pt", 'end_correction': 0},
    'figure4': {'start': "cfbox=figure 1pt 0pt, ", 'end': ""},
    'figure5': {'start': "\\fcolorbox{figure}{white}{", 'end': "}", 'start_correction': -15, 'end_correction': 13},
    'figure6': {'start': "cfbox=figure 1pt 0pt, ", 'end': ""},
    'figure7': {'start': "\\fcolorbox{figure}{white}{", 'end': "}", 'start_correction': -9},
    'caption': {'start': "\\textcolor{caption}{", 'end': "}", 'start_correction': -9},
    'caption2': {'start': "\\textcolor{caption}{", 'end': "}"},
    'footnote': {'start': "\\textcolor{footnote_color}{", 'end': "}"},
    'footnote2': {'start': "\\textcolor{footnote_color}{", 'end': "}"},
    'footnote3': {'start': "\\textcolor{footnote_color}{", 'end': "}"},
    'table': {'start': "\\textcolor{table}{", 'end': "}", 'start_correction': -15, 'end_correction': 13},
    'table2': {'start': "\\color{table}", 'end': "\\color{black}", 'start_correction': 0, 'end_correction': 0},
    'table3': {'start': "\\textcolor{table}{", 'end': "}", 'start_correction': -17, 'end_correction': 15},
    'list': {'start': "\\textcolor{list}{", 'end': "}", 'start_correction': -15, 'end_correction': 13}
}

"""remove custom margin expressions"""
# custom margin expression. Remove to make the format more similar
custom_margin = ['\\textwidth', '\\textheight', '\\hoffset', '\\voffset', '\\oddsidemargin', '\\parindent',
                 '\\evensidemargin', '\\topmargin']

"""new latex header"""
_LATEX_PACKAGES = r"""
\usepackage{xcolor}
\usepackage{etoolbox}
\usepackage{sectsty}
\usepackage[export]{adjustbox}
\usepackage[font={color=caption,bf}]{caption}
"""
_LATEX_COLOR = r"""
\definecolor{display}{RGB}{255,0,255}
\definecolor{inline0}{RGB}{0,255,0}
\definecolor{inline1}{RGB}{0,250,0}
\definecolor{inline2}{RGB}{0,245,0}
\definecolor{inline3}{RGB}{0,240,0}
\definecolor{inline4}{RGB}{0,235,0}
\definecolor{inline5}{RGB}{0,230,0}
\definecolor{inline6}{RGB}{0,225,0}
\definecolor{inline7}{RGB}{0,220,0}
\definecolor{inline8}{RGB}{0,215,0}
\definecolor{inline9}{RGB}{0,210,0}
\definecolor{inline10}{RGB}{0,205,0}
\definecolor{inline11}{RGB}{0,200,0}
\definecolor{inline12}{RGB}{0,195,0}
\definecolor{inline13}{RGB}{0,190,0}
\definecolor{inline14}{RGB}{0,185,0}
\definecolor{inline15}{RGB}{0,180,0}
\definecolor{inline16}{RGB}{0,175,0}
\definecolor{inline17}{RGB}{0,170,0}
\definecolor{inline18}{RGB}{0,165,0}
\definecolor{inline19}{RGB}{0,160,0}
\definecolor{table}{RGB}{0,0,255}
\definecolor{figure}{RGB}{255,0,0}
\definecolor{header1}{RGB}{240,255,0}
\definecolor{header2}{RGB}{220,255,0}
\definecolor{header3}{RGB}{200,255,0}
\definecolor{header1*}{RGB}{230,255,0}
\definecolor{header2*}{RGB}{210,255,0}
\definecolor{header3*}{RGB}{190,255,0}
\definecolor{caption}{RGB}{0,240,255}
\definecolor{footnote_color}{RGB}{0,120,240}
\definecolor{bibliography}{RGB}{255,100,0}
\definecolor{list}{RGB}{255,0,120}
"""

_LATEX_NO_COLOR = r"""
\definecolor{display}{RGB}{0,0,0}
\definecolor{inline}{RGB}{0,0,0}
\definecolor{inline1}{RGB}{0,0,0}
\definecolor{inline2}{RGB}{0,0,0}
\definecolor{inline3}{RGB}{0,0,0}
\definecolor{inline4}{RGB}{0,0,0}
\definecolor{inline5}{RGB}{0,0,0}
\definecolor{inline6}{RGB}{0,0,0}
\definecolor{inline7}{RGB}{0,0,0}
\definecolor{inline8}{RGB}{0,0,0}
\definecolor{inline9}{RGB}{0,0,0}
\definecolor{inline10}{RGB}{0,0,0}
\definecolor{inline11}{RGB}{0,0,0}
\definecolor{inline12}{RGB}{0,0,0}
\definecolor{inline13}{RGB}{0,0,0}
\definecolor{inline14}{RGB}{0,0,0}
\definecolor{inline15}{RGB}{0,0,0}
\definecolor{inline16}{RGB}{0,0,0}
\definecolor{inline17}{RGB}{0,0,0}
\definecolor{inline18}{RGB}{0,0,0}
\definecolor{inline19}{RGB}{0,0,0}
\definecolor{table}{RGB}{0,0,0}
\definecolor{figure}{RGB}{255,255,255}
\definecolor{header1}{RGB}{0,0,0}
\definecolor{header2}{RGB}{0,0,0}
\definecolor{header3}{RGB}{0,0,0}
\definecolor{caption}{RGB}{0,0,0}
\definecolor{footnote_color}{RGB}{0,0,0}
\definecolor{bibliography}{RGB}{0,0,0}
\definecolor{list}{RGB}{0,0,0}
"""
_LATEX_ENV = r"""
\renewcommand\footnoterule{\color{footnote_color}\kern-3pt \hrule width 2in \kern 2.6pt}
\renewcommand\thefootnote{\textcolor{footnote_color}{\arabic{footnote}}}
\AtBeginEnvironment{eqnarray}{\color{display}}
\AtBeginEnvironment{eqnarray*}{\color{display}}
\AtBeginEnvironment{equation}{\color{display}}
\AtBeginEnvironment{equation*}{\color{display}}
\AtBeginEnvironment{align}{\color{display}}
\AtBeginEnvironment{align*}{\color{display}}
\AtBeginEnvironment{flalign}{\color{display}}
\AtBeginEnvironment{flalign*}{\color{display}}
\AtBeginEnvironment{gather}{\color{display}}
\AtBeginEnvironment{gather*}{\color{display}}
\AtBeginEnvironment{multline}{\color{display}}
\AtBeginEnvironment{multline*}{\color{display}}
\AtBeginEnvironment{alignat}{\color{display}}
\AtBeginEnvironment{alignat*}{\color{display}}
\AtBeginEnvironment{eqalign}{\color{display}}
\AtBeginEnvironment{eqalign*}{\color{display}}
\AtBeginEnvironment{eqalignno}{\color{display}}
\AtBeginEnvironment{eqalignno*}{\color{display}}
\AtBeginEnvironment{aligned}{\color{display}}
\AtBeginEnvironment{aligned*}{\color{display}}
\AtBeginEnvironment{be}{\color{display}}
\AtBeginEnvironment{bea}{\color{display}}
\AtBeginEnvironment{beq}{\color{display}}
\AtBeginEnvironment{beeq}{\color{display}}
\AtBeginEnvironment{ber}{\color{display}}
\AtBeginEnvironment{beqa}{\color{display}}
\AtBeginEnvironment{displaymath}{\color{display}}
\AtBeginEnvironment{subeqnarray}{\color{display}}
\AtBeginEnvironment{figure}{\color{caption}}
\AtBeginEnvironment{figure*}{\color{caption}}
\AtBeginEnvironment{table}{\color{table}}
\AtBeginEnvironment{thebibliography}{\color{bibliography}}
\AtBeginEnvironment{itemize}{\color{list}}
\AtBeginEnvironment{enumerate}{\color{list}}
\AtBeginEnvironment{description}{\color{list}}
"""

LATEX_COLOR = _LATEX_PACKAGES + _LATEX_COLOR + _LATEX_ENV
LATEX_NO_COLOR = _LATEX_PACKAGES + _LATEX_NO_COLOR + _LATEX_ENV
