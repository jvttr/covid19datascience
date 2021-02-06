from time import time
from datetime import date
import pandas as pd
import numpy as np
from xlsxwriter.worksheet import (
    Worksheet, cell_number_tuple, cell_string_tuple)

class Timer:
    def __init__(self):
        self.__start = time()
        self.__running = True

    def stop(self):
        if self.__running:
            self.__running = False
            self.__end = time()
            self.__time_elapsed = self.__end - self.__start
            return self.__time_elapsed
        else:
            print('Timer already stoped')

    def time(self):
        if not self.__running:
            return self.__time_elapsed
        else:
            return time() - self.__start

    def reset(self):
        self.__running = True
        self.__start = time()
        self.__end = 0

def isvaliddate(date,begin=date(2020,3,12),end=date.today()):
	if date != pd.NaT:
		if date >= begin and date <= end:
			return True
	return False

def get_better_notifica(df):
    scores = np.zeros(len(df))

    for i, serie in enumerate(df.iterrows()):
        _, row = serie

        if row['idade'] != -99:
            scores[i]+=50

        if row['nome_mae']:
            scores[i]+=50

        if row['cpf']:
            scores[i]+=50

        if not row['nome_mae'] and not row['cpf'] and row['data_nascimento'] == pd.NaT:
            scores-=500

        if row['cod_classificacao_final'] == 2:
            scores[i]+=100

        if row['cod_criterio_classificacao'] == 1:
            scores[i]+=10

        if row['cod_evolucao'] == 2:
            if row['data_cura_obito'] != pd.NaT:
                scores[i]+=1000
            else:
                scores[i]-=100

        if row['cod_metodo'] == 1:
            scores[i]+=10

        if row['cod_status_notificacao'] in [1, 2]:
            scores[i]+=10

        if row['excluir_ficha'] == 2:
            scores[i]+=10

        if row['cod_origem'] == 1:
            scores[i]+=10

        if row['data_1o_sintomas'] != pd.NaT:
            scores[i]+=50

        if row['data_coleta'] != pd.NaT:
            scores[i]+=40

        if row['data_recebimento'] != pd.NaT:
            scores[i]+=30

        if row['data_liberacao'] != pd.NaT:
            scores[i]+=20

    i = np.argmax(scores)
    return df.iloc[i].name


def get_column_width(worksheet: Worksheet, column: int):
    """Get the max column width in a `Worksheet` column."""
    strings = getattr(worksheet, '_ts_all_strings', None)
    if strings is None:
        strings = worksheet._ts_all_strings = sorted(
            worksheet.str_table.string_table,
            key=worksheet.str_table.string_table.__getitem__)
    lengths = set()
    for _, colums_dict in worksheet.table.items():  # type: int, dict
        data = colums_dict.get(column)
        if not data:
            continue
        if type(data) is cell_string_tuple:
            iter_length = len(strings[data.string])
            if not iter_length:
                continue
            lengths.add(iter_length)
            continue
        if type(data) is cell_number_tuple:
            iter_length = len(str(data.number))
            if not iter_length:
                continue
            lengths.add(iter_length)
    if not lengths:
        return None
    return max(lengths)

def set_column_autowidth(worksheet: Worksheet, column: int):
    """
    Set the width automatically on a column in the `Worksheet`.
    !!! Make sure you run this function AFTER having all cells filled in
    the worksheet!
    """
    maxwidth = get_column_width(worksheet=worksheet, column=column)
    if maxwidth is None:
        return
    worksheet.set_column(first_col=column, last_col=column, width=maxwidth)

def auto_fit_columns(wk,df):
    for i, _ in enumerate(df.columns):
        set_column_autowidth(wk,i)