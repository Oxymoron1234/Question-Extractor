# import airflow
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.base_aws import AwsGenericHook

from datetime import datetime
import requests


LINKS_ENEM = {
    "2010_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2010/dia1_caderno1_azul_com_gab.pdf',
    "2010_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2010/dia2_caderno7_azul_com_gab.pdf',
    "2010_3":'https://download.inep.gov.br/educacao_basica/enem/provas/2010/AZUL_quarta-feira_GAB.pdf',
    "2010_4":'https://download.inep.gov.br/educacao_basica/enem/provas/2010/AZUL_quinta-feira_GAB.pdf',

    "2011_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2011/01_AZUL_GAB.pdf',
    "2011_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2011/07_AZUL_GAB.pdf',
    "2011_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2011/PPL_ENEM_2011_03_BRANCO.pdf',
    "2011_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2011/PPL_ENEM_2011_06_CINZA.pdf',

    "2012_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2012/caderno_enem2012_sab_azul.pdf',
    "2012_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2012/caderno_enem2012_dom_azul.pdf',
    "2012_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2012/prova_caderno_branco_3_2012.pdf',
    "2012_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2012/prova_caderno_cinza_6_2012.pdf',

    "2013_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2013/caderno_enem2013_sab_azul.pdf',
    "2013_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2013/caderno_enem2013_dom_azul.pdf',
    "2013_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2013/prova_caderno_branco_3_2013.pdf',
    "2013_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2013/prova_caderno_cinza_6_2013.pdf',

    "2014_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2014/CAD_ENEM_2014_DIA_1_01_AZUL.pdf',
    "2014_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2014/CAD_ENEM_2014_DIA_2_07_AZUL.pdf',
    "2014_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2014/prova_caderno_branco_3_2014.pdf',
    "2014_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2014/prova_caderno_cinza_6_2014.pdf',

    "2015_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2015/CAD_ENEM%202015_DIA%201_01_AZUL.pdf',
    "2015_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2015/CAD_ENEM%202015_DIA%202_07_AZUL.pdf',
    "2011_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2015/PPL_ENEM_2011_09_BRANCO.pdf',
    "2011_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2015/PPL_ENEM_2011_12_BRANCO.pdf',

    "2016_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2016/CAD_ENEM_2016_DIA_1_01_AZUL.pdf',
    "2016_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2016/CAD_ENEM_2016_DIA_2_07_AZUL.pdf',
    "2016_3":'https://download.inep.gov.br/educacao_basica/enem/provas/2016/CAD_ENEM_2016_DIA_1_01_AZUL_2.pdf',
    "2016_4":'https://download.inep.gov.br/educacao_basica/enem/provas/2016/CAD_ENEM_2016_DIA_2_07_AZUL_2.pdf',

    "2017_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2017/cad_1_prova_azul_5112017.pdf',
    "2017_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2017/cad_7_prova_azul_12112017.pdf',
    "2017_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2017/provas/P2_01_AZUL.pdf',
    "2017_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2017/provas/P2_07_AZUL.pdf',

    "2018_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2018/1DIA_01_AZUL_BAIXA.pdf',
    "2018_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2018/2DIA_07_AZUL_BAIXA.pdf',
    "2018_3":'https://download.inep.gov.br/educacao_basica/enem/provas/2018/Caderno_13_1_dia_PPL_AZUL.pdf',
    "2018_4":'https://download.inep.gov.br/educacao_basica/enem/provas/2018/Caderno_19_2_dia_PPL_AZUL.pdf',

    "2019_1":'https://download.inep.gov.br/educacao_basica/enem/provas/2019/caderno_de_questoes_1_dia_caderno_1_azul_aplicacao_regular.pdf',
    "2019_2":'https://download.inep.gov.br/educacao_basica/enem/provas/2019/caderno_de_questoes_2_dia_caderno_7_azul_aplicacao_regular.pdf',
    "2019_3":'https://download.inep.gov.br/educacao_basica/enem/ppl/2019/provas/BAIXA_PPL_1_DIA_CADERNO_1_AZUL.pdf',
    "2019_4":'https://download.inep.gov.br/educacao_basica/enem/ppl/2019/provas/BAIXA_PPL_2_DIA_CADERNO_7_AZUL.pdf',

    "2020_1":'https://download.inep.gov.br/enem/provas_e_gabaritos/2020_PV_impresso_D1_CD1.pdf',
    "2020_2":'https://download.inep.gov.br/enem/provas_e_gabaritos/2020_PV_impresso_D2_CD7.pdf',
    "2020_3":'https://download.inep.gov.br/enem/provas_e_gabaritos/2020_PV_reaplicacao_PPL_D1_CD1.pdf',
    "2020_4":'https://download.inep.gov.br/enem/provas_e_gabaritos/2020_PV_reaplicacao_PPL_D2_CD7.pdf',

    "2021_1":'https://download.inep.gov.br/enem/provas_e_gabaritos/2021_PV_impresso_D1_CD1.pdf',
    "2021_2":'https://download.inep.gov.br/enem/provas_e_gabaritos/2021_PV_impresso_D2_CD7.pdf',
    "2021_3":'https://download.inep.gov.br/enem/provas_e_gabaritos/2021_PV_reaplicacao_PPL_D1_CD1.pdf',
    "2021_4":'https://download.inep.gov.br/enem/provas_e_gabaritos/2021_PV_reaplicacao_PPL_D2_CD7.pdf',

    "2022_1":'https://download.inep.gov.br/enem/provas_e_gabaritos/2022_PV_impresso_D1_CD1.pdf',
    "2022_2":'https://download.inep.gov.br/enem/provas_e_gabaritos/2022_PV_impresso_D2_CD7.pdf',
    "2022_3":'https://download.inep.gov.br/enem/provas_e_gabaritos/2022_PV_reaplicacao_PPL_D1_CD1.pdf',
    "2022_4":'https://download.inep.gov.br/enem/provas_e_gabaritos/2022_PV_reaplicacao_PPL_D2_CD7.pdf',
}

AWS_CONN_ID = "AWSConnection"
YEAR_VARIABLE = "year"

def download_pdfs_from_year(
        year_variable,
        bucket
    ):
    conn = S3Hook(aws_conn_id=AWS_CONN_ID)
    client = conn.get_conn()

    year = Variable.get(year_variable)

    year_keys = [key for key in LINKS_ENEM.keys() if year in key]

    for key in year_keys:
        print(f"Downloading {key}")
        url = LINKS_ENEM[key]
        r = requests.get(
            url, 
            allow_redirects=True,
            verify=False
        )

        client.put_object(
            Body=r.content,
            Key=f"pdf_{key}.pdf",
            Bucket=bucket,
        )


    year = str(int(year)+1)
    Variable.set(year_variable, year)


def trigger_process_enem_pdf_glue_job(
    job_name
):
    
    session = AwsGenericHook(aws_conn_id=AWS_CONN_ID)
    boto3_session = session.get_session(
        region_name='ap-south-1',
    )
        
    client = boto3_session.client('glue')
    client.start_job_run(
        JobName=job_name,
    )

default_args = {
    'owner': 'ENEM_PDF',
    'depends_on_past': False,
    'start_date': datetime(2021, 1, 1),
}

dag = DAG(
    'process_enem_pdf_aws',
    default_args=default_args,
    description='Process ENEM PDFs using AWS',
    tags=['enem'],
    catchup=False,
)

with dag:

    download_pdf_upload_s3 = PythonOperator(
        task_id='download_pdf_upload_s3',
        python_callable=download_pdfs_from_year,
        op_kwargs={
            'year_variable': 'year',
            'bucket': 's3-lamda-glue-airflow01',
        },
    )

    trigger_glue_job = PythonOperator(
        task_id='trigger_glue_job',
        python_callable=trigger_process_enem_pdf_glue_job,
        op_kwargs={
            'job_name': 'Spark_EnemExtractQuestionsJSON'
        },
    )

    download_pdf_upload_s3 >> trigger_glue_job