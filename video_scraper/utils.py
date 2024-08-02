from datetime import datetime

# Mapeamento dos meses em português para os equivalentes numéricos
MONTHS = {
    'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04',
    'mai.': '05', 'jun.': '06', 'jul.': '07', 'ago.': '08',
    'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
}

def parse_date(date_str):
    """Converte uma data em português para o formato dd/mm/yyyy."""
    parts = date_str.split(' ')
    day = parts[0]
    month = MONTHS[parts[2]]
    year = parts[4]
    return f'{day}/{month}/{year}'
