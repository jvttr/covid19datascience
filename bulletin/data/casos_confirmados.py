from os.path import dirname, join, isfile
from datetime import datetime, timedelta
from unidecode import unidecode
from hashlib import sha256
import pandas as pd
import codecs

from sys import exit

from bulletin import __file__ as __root__
from bulletin.commom import static
from bulletin.commom.normalize import normalize_text, normalize_labels, normalize_number, normalize_municipios, normalize_igbe, trim_overspace

class CasosConfirmados:
    def __init__(self, pathfile:str=join(dirname(__root__),'tmp','Casos confirmados.xlsx')):
        self.pathfile = pathfile
        self.__source = None
        self.database = { 'casos': join(dirname(__root__),'tmp','casos.pkl'), 'obitos': join(dirname(__root__),'tmp','obitos.pkl')}
        self.checksum_file = join(dirname(__root__),'tmp','casos_confirmados_checksum')
        self.errorspath = ''

        if isfile(self.pathfile):
            saved_checksum = None
            if isfile(self.checksum_file):
                with open(self.checksum_file, "r") as checksum:
                    saved_checksum = checksum.read()
                    print(f"saved checksum: {saved_checksum}")

            with open(self.pathfile, "rb") as filein:
                bytes = filein.read()
                self.checksum = sha256(bytes).hexdigest()
                print(f"current checksum: {self.checksum}")

            if saved_checksum != self.checksum:
                print(f"Parece que o arquivo {self.pathfile} sofreu alterações, considere usar o método update")
            else:
                print(f"Tudo certo, nenhuma alteração detectada")

            if isfile(self.database['casos']) and isfile(self.database['obitos']):
                casos = pd.read_pickle(self.database['casos'])
                obitos = pd.read_pickle(self.database['obitos'])
                self.__source = { 'casos': casos, 'obitos': obitos }
                print(f"{self.database} carregado")
            else:
                print(f"{self.database} não encontrado, utilizando o método update")
                self.update()

        else:
            exit(f"{self.pathfile} não encontrado, insira o arquivo para dar continuidade")

    def shape(self):
        return (len(self.__source['casos']),len(self.__source['obitos']))

    def novos_casos(self, casos_raw):
        casos_confirmados =  self.__source['casos']
        casos_raw = casos_raw.sort_values(by='paciente')

        print(f"casos novos: {casos_raw.shape[0]}")

        print(f"casos novos duplicados: {casos_raw.loc[casos_raw.duplicated(subset='hash')].shape[0]}")
        casos_raw.loc[casos_raw.duplicated(subset='hash')].to_excel(join(self.errorspath,'casos_raw_duplicates.xlsx'))
        casos_raw = casos_raw.drop_duplicates(subset='hash')

        dropar = casos_raw.loc[casos_raw['data_liberacao'].isnull()]
        dropar.to_excel(join(self.errorspath,'casos_raw_sem_liberacao.xlsx'))
        print(f"casos novos sem diagnóstico: {dropar.shape[0]}")
        # casos_raw = casos_raw.drop(index=dropar.index)

        dropar = casos_raw.loc[casos_raw['nome_exame'].isnull()]
        dropar.to_excel(join(self.errorspath,'casos_raw_sem_nome_exame.xlsx'))
        print(f"casos novos sem laboratório: {dropar.shape[0]}")
        # casos_raw = casos_raw.drop(index=dropar.index)

        dropar = casos_raw.loc[casos_raw['sexo'].isnull()]
        print(f"casos novos sem sexo: {dropar.shape[0]}")
        dropar.to_excel(join(self.errorspath,'casos_raw_sem_sexo.xlsx'))
        # casos_raw = casos_raw.drop(index=dropar.index)

        print(f"casos novos validos: {casos_raw.shape[0]}")

        index_casos_duplicados = casos_raw.loc[casos_raw['hash'].isin(casos_confirmados['hash'])].index.to_list()
        print(f"casos já em casos com a mesma idade: {len(index_casos_duplicados)}")
        index_casos_duplicados_idade_less = casos_raw.loc[casos_raw['hash_less'].isin(casos_confirmados['hash'])].index.to_list()
        print(f"casos já em casos com a idade - 1: {len(index_casos_duplicados_idade_less)}")
        index_casos_duplicados_idade_more = casos_raw.loc[casos_raw['hash_more'].isin(casos_confirmados['hash'])].index.to_list()
        print(f"casos já em casos com a idade + 1: {len(index_casos_duplicados_idade_more)}")
        print(f"dentre os quais {len(set(index_casos_duplicados_idade_more).intersection(index_casos_duplicados)) + len(set(index_casos_duplicados_idade_less).intersection(index_casos_duplicados))} são casos em comum, o que leva a crer que estão duplicados na planilha já com idade a mais ou idade a menos")
        index_duplicados = list(set(index_casos_duplicados + index_casos_duplicados_idade_less + index_casos_duplicados_idade_more))
        print(f"sendo assim, {len(index_duplicados)} casos que já se encontram na planilha serão removidos")

        print(f"\nentão, de {len(casos_raw)} casos baixados hoje  {len(casos_raw)-len(index_duplicados)} serão adicionados\n")
        casos_raw = casos_raw.drop(index=index_duplicados)

        casos_raw['data_com'] = [ "" ] * len(casos_raw)
        novos_casos = casos_raw[['id','paciente','sexo','idade','mun_resid', 'mun_atend', 'rs', 'nome_exame','data_liberacao','data_com','data_1o_sintomas','hash']]
        novos_casos.to_excel('novos_casos.xlsx', index=False)

        return novos_casos

    def novos_obitos(self, novos_casos, obitos_raw):
        casos_confirmados =  self.__source['casos']
        obitos_confirmados = self.__source['obitos']
        obitos_raw = obitos_raw.sort_values(by='paciente')

        obitos_curitiba = pd.read_excel(join(dirname(__root__),'tmp','obitos_curitiba.xlsx'))

        obitos_curitiba['paciente'] = obitos_curitiba['paciente'].apply(lambda x: trim_overspace(normalize_text(x)))
        obitos_curitiba['mun_resid'] = obitos_curitiba['mun_resid'].apply(lambda x: trim_overspace(normalize_text(x)))
        obitos_curitiba['idade'] = obitos_curitiba['idade'].apply(normalize_number)

        obitos_curitiba['rs'] = obitos_curitiba['rs'].apply(lambda x: normalize_number(x,fill='99'))
        obitos_curitiba['rs'] = obitos_curitiba['rs'].apply(lambda x: str(x).zfill(2) if x != 99 else None)

        obitos_curitiba['hash'] = obitos_curitiba.apply(lambda row: sha256(str.encode(row['paciente']+str(row['idade'])+row['mun_resid'])).hexdigest(), axis=1)
        obitos_curitiba['hash_less'] = obitos_curitiba.apply(lambda row: sha256(str.encode(row['paciente']+str(row['idade']-1)+row['mun_resid'])).hexdigest(), axis=1)
        obitos_curitiba['hash_more'] = obitos_curitiba.apply(lambda row: sha256(str.encode(row['paciente']+str(row['idade']+1)+row['mun_resid'])).hexdigest(), axis=1)

        print(f"obitos novos notifica {obitos_raw.shape[0]} + {obitos_curitiba.shape[0]} curitiba\n")

        obitos_raw = obitos_raw.append(obitos_curitiba, ignore_index=True)

        obitos_raw_duplicates = obitos_raw.loc[obitos_raw.duplicated(subset='hash')]
        print(f"obitos novos duplicados: {obitos_raw_duplicates.shape[0]}")
        obitos_raw_duplicates.to_excel(join(self.errorspath,'obitos_raw_duplicates.xlsx'))
        obitos_raw = obitos_raw.drop_duplicates(subset='hash')

        index_obitos_duplicados = obitos_raw.loc[obitos_raw['hash'].isin(obitos_confirmados['hash'])].index.to_list()
        print(f"obitos já em obitos com a mesma idade: {len(index_obitos_duplicados)}")
        index_obitos_duplicados_idade_less = obitos_raw.loc[obitos_raw['hash_less'].isin(obitos_confirmados['hash'])].index.to_list()
        print(f"obitos já em obitos com a idade - 1: {len(index_obitos_duplicados_idade_less)}")
        index_obitos_duplicados_idade_more = obitos_raw.loc[obitos_raw['hash_more'].isin(obitos_confirmados['hash'])].index.to_list()
        print(f"obitos já em obitos com a idade + 1: {len(index_obitos_duplicados_idade_more)}")

        obitos_duplicados_idade_diferente = list(set(index_obitos_duplicados_idade_more).intersection(index_obitos_duplicados).union(set(index_obitos_duplicados_idade_less).intersection(index_obitos_duplicados)))
        if len(obitos_duplicados_idade_diferente) > 0:
            print(f"dentre os quais {len(obitos_duplicados_idade_diferente)} são obitos duplicados com idade diferente")

        index_idade_less = obitos_raw.loc[obitos_raw['hash_less'].isin(casos_confirmados['hash'])].index
        print(f"obitos que estão nos casos porém com um ano a menos {index_idade_less.shape[0]}")
        if len(index_idade_less) > 0:
            obitos_raw.loc[index_idade_less,'idade'] -= 1
            obitos_raw.loc[index_idade_less,'hash'] = obitos_raw.loc[index_idade_less].apply(lambda row: sha256(str.encode(row['paciente']+str(row['idade'])+row['mun_resid'])).hexdigest(), axis=1)

        index_idade_more = obitos_raw.loc[obitos_raw['hash_more'].isin(casos_confirmados['hash'])].index
        print(f"obitos que estão nos casos porém com um ano a mais {index_idade_more.shape[0]}")
        if len(index_idade_more) > 0:
            obitos_raw.loc[index_idade_more,'idade'] += 1
            obitos_raw.loc[index_idade_more,'hash'] = obitos_raw.loc[index_idade_less].apply(lambda row: sha256(str.encode(row['paciente']+str(row['idade'])+row['mun_resid'])).hexdigest(), axis=1)

        obitos_nao_casos = obitos_raw.loc[~(obitos_raw['hash'].isin(casos_confirmados['hash']) | obitos_raw['hash'].isin(novos_casos['hash']))]
        obitos_nao_casos.to_excel(join(self.errorspath,'obitos_nao_casos.xlsx'))
        print(f"obitos que não estão nos casos {obitos_nao_casos.shape[0]}")

        index_duplicados = list(set(index_obitos_duplicados + index_obitos_duplicados_idade_less + index_obitos_duplicados_idade_more + obitos_nao_casos.index.to_list()))
        print(f"sendo assim, {len(index_duplicados) + len(obitos_raw_duplicates)} obitos que já se encontram na planilha serão removidos")
        print(f"\nentão, de {len(obitos_raw) - len(obitos_curitiba) + len(obitos_raw_duplicates)} obitos baixados hoje + {len(obitos_curitiba)} inseridos de Curitiba, {len(obitos_raw)-len(index_duplicados)-len(obitos_nao_casos)} serão adicionados\n")
        obitos_raw = obitos_raw.drop(index=index_duplicados)


        novos_obitos = obitos_raw[['id','paciente','sexo','idade','mun_resid', 'rs', 'data_cura_obito','hash']]
        novos_obitos.to_excel('novos_obitos.xlsx', index=False)

        return novos_obitos


    def relatorio(self, novos_casos, novos_obitos):
        casos_confirmados =  self.__source['casos']
        casos_exclucoes = casos_confirmados.loc[casos_confirmados['mun_resid'] == 'EXCLUIR']
        casos_confirmados = casos_confirmados.drop(index=casos_exclucoes.index)

        casos_confirmadosPR = casos_confirmados.loc[casos_confirmados['rs'].notnull()]

        obitos_confirmados =  self.__source['obitos']
        obitos_exclucoes = obitos_confirmados.loc[obitos_confirmados['municipio'] == 'EXCLUIR']
        obitos_confirmados = obitos_confirmados.drop(index=obitos_exclucoes.index)

        obitos_confirmadosPR = obitos_confirmados.loc[obitos_confirmados['rs'].notnull()]

        print(f"Casos confirmados excluidos: {len(casos_exclucoes)}")
        print(f"Total de casos: {len(casos_confirmados)} + {len(novos_casos)}")

        print(f"Obitos confirmados excluidos: {len(obitos_exclucoes)}")
        print(f"Total de obitos: {len(obitos_confirmados)} + {len(novos_obitos)}\n\n")


        novos_casosPR = novos_casos.loc[novos_casos['rs'].notnull()].copy()
        print(f"Total de casos PR: {len(casos_confirmadosPR)} + {len(novos_casosPR)}")

        novos_obitosPR = novos_obitos.loc[novos_obitos['rs'].notnull()].copy()
        print(f"Total de obitos PR: {len(obitos_confirmadosPR)} + {len(novos_obitosPR)}")

        novos_casosFora = novos_casos.loc[novos_casos['rs'].isnull()].copy()
        print(f"Total de casos Fora: {len(casos_confirmados) - len(casos_confirmadosPR)} + {len(novos_casosFora)}")

        novos_obitosFora = novos_obitos.loc[novos_obitos['rs'].isnull()].copy()
        print(f"Total de obitos Fora: {len(obitos_confirmados) - len(obitos_confirmadosPR)} + {len(novos_obitosFora)}")

        novos_obitosPR_group = novos_obitosPR.groupby(by='mun_resid')
        today = datetime.today()
        ontem = today - timedelta(1)
        anteontem = ontem - timedelta(1)


        retroativos = novos_casosPR.loc[(novos_casosPR['data_liberacao'] <= anteontem)].sort_values(by='data_liberacao')

        with codecs.open(f"relatorio_{(today.strftime('%d/%m/%Y_%Hh').replace('/','_').replace(' ',''))}.txt","w","utf-8-sig") as relatorio:
            relatorio.write(f"{len(novos_casosPR):,} novos casos residentes divulgados ".replace(',','.'))

            if len(novos_casosFora) > 0:
                relatorio.write(f"e {len(novos_casosFora):,} não residente{'s' if len(novos_casosFora) > 1 else ''} ".replace(',','.'))
            relatorio.write(f"no PR.")

            if len(retroativos) > 0:
                relatorio.write(f" Sendo:\n")
                relatorio.write(f"Em {today.strftime('%d/%m/%Y')}: {len(novos_casosPR.loc[(novos_casosPR['data_liberacao'] > anteontem)])} novos casos confirmados.\n")
                relatorio.write(f"{len(retroativos)} casos retroativos confirmados do período de {retroativos.iloc[0]['data_liberacao'].strftime('%d/%m/%Y')} à {retroativos.iloc[-1]['data_liberacao'].strftime('%d/%m/%Y')}.\n")
            else:
                relatorio.write(f" \n")

            relatorio.write(f"{len(casos_confirmadosPR)+len(novos_casosPR):,} casos confirmados residentes do PR.\n".replace(',','.'))
            relatorio.write(f"{len(casos_confirmados)+len(novos_casos):,} total geral.\n\n".replace(',','.'))
            relatorio.write(f"{len(novos_obitosPR):,} Óbitos residentes do PR:\n".replace(',','.'))

            for municipio, obitos in novos_obitosPR_group:
                relatorio.write(f"{len(obitos):,} {municipio}\n".replace(',','.'))

            if len(novos_obitosFora) > 0:
                relatorio.write(f"{len(novos_obitosFora):,} Óbito{'s' if len(novos_obitosFora) > 1 else ''} não residente{'s' if len(novos_obitosFora) > 1 else ''} do PR.\n\n".replace(',','.'))

            relatorio.write(f"{len(obitos_confirmadosPR)+len(novos_obitosPR):,} óbitos residentes do PR.\n".replace(',','.'))
            relatorio.write(f"{len(obitos_confirmados)+len(novos_obitos):,} total geral.\n\n".replace(',','.'))

            for _, row in novos_obitos.iterrows():
                relatorio.write(f"{row['sexo']}\t{row['idade']}\t{row['mun_resid'] if row['rs'] else row['mun_resid'] + ' - Fora'}\t{row['rs'] if row['rs'] else ''}\t{row['data_cura_obito'].day}/{static.meses[row['data_cura_obito'].month-1]}\n")
            relatorio.write('\n')


            if len(retroativos) > 0:
                novos_casosPR['month'] = novos_casosPR.apply(lambda x: x['data_liberacao'].month, axis=1)
                relatorio.write('Casos por meses:\n')
                for group, value in novos_casosPR.groupby(by='month'):
                    relatorio.write(f"{static.meses[int(group)-1]}: {len(value)}\n")
                relatorio.write('\n')

                relatorio.write('Obitos por meses:\n')
                novos_obitosPR['month'] = novos_obitosPR.apply(lambda x: x['data_cura_obito'].month, axis=1)
                for group, value in novos_obitosPR.groupby(by='month'):
                    relatorio.write(f"{static.meses[int(group)-1]}: {len(value)}\n")
                relatorio.write('\n')

                for group, value in novos_casosPR.groupby(by='data_liberacao'):
                    relatorio.write(f"{group.strftime('%d/%m/%Y')}\t{len(value)}\n")

        with codecs.open(f"relatorio_{(today.strftime('%d/%m/%Y_%Hh').replace('/','_').replace(' ',''))}.txt","r","utf-8-sig") as relatorio:
            print("\nrelatorio:\n")
            print(relatorio.read())

    def update(self):
        print(f"Atualizando o arquivo {self.database} com o {self.pathfile}...")

        # casos = pd.read_excel(self.pathfile,'Casos confirmados',usecols='B,C,D,F,G')
        casos = pd.read_excel(self.pathfile,
                            'Casos confirmados',
                            usecols='B,C,D,F,G',
                            converters = {
                               'Nome': normalize_text,
                               'Idade': normalize_number,
                               'IBGE_RES_PR': normalize_igbe,
                               'Mun Resid': normalize_municipios
                            })

        casos.columns = [ normalize_labels(x) for x in casos.columns ]
        casos = casos.rename(columns={'rs_res_pr': 'rs'})

        # casos = casos.loc[casos['mun_resid'] != 'EXCLUIR']

        municipios = static.municipios.copy()[['ibge','uf','municipio']]
        municipios['municipio'] = municipios['municipio'].apply(normalize_text)

        # casosPR = casos.loc[casos['ibge_res_pr'] != -1].copy()
        # municipiosPR = municipios.loc[municipios['uf']=='PR']
        # casosPR = pd.merge(left=casosPR, right=municipiosPR, how='left', left_on='ibge_res_pr', right_on='ibge')


        # casosFora = casos.loc[casos['ibge_res_pr'] == -1].copy()
        # municipiosFora = municipios.loc[municipios['uf']!='PR']
        # casosFora = pd.merge(left=casosFora, right=municipiosFora, how='left', left_on='mun_resid', right_on='municipio')

        # casos = casosPR.append(casosFora, ignore_index=True).sort_values(by='nome')
        # casos = casos.drop(columns=(['ibge_res_pr']))

        casos['hash'] = casos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade'])+row['mun_resid'])).hexdigest(), axis=1)
        casos['hash_less'] = casos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade']-1)+row['mun_resid'])).hexdigest(), axis=1)
        casos['hash_more'] = casos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade']+1)+row['mun_resid'])).hexdigest(), axis=1)

        obitos = pd.read_excel(self.pathfile,
                            'Obitos',
                            usecols='B,C,D,F,G,I',
                            converters = {
                               'Nome': normalize_text,
                               'Idade': normalize_number,
                               'IBGE_RES_PR': normalize_igbe,
                               'Município': normalize_municipios
                            })

        obitos.columns = [ normalize_labels(x) for x in obitos.columns ]
        obitos = obitos.rename(columns={'rs_res_pr': 'rs'})

        # obitos = obitos.loc[obitos['municipio'] != 'EXCLUIR']

        obitos['hash'] = obitos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade'])+row['municipio'])).hexdigest(), axis=1)
        obitos['hash_less'] = obitos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade']-1)+row['municipio'])).hexdigest(), axis=1)
        obitos['hash_more'] = obitos.apply(lambda row: sha256(str.encode(row['nome']+str(row['idade']+1)+row['municipio'])).hexdigest(), axis=1)


        # index_idade_less = obitos.loc[obitos['hash_less'].isin(casos['hash'])].index
        # obitos.loc[index_idade_less,'idade'] -= 1
        # obitos.loc[index_idade_less,'hash'] = obitos.loc[index_idade_less].apply(lambda row: sha256(str.encode(row['nome']+str(row['idade'])+row['municipio'])).hexdigest(), axis=1)

        # index_idade_more = obitos.loc[obitos['hash_more'].isin(casos['hash'])].index
        # obitos.loc[index_idade_more,'idade'] += 1
        # obitos.loc[index_idade_more,'hash'] = obitos.loc[index_idade_more].apply(lambda row: sha256(str.encode(row['nome']+str(row['idade'])+row['municipio'])).hexdigest(), axis=1)

        # obitos1 = obitos[['hash','data_do_obito']]
        # casos = pd.merge(left=casos, right=obitos1, how='left', on='hash')

        casos.to_pickle(self.database['casos'])
        obitos.to_pickle(self.database['obitos'])

        with open(self.checksum_file, "w") as checksum:
            checksum.write(self.checksum)

        print(f"{self.database} salvo e {self.checksum_file} atualizado")

        self.__source = { 'casos': casos, 'obitos': obitos }

    def get_casos(self):
        try:
            return self.__source['casos'].copy()
        except:
            exit("Fonte de dados não encontrada, primeiro utilize o método update")

    def get_obitos(self):
        try:
            return self.__source['obitos'].copy()
        except:
            exit("Fonte de dados não encontrada, primeiro utilize o método update")
    #
    # def get_recuperados(self):
    #     try:
    #         return self.__source.loc[self.__source['evolucao'] == 1].copy()
    #     except e:
    #         exit("Fonte de dados não encontrada, primeiro utilize o método update")
    #
    # def get_casos_ativos(self):
    #     try:
    #         return self.__source.loc[self.__source['evolucao'] == 3].copy()
    #     except e:
    #         exit("Fonte de dados não encontrada, primeiro utilize o método update")
    #
    # def get_obitos_nao_covid(self):
    #     try:
    #         return self.__source.loc[self.__source['evolucao'] == 4].copy()
    #     except e:
    #         exit("Fonte de dados não encontrada, primeiro utilize o método update")