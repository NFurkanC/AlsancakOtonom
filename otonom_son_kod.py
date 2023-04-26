import cv2
import numpy as np
from pySerialTransfer import pySerialTransfer as txfer
import time
import math

def round_to_multiple(number, multiple): # EK KOD
    return multiple * round(number / multiple)


yaricap_alt = 0
class struct(object):
    gyroX = 0
    gyroY = 0
    comm_test = 0
    basinc = 0
    sicaklik = 0

class struct1(object):
    birinci_button = 0
    ikinci_button = 0
    aracin_ileri_degeri = 0
    aracin_x_degeri = 0
    aracin_y_degeri = 0
    aracin_donus_degeri = 0


rovVeriAl = struct
rovVeriGonder = struct1

cap = cv2.VideoCapture(1)
cap_alt = cv2.VideoCapture(1)

A = 120
T = 40
f = 1 / T

dict = {"mid": 0, "right": math.pi/2, "left": - math.pi / 2}

startpoint = "left"

oncam = True
ileri_kontrol = False
ileri_kontrol_alt = False
her_ne_olursa_olsun_asagi_in =False

yaricap = 0
noktax = 0
noktay = 0

noktax_alt = 0
noktay_alt = 0
radius = 0

alan = 0
rect_color = [0,0,0]
rect_color_alt = [0,0,0]

link = txfer.SerialTransfer('COM4' , baud = 112500)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')

writer1 = cv2.VideoWriter('sualti11.avi', fourcc, 20.0, (640, 480))
link.open()

time.sleep(2)

hedef_bas = time.time() + 2

while hedef_bas > time.time():
    rovVeriGonder.aracin_ileri_degeri = 80

timestart = time.time()

while True:
    time.sleep(0.01)

    ret , frame = cap.read()
    ret_2 , frame_alt = cap_alt.read()
    
    if ret is None:
        print("kamera 1 çalışmadı")
        continue
    if ret_2 is None:
        print("kamera 2 çalışmadı")
        continue

    #frame = cv2.flip(frame , 1)   #araçta olmayacak
    #frame_alt = cv2.flip(frame_alt , 1)

    frame = cv2.medianBlur(frame , 5)

    asagi = np.array([0,0,30])
    yukari = np.array([64,100,140]) # 64 100 140

    if oncam == True:

        hsv_frame = cv2.cvtColor(frame , cv2.COLOR_BGR2HSV)

        maske = cv2.inRange(hsv_frame , asagi , yukari)

        (kontur , hierarsi) = cv2.findContours(maske.copy() , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)

        for knt in kontur:
            alan = cv2.contourArea(knt)

            if alan > 30:
                c = max(kontur , key=cv2.contourArea)
                dikdortgen = cv2.minAreaRect(c)
                ((x , y) , (genislik , yukseklik) , rotasyon) =  dikdortgen

                M = cv2.moments(c)

                if M["m00"] == 0.0:
                    M["m00"] = 0.00000001
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))   # nesnenin orta noktasının bulunması
                noktax = center[0]   #orta noktanın x ekseninin bulunması
                noktay = center[1]   #y ekseninin bulunması
                

                yaricap = int(max(genislik , yukseklik) / 2)
                alan = 3.14*yaricap*yaricap

                cv2.circle(frame , center , 1 , (255,0,0) , 2)
                cv2.circle(frame , center , yaricap , (0,0,255) , 2)

        if len(kontur) == 0:
            yaricap = 0
        

        fark_x = noktax - 320
        hiz_x = (fark_x * 1.5) #ayarlanacak deger anlamına geliyor

        #yaricap = yaricap * 0.1 # KALDIR YARIÇAP
        
        if ileri_kontrol == False: #dogru yada yanlıs olabilir

            if yaricap > 70: # HATALI ALGILAMALARIN FİLTRELENMESİ - ben bir cisim gordüysem aracın cisme sagda ve soldan ortalanması icin gerekli hiz degerlerini yazdir. 90'ın üstündeki çemberler göz önüne alınır
                rovVeriGonder.aracin_x_degeri = int(hiz_x) 
                if rovVeriGonder.aracin_x_degeri > 200: rovVeriGonder.aracin_x_degeri = 200
                if rovVeriGonder.aracin_x_degeri < -200: rovVeriGonder.aracin_x_degeri = -200 #sınırlama degerleri
                rovVeriGonder.aracin_ileri_degeri = 0
                rovVeriGonder.aracin_y_degeri = 0
                #print("motor hizi : " , int(hiz_x))
                if 300 < noktax < 340: #arac hareketleri sonucunda ortalama islemi gerceklestirdiyse
                    print("düz git") 
                    ileri_time1 = time.time() #timer baslat **** Timerin ilk ayagına bir kere girmeli ****
                    rect_color = [255,0,0] #timerin ilk ayagına her girdiginde timer sıfırlanır
                    ileri_kontrol = True #bu if bloguna br daha girilmeyecegi anlamına gelir (tekrar ileri_kontrol degeri == False olana kadar)
            else:
                
                #"""
                x = time.time() - timestart
                spd = int(A * math.cos(2 * math.pi * f * x + dict[startpoint]))
                spd = round_to_multiple(spd, 5)
                #"""
                
                """

                time1 = time.time()

                
                if time1 - timestart < 5:
                    spd = -60
                    
                else:

                    time1 = time1 - timestart + 5

                    time1 = time1 % 20

                    if time1 > 10:
                        spd = 60
                    else:
                        spd = -60
                
                """
                
                """
                if time1 - timestart < 5:
                    time1 = -60
                    
                time1 = time1 - timestart

                time1 = time1 % 20


                if time1 > 10:
                    time1 = 60
                else:
                    time1 = -60

                spd = time1

                """

                print(spd)
                rovVeriGonder.aracin_x_degeri = spd
                rovVeriGonder.aracin_ileri_degeri = 120 # 80 yaptık ilk
                rovVeriGonder.aracin_y_degeri = 0

        else: #ileri_ontrol degerinin False oldugu yer burasidir. 
            ileri_time2 = time.time() #****ikinci ayagına ise her seferinde girmeli ****
            ileri_simdi_zamani = ileri_time2 - ileri_time1 #timerin saymaya baslar 
            if(ileri_simdi_zamani <= 3): #timerim 4 saniyden küçükce bu if bloguna gir
                #print("zaman degeri : ", ileri_simdi_zamani)
                rovVeriGonder.aracin_ileri_degeri = 80 #araca ileri degeri vermek
                rovVeriGonder.aracin_x_degeri = 0
                rovVeriGonder.aracin_y_degeri = 0
            else:  #4 saniye gectiyse terar ileri kontrol degerini false yap ve cisim algılamaya ve ortalamaya calis
                ileri_kontrol = False

        if yaricap > 105: # ALT KAMERAYA GEC -  her ne olursa olsun yaricap 220'nin üstünde ise oncam cık !!!!!!!!!!!!
            print("yaricap artti oncam false")
            rovVeriGonder.aracin_x_degeri = 0
            rovVeriGonder.aracin_ileri_degeri = 0
            rovVeriGonder.aracin_y_degeri = 0
            oncam = False
        else:
            #print("motor hizi : " , hiz_x)
            rect_color = [0,0,0]

        cv2.rectangle(frame , (300 , 220) , (340 , 260) , rect_color , 2)
        writer1.write(frame)
        cv2.imshow("Frame" , frame)

# 0 0 0
# 33 228 242

#oncam false

    else: #ON CAMERA FALSE

        asagi_alt = np.array([0,75,67]) # (0-) 0 0 0 (1-) 0 0 0 (2-) 0 99 0
        yukari_alt = np.array([26,255,212]) # (0-) 33, 228, 242 (1-) 29 216 206 (2-) 23 255 207

        hsv_frame_alt = cv2.cvtColor(frame_alt , cv2.COLOR_BGR2HSV)

        maske_alt = cv2.inRange(hsv_frame_alt , asagi_alt , yukari_alt)

        (kontur_alt , hierarsi_alt) = cv2.findContours(maske_alt.copy() , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)

        for knt_alt in kontur_alt:
            alan_alt = cv2.contourArea(knt_alt)

            if alan_alt > 67:
                c = max(kontur_alt , key=cv2.contourArea)
                dikdortgen = cv2.minAreaRect(c)
                ((x , y) , (genislik , yukseklik) , rotasyon) =  dikdortgen

                M = cv2.moments(c)

                if M["m00"] == 0.0:
                    M["m00"] = 0.00000001
                center_alt = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))   # nesnenin orta noktasının bulunması
                noktax_alt = center_alt[0]   #orta noktanın x ekseninin bulunması
                noktay_alt = center_alt[1]   #y ekseninin bulunması

                yaricap_alt = int(max(genislik , yukseklik) / 2)
                alan_alt = 3.14*yaricap_alt*yaricap_alt

                cv2.circle(frame_alt , center_alt , 1 , (255,0,0) , 2)
                cv2.circle(frame_alt , center_alt , yaricap_alt , (0,0,255) , 2)

        if len(kontur_alt) == 0:
            yaricap_alt = 0
        #alt kamerada bir sag- sol hareketi yapmam lazım 
        #alt kamerada bir ileri geri hareketi yapmam lazım 
        fark_x_alt = noktax_alt - 320
        hiz_x_alt = (fark_x_alt * 0.5)

        fark_y_alt = noktay_alt - 240
        hiz_y_alt = (fark_y_alt * 0.6)

        #yaricap_alt = yaricap_alt * 0.1 # KALDIRILACAK YARIÇAPALT

        if ileri_kontrol_alt == False: # İLERİ GİDEREK ORTALAMA 

            if yaricap_alt > 90:
                rovVeriGonder.aracin_x_degeri = int(hiz_x_alt)
                rovVeriGonder.aracin_ileri_degeri = 0
                rovVeriGonder.aracin_y_degeri = 0

                if 300 < noktax_alt < 340:
                    print("sag ve sol eksende ortaladim ileri geri yaparak ortalamam lazim")
                    rect_color_alt = [255,0,0]
                    ileri_time1_alt = time.time()
                    ileri_kontrol_alt = True

                else:
                    rect_color_alt = [0,0,0]


            else: 
                print("arac henüz cember gormedi ilerleyip goruruz..")
                rovVeriGonder.aracin_x_degeri = 0
                rovVeriGonder.aracin_ileri_degeri = 80
                rovVeriGonder.aracin_y_degeri = 0

        else:  #  körlemesine ileri

            ileri_time2_alt = time.time()
            ileri_simdi_zamani_alt = ileri_time2_alt - ileri_time1_alt

            if ileri_simdi_zamani_alt <=0.5:
                rovVeriGonder.aracin_x_degeri = 0
                rovVeriGonder.aracin_ileri_degeri = 80
                rovVeriGonder.aracin_y_degeri = 0

            elif ileri_simdi_zamani_alt >0.5:

                ileri_kontrol_alt = False

        if yaricap_alt > 170: # ALT KAMERA INIS - gelmek istediğim 240 degerine pay vererek geldim.!!!!!!!!!!!!!! **
            rect_color_alt = [0,255,0] #**
            print("Aşaği in ve çemebre otur degerini true yap") #**
            her_ne_olursa_olsun_asagi_in = True #buraya bir kere girmesi yetecek #**

        #if yaricap_alt > 300: # ALT KAMERA INIS - gelmek istediğim 240 degerine pay vererek geldim.!!!!!!!!!!!!!!
        #    rect_color_alt = [0,255,0]
        #    print("Aşaği in ve çemebre otur degerini true yap")
        #    her_ne_olursa_olsun_asagi_in = True #buraya bir kere girmesi yetecek
  
        #else:
        #    rect_color_alt = [255,0,0]
        #her_ne_olursa_olsun_asagi_in = False # garanti durdurmak için NORMALDE KALDIRILACAK
        if her_ne_olursa_olsun_asagi_in:
            
            rect_color_alt = [0,255,0]
            print("asagi iniyor ve oturuyorum.. ")
            rovVeriGonder.aracin_x_degeri = 0
            rovVeriGonder.aracin_ileri_degeri = 0
            rovVeriGonder.aracin_y_degeri = 50 #!!!!!!!!!!!!!!!!!! 50 20 falan yap

        else: #**
            rect_color_alt = [255,0,0] #**


        cv2.rectangle(frame_alt , (300 , 220) , (340 , 260) , rect_color_alt , 2)
        cv2.imshow("Alt Kamera" , frame_alt)
        cv2.imshow("Maske" , maske_alt)

    #Haberlesmenin basladıgı yer
    '''
    rovVeriGonder.birinci_button = 1
    rovVeriGonder.ikinci_button = 1
    
    rovVeriGonder.aracin_ileri_degeri = 80
    rovVeriGonder.aracin_x_degeri = 0
    rovVeriGonder.aracin_y_degeri = 0 #yükseliş
    rovVeriGonder.aracin_donus_degeri = 0
    '''
    #rovVeriGonder.aracin_y_degeri = 0 #yükseliş çalışmayacaksa yorum satırından çıkarın

    sendSize = 0
    try:
        sendSize = link.tx_obj(rovVeriGonder.aracin_ileri_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_y_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_x_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_donus_degeri, start_pos=sendSize)
    except:#KALDIRILACAK
        print("sendsizehata")

    try:#KALDIRILACAK
        link.send(sendSize)
    except:#KALDIRILACAK
        print("sendhata")
    #veriyi gonderiyorum 

    if not link.available(): #kontrol tarafı
        print("hata")
        print(f"link status {link.status}")
        if link.status < 1:
            if link.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif link.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif link.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(link.status))
    
    veriBoyut = 0
    try: #KALDIRILACAK
        rovVeriAl.gyroX = link.rx_obj(obj_type=type(rovVeriAl.gyroX), obj_byte_size=sendSize, start_pos=veriBoyut)
        rovVeriAl.gyroY = link.rx_obj(obj_type=type(rovVeriAl.gyroY), obj_byte_size=sendSize, start_pos=veriBoyut + 4)
        rovVeriAl.comm_test = link.rx_obj(obj_type=type(rovVeriAl.comm_test), obj_byte_size=sendSize, start_pos=veriBoyut + 8)
        rovVeriAl.basinc = link.rx_obj(obj_type=type(rovVeriAl.basinc), obj_byte_size=sendSize, start_pos=veriBoyut + 12)
        rovVeriAl.sicaklik = link.rx_obj(obj_type=type(rovVeriAl.sicaklik), obj_byte_size=sendSize, start_pos=veriBoyut + 16)
    except:#KALDIRILACAK
        print("verialhata")
    '''
    print("gyroX gonderilen deger : ", str(rovVeriAl.gyroX))
    print("gyroy dongerilen deger", str(rovVeriAl.gyroY))
    print("commTEstdegeri : ", str(rovVeriAl.comm_test))



    print("Sicaklik degeri : ", str(rovVeriAl.sicaklik))
    print("**************************")
    '''
    #print('aaracinx_degeri : ',rovVeriAl.sicaklik )
    if oncam:
        print("yaricap: ", yaricap),
    else:
        print("yaricap_alt : " , yaricap_alt)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        
        rovVeriGonder.aracin_ileri_degeri = 0
        rovVeriGonder.aracin_x_degeri = 0
        rovVeriGonder.aracin_y_degeri = 0 #yükseliş
        rovVeriGonder.aracin_donus_degeri = 0
        time.sleep(2)
        sendSize = 0
        sendSize = link.tx_obj(rovVeriGonder.aracin_ileri_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_y_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_x_degeri, start_pos=sendSize)
        sendSize = link.tx_obj(rovVeriGonder.aracin_donus_degeri, start_pos=sendSize)

        link.send(sendSize)

        if not link.available(): #kontrol tarafı
            if link.status < 1:
                if link.status == txfer.CRC_ERROR:
                    print('ERROR: CRC_ERROR while exiting')
                elif link.status == txfer.PAYLOAD_ERROR:
                    print('ERROR: PAYLOAD_ERROR while exiting')
                elif link.status == txfer.STOP_BYTE_ERROR:
                    print('ERROR: STOP_BYTE_ERROR while exiting')
                else:
                    print('ERROR: {}'.format(link.status))
        break

cap.release()
cap_alt.release()
writer1.release()
cv2.destroyAllWindows()