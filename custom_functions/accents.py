def remove_accents(text):
    """
    Metoda służąca do usuwania polskich znaków
    Pomysł: http://gentle.pl/2017/07/19/usuwanie_polskich_znakow_python.html
    """
    accents = 'ąćęłńóśźż'
    replacements = 'acelnoszz'
    translator = str.maketrans(accents, replacements)
    return text.translate(translator)