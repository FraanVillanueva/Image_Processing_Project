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
    L=0
    for q in range(20):
        for w in range(20):
            L+=imagen[q][w]

    Lfinal=L/(20*20)
    return Lfinal

def quitar_fondo(data,im):
    imagen=im.load()
    L=color_fondo(data)
    for y in range(im.size[1]-1):
        for x in range(im.size[0]-1):
            deltac = math.sqrt((imagen[x,y] - L) ** 2)
            if deltac<min_delta_c:
                imagen[x,y]=0
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
    lienzo=Image.new("L",(len(gx),len(gx[0])),color=0)
    for j in range(5,len(gx)-5):
        for i in range(5,len(gx[0])-5):
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

#ESQUELETONIZACION HUELLA
def squeletonizacion(imagen):
    squeleto = np.zeros(imagen.shape,np.uint8)
    while True:
        erosion = cv2.erode(imagen, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))
        dilatacion = cv2.dilate(erosion,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3)))
        cascara = cv2.subtract(imagen,dilatacion)
        squeleto = cv2.bitwise_or(squeleto,cascara)
        imagen = erosion
        if cv2.countNonZero(imagen)==0:
            break
    cv2.imwrite("squeleton.jpg",squeleto)

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
    def condicion(i, j):
        if min <= lista[j][i].item() <= max: lienzo.putpixel((i, j), 255)
    [condicion(i, j) for i in (i for i in range(int(ancho))) for j in (i for i in range(int(largo)))]
   # for i in range(int(ancho)):
   #     for j in range(int(largo)):
   #         pixel=lista[j][i].item()
   #         if min<=pixel<=max:
   #             lienzo.putpixel((i,j),255)
    return lienzo

def poner_contorno(imagen_original,canvas,huella_contorno):
    # contornos
    data = im_lista(imagen_original)
    objeto = Image.open("obj_chico.jpg")
    gaus = filtro_gaussiano(objeto)
    convolucion = signal.convolve2d(np.array(data), np.array(gaus), mode="same", fillvalue=0)
    contorno = mascara(convolucion, float(0.5e-20), float(1.01e-20))
    sob = sobel(imagen_original)
    # resize huella(11,15)
    huella = huella_contorno.resize((11,15), Image.BILINEAR)
    # insertarlo en la imagen
    for j in range(10, size[1] - 10):
        for i in range(10, size[0] - 10):
            cont = contorno.getpixel((i, j))
            sobe = sob.getpixel((i, j))
            if cont == 255 or sobe == 255:
                for n in range(-5, 6):
                    for m in range(-7, 8):
                        p_huella = huella.getpixel((5 + n,7-m))
                        if p_huella!=0:
                            canvas.putpixel((i+n,j+m),0)

#PONERLE COLOR A HUELLA
def huella_color(huella_contorno,imagen_original,canvas):
    #huella resize
    huella = huella_contorno.resize((41,61), Image.BILINEAR)
    for y in range(31, size[1] - 31, 61):
        for x in range(21, size[0] - 21, 41):
            if y%2==0 and x<size[0] - 71:
                x=x+25
                pixel_comp = imagen_original.getpixel((x, y))
                if pixel_comp != 0:
                    for n in range(-20, 21):
                        for m in range(-30, 31):
                            p_huella = huella.getpixel((20 + n, 30 - m))
                            if p_huella != 0:
                                canvas.putpixel((x + n, y + m), pixel_comp)
            elif y%2!=0:
                pixel_comp = imagen_original.getpixel((x, y))
                if pixel_comp !=0:
                    for n in range(-20, 21):
                        for m in range(-30, 31):
                            p_huella = huella.getpixel((20 + n,30-m))
                            if p_huella!=0:
                                canvas.putpixel((x+n,y+m),pixel_comp)

    return canvas


#___________________________________________________MAIN_______________________________________________________________

#_____________HUELLA_____________
huella=Image.open("huella.jpg")

#sobel y valor umbral
huella_contorno=sobel(huella)

#pasar de PIL a CV2
opencvImage = np.asarray(huella_contorno)

#esqueletonizar
squeletonizacion(opencvImage)
huella_contorno=Image.open("squeleton.jpg")


#_____________ROSTRO____________

#se quita fondo
imagen_original=Image.open("rostro.jpg").convert("L")
data=imagen_filas(imagen_original)
quitar_fondo(data,imagen_original)

#resize
imagen_original=imagen_original.resize((int(imagen_original.size[0]*3),int(imagen_original.size[1]*3)),Image.BILINEAR)

#dimensiones imagen
size=imagen_original.size


#___________LIENZO_______________
#nuevo lienzo
canvas= Image.new("L",size,color="white")

#poner colores
canvas=huella_color(huella_contorno,imagen_original,canvas)

#poner contornos
poner_contorno(imagen_original,canvas,huella_contorno)

#show lienzo
canvas.save("rostro_L_300_40.jpg")