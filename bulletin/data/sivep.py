#-----------------------------------------------------------------------------------------------------------------------------#
# Classe de tratamento de dados do SIVEP-Gripe Paraná
# Todos os direitos reservados ao autor
#-----------------------------------------------------------------------------------------------------------------------------#

from os.path import dirname, join, isdir
from datetime import datetime
from os import makedirs
import pandas as pd
from simpledbf import Dbf5
from bulletin import __file__ as __root__
from bulletin.commom import static

class sivep:
    
    def __init__(self, pathfile=''):
        self.__source = None
        self.pathfile = pathfile
        self.database = join(dirname(__root__),'resources','database','sivep.pkl')
        self.errorspath = join('output','errors','sivep',datetime.today().strftime('%B_%Y'))

        if not isdir(self.errorspath):
            makedirs(self.errorspath)

        if not isdir(dirname(self.database)):
            makedirs(dirname(self.database))

    def __len__(self):
        return len(self.__source)

    def read(self,pathfile, append=False):
        srag = Dbf5(pathfile, codec = 'cp860').to_dataframe()

        if isinstance(self.__source, pd.DataFrame) and append:
            self.__source = self.__source.append(srag, ignore_index=True)
        else:
            self.__source = srag
    
    def read_all_database_files(self):
        last_digit = ['0', '1']

        for x in last_digit:
            self.read(join('input','dbf',f"SRAG202{x}.dbf"), append=True)

    def load(self):
        try:
            self.__source = pd.read_pickle(self.database)
        except:
            raise Exception(f"Arquivo {self.database} não encontrado")

    def save(self, df=None):
        if isinstance(df, pd.DataFrame) and len(df) > 0:
            new_df = df
            self.__source = new_df
        elif isinstance(self.__source, pd.DataFrame) and len(self.__source) > 0:
            new_df = self.__source
        else:
            raise Exception('Não é possível salvar um DataFrame inexistente, realize a leitura antes ou passe como para esse método')

        new_df.to_pickle(self.database)
    
    def to_notifica(self):
        self.__source = self.__source[['NU_NOTIFIC', 'DT_NOTIFIC', 'DT_SIN_PRI', 'SG_UF_NOT', 'CO_MUN_NOT', 'ID_UNIDADE',
            'NU_CPF', 'NM_PACIENT', 'CS_SEXO', 'DT_NASC', 'NU_IDADE_N', 'TP_IDADE', 'CS_GESTANT',
            'CS_RACA', 'CS_ETINIA', 'NM_MAE_PAC', 'NU_CEP', 'ID_PAIS', 'SG_UF',
            'CO_MUN_RES', 'NM_BAIRRO', 'NM_LOGRADO', 'NU_NUMERO', 'FEBRE', 'TOSSE',
            'GARGANTA', 'DISPNEIA', 'DESC_RESP', 'SATURACAO', 'DIARREIA', 'VOMITO',
            'OUTRO_SIN', 'PUERPERA', 'CARDIOPATI', 'SIND_DOWN', 'HEPATICA', 'DIABETES',
            'NEUROLOGIC', 'PNEUMOPATI', 'IMUNODEPRE', 'RENAL', 'OBESIDADE', 'OUT_MORBI',
            'ANTIVIRAL', 'TP_ANTIVIR', 'HOSPITAL', 'UTI', 'RAIOX_RES', 'AMOSTRA', 
            'DT_COLETA', 'REQUI_GAL', 'DT_PCR', 'TP_FLU_PCR', 'PCR_PARA1',
            'PCR_PARA2', 'PCR_PARA3', 'PCR_PARA4', 'PCR_ADENO', 'PCR_METAP', 'PCR_RESUL',
            'PCR_RINO', 'PCR_OUTRO', 'LAB_PCR', 'CLASSI_FIN', 'CRITERIO', 'EVOLUCAO',
            'DT_EVOLUCA', 'DT_ENCERRA', 'NOME_PROF', 'HISTO_VGM', 'LO_PS_VGM', 'DT_VGM',
            'DT_RT_VGM', 'PCR_SARS2', 'PAC_COCBO', 'PERD_OLFT', 'PERD_PALA', 'TOMO_RES', 'NU_DO']]

        self.__source = self.__source.rename(
            columns={
                'NU_NOTIFIC': 'id',
                'LAB_PCR': 'lab_executor',
                'DT_NOTIFIC': 'data_notificacao',
                'DT_SIN_PRI': 'data_1o_sintomas',
                'CO_MUN_NOT': 'ibge_unidade_notifica',
                'ID_UNIDADE': 'nome_unidade_notifica',
                'NU_CPF': 'cpf',
                'NM_PACIENT': 'paciente',
                'CS_SEXO': 'sexo',
                'DT_NASC': 'data_nascimento',
                'CS_RACA': 'raca_cor',
                'NM_MAE_PAC': 'nome_mae',
                'NU_CEP': 'cep_residencia',
                'CO_MUN_RES': 'ibge_residencia',
                'NM_BAIRRO': 'bairro_residencia',
                'NM_LOGRADO': 'logradouro_residencia',
                'NU_NUMERO': 'numero_residencia',
                'FEBRE': 'febre',
                'TOSSE': 'tosse',
                'GARGANTA': 'dor_garganta',
                'DISPNEIA': 'dispneia',
                'SATURACAO': 'saturacao_o2',
                'DIARREIA': 'diarreia',
                'VOMITO': 'nausea_vomitos',
                'OUTRO_SIN': 'outros_sintomas',
                'PUERPERA': 'puerperio',
                'CARDIOPATI': 'doenca_cardiovascular',
                'SIND_DOWN': 'sindrome_down',
                'HEPATICA': 'doenca_hepatica',
                'DIABETES': 'diabetes',
                'NEUROLOGIC': 'doenca_neurologica',
                'PNEUMOPATI': 'doenca_pulmonar',
                'IMUNODEPRE': 'imunodeficiencia',
                'RENAL': 'doenca_renal',
                'OBESIDADE': 'obesidade',
                'OUT_MORBI': 'outras_morbidades',
                'HOSPITAL': 'hospitalizado',
                'AMOSTRA': 'coleta_amostra',
                'DT_COLETA': 'data_coleta',
                'REQUI_GAL': 'requisicao',
                'DT_PCR': 'data_liberacao',
                'DT_EVOLUCA': 'data_cura_obito',
                'DT_ENCERRA': 'data_encerramento',
                'NOME_PROF': 'nome_notificador',
                'HISTO_VGM': 'historico_viagem',
                'LO_PS_VGM': 'local_viagem',
                'DT_VGM': 'data_ida_local',
                'DT_RT_VGM': 'data_retorno_local',
                'PERD_OLFT': 'perda_olfato_paladar',
                'NU_DO': 'numero_do',
                'PAC_COCBO': 'cod_cbo'
            })

        self.__source.loc[self.__source['EVOLUCAO'] == '1', 'evolucao'] = '1'
        self.__source.loc[self.__source['EVOLUCAO'] == '2', 'evolucao'] = '2'
        self.__source.loc[self.__source['EVOLUCAO'] == '3', 'evolucao'] = '4'
        self.__source.loc[self.__source['EVOLUCAO'] == '9', 'evolucao'] = '3'
        self.__source.loc[self.__source['EVOLUCAO'].isnull(), 'evolucao'] = '3'

        self.__source.loc[(self.__source['TP_IDADE'] == '1') | (self.__source['TP_IDADE'] == '2'), 'idade'] = 0
        self.__source['NU_IDADE_N'] = pd.to_numeric(self.__source['NU_IDADE_N'], downcast = 'integer')
        self.__source.loc[self.__source['TP_IDADE'] == '3', 'idade'] = self.__source['NU_IDADE_N']

        self.__source.loc[self.__source['ANTIVIRAL'] == '1', 'uso_antiviral'] = '1'
        self.__source.loc[self.__source['ANTIVIRAL'] == '2', 'uso_antiviral'] = '2'
        self.__source.loc[self.__source['ANTIVIRAL'] == '9', 'uso_antiviral'] = '0'
        self.__source.loc[self.__source['TP_ANTIVIR'] == '1', 'uso_antiviral'] = '3'
        self.__source.loc[self.__source['TP_ANTIVIR'] == '2', 'uso_antiviral'] = '0'
        self.__source.loc[self.__source['TP_ANTIVIR'] == '3', 'uso_antiviral'] = '0'
        self.__source.loc[(self.__source['TP_ANTIVIR'].isnull()) | (self.__source['ANTIVIRAL'].isnull()), 'uso_antiviral'] = '0'

        self.__source.loc[self.__source['RAIOX_RES'] == '1', 'raiox_torax'] = '1'
        self.__source.loc[self.__source['RAIOX_RES'] == '4', 'raiox_torax'] = '2'
        self.__source.loc[self.__source['RAIOX_RES'] == '2', 'raiox_torax'] = '3'
        self.__source.loc[self.__source['RAIOX_RES'] == '3', 'raiox_torax'] = '4'
        self.__source.loc[self.__source['RAIOX_RES'] == '5', 'raiox_torax'] = '5'
        self.__source.loc[(self.__source['RAIOX_RES'].isnull()) | (self.__source['RAIOX_RES'] == '6') | (self.__source['RAIOX_RES'] == '9'), 'raiox_torax'] = '0'

        self.__source.loc[self.__source['CLASSI_FIN'] == '1', 'classificacao_final'] = '3'
        self.__source.loc[self.__source['CLASSI_FIN'] == '2', 'classificacao_final'] = '3'
        self.__source.loc[self.__source['CLASSI_FIN'] == '3', 'classificacao_final'] = '3'
        self.__source.loc[self.__source['CLASSI_FIN'] == '4', 'classificacao_final'] = '5'
        self.__source.loc[self.__source['CLASSI_FIN'] == '5', 'classificacao_final'] = '2'
        self.__source.loc[self.__source['CLASSI_FIN'].isnull(), 'classificacao_final'] = '1'

        self.__source.loc[self.__source['CRITERIO'] == '1', 'criterio_classificacao'] = '1'
        self.__source.loc[self.__source['CRITERIO'] == '2', 'criterio_classificacao'] = '2'
        self.__source.loc[self.__source['CRITERIO'] == '3', 'criterio_classificacao'] = '6'
        self.__source.loc[self.__source['CRITERIO'] == '4', 'criterio_classificacao'] = '5'
        self.__source.loc[self.__source['CRITERIO'].isnull(), 'criterio_classificacao'] = '3'

        self.__source.loc[self.__source['TOMO_RES'] == 1, 'tomografia'] = '1'
        self.__source.loc[((self.__source['TOMO_RES'] == 2) | (self.__source['TOMO_RES'] == 3) |
                 (self.__source['TOMO_RES'] == 4) | (self.__source['TOMO_RES'] == 5)), 'tomografia'] = '4'
        self.__source.loc[((self.__source['TOMO_RES'] == 6) | (self.__source['TOMO_RES'] == 9) | (self.__source['TOMO_RES'] == 0)), 'tomografia'] = '0'

        self.__source.loc[self.__source['CS_GESTANT'] == '0', 'gestante'] = '3'
        self.__source.loc[(self.__source['CS_GESTANT'] == '1') | (self.__source['CS_GESTANT'] == '2') | (self.__source['CS_GESTANT'] == '3') |
                 (self.__source['CS_GESTANT'] == '4'), 'gestante'] = '1'
        self.__source.loc[self.__source['CS_GESTANT'] == '5', 'gestante'] = '2'
        self.__source.loc[(self.__source['CS_GESTANT'] == '6') | (self.__source['CS_GESTANT'] == '9'), 'gestante'] = '3'

        self.__source.loc[self.__source['CS_GESTANT'] == '1', 'periodo_gestacao'] = '1'
        self.__source.loc[self.__source['CS_GESTANT'] == '2', 'periodo_gestacao'] = '2'
        self.__source.loc[self.__source['CS_GESTANT'] == '3', 'periodo_gestacao'] = '3'
        self.__source.loc[self.__source['CS_GESTANT'] == '4', 'periodo_gestacao'] = '4'
        self.__source.loc[(self.__source['gestante'] == '2') | (self.__source['gestante'] == '3'), 'periodo_gestacao'] = '0'

        self.__source.loc[self.__source['PCR_RESUL'] == '1', 'resultado'] = '12'
        self.__source.loc[self.__source['PCR_RESUL'] == '2', 'resultado'] = '13'
        self.__source.loc[self.__source['PCR_RESUL'] == '3', 'resultado'] = '14'
        self.__source.loc[((self.__source['PCR_RESUL'] == '4') | (self.__source['PCR_RESUL'] == '5') | (self.__source['PCR_RESUL'] == '9') |
                (self.__source['PCR_RESUL'].isnull())), 'resultado'] = ''
        self.__source.loc[self.__source['TP_FLU_PCR'] == '1', 'resultado'] = '1'
        self.__source.loc[self.__source['TP_FLU_PCR'] == '2', 'resultado'] = '2'
        self.__source.loc[self.__source['PCR_PARA1'] == '1', 'resultado'] = '5'
        self.__source.loc[self.__source['PCR_PARA2'] == '1', 'resultado'] = '5'
        self.__source.loc[self.__source['PCR_PARA3'] == '1', 'resultado'] = '5'
        self.__source.loc[self.__source['PCR_PARA4'] == '1', 'resultado'] = '5'
        self.__source.loc[self.__source['PCR_ADENO'] == '1', 'resultado'] = '3'
        self.__source.loc[self.__source['PCR_METAP'] == '1', 'resultado'] = '7'
        self.__source.loc[self.__source['PCR_RINO'] == '1', 'resultado'] = '6'
        self.__source.loc[self.__source['PCR_OUTRO'] == '1', 'resultado'] = '10'
        self.__source.loc[self.__source['PCR_SARS2'] == '1', 'resultado'] = '9'

        self.__source.loc[self.__source['raca_cor'] == '3', 'raca_cor'] = '-1'
        self.__source.loc[self.__source['raca_cor'] == '4', 'raca_cor'] = '3'
        self.__source.loc[self.__source['raca_cor'] == '-1', 'raca_cor'] = '4'
        self.__source.loc[self.__source['raca_cor'] == '9', 'raca_cor'] = '99'
        self.__source.loc[self.__source['raca_cor'].isnull(), 'raca_cor'] = '99'

        self.__source.loc[self.__source['febre'] == '1', 'febre'] = '1'
        self.__source.loc[self.__source['febre'] == '2', 'febre'] = '2'
        self.__source.loc[self.__source['febre'] == '9', 'febre'] = '3'
        self.__source.loc[self.__source['febre'].isnull(), 'febre'] = '3'

        self.__source.loc[self.__source['tosse'] == '1', 'tosse'] = '1'
        self.__source.loc[self.__source['tosse'] == '2', 'tosse'] = '2'
        self.__source.loc[self.__source['tosse'] == '9', 'tosse'] = '3'
        self.__source.loc[self.__source['tosse'].isnull(), 'tosse'] = '3'

        self.__source.loc[self.__source['dor_garganta'] == '1', 'dor_garganta'] = '1'
        self.__source.loc[self.__source['dor_garganta'] == '2','dor_garganta'] = '2'
        self.__source.loc[self.__source['dor_garganta'] == '9', 'dor_garganta'] = '3'
        self.__source.loc[self.__source['dor_garganta'].isnull(), 'dor_garganta'] = '3'

        self.__source.loc[(self.__source['dispneia'] == '1') | (self.__source['DESC_RESP'] == '1'), 'dispneia'] = '1'
        self.__source.loc[(self.__source['dispneia'] == '2') | (self.__source['DESC_RESP'] == '2'), 'dispneia'] = '2'
        self.__source.loc[(self.__source['dispneia'] == '9') | (self.__source['DESC_RESP'] == '9'), 'dispenia'] = '3'
        self.__source.loc[(self.__source['dispneia'].isnull()) & (self.__source['DESC_RESP'].isnull()), 'dispenia'] = '3'

        self.__source.loc[self.__source['saturacao_o2'] == '1', 'saturacao_o2'] = '1'
        self.__source.loc[self.__source['saturacao_o2'] == '2','saturacao_o2'] = '2'
        self.__source.loc[self.__source['saturacao_o2'] == '9', 'saturacao_o2'] = '3'
        self.__source.loc[self.__source['saturacao_o2'].isnull(), 'saturacao_o2'] = '3'

        self.__source.loc[self.__source['diarreia'] == '1', 'diarreia'] = '1'
        self.__source.loc[self.__source['diarreia'] == '2','diarreia'] = '2'
        self.__source.loc[self.__source['diarreia'] == '9', 'diarreia'] = '3'
        self.__source.loc[self.__source['diarreia'].isnull(), 'diarreia'] = '3'

        self.__source.loc[self.__source['nausea_vomitos'] == '1', 'nausea_vomitos'] = '1'
        self.__source.loc[self.__source['nausea_vomitos'] == '2','nausea_vomitos'] = '2'
        self.__source.loc[self.__source['nausea_vomitos'] == '9', 'nausea_vomitos'] = '3'
        self.__source.loc[self.__source['nausea_vomitos'].isnull(), 'nausea_vomitos'] = '3'

        self.__source.loc[self.__source['outros_sintomas'] == '1', 'outros_sintomas'] = '1'
        self.__source.loc[self.__source['outros_sintomas'] == '2','outros_sintomas'] = '2'
        self.__source.loc[self.__source['outros_sintomas'] == '9', 'outros_sintomas'] = '3'
        self.__source.loc[self.__source['outros_sintomas'].isnull(), 'outros_sintomas'] = '3'

        self.__source.loc[self.__source['puerperio'] == '1', 'puerperio'] = '1'
        self.__source.loc[self.__source['puerperio'] == '2','puerperio'] = '2'
        self.__source.loc[self.__source['puerperio'] == '9', 'puerperio'] = '3'
        self.__source.loc[self.__source['puerperio'].isnull(), 'puerperio'] = '3'

        self.__source.loc[self.__source['doenca_cardiovascular'] == '1', 'doenca_cardiovascular'] = '1'
        self.__source.loc[self.__source['doenca_cardiovascular'] == '2','doenca_cardiovascular'] = '2'
        self.__source.loc[self.__source['doenca_cardiovascular'] == '9', 'doenca_cardiovascular'] = '3'
        self.__source.loc[self.__source['doenca_cardiovascular'].isnull(), 'doenca_cardiovascular'] = '3'

        self.__source.loc[self.__source['doenca_hepatica'] == '1', 'doenca_hepatica'] = '1'
        self.__source.loc[self.__source['doenca_hepatica'] == '2','doenca_hepatica'] = '2'
        self.__source.loc[self.__source['doenca_hepatica'] == '9', 'doenca_hepatica'] = '3'
        self.__source.loc[self.__source['doenca_hepatica'].isnull(), 'doenca_hepatica'] = '3'

        self.__source.loc[self.__source['diabetes'] == '1', 'diabetes'] = '1'
        self.__source.loc[self.__source['diabetes'] == '2','diabetes'] = '2'
        self.__source.loc[self.__source['diabetes'] == '9', 'diabetes'] = '3'
        self.__source.loc[self.__source['diabetes'].isnull(), 'diabetes'] = '3'

        self.__source.loc[self.__source['doenca_neurologica'] == '1', 'doenca_neurologica'] = '1'
        self.__source.loc[self.__source['doenca_neurologica'] == '2','doenca_neurologica'] = '2'
        self.__source.loc[self.__source['doenca_neurologica'] == '9', 'doenca_neurologica'] = '3'
        self.__source.loc[self.__source['doenca_neurologica'].isnull(), 'doenca_neurologica'] = '3'

        self.__source.loc[self.__source['sindrome_down'] == '1', 'sindrome_down'] = '1'
        self.__source.loc[self.__source['sindrome_down'] == '2','sindrome_down'] = '2'
        self.__source.loc[self.__source['sindrome_down'] == '9', 'sindrome_down'] = '3'
        self.__source.loc[self.__source['sindrome_down'].isnull(), 'sindrome_down'] = '3'

        self.__source.loc[self.__source['doenca_pulmonar'] == '1', 'doenca_pulmonar'] = '1'
        self.__source.loc[self.__source['doenca_pulmonar'] == '2','doenca_pulmonar'] = '2'
        self.__source.loc[self.__source['doenca_pulmonar'] == '9', 'doenca_pulmonar'] = '3'
        self.__source.loc[self.__source['doenca_pulmonar'].isnull(), 'doenca_pulmonar'] = '3'

        self.__source.loc[self.__source['doenca_renal'] == '1', 'doenca_renal'] = '1'
        self.__source.loc[self.__source['doenca_renal'] == '2','doenca_renal'] = '2'
        self.__source.loc[self.__source['doenca_renal'] == '9', 'doenca_renal'] = '3'
        self.__source.loc[self.__source['doenca_renal'].isnull(), 'doenca_renal'] = '3'

        self.__source.loc[self.__source['obesidade'] == '1', 'obesidade'] = '1'
        self.__source.loc[self.__source['obesidade'] == '2','obesidade'] = '2'
        self.__source.loc[self.__source['obesidade'] == '9', 'obesidade'] = '3'
        self.__source.loc[self.__source['obesidade'].isnull(), 'obesidade'] = '3'

        self.__source.loc[self.__source['outras_morbidades'] == '1', 'outras_morbidades'] = '1'
        self.__source.loc[self.__source['outras_morbidades'] == '2','outras_morbidades'] = '2'
        self.__source.loc[self.__source['outras_morbidades'] == '9', 'outras_morbidades'] = '3'
        self.__source.loc[self.__source['outras_morbidades'].isnull(), 'outras_morbidades'] = '3'

        self.__source.loc[self.__source['hospitalizado'] == '1', 'hospitalizado'] = '1'
        self.__source.loc[self.__source['hospitalizado'] == '2','hospitalizado'] = '2'
        self.__source.loc[self.__source['hospitalizado'] == '9', 'hospitalizado'] = '3'
        self.__source.loc[self.__source['hospitalizado'].isnull(), 'hospitalizado'] = '3'

        self.__source.loc[self.__source['UTI'] == '1', 'tipo_internacao'] = '2'
        self.__source.loc[((self.__source['UTI'] == '2') | (self.__source['UTI'] == '9') | (self.__source['UTI'].isnull())) & (self.__source['hospitalizado'] == '1'), 'tipo_internacao'] = '3'
        self.__source.loc[self.__source['hospitalizado'] != '1', 'tipo_internacao'] = '3'

        self.__source.loc[self.__source['coleta_amostra'] == '1', 'coleta_amostra'] = '1'
        self.__source.loc[self.__source['coleta_amostra'] == '2','coleta_amostra'] = '2'
        self.__source.loc[self.__source['coleta_amostra'] == '9', 'coleta_amostra'] = '3'
        self.__source.loc[self.__source['coleta_amostra'].isnull(), 'coleta_amostra'] = '3'

        self.__source.loc[self.__source['historico_viagem'] == '1', 'historico_viagem'] = '1'
        self.__source.loc[self.__source['historico_viagem'] == '2','historico_viagem'] = '2'
        self.__source.loc[self.__source['historico_viagem'].isnull(), 'historico_viagem'] = '0'

        self.__source.loc[(self.__source['perda_olfato_paladar'] == '1') | (self.__source['PERD_PALA'] == '1'), 'perda_olfato_paladar'] = '1'
        self.__source.loc[(self.__source['perda_olfato_paladar'] == '2') | (self.__source['PERD_PALA'] == '2'), 'perda_olfato_paladar'] = '2'
        self.__source.loc[(self.__source['perda_olfato_paladar'] == '9') | (self.__source['PERD_PALA'] == '9'), 'perda_olfato_paladar'] = '3'
        self.__source.loc[(self.__source['perda_olfato_paladar'].isnull()) & (self.__source['PERD_PALA'].isnull()), 'perda_olfato_paladar'] = '3'

        self.__source.loc[self.__source['sexo'] == 'M', 'sexo'] = '1'
        self.__source.loc[self.__source['sexo'] == 'F','sexo'] = '2'
        self.__source.loc[self.__source['sexo'] == 'I','sexo'] = '2'

        self.__source.loc[self.__source['cod_cbo'].isnull(), 'cod_cbo'] = '0'

        self.__source["data_notificacao"] = self.__source["data_notificacao"].apply(pd.to_datetime)
        self.__source["data_1o_sintomas"] = self.__source["data_1o_sintomas"].apply(pd.to_datetime)
        self.__source["data_nascimento"] = self.__source["data_nascimento"].apply(pd.to_datetime)
        self.__source["data_liberacao"] = self.__source["data_liberacao"].apply(pd.to_datetime)
        self.__source["data_cura_obito"] = self.__source["data_cura_obito"].apply(pd.to_datetime)
        self.__source["data_encerramento"] = self.__source["data_encerramento"].apply(pd.to_datetime)
        self.__source["data_ida_local"] = self.__source["data_ida_local"].apply(pd.to_datetime)
        self.__source["data_retorno_local"] = self.__source["data_retorno_local"].apply(pd.to_datetime)

        municipios = static.municipios[['cod_uf','ibge']]
        municipios = municipios.rename(columns={'ibge':'ibge_residencia', 'cod_uf': 'uf_residencia'})
        self.__source['ibge_residencia'] = pd.to_numeric(self.__source['ibge_residencia'], downcast = 'integer')
        self.__source = pd.merge(left=self.__source, right=municipios, how='left', on='ibge_residencia')
        self.__source.loc[self.__source['uf_residencia'].isnull(), 'uf_residencia'] = '0'

        municipios = municipios.rename(columns={'ibge_residencia':'ibge_unidade_notifica', 'uf_residencia': 'uf_unidade_notifica'})
        self.__source['ibge_unidade_notifica'] = pd.to_numeric(self.__source['ibge_unidade_notifica'], downcast = 'integer')
        self.__source = pd.merge(left=self.__source, right=municipios, how='left', on='ibge_unidade_notifica')
        self.__source.loc[self.__source['uf_unidade_notifica'].isnull(), 'uf_unidade_notifica'] = '0'

        pais = static.pais[['co_pais','ds_pais']]
        pais = pais.rename(columns={'ds_pais':'ID_PAIS', 'co_pais': 'pais_residencia'})
        self.__source['ID_PAIS'] = self.__source['ID_PAIS'].astype('string')
        self.__source = pd.merge(left=self.__source, right=pais, how='left', on='ID_PAIS')
        self.__source.loc[self.__source['pais_residencia'].isnull(), 'pais_residencia'] = '0'

        etnia = static.etnia[['co_etnia','etnia']]
        etnia = etnia.rename(columns={'etnia':'CS_ETINIA', 'co_etnia': 'etnia'})
        self.__source['CS_ETINIA'] = self.__source['CS_ETINIA'].astype('string')
        self.__source = pd.merge(left=self.__source, right=etnia, how='left', on='CS_ETINIA')
        self.__source.loc[self.__source['etnia'].isnull(), 'etnia'] = '0'

        self.__source.loc[self.__source['nome_mae'].isnull(), 'nome_mae'] = ''
        nao = set(['NAO','CONSTA','INFO','INFORMADO','CONTEM',''])
        self.__source.loc[ [True if set(nome_mae.split(" ")).intersection(nao) else False for nome_mae in self.__source['nome_mae'] ], 'nome_mae'] = None

        self.__source = self.__source[['id', 'data_notificacao', 'data_1o_sintomas', 'uf_unidade_notifica', 'ibge_unidade_notifica', 'nome_unidade_notifica',
                     'cpf', 'paciente', 'sexo', 'data_nascimento', 'idade', 'gestante', 'periodo_gestacao', 'raca_cor', 'etnia',
                     'nome_mae', 'cep_residencia', 'pais_residencia', 'uf_residencia', 'ibge_residencia', 'bairro_residencia',
                     'logradouro_residencia', 'numero_residencia', 'febre', 'tosse', 'dor_garganta', 'dispneia', 'dispneia',
                     'saturacao_o2', 'diarreia', 'nausea_vomitos', 'outros_sintomas', 'puerperio', 'doenca_cardiovascular',
                     'sindrome_down', 'doenca_hepatica', 'diabetes', 'doenca_neurologica', 'doenca_pulmonar', 'imunodeficiencia',
                     'doenca_renal', 'obesidade', 'outras_morbidades', 'uso_antiviral', 'hospitalizado', 'tipo_internacao',
                     'raiox_torax', 'coleta_amostra', 'data_coleta', 'requisicao', 'data_liberacao', 'resultado', 'lab_executor',
                     'classificacao_final', 'criterio_classificacao', 'evolucao', 'data_cura_obito', 'data_encerramento',
                     'nome_notificador', 'historico_viagem', 'local_viagem', 'data_ida_local', 'data_retorno_local',
                     'perda_olfato_paladar', 'perda_olfato_paladar', 'tomografia', 'numero_do', 'cod_cbo']]

        self.__source['sistema'] = 'SIVEP'
    
    #Métodos usados após to_notifica()
    
    def shape(self):
        return (len(self.__source.loc[(self.__source['classificacao_final'] == '2')]),
                len(self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '2')]),
                len(self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '1')]),
                len(self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '3')]))
    
    def get_casos(self):
        return self.__source.loc[self.__source['classificacao_final'] == '2'].copy()

    def get_obitos(self):
        return self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '2')].copy()

    def get_recuperados(self):
        return self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '1')].copy()

    def get_casos_ativos(self):
        return self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '3')].copy()

    def get_obitos_nao_covid(self):
        return self.__source.loc[(self.__source['classificacao_final'] == '2') & (self.__source['evolucao'] == '4')].copy()
