#!/usr/bin/env python3
"""One-time, reproducible source migration to 06_REFERENCE_STYLE.md Academic 3.3."""
from pathlib import Path
p=Path(__file__).with_name('build_book.py')
s=p.read_text(encoding='utf-8')

mini = r'''
# Each theory subsection ends with exactly three original mini-exercises and short answers.
THEORY_MINI = [
 [(r'Назовите тип записи $4+5=9$.',r'Истинное числовое высказывание.'),
  (r'Доказывает ли проверка $n=1,2$ формулу для всех целых $n$?',r'Нет, проверены два случая.'),
  (r'Как обосновать $n+0=n$ для произвольного $n$?',r'Свойством нуля при сложении.')],
 [(r'Является ли запись $x+1=3$ замкнутым высказыванием?',r'Нет, переменная свободна.'),
  (r'Что означает $x\in\mathbb Z$?',r'Переменная принимает целые значения.'),
  (r'Верно ли $x^2\ge x$ для всех $x\in\mathbb R$?',r'Нет, $x=\tfrac12$ — контрпример.')],
 [(r'Укажите натуральный свидетель $n^2=16$.',r'$n=4$.'),
  (r'Истинно ли $\forall n\in\mathbb N\colon n+1>n$?',r'Да, прибавление $1>0$ увеличивает число.'),
  (r'Существует ли наибольшее целое число?',r'Нет: для любого $m$ число $m+1$ больше.')],
 [(r'Опровергает ли $x=0$ условие $x^2>0$ на $\mathbb R$?',r'Да, $0^2=0$.'),
  (r'Можно ли проверять натуральное число значением $-1$?',r'Нет, $-1\notin\mathbb N$.'),
  (r'Становится ли гипотеза ложной, если доказательство пока неизвестно?',r'Нет.')],
 [(r'Достаточно ли трёх примеров для универсального утверждения о $\mathbb N$?',r'Нет.'),
  (r'Достаточен ли перебор всех $x\in\{0,1\}$?',r'Да, если область состоит ровно из двух элементов.'),
  (r'Истинно ли $x^2>0$ при $x=0$?',r'Нет.')],
 [(r'Что следует из $a=b$ после прибавления $2$?',r'$a+2=b+2$.'),
  (r'Верно ли $x^2=9\Rightarrow x=3$ для вещественных $x$?',r'Нет, также $x=-3$.'),
  (r'Что должно завершать математическое доказательство?',r'Ровно тот вывод, который требовалось доказать.')],
 [(r'Раскройте квадрат $(a+1)^2$.',r'$a^2+2a+1$.'),
  (r'Докажите $x^2+2x+1\ge0$.',r'Это $(x+1)^2\ge0$.'),
  (r'Можно ли сократить $0x=0y$ на нуль?',r'Нет, деление на нуль запрещено.')],
 [(r'Следует ли $x>5\Rightarrow x>3$?',r'Да, по транзитивности.'),
  (r'Верно ли обратное $x>3\Rightarrow x>5$?',r'Нет, $x=4$.'),
  (r'Если $a=b$, обязательно ли $a^2=b^2$?',r'Да, возведение в квадрат сохраняет равенство.')],
 [(r'Чётно ли $n(n+1)$ для любого целого $n$?',r'Да, один из множителей чётный.'),
  (r'Вычислите $(-1)\cdot0$.',r'$0$.'),
  (r'Истинно ли $x^2\ge0$ при всех $x\in\mathbb R$?',r'Да, квадрат неотрицателен.')],
 [(r'Равные диагонали всегда означают прямоугольник?',r'Нет, например, у равнобедренной трапеции они равны.'),
  (r'Можно ли обосновать параллельность словами «видно на рисунке»?',r'Нет, нужно условие или доказательство.'),
  (r'Может ли рисунок служить подсказкой?',r'Да, если вывод затем обоснован.')],
 [(r'Почему нельзя делить на произвольный $a$ без проверки?',r'$a$ может быть нулём.'),
  (r'Сколько корней у $x^2=4$ над $\mathbb R$?',r'Два: $2$ и $-2$.'),
  (r'Что проверяют после нахождения кандидатов?',r'Допустимость и подстановку каждого ответа.')],
 [(r'Что указывают перед универсальным доказательством?',r'Произвольный объект и его область.'),
  (r'Нужно ли объяснять неочевидный переход?',r'Да, указать применённое правило.'),
  (r'Что писать в заключении?',r'Точную требуемую формулировку.')],
 [(r'Что полезно сделать после прочитанного решения?',r'Воспроизвести ключевое рассуждение самостоятельно.'),
  (r'В каком случае достаточно одного контрпримера?',r'Для опровержения утверждения «для всех».'),
  (r'Какая тема следует за этим уроком?',r'Контрпримеры, прямые и обратные утверждения.')],
]
assert len(THEORY_MINI)==len(THEORY)==13 and all(len(t)==3 for t in THEORY_MINI)

# Nine learning blocks reuse all 90 canonical problems without changing their IDs.
FLOW_BLOCKS = [
 ('Высказывание и область', 'Проверка истинности', 'Определите область и смысл записи',
  'Есть свободная переменная?', 'Уточните значение или квантор', 'Вычислите и обоснуйте результат',
  'Сформулируйте точный статус'),
 ('Существование и конечная проверка', 'Поиск свидетельства', 'Назовите требуемый объект',
  'Подходит конкретный свидетель?', 'Проверьте все условия', 'Исследуйте допустимую область',
  'Докажите существование или невозможность'),
 ('Прямое доказательство и контрпример', 'Выбор способа', 'Выделите квантор и заключение',
  'Требуется «для всех»?', 'Возьмите произвольный объект', 'Поищите допустимый контрпример',
  'Запишите общий аргумент или опровержение'),
 ('Алгебра и ограничения', 'Проверка переходов', 'Запишите предпосылки и равенства',
  'Все операции допустимы?', 'Выполните преобразования', 'Уточните область и делитель',
  'Проверьте каждую математическую стрелку'),
 ('Следствие, обратное, кванторы', 'Анализ логики', 'Разделите предпосылку и вывод',
  'Нужно обратное утверждение?', 'Проверьте обратную стрелку', 'Докажите только прямой вывод',
  'Различайте «следует» и «равносильно»'),
 ('Полнота и случаи', 'Контроль доказательства', 'Укажите область и варианты',
  'Все случаи перечислены?', 'Проверьте каждый случай', 'Найдите пропущенную границу',
  'Сделайте вывод для всей области'),
 ('Кванторы и синтез', 'Управление зависимостями', 'Запишите кванторы в нужном порядке',
  'Свидетель зависит от переменной?', 'Постройте свидетель после выбора', 'Проверьте постоянный кандидат',
  'Обоснуйте итог с правильными кванторами'),
 ('Границы и единственность', 'Полное решение', 'Получите список кандидатов',
  'Все кандидаты допустимы?', 'Проверьте подстановкой', 'Отбросьте нарушающие условие',
  'Докажите отсутствие остальных решений'),
 ('Олимпиадное доказательство', 'Построение идеи', 'Разделите цель на условия',
  'Есть универсальный механизм?', 'Используйте тождество или оценку', 'Ищите крайний допустимый случай',
  'Сверьте необходимость, достаточность и итог'),
]
assert len(FLOW_BLOCKS)==9
'''
needle='assert len(THEORY_ANSWERS)==len(THEORY)==13'
assert needle in s
s=s.replace(needle,mini+'\n'+needle,1)
s=s.replace("'theory':THEORY,'examples':EXAMPLES", "'theory':THEORY,'theory_mini':THEORY_MINI,'flow_blocks':FLOW_BLOCKS,'examples':EXAMPLES",1)
# PDFLaTeX-compatible standalone source and exact Academic 3.3 geometry/palette.
s=s.replace(r'\documentclass[12pt,a4paper,openany]{book}',r'\documentclass[11pt,a4paper,openany]{book}')
s=s.replace(r'\usepackage[margin=22mm,top=22mm,bottom=22mm,headheight=15pt,headsep=8mm]{geometry}',r'\usepackage{geometry}'+'\n'+r'\geometry{left=20mm,right=20mm,top=20mm,bottom=22mm}'+'\n'+r'\setlength{\headheight}{14pt}'+'\n'+r'\setlength{\headsep}{5mm}')
old=r'''\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{russian}
\setotherlanguage{english}
\setmainfont{Noto Serif}
\setsansfont{PT Sans}
\setmonofont{DejaVu Sans Mono}[Scale=.79]'''
new=r'''\usepackage[utf8]{inputenc}
\usepackage[T2A]{fontenc}
\usepackage[russian]{babel}
\usepackage{dejavu}'''
assert old in s
s=s.replace(old,new,1)
s=s.replace(r'\usepackage{booktabs,longtable,array,multicol,enumitem}',r'\usepackage{booktabs,tabularx,longtable,array,multicol,enumitem,needspace,lastpage,bookmark}')
s=s.replace(r'\definecolor{mbaccent}{HTML}{08796D}',r'\definecolor{mbaccent}{HTML}{486780}')
s=s.replace(r'\definecolor{mbgold}{HTML}{A76C29}',r'\definecolor{mbgold}{HTML}{66798B}')
s=s.replace(r'\definecolor{mbpurple}{HTML}{7656A0}',r'\definecolor{mbpurple}{HTML}{486780}')
s=s.replace(r'\definecolor{mbpale}{HTML}{EEF7F4}',r'\definecolor{mbpale}{HTML}{F8FAFB}')
s=s.replace(r'\definecolor{mbcream}{HTML}{FBF3E7}',r'\definecolor{mbcream}{HTML}{FFFFFF}')
s=s.replace(r'\definecolor{mbink}{HTML}{152A31}',r'\definecolor{mbink}{HTML}{243447}')
s=s.replace(r'\definecolor{mbmuted}{HTML}{546670}',r'\definecolor{mbmuted}{HTML}{66798B}'+'\n'+r'\definecolor{mbline}{HTML}{BAC9D4}')
s=s.replace(r'\usepackage[colorlinks=true,linkcolor=mbaccent,urlcolor=mbaccent]{hyperref}',r'\usepackage[colorlinks=true,linkcolor=mbaccent,urlcolor=mbaccent,pdfencoding=auto]{hyperref}'+'\n'+r'\hypersetup{pdftitle={Что такое математическое доказательство? Истинность утверждений},pdfauthor={Лёвин Артём Александрович},pdfsubject={Пособие для самостоятельного изучения олимпиадной математики},pdfkeywords={математическое доказательство, логика, олимпиада, Math Blast}}')
start=s.index(r'\pagestyle{fancy}\fancyhf{}')
end=s.index(r'\begin{document}',start)
s=s[:start]+r'''\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{mbmuted}Математическая логика}
\fancyhead[R]{\small\color{mbmuted}Доказательства и истинность}
\fancyfoot[C]{\small\color{mbmuted}\thepage\,/\,\pageref{LastPage}}
\renewcommand{\headrulewidth}{.35pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{mbline}\leaders\hrule height \headrulewidth\hfill}}
\setlength{\parindent}{0pt}\setlength{\parskip}{.43em}
\linespread{1.21}\setlength{\jot}{7pt}
\setcounter{secnumdepth}{2}\setcounter{tocdepth}{2}
\setlist[itemize]{leftmargin=*,topsep=4pt,itemsep=3pt}
\setlist[enumerate]{leftmargin=*,topsep=5pt,itemsep=4pt}
\newtcolorbox{keybox}[1][]{enhanced,breakable,colback=white,colframe=white,
  borderline west={.7pt}{0pt}{mbaccent},arc=0pt,boxrule=0pt,left=3.5mm,right=3mm,top=1.5mm,bottom=1.5mm,#1}
\newtcolorbox{learnbox}[1][]{enhanced,breakable,colback=white,colframe=white,
  borderline west={.5pt}{0pt}{mbline},arc=0pt,boxrule=0pt,left=3.5mm,right=3mm,top=1.5mm,bottom=1.5mm,#1}
\newcommand{\mtag}[1]{\textsf{\small\color{mbaccent}\bfseries #1}}
\newcommand{\muid}[1]{\texttt{\footnotesize #1}}
\renewcommand{\arraystretch}{1.38}
\setlength{\emergencystretch}{1.2em}
\newcommand{\mathshowcase}{%
\[\begin{aligned}
(a+b)^2 &= (a+b)(a+b)\\
        &= a^2+ab+ba+b^2\\
        &= a^2+2ab+b^2.
\end{aligned}\]}
''' + s[end:]
s=s.replace(r'\frontmatter'+'\n','',1).replace(r'\mainmatter'+'\n','',1)
start=s.index(r'\thispagestyle{empty}'+'\n')
end=s.index(r'\chapter*{Как пользоваться книгой}',start)
cover=r'''\thispagestyle{empty}
\begin{center}
\vspace*{23mm}
{\small\color{mbaccent}\bfseries MATH BLAST / УЧЕБНОЕ ПОСОБИЕ}\par
\vspace{21mm}
{\fontsize{26}{34}\selectfont\bfseries Что такое математическое\\[3mm] доказательство?}\par
\vspace{6mm}
{\fontsize{17}{24}\selectfont Истинность утверждений}\par
\vspace{20mm}
\begin{tikzpicture}[x=1cm,y=1cm]
\draw[mbaccent,line width=.65pt] (-5,0) .. controls (-2.8,1.45) and (-1.4,-1.0) .. (0,.1)
  .. controls (1.5,1.2) and (3.1,-.75) .. (5,0);
\end{tikzpicture}\par
\vspace{22mm}
{\small\color{mbmuted}Олимпиадная математика с нуля / 10–11 классы}\par
\vspace{3mm}
{\small Модуль 01 · Неделя 01 · Занятие 01 / 144}\par
\vspace{3mm}
{\small 30 разобранных примеров · 90 задач с полными решениями}\par
\vspace{17mm}
{\small Ученик:\enspace\rule[-.8ex]{85mm}{.4pt}}\par
\vspace{5mm}
{\small 20 ноября 2026 года}\par
\vfill
{\small\color{mbink}Лёвин Артём Александрович эксклюзивно для\enspace\rule[-.8ex]{70mm}{.4pt}}\par
\vspace{10mm}
\end{center}
\clearpage
'''
s=s[:start]+cover+s[end:]
# Make book.tex autonomous: embed the TikZ text rather than using external includes.
look = next(line for line in s.splitlines() if 'figures/' in line and "ch['fig']" in line and 'emit(' in line)
s = s.replace(look, r"    emit('\\begin{center}\n'+FIGURES[ch['fig']]+'\n\\end{center}\n')", 1)
# Three original mini-exercises with immediate short answers.
needle=next(line for line in s.splitlines() if 'Проверьте понимание.' in line and 'emit(' in line)
addon = "\n".join([
    r"    emit('\\Needspace{9\\baselineskip}\n\\subsection*{Мини-тренировка: три коротких шага}\n\\begin{enumerate}[label=\\arabic*),leftmargin=*,itemsep=3pt]\n')",
    r"    for q,a in THEORY_MINI[i-1]:",
    r"        emit('\\item '+plain(q)+' \\textit{('+plain(a)+')}\n')",
    r"    emit('\\end{enumerate}\n')",
])
s = s.replace(needle, needle+'\n'+addon,1)
find=next(line for line in s.splitlines() if "for p in ch['paragraphs']:emit" in line)
s=s.replace(find,find+'\n'+r"    if i==7:"+'\n'+r"        emit('\\noindent\\textbf{Образец записи вычисления по шагам.}\n\\mathshowcase\n')",1)
# New standalone 9 algorithm pages and 9 ten-task training blocks, plus 4-col tables.
a=s.index("for lev in ['A','B','C','D']:\n    emit(")
b=s.index("\nemit(r'''\\chapter{Подсказки: открывайте последовательно}",a)
new=r"""for block_i, (block_title, start_text, action_text, gate_text, yes_text, no_text, finish_text) in enumerate(FLOW_BLOCKS,1):
    members=PROBLEMS[(block_i-1)*10:block_i*10]
    assert len(members)==10
    # Stand-alone instructional flowchart page; no exercises on this page.
    emit('\\clearpage\\phantomsection\\addcontentsline{toc}{section}{Алгоритм '+str(block_i)+': '+plain(block_title)+'}\\n')
    emit('\\section*{Алгоритм '+str(block_i)+'. '+plain(block_title)+'}\\n')
    emit('\\vspace{18mm}\\begin{center}\\n')
    emit(r'''\begin{tikzpicture}[>=Stealth,
      flowstart/.style={ellipse,draw=mbaccent,line width=.6pt,align=center,text width=47mm,minimum height=12mm},
      flowstep/.style={rounded corners=3pt,rectangle,draw=mbline,line width=.6pt,align=center,text width=58mm,minimum height=14mm},
      flowdecision/.style={diamond,aspect=2.1,draw=mbaccent,line width=.7pt,align=center,text width=33mm,inner sep=1mm},
      flowbranch/.style={rectangle,rounded corners=3pt,draw=mbline,line width=.6pt,align=center,text width=49mm,minimum height=20mm},
      flowarrow/.style={-{Stealth[length=2.7mm]},draw=mbaccent,line width=.65pt}]
''')
    emit('\\node[flowstart] (start) at (0,0) {'+plain(start_text)+'};\\n')
    emit('\\node[flowstep] (act) at (0,-2) {'+plain(action_text)+'};\\n')
    emit('\\node[flowdecision] (gate) at (0,-4.4) {'+plain(gate_text)+'};\\n')
    emit('\\node[flowbranch] (yes) at (-4.0,-7.4) {'+plain(yes_text)+'};\\n')
    emit('\\node[flowbranch] (no) at (4.0,-7.4) {'+plain(no_text)+'};\\n')
    emit('\\node[flowstart] (finish) at (0,-10.1) {'+plain(finish_text)+'};\\n')
    emit(r'''\draw[flowarrow] (start)--(act);
\draw[flowarrow] (act)--(gate);
\draw[flowarrow] (gate.south west)--node[above left,sloped,font=\footnotesize]{да}(yes.north);
\draw[flowarrow] (gate.south east)--node[above right,sloped,font=\footnotesize]{нет}(no.north);
\draw[flowarrow] (yes.south) |- ([xshift=-12mm]finish.north);
\draw[flowarrow] (no.south) |- ([xshift=12mm]finish.north);
\end{tikzpicture}
''')
    emit('\\end{center}\\par\\vspace{7mm}\\noindent\\textit{Что заметить:} '+plain(action_text)+'. '+plain(finish_text)+'.\\n')
    emit('\\clearpage\\section{Тренировочный блок '+str(block_i)+' · '+plain(block_title)+'}\\n')
    emit('\\textit{Десять задач: от первого применения метода к самостоятельной проверке.}\\par\\n')
    for p in members:
        emit('\\Needspace{4\\baselineskip}\\noindent\\hypertarget{'+p['id']+'}{}\\muid{'+p['id']+'}\\quad '+plain(p['topic'])+'\\par\\n')
        emit(plain(p['prompt'])+'\\par\\medskip\\n')
    emit('\\clearpage\\section*{Ответы к тренировочному блоку '+str(block_i)+'}\\n')
    emit('\\addcontentsline{toc}{subsection}{Ответы к тренировочному блоку '+str(block_i)+'}\\n')
    emit('\\begingroup\\footnotesize\\renewcommand{\\arraystretch}{1.45}\\n')
    emit('\\begin{tabularx}{\\textwidth}{@{}p{10mm}X p{10mm}X@{}}\\toprule № & Ответ / идея & № & Ответ / идея\\\\\\midrule\\n')
    for j in range(5):
        lhs=members[j];rhs=members[j+5]
        emit(str((block_i-1)*10+j+1)+' & '+plain(lhs['answer'])+' & '+str((block_i-1)*10+j+6)+' & '+plain(rhs['answer'])+'\\\\\\n')
    emit('\\bottomrule\\end{tabularx}\\endgroup\\n')
"""
s=s[:a]+new+s[b:]
# Adapt table visual to booktabs + tabularx already used above, keep longtables for exhaustive appendix.
# Align compiler with pdfLaTeX and preserve build logs.
s=s.replace('"""Math Blast / MB-W01-L1. Reproducible XeLaTeX builder.', '"""Math Blast / MB-W01-L1. Reproducible pdfLaTeX Academic 3.3 builder.')
s=s.replace("['xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','book.tex']", "['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','book.tex']")
s=s.replace("f'xelatex-pass-{n+1}.log'", "f'pdflatex-pass-{n+1}.log'")
s=s.replace("print('xelatex pass'", "print('pdflatex pass'")
s=s.replace(" 'build_command':'python build_book.py --compile',", " 'style_name':'Академический 3.3','style_source':'06_REFERENCE_STYLE.md','mini_exercises':39,'algorithm_pages':9,'training_blocks':9,'build_engine':'pdfLaTeX','student_name_field':'blank_line_for_handwriting',\n 'build_command':'python build_book.py --compile',")
p.write_text(s,encoding='utf-8')
print('Patched generator',p,'size',len(s))
