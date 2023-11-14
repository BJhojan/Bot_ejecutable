import tkinter as tk
import shutil
from tkinter import filedialog
import threading as th
import pygame
from flet import *
from time import sleep
import importlib
import asyncio
import webbrowser
from twitchio.ext import commands as cm
import json
import os


def read(source):
    with open(source, "r") as sr:
        return json.load(sr)


def edit(source, data):
    with open(source, "w") as sr:
        json.dump(data, sr, indent=4)


def editar_txt(source, data: list):
    up_data = ""
    with open(source, "w") as sr:
        for i in data:
            if up_data != "":
                up_data = f"{up_data}{i}           "
            else:
                up_data = f"{i}           "
        sr.write(up_data)


chat_twitch = "C:/Twitch_bot_data/Bot/info_chat.json"
twitch_token = "C:/Twitch_bot_data/Bot/tokens/tokens.json"
source_comandos = "C:/Twitch_bot_data/Bot/comandos/comandos.json"
sonido_saludo = "C:/Twitch_bot_data/audios/batman.wav"
style_url = "C:/Twitch_bot_data/interfaz/estilos/estilos_app.json"
ruta_guardar_audio = "C:/Twitch_bot_data/audios"
top_puntos_source = "C:/Twitch_bot_data/Bot/comandos/top_puntos.txt"


if not os.path.exists("C:/Twitch_bot_data"):
    os.makedirs("C:/Twitch_bot_data/Bot/tokens")
    os.makedirs("C:/Twitch_bot_data/Bot/comandos")
    os.makedirs(ruta_guardar_audio)
    os.makedirs("C:/Twitch_bot_data/interfaz/estilos")
    with open(chat_twitch,"w") as archivo:
        json.dump({
            "1": {
            "nombre": "prueba",
            "puntos": 0,
            "mensajes": 0,
            "mensajes acumulados": 0
            }}, archivo, indent=4
        )
    with open(twitch_token, "w") as archivo:
        json.dump(
            {
                "twitch_token": "",
                "bot_name": "",
                "bot_iniciado": False
            }, archivo, indent=4
        )
    with open(source_comandos,"w") as archivo:
        json.dump({
            "puntos": {
                "informacion": "Muestra los puntos que tienen los espectadores",
                "mensaje": {
                    "enviar": True,
                    "mensaje": "@{user} tienes {puntos} puedes usar el comando !comandos para saber que hacer con ellos."
                },
                "costo": 0,
                "accion": {
                    "sonido": {
                        "reproducir": False,
                        "url": ""
                    },
                    "accion": {
                        "tecla": {
                            "precionar": False,
                            "tecla": ""
                        },
                        "otra": ""
                    }
                },
                "insuficiente": "@{user} necesitas {costo} puntos para poder ejecutar esta accion."
            },
            "comandos": {
                "informacion": "Muestra todos los comandos que esten disponibles en este momento.",
                "mensaje": {
                    "enviar": True,
                    "mensaje": "@{user} los comandos que puedes usar son: {comandos}"
                },
                "costo": 0,
                "accion": {
                    "sonido": {
                        "reproducir": False,
                        "url": ""
                    },
                    "accion": {
                        "tecla": {
                            "precionar": False,
                            "tecla": ""
                        },
                        "otra": ""
                    }
                },
                "insuficiente": "@{user} necesitas {costo} puntos para poder ejecutar esta accion."
            }
            }, archivo, indent=4
        )
    with open(style_url, "w") as archivo:
        json.dump({
            "page": {
                "title": "Proyecto ahora si",
                "width": 1264,
                "height": 700,
                "bgcolor": "grey200",
                "resizable": False,
                "maximizable": False
            },
            "main container": {
                "width": 1264,
                "height": 500
            },
            "text": {
                "size": 50,
                "color": "black"
            },
            "button": {
                "color": "black",
                "bgcolor": "grey200"
            },
            "progres bar": {
                "width": 400,
                "color": "amber",
                "bgcolor": "#eeeeee"
            },
            "icons": {
                "color": "blue400",
                "size": 40
            },
            "elements": {
                "bgcolor": "black",
                "width": 200,
                "height": 200
            },
            "bot": {
                "column": {
                    "width": 400,
                    "height": 326
                }
            }}, archivo, indent=4
        )
    with open(top_puntos_source, "w") as archivo:
        archivo.write("")

mensaje_no_puntos = "@{user} necesitas {costo} puntos para poder ejecutar esta accion."

def crear_usuario(id, nombre):
    data = read(chat_twitch)
    data[id] = {
        "nombre": nombre,
        "puntos": 100,
        "mensajes": 0,
        "mensajes acumulados": 0
    }
    edit(chat_twitch, data)
    print(f"Se creo el usuario {nombre}")


def sumar_puntos(id, sumar=50):
    data = read(chat_twitch)
    mensajes = data[id]["mensajes"]
    if mensajes >= 5:
        data[id]["puntos"] += sumar
        data[id]["mensajes"] = 0
    else:
        data[id]["mensajes"] += 1
    data[id]["mensajes acumulados"] += 1
    edit(chat_twitch, data)


def restar_puntos(id, restar=50):
    data = read(chat_twitch)
    if data[id]["puntos"] >= restar:
        data[id]["puntos"] -= restar
        res = True
    else:
        res = False
    edit(chat_twitch, data)
    return res


pygame.mixer.init()


def reproducir(file):
    try:
        # Cargar el archivo de sonido
        sound = pygame.mixer.Sound(file=file)

        # Reproducir el sonido en un nuevo canal
        channel = pygame.mixer.find_channel()
        channel.play(sound)
    except Exception as ex:
        print(f"Error en el audio {ex}")


def primer_palabra(text, prefix):
    # Eliminar el signo de exclamación
    frase_sin_exclamacion = text.replace(prefix, "")
    # Dividir la frase en palabras
    palabras = frase_sin_exclamacion.split()
    # Obtener la primera palabra
    primera_palabra = palabras[0]
    return primera_palabra


def iniciar_bot():
    loop = asyncio.new_event_loop()

    # Establecer el bucle de eventos para el hilo actual
    asyncio.set_event_loop(loop)
    importlib.reload(cm)

    tk = read(twitch_token)

    # Nombre de twitch con el que ejecuto las acciones
    bot_name = tk["bot_name"]
    # Token de twitch con el que accedo al canal
    token = tk["twitch_token"]
    # Id de twitch para conectarme al servidor
    # client = "tpj9obe23y40oabejhq3et8xfftj1g"

    users_obs = []
    saludo = []

    # Inicializador del bot de twitch
    bot = cm.Bot(
        # Se asigna el token
        token=token,
        # Se asigna el cliente
        # client_id = client,
        # Se asigna el nombre al bot
        nick=bot_name,
        # Se asigna el prefijo con el que se va a llamar al bot desde el chat
        prefix="]",
        # Canal en el que se ejecuta el bot
        initial_channels=[bot_name]
    )

    @bot.event()
    async def event_ready():
        print("El bot esta en linea")

    @bot.event()
    async def event_message(ctx):
        global users_obs
        try:
            usuario = ctx.author.name
            id = str(ctx.author.id)
            mensaje = ctx.content.lower()
            try:
                if not id in read(chat_twitch):
                    await ctx.channel.send(f"Bienvenido @{usuario}, gracias por pasarte por aqui. Ahora tenemos puntos del canal, solo escribe !puntos y te dire como puedes canjearlos.")
                    crear_usuario(id, usuario)
                else:
                    sumar_puntos(id)
            except Exception as ex:
                print(f"Ha ocurrido un error con tu mensaje {ex}")
                pass
            try:
                if "!" in mensaje:
                    puntos = read(
                        chat_twitch)[id]["puntos"]
                    invocador = primer_palabra(mensaje, "!")
                    data = read(source_comandos)
                    comando = data[invocador]
                    costo = comando["costo"]
                    acciones = comando["accion"]
                    leer_comandos = ""
                    for i in data:
                        costo_comando = data[i]["costo"]
                        if leer_comandos == "":
                            leer_comandos = f"{i}: {costo_comando}"
                        else:
                            leer_comandos = f"{leer_comandos}, {i}: {costo_comando}"
                    leer_comandos = f"{leer_comandos}."
                    if puntos >= costo:
                        restar_puntos(id, costo)
                        enviar = comando["mensaje"]
                        if enviar["enviar"]:
                            puntos = read(
                                chat_twitch)[id]["puntos"]
                            mensaje_enviado = enviar["mensaje"]
                            try:
                                formato = mensaje_enviado.format(
                                    user=usuario, costo=costo, puntos=puntos, comandos=leer_comandos)
                            except Exception as ex:
                                formato = mensaje_enviado
                                print(
                                    f"Error en la ejecucion del formato del mensaje {ex}")
                            await ctx.channel.send(formato)
                        if acciones["accion"]:
                            sonido = acciones["sonido"]
                            if sonido["reproducir"]:
                                reproducir(sonido["url"])
                            accion = acciones["accion"]
                            # if accion["tecla"]["precionar"]:

                    else:
                        mensaje_enviado = comando["insuficiente"].format(user=usuario, costo=costo)
                        await ctx.channel.send(mensaje_enviado)
                save = []
                if not id in saludo:
                    reproducir(sonido_saludo)
                    saludo.append(id)
                data_save = read(chat_twitch)
                if len(users_obs) > 4:
                    users_obs.pop(0)
                elif len(users_obs) == 0:
                    users_obs.append(id)
                for i in users_obs:
                    if not id in users_obs:
                        users_obs.append(id)
                for i in users_obs:
                    names = data_save[users_obs[users_obs.index(i)]]["nombre"]
                    points = data_save[users_obs[users_obs.index(i)]]["puntos"]
                    save.append(f"{names}: {points}")
                editar_txt(top_puntos_source, save)
            except Exception as ex:
                print(f"Error con la invocacion de un comando {ex}")
        except:
            pass

    async def enviar_mensaje(mensaje):
        channel = bot.get_channel(bot_name)
        await channel.send(mensaje)

    try:
        bot.run()
    except Exception as ex:
        tk["bot_iniciado"] = False
        edit(twitch_token, tk)
        print(ex)


def multi(fun):
    start = th.Thread(target=fun)
    start.start()

def crear_comando(nombre:str, informacion:str, mensaje:str="", costo:int=100, url_sonido:str="", tecla:str="", otra:str="", insuficiente:str=mensaje_no_puntos):
    data = read(source_comandos)
    
    enviar = False
    reproducir = False
    precionar = False
    
    if mensaje != "":
        enviar = True
    if url_sonido != "":
        if url_sonido == None:
            url_sonido = ""
        else:
            reproducir = True
    if tecla != "":
        precionar = True
        
    
    data[nombre] = {
            "informacion": informacion,
            "mensaje": {
                "enviar": enviar,
                "mensaje": mensaje
            },
            "costo": int(costo),
            "accion": {
                "sonido": {
                    "reproducir": reproducir,
                    "url": url_sonido
                },
                "accion": {
                    "tecla": {
                        "precionar": precionar,
                        "tecla": tecla
                    },
                    "otra": otra
            }
            },
            "insuficiente": insuficiente
    }
    edit(source_comandos, data)


def separarTexto(texto, palabra, elemento=1):
    # Divide el texto en una lista de 2 elementos usando como separador la palabra o frase que se ingresa
    partes = texto.split(palabra)
    # Elige unicamente el segundo elemento de la lista que es el que sera enviado a la funcion que lo solicite
    # strip() elimina los espacios en blanco alrededor del texto
    resultado = partes[elemento].strip()

    # Envia la informacion separada
    return resultado


def seleccionar_archivo():
    try:
        root = tk.Tk()
        # Hacer que la ventana esté siempre en primer plano
        root.attributes('-topmost', True)
        root.withdraw()  # Ocultar la ventana de Tkinter
        # Mostrar el cuadro de diálogo para seleccionar archivo
        ruta_archivo = filedialog.askopenfilename()
        root.destroy()  # Destruir la ventana de Tkinter
        return ruta_archivo
    except Exception as ex:
        print(f"error con el audio {ex}")


def guardar_archivo(ruta, destino):
    try:
        # Copiar el archivo a la carpeta de destino
        shutil.copy(ruta, destino)
        rut = separarTexto(ruta, "/", -1)
        return f"{destino}/{rut}"
    except:
        pass


## Organizar todo el codigo separando las variables fundamentales y crear un sistema de inicio de sesion para el codigo
style = read(style_url)

container = Container(width=style["main container"]["width"],height=style["main container"]["height"])

text_size = style["text"]["size"]

text_color = style["text"]["color"]

button_style = ButtonStyle(color=style["button"]["color"],shape=BeveledRectangleBorder())

button_bg_color = style["button"]["bgcolor"]

barra_carga = [Column([Text("Cargando datos", style="headlineSmall"),
            ProgressBar(width=style["progres bar"]["width"], color=style["progres bar"]["color"], bgcolor=style["progres bar"]["bgcolor"])],alignment=MainAxisAlignment.CENTER)]
            
def reset_bot():
    tk = read(twitch_token)
    tk["bot_iniciado"] = False
    edit(twitch_token,tk)
reset_bot()

icons_color = style["icons"]["color"]

icons_size = style["icons"]["size"]

back_ico = IconButton(
    icon=icons.DOOR_BACK_DOOR_OUTLINED,
    icon_color=icons_color,
    icon_size=icons_size
)

element = Container(bgcolor=style["elements"]["bgcolor"],width=style["elements"]["width"],height=style["elements"]["height"])


def main(page: Page):
    global bot
    
    page.title = style["page"]["title"]
    page.window_width = style["page"]["width"]
    page.window_height = style["page"]["height"]
    page.bgcolor = style["page"]["bgcolor"]
    page.window_resizable = style["page"]["resizable"]
    page.window_maximizable = style["page"]["maximizable"]


    
    
    def bot(e=None):
        
        def bot_iniciar(e):
            bot_start = read(twitch_token)
            bot_style = style["bot"]
            back_ico.on_click = bot_iniciar
            
            def validacion_twitch():
                
                def token(e):
                    
                    
                    alert = AlertDialog(
                        title=Text("Bot Token."),
                        content=Column(
                            [
                                Text("Ingresa al link, preciona conectar, autorizar y copia toda la informacion del recuadro que te aparece al final.",height=70,width=300)
                            ],height=50,alignment=MainAxisAlignment.START
                        ),
                        actions=[
                            Column([TextButton("twitch token", on_click=lambda e: webbrowser.open('https://twitchapps.com/tmi/'))], horizontal_alignment=CrossAxisAlignment.CENTER, width=300)
                        ]
                    )

                    page.dialog = alert
                    alert.open = True
                    page.update()
                
                def nombre(e):
                    alert = AlertDialog(
                        title=Text("Nombre de usuario."),
                        content=Text("Nombre de twitch exactamente como lo tienes en tu cuenta.")
                    )

                    page.dialog = alert
                    alert.open = True
                    page.update()
                
                def iniciar_sesion(e):
                    user_name = bot_name.content.controls[0].value
                    user_token = twitch_token_input.content.controls[0].value
                    user_data = {
                        "twitch_token": user_token,
                        "bot_name": user_name,
                        "bot_iniciado": False
                    }
                    edit(twitch_token,user_data)
                    bot_iniciar(None)
                
                bot_name = Container(Row([TextField(label="Nombre del Bot",width=200),IconButton(icons.QUESTION_MARK,on_click=nombre)],alignment=MainAxisAlignment.START),width=250)
                twitch_token_input = Container(Row([TextField(label="twitch token", width=200),IconButton(icons.QUESTION_MARK,on_click=token)],alignment=MainAxisAlignment.START),width=250)
                enviar_tokens = Container(TextButton("Guardar datos",width=250,height=57,style=ButtonStyle(shape=BeveledRectangleBorder()),on_click=iniciar_sesion),border=border.all(1,color="black"))

                info_twitch = Column([bot_name, twitch_token_input,enviar_tokens],horizontal_alignment=CrossAxisAlignment.CENTER, width=500, alignment=MainAxisAlignment.CENTER)
                container.content = info_twitch
                container.update()
            
            if not bot_start["bot_iniciado"]:
                bot_start["bot_iniciado"] = True
                container.content = Row(barra_carga,alignment=MainAxisAlignment.CENTER)
                edit(twitch_token,bot_start)
                multi(iniciar_bot)
                
                
                container.update()
                sleep(2)
                if not read(twitch_token)["bot_iniciado"]:
                    validacion_twitch()
                    return
            
            
            columna = Column([],scroll=ScrollMode.AUTO,height=bot_style["column"]["height"],width=bot_style["column"]["width"])
            
            def comandos(e="",sonidos=False):
                
                def comando_inputs(e):
                    global audio_ruta
                    
                    if e.control.content != None:
                        
                        elemento = read(source_comandos)[e.control.content.controls[0].value]
                        
                        elements = [e.control.content.controls[0].value,elemento["informacion"],elemento["mensaje"]["mensaje"],elemento["costo"],elemento["accion"]["sonido"]["url"],elemento["accion"]["accion"]["tecla"]["tecla"]]
                    
                    
                    else:
                        
                        elements = ["","","",50,"",""]
                    
                    
                    audio_ruta = elements[4]
                    
                    def seleccionar_audios(e):
                        global audio_ruta
                        
                        audio_ruta = seleccionar_archivo()
                    
                    
                    def enviar_comando_inputs(e):
                        global audio_ruta
                        alerta.open = False
                        
                        page.update()
                        
                        if nombre_input.value != "":
                            
                            if audio_ruta == "":
                                
                                audio_ruta = guardar_archivo(audio_ruta,ruta_guardar_audio)
                            
                            
                            crear_comando(
                                nombre_input.value,
                                informacion_input.value,
                                mensaje_input.value,
                                costo_input.value,
                                audio_ruta,
                                # tecla_input.value
                            )
                            
                            comandos(sonidos=sonidos)
                        
                    
                    nombre_input = TextField(label="Nombre",value=elements[0])
                    
                    informacion_input = TextField(label="Detalles",value=elements[1])
                    
                    mensaje_input = TextField(label="Mensaje para el chat",value=elements[2])
                    
                    costo_input = TextField(label="Costo del comando",value=elements[3])
                    
                    sonido_input = Container(TextButton("Seleccionar audio",width=300,height=57,style=ButtonStyle   (shape=BeveledRectangleBorder()),on_click=seleccionar_audios),border=border.all(1,color="black"),border_radius=5)
                    
                    # tecla_input = TextField(label="Tecla a precionar",value=elements[5])
                    
                    enviar_inputs = Container(TextButton("Guardar comando",on_click=enviar_comando_inputs,width=250,height=57,style=ButtonStyle(shape=BeveledRectangleBorder())),border=border.all(1,color="black"))
                    
                    info_inputs = Column(
                        [
                            nombre_input,
                            informacion_input,
                            mensaje_input,
                            costo_input,
                            sonido_input,
                            # tecla_input,
                            enviar_inputs
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER)
                    
                    alerta = AlertDialog(
                        title=Text("Creación de comando"),
                        content=Text("@{user},{puntos}, {costo}",width=250),
                        actions=[
                            info_inputs
                        ],
                        actions_alignment=MainAxisAlignment.CENTER
                    )

                    page.dialog = alerta
                    
                    alerta.open = True
                    
                    page.update()
                
                
                observaciones = Text(size=20,text_align=TextAlign.CENTER,width=1000,color=text_color)
                    
                comandos_iconos = Row(
                    [
                        back_ico,
                        IconButton(
                            icon=icons.ADD_CIRCLE,
                            icon_color=icons_color,
                            icon_size=icons_size,
                            on_click=comando_inputs
                        ),
                        # IconButton(
                        #     icon=icons.EDIT,
                        #     icon_color=icons_color,
                        #     icon_size=icons_size
                        # ),
                        observaciones
                    ],vertical_alignment=CrossAxisAlignment.CENTER,height=60
                )
                
                elementos_comandos = []
                
                comandos_leer = read(source_comandos)
                
                def change(e:ContainerTapEvent):
                    
                    if e.data == "true":
                        
                        e.control.bgcolor = "green200"
                        
                        observaciones.value = e.control.content.content.controls[2].value
                    
                    
                    else:
                        
                        e.control.bgcolor = "blue50"
                        
                        observaciones.value = ""
                    
                    
                    container.update()
                
                
                def ingresar_datos():
                    
                    if sonidos:
                        
                        for i in comandos_leer:
                            
                            if comandos_leer[i]["accion"]["sonido"]["reproducir"]:
                                cost = comandos_leer[i]["costo"]
                                info = comandos_leer[i]["informacion"]
                                
                                ele = Container(
                                    ElevatedButton(
                                        content=Column(
                                            [
                                                Text(i,size=30,text_align=TextAlign.CENTER,color="black"),
                                                Text(f"Costo: {cost}",size=20,text_align=TextAlign.CENTER,color="black"),
                                                Text(info,size=15,text_align=TextAlign.START,height=87,color="black")
                                            ]),
                                        style=ButtonStyle(shape=BeveledRectangleBorder()),
                                        on_click=comando_inputs
                                    ),
                                    width=200,
                                    height=200,
                                    padding=5,
                                    bgcolor="blue50",
                                    on_hover=change
                                )
                                
                                elementos_comandos.append(ele)
                    
                    
                    else:
                        
                        for i in comandos_leer:
                            
                            if not comandos_leer[i]["accion"]["sonido"]["reproducir"]:
                                cost = comandos_leer[i]["costo"]
                                info = comandos_leer[i]["informacion"]
                                
                                ele = Container(
                                    ElevatedButton(
                                        content=Column(
                                            [
                                                Text(i,size=30,text_align=TextAlign.CENTER,color="black"),
                                                Text(f"Costo: {cost}",size=20,text_align=TextAlign.CENTER,color="black"),
                                                Text(info,size=15,text_align=TextAlign.START,height=87,color="black")
                                            ]),
                                        style=ButtonStyle(shape=BeveledRectangleBorder()),
                                        on_click=comando_inputs
                                    ),
                                    width=200,
                                    height=200,
                                    padding=5,
                                    bgcolor="blue50",
                                    on_hover=change
                                )
                                
                                elementos_comandos.append(ele)
                    
                    
                    comandos_elementos = Row(controls=elementos_comandos,wrap=True,height=600,scroll=ScrollMode.ADAPTIVE)
                    
                    comandos_interfaz = Stack([Column([comandos_iconos,comandos_elementos],horizontal_alignment=CrossAxisAlignment.CENTER)])
                    
                    container.content = comandos_interfaz
                    container.update()
                
                
                ingresar_datos()
            
                
            def sonidos(e):
                comandos(sonidos=True)
            
            
            def puntos(e):
                base = read(chat_twitch)
                columna.controls = []
                
                for i in base:
                    user = base[i]["nombre"]
                    puntaje = base[i]["puntos"]
                    texto = Text(f"{user}:   {puntaje}",color=colors.BLACK,size=25)
                    
                    columna.controls.append(texto)
                    bot_menu.update()
            
            
            bot_elementos = [
                ElevatedButton(content=Text("Comandos",color=colors.BLACK,size=30),width=250,height=250,style=button_style,bgcolor=button_bg_color,on_click=comandos),
                ElevatedButton(content=Text("Sonidos",color=colors.BLACK,size=30),width=250,height=250,style=button_style,bgcolor=button_bg_color,on_click=sonidos),
                ElevatedButton(content=Text("Puntos",color=colors.BLACK,size=30),width=250,height=250,style=button_style,bgcolor=button_bg_color,on_click=puntos),
                ElevatedButton(content=Text("Minijuegos",color=colors.BLACK,size=30),width=250,height=250,style=button_style,bgcolor=button_bg_color),
                columna
            ]
            
            bot_menu = Row(bot_elementos,alignment=MainAxisAlignment.CENTER,vertical_alignment=CrossAxisAlignment.START,wrap=True)
            
            container.content = bot_menu
            page.appbar = AppBar(
                title=TextButton(content=Text(
                    "Menu", color=colors.BLACK, size=30), on_click=bot_iniciar),
                center_title=True,
                bgcolor=colors.SURFACE_VARIANT
            )
            page.update()
        
        elemento = ElevatedButton(content=Text("Iniciar Bot",color=text_color,size=text_size),width=500,height=300,style=button_style,bgcolor=button_bg_color,on_click=bot_iniciar)
        
        container.content = Row([elemento],alignment=MainAxisAlignment.CENTER)
        container.update()
    

    
    page.add(container)
    
    bot()


if __name__ == "__main__":
    app(target=main)