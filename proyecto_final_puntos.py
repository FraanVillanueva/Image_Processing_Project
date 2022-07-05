import cv2
import math
import numpy as np
from scipy import signal
from PIL import ImageFilter
from PIL import Image
from PIL import ImageOps

#QUITAR FONDO
min_delta_c = 40
def imagen_filas(im):
    imagen=[]
    data=im.getdata(band=None)
    for i in range(im.size[1]):
        an=[]
        for j in range(im.size[0]*i,im.size[0]*(i+1)):
            an.append(data[j])
        imagen.append(an)
    return imagen

def color_fondo(imagen):#imagen=data
    rgb=[0,0,0]
    for q in range(20):
        for w in range(20):
            rgb[0]+=imagen[q][w][0]
            rgb[1]+=imagen[q][w][1]
            rgb[2]+=imagen[q][w][2]
    rgb[0]=rgb[0]/(20*20)
    rgb[1]=rgb[1]/(20*20)
    rgb[2]=rgb[2]/(20*20)
    return rgb

def quitar_fondo(data,im):
    imagen=im.load()
    rgb=color_fondo(data)
    for y in range(im.size[1]-1):
        for x in range(im.size[0]-1):
            deltac = math.sqrt(((imagen[x,y][1] - rgb[1]) ** 2))
            if deltac<min_delta_c:
                imagen[x,y]=(0,0,0)
    return imagen

#FUNCIONES PARA SOBEL
def sobel_x(imagen):
    matriz=np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    im=np.array(imagen)
    conv=signal.convolve2d(im,matriz,mode="full",fillvalue=0)
    return conv

def sobel_y(imagen):
    matriz=np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
    im=np.array(imagen)
    conv=signal.convolve2d(im,matriz,mode="full",fillvalue=0)
    return conv

def primera_derivada(imagen):
    gx=sobel_x(imagen)
    gy=sobel_y(imagen)
    lienzo=Image.new("L",(len(gx),len(gx[0])))
    for j in range(len(gx)):
        for i in range(len(gx[0])):
            x=gx[j][i].item()
            y = gy[j][i].item()
            g=int(math.sqrt(x**2+y**2))
            lienzo.putpixel((j,i),g)
    threshold(lienzo)
    lienzo=ImageOps.mirror(lienzo.rotate(270, expand=True))
    return (lienzo)

def threshold(imagen):
    for x in range(imagen.size[0]):
        for y in range(imagen.size[1]):
            pixel=imagen.getpixel((x,y))
            if 100>pixel:
                imagen.putpixel((x,y),0)

            else:
                imagen.putpixel((x,y),255)

def sobel(imagen):
    # PASAR IMAGEN A GRIS PARA APLICAR 1 GAUSSIANA
    im = imagen.convert("L")
    # GAUSSIANA PARA IMPEFECCIONES Y PRIMERA DERIVADA(radius=10)
    img1 = im.filter(ImageFilter.GaussianBlur(radius=1))
    lienzo = primera_derivada(img1)
    return lienzo

#CONTORNO ROSTRO
def filtro_gaussiano(objeto):
    filtro=[]
    dev_est=100000000000000000000000
    cero=(int(objeto.size[1]/2),int(objeto.size[1]/2))
    for i in range(objeto.size[1]):
        lista=[]
        for j in range(objeto.size[1]):
            x=i-cero[0]
            y=cero[1]-j
            G = (1 / (2 * math.pi * (dev_est * 2))) * np.exp(-((x ** 2) + (y ** 2)) / (2 * dev_est * 2))
            lista.append(G)
        filtro.append(lista)
    return filtro

def im_lista(imagen):
    imag=imagen.convert(mode="L")
    im=[]
    for j in range(imagen.size[1]):
        fila=[]
        for i in range(imagen.size[0]):
            gray = imag.getpixel((i,j))
            fila.append(gray)
        im.append(fila)
    return im

def mascara(lista,min,max):
    ancho=len(lista[0])
    largo=len(lista)
    lienzo=Image.new("L",(ancho,largo),color=0)
    for i in range(int(ancho)):
        for j in range(int(largo)):
            pixel=lista[j][i].item()
            if min<=pixel<=max:
                lienzo.putpixel((i,j),255)
    return lienzo

def poner_contorno(imagen_original):
    # contornos
    data = im_lista(imagen_original)
    objeto = Image.open("obj_chico.jpg")
    gaus = filtro_gaussiano(objeto)
    convolucion = signal.convolve2d(np.array(data), np.array(gaus), mode="same", fillvalue=0)
    contorno = mascara(convolucion, float(0.5e-20), float(1.01e-20))
    sob = sobel(imagen_original)
    #insertarlo en la imagen
    for j in range(10, size[1] - 10):
        for i in range(10, size[0] - 10):
            cont = contorno.getpixel((i, j))
            sobe = sob.getpixel((i, j))
            if cont == 255 or sobe == 255:
                canvas.putpixel((i, j), 0)
                canvas.putpixel((i, j+1), 0)
                canvas.putpixel((i, j-1), 0)
                canvas.putpixel((i+1, j), 0)
                canvas.putpixel((i-1, j), 0)


#PONERLE COLOR A HUELLA
def huella_color(huella,imagen_original,canvas):
    for y in range(10, size[1] - 10, 5):
        for x in range(10, size[0] - 10, 5):
            if y%2==0 and x<size[0] - 14:
                x+=3
                pixel_comp = imagen_original.getpixel((x, y))
                pixel = (pixel_comp[0] + pixel_comp[1] + pixel_comp[2]) / 3
                if pixel != 0:
                    for yy in range(-2, 3):
                        if abs(yy) == 0:
                            for n in range(-2, 3):
                                canvas.putpixel((x + n, y - yy), pixel_comp)
                        elif abs(yy) == 1:
                            for n in range(-1, 2):
                                canvas.putpixel((x + n, y - yy), pixel_comp)
                        else:
                            canvas.putpixel((x, y - yy), pixel_comp)
            elif y%2!=0:
                pixel_comp = imagen_original.getpixel((x, y))
                pixel = (pixel_comp[0] + pixel_comp[1] + pixel_comp[2]) / 3
                if pixel != 0:
                    for yy in range(-2, 3):
                        if abs(yy) == 0:
                            for n in range(-2, 3):
                                canvas.putpixel((x + n, y - yy), pixel_comp)
                        elif abs(yy) == 1:
                            for n in range(-1, 2):
                                canvas.putpixel((x + n, y - yy), pixel_comp)
                        else:
                            canvas.putpixel((x, y - yy), pixel_comp)

    return canvas



#___________________________________________________MAIN_______________________________________________________________

#_____________ROSTRO____________

#se quita fondo
imagen_original=Image.open("rostro.jpg")
data=imagen_filas(imagen_original)
quitar_fondo(data,imagen_original)

#resize (para que sea más rapido)
imagen_original=imagen_original.resize((int(imagen_original.size[0]*0.75),int(imagen_original.size[1]*0.75)),Image.NEAREST)

#dimensiones imagen
size=imagen_original.size


#___________LIENZO_______________
#nuevo lienzo
canvas= Image.new("RGB",size,color="white")

#poner colores
huella=1
canvas=huella_color(huella,imagen_original,canvas)

#poner contornos
poner_contorno(imagen_original)

#show lienzo
canvas.save("rostro_puntos.jpg")