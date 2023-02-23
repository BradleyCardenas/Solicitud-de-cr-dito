import streamlit as st
import urllib.request
import json
import os
import ssl
import re

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.


st.title('Predicción de créditos')
st.write('Llene los campos para determinar si es sujeto de aprobación')

answers = {}
with st.form('form'):
    answers['age'] = st.number_input('Edad', 18, 80)
    answers['job'] = st.selectbox('Tipo de trabajo', ('technician', 'unknown', 'blue-collar', 'admin', 'housemaid','retired', 'services', 'entrepreneur', 'unemployed', 'management','self-employed', 'student'))
    answers['marital'] = st.selectbox('Estado civil', ('married', 'divorced', 'single', 'unknown'))
    answers['education'] = st.selectbox('Grado de estudio', ('illiterate', 'basic.4y', 'basic.6y', 'basic.9y', 'high.school', 'professional.course', 'unknown', 'university.degree'))
    answers['default'] = st.radio('¿Ya cuenta con un crédito?',('yes', 'no', 'unknown'))
    answers['housing'] = st.radio('¿Tiene propiedades?', ('yes', 'no', 'unknown'))
    answers['loan'] = st.radio('¿Cuenta con otros préstamos?', ('yes', 'no', 'unknown'))
    answers['contact'] = st.radio('Seleccione el medio por el que le contactaron', ('cellular', 'telephone'))
    answers['month'] = st.selectbox('Seleccione el mes en el que solicitó el crédito', ('ene', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'))
    #answers['day_of_week'] = st.selectbox('Seleccione el día de la semana en que solicitó el crédito', ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'))
    answers['duration'] = st.slider('Seleccione la duración de la reunión en la que solicitó el crédito', 0, 5000)
    answers['campaign'] = st.slider('Seleccione el número de veces que le contactaron hasta que accedió a solicitar el crédito', 1, 60)
    answers['pdays'] = st.slider('Seleccione el pdays', 0, 999)
    answers['previous']  = st.number_input('Seleccione el previo', 0, 7)
    answers['poutcome'] = st.radio('Indique el estado de su solicitud de crédito', ('success', 'failure', 'nonexistent'))
    answers['emp.var.rate'] = st.slider('Indique la variabilidad de empleabilidad', -4.0, 2.0, step = .1)
    answers['cons.price.idx'] = st.slider('Indique la constante de precio del idx', 92.0, 95.0, step = .001)
    answers['cons.conf.idx'] = st.slider('Indique la constante de configuración del idx', -51.0, -27.0, step = .1)
    answers['euribor3m'] = st.slider('Indique su euribor3m', 0.0, 6.0, step = .01)
    answers['nr.employed'] = st.slider('Indique la variabilidad de empleabilidad', 4900.0, 5300.0, step = .1)

    if st.form_submit_button('Enviar solicitud'):
        data =  {
            "Inputs": {
                "data": [
                answers
                ]
            },
            "GlobalParameters": {
                "method": "predict"
            }
        }

        body = str.encode(json.dumps(data))
        url = 'https://fca-regression.eastus2.inference.ml.azure.com/score'
        api_key = 'AnVcIXbYyV9KbCKmAGmbV2gNhpMAdmXg'
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'fca-deploy2' }
        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)

            result = response.read()
            result = re.findall('\["(.+)"\]', result.decode())
            if result[0] == 'yes':
                st.success('¡Felicidades, ha sido aprobada su solicitud!', icon="✅")
            else: 
                st.error('Vuelva pronto y mejore sus requisitos', icon="❌")
        
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
