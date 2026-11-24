#!/usr/bin/env python3
"""Replaces cover student name placeholders with handwriting rules in source templates."""
from pathlib import Path
root=Path(__file__).resolve().parent
old1=r'{\small Ученик: \texttt{ФИО\_Ученика}}\par'
new1=r'{\small Ученик:\enspace\rule[-.8ex]{85mm}{.4pt}}\par'
old2=r'{\small\color{mbink}Лёвин Артём Александрович эксклюзивно для ФИО\_Ученика}\par'
new2=r'{\small\color{mbink}Лёвин Артём Александрович эксклюзивно для\enspace\rule[-.8ex]{70mm}{.4pt}}\par'
for file in ['build_book.py','apply_style33.py','book.tex']:
    p=root/file
    s=p.read_text(encoding='utf-8')
    assert s.count(old1)==1,(file,'top',s.count(old1))
    assert s.count(old2)==1,(file,'bottom',s.count(old2))
    s=s.replace(old1,new1).replace(old2,new2)
    if file in ['build_book.py','apply_style33.py']:
        s=s.replace("'student_placeholder':'ФИО_Ученика'", "'student_name_field':'blank_line_for_handwriting'")
    p.write_text(s,encoding='utf-8')
qa=root/'qa'/'check_style33.py'; s=qa.read_text(encoding='utf-8')
s=s.replace("'title_has_student_placeholder':'ФИО_Ученика' in full,", "'title_has_blank_student_field':r'\\rule[-.8ex]{85mm}{.4pt}' in tex and 'Ученик:' in texts[0] and 'ФИО_Ученика' not in texts[0],")
s=s.replace("'title_has_required_attribution':'Лёвин Артём Александрович эксклюзивно для ФИО_Ученика' in full,", "'title_has_blank_attribution_field':r'\\rule[-.8ex]{70mm}{.4pt}' in tex and 'Лёвин Артём Александрович эксклюзивно для' in texts[0],")
qa.write_text(s,encoding='utf-8')
readme=root/'README.md';s=readme.read_text(encoding='utf-8').replace('Титул с незаполненным полем `ФИО_Ученика` согласно правилу не выдумывать ФИО.', 'Титул содержит две пустые линии для заполнения имени ученика от руки — в поле «Ученик» и после авторской подписи.');readme.write_text(s,encoding='utf-8')
print('Updated source templates and QA')
