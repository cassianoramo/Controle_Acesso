import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import csv
from datetime import datetime

leitorRFid = SimpleMFRC522()
usuarios = {837196207282: "Fulano" , 11 : "Beltrano",  634156810886:"Ciclano"}
usuarios_autorizados = {837196207282: "Fulano" , 11: "Beltrano"}
acesso_diario = {}
tempo_entrada = {}
numero_tentativas = {}

led_verde = 5
led_vermelho = 3
buzzer = 37
entrada = False
tentativas_invasao = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led_verde, GPIO.OUT)
GPIO.setup(led_vermelho, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)



def verificar_tag(tag):
    if tag in usuarios_autorizados:
            
            if tag not in acesso_diario:
                print(f"Bem vindo {usuarios_autorizados[tag]}!")
                acesso_diario[tag] = usuarios_autorizados  
                print(acesso_diario)
                global entrada
                entrada = True
                ligar_leds("verde", invasao=False)
                novo_log(tag, {usuarios[tag]}, "Usuário autorizado","Entrada",None)
                
                tempo_entrada[tag] = datetime.now()
                print(tempo_entrada)
            elif entrada == True:
                print(f"Volte Sempre {usuarios_autorizados[tag]}!")
                tempo_inicial = tempo_entrada[tag]
                tempo_atual = datetime.now()
                tempo_na_sala = tempo_atual - tempo_inicial
                
                entrada = False
                print(tempo_na_sala)
                novo_log(tag, {usuarios[tag]}, "Usuário autorizado", "Saida", tempo_na_sala)
            else:
                print(f"Bem vindo de volta {usuarios_autorizados[tag]}!")
                entrada = True
                ligar_leds("verde", invasao=False)
                novo_log(tag, {usuarios[tag]}, "Usuário autorizado", "Entrada",None)

    elif tag in usuarios :
        print(f"Você não tem acesso a este projeto, {usuarios[tag]}" )
        
        ligar_leds("vermelho", invasao=False)
        
        if tag not in numero_tentativas:
            numero_tentativas[tag] = (usuarios[tag], 1)
        else:
            
            nome, tentativas = numero_tentativas[tag]
            tentativas += 1
            numero_tentativas[tag] = (nome, tentativas)


        nome, tentativas = numero_tentativas[tag]
        novo_log(tag, {nome}, f"Usuário não autorizado - Tentativas: {tentativas}", None, None)
    else:
        print(f"Identificação não encontrada!")
        global tentativas_invasao 
        tentativas_invasao += 1
        ligar_leds("vermelho", invasao=True)
        novo_log(tag, f"Tentativas de invasão: {tentativas_invasao}", None, None, None)

def ligar_leds(led, invasao):
    if led == "verde":
        GPIO.output(37, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(37, GPIO.LOW)
        for i in range(5):
                GPIO.output(5, GPIO.HIGH)
                #print("LED ligado")
                time.sleep(1)
                GPIO.output(5, GPIO.LOW)                
                #print("LED desligado")
                time.sleep(1)
    elif led == "vermelho" and invasao == False:
        for i in range(5):
                GPIO.output(3, GPIO.HIGH)
                GPIO.output(37, GPIO.HIGH)
                #print("LED ligado")
                time.sleep(1)
                GPIO.output(3, GPIO.LOW)
                GPIO.output(37, GPIO.LOW)
                #print("LED desligado")
                time.sleep(1)
    elif led == "vermelho" and invasao == True:
        for i in range(2):
            GPIO.output(3, GPIO.HIGH)
            GPIO.output(37, GPIO.HIGH)
            #print("LED ligado")
            time.sleep(1)
            GPIO.output(3, GPIO.LOW)
            #print("LED desligado")
            time.sleep(1)
    GPIO.output(37, GPIO.LOW)

def novo_log(log, usuario, autorizacao, entrada_saida, tempo):
    with open('logs.csv', mode='a', newline='') as arquivo_csv:
        dados = csv.writer(arquivo_csv)
        
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        dados.writerow([data_hora, log, usuario,autorizacao, entrada_saida, tempo])

while True:
    try: 
        GPIO.output(5, GPIO.LOW)
        GPIO.output(3, GPIO.LOW)
        print(tentativas_invasao)
        print("Aguardando leitura da tag")
        tag, text = leitorRFid.read()
        #print(f"ID do cartão: {tag}")
        #print(f"Texto: {text}")
        print(entrada)
        print(numero_tentativas)
        #tag = int(input("Digite o ID do usuário: "))
        verificar_tag(tag)


    finally:
     #GPIO.cleanup()
     print("Fim do programa")