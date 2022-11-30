import random as ra
import haravasto
import math
import json

IKKUNAN_LEVEYS = 1200
IKKUNAN_KORKEUS = 600
PUTOAMISKIIHTYVYYS = 0.5
PK_GRAFIIKKASORSA = 0.4
ALKUP_X = 70
ALKUP_Y = 100
VOIMAKERROIN = 0.4
POMPPUKERROIN = -0.4

peli = {
    "laatikot": [],
    "esteet": [],
    "n_sorsat": 5,
    "taso": 0,
    "x": ALKUP_X,
    "y": ALKUP_Y,
    "kulma": 0,
    "voima": 0,
    "vx": 0,
    "vy": 0,
    "lennossa": False,
    "kuva": "sorsa",
    "tila": "paavalikko",
    "tulos": 0,
    "paalla": False
    }

grafiikkasorsa = {
    "x": -400,
    "y": -70,
    "vx": 20,
    "vy": 20,
    "kuva": "sorsa"
}

#Grafiikkasorsa

def lento_grafiikkasorsa(kulunut_aika):
    """
    Funktio alkunäytössä näkyvän sorsan lennolle.
    """
    grafiikkasorsa["x"] += grafiikkasorsa["vx"]
    grafiikkasorsa["y"] += grafiikkasorsa["vy"]
    grafiikkasorsa["vy"] -= PK_GRAFIIKKASORSA
    if grafiikkasorsa["x"] >= IKKUNAN_LEVEYS + 360:
        grafiikkasorsa["x"] = IKKUNAN_LEVEYS + 360
        grafiikkasorsa["vx"] *= -1
        grafiikkasorsa["vy"] *= -1
        grafiikkasorsa["vy"] -= PK_GRAFIIKKASORSA
        vaihda_kuva(grafiikkasorsa)
    if grafiikkasorsa["x"] <= -400:
        grafiikkasorsa["x"] = -400
        grafiikkasorsa["vx"] *= -1
        grafiikkasorsa["vy"] *= -1
        grafiikkasorsa["vy"] -= PK_GRAFIIKKASORSA
        vaihda_kuva(grafiikkasorsa)

#Sorsaan liittyvät funktiot

def alkutila():
    """
    Asettaa pelin takaisin alkutilaan, eli sorsan lähtöpaikkaan, 
    sen nopeudet nollaan, sekä lentotilan epätodeksi.
    """    
    peli["x"] = ALKUP_X
    peli["y"] = ALKUP_Y
    peli["vx"] = 0
    peli["vy"] = 0
    peli["n_sorsat"] -= 1
    peli["lennossa"] = False
    peli["kuva"] = "sorsa"

def muunna_koordinaateiksi(sade, kulma):
    """
    Muuntaa napakoordinaatit koordinaateiksi.
    """
    koordx = math.cos(kulma) * sade
    koordy = math.sin(kulma) * sade
    return koordx, koordy

def ammu(x, y, nappi=haravasto.HIIRI_VASEN, muokkausnapit=haravasto.MOD_SHIFT):
    """
    Funktio lähettää sorsan liikkeelle ja laskee sille lähtönopeuden, 
    sijoittaen x- ja y-nopeusvektorit globaaliin sanakirjaan.
    """
    nollatilanne = laske_etaisyys(peli["x"], peli["y"], ALKUP_X, ALKUP_Y) <= 20
    if nollatilanne:
        peli["x"] = ALKUP_X
        peli["y"] = ALKUP_Y
    elif not peli["lennossa"] and peli["paalla"]:
        peli["voima"] = laske_etaisyys(peli["x"], peli["y"], ALKUP_X, ALKUP_Y)
        if peli["voima"] > 69:
            peli["voima"] = 69
        peli["kulma"] = math.atan2((ALKUP_Y - peli["y"]), (ALKUP_X - peli["x"]))
        peli["vx"], peli["vy"] = muunna_koordinaateiksi(peli["voima"], peli["kulma"])
        peli["vx"] *= VOIMAKERROIN
        peli["vy"] *= VOIMAKERROIN
        peli["lennossa"] = True

def lento(kulunut_aika):
    """
    Funktio päivittää laatikon muuttuneet x- ja y-koordinaatit 
    kappaleen nopeusvektorien perusteella.
    """
    peli["x"] += peli["vx"]
    peli["y"] += peli["vy"]
    peli["vy"] -= PUTOAMISKIIHTYVYYS
    if peli["y"] <= 0:
        peli["y"] = 0
        peli["vy"] *= POMPPUKERROIN
        peli["vx"] *= 0.7
    if peli["x"] > IKKUNAN_LEVEYS + 50 or peli["x"] < -80:
        alkutila()
    elif abs(peli["vx"]) < 0.01 and abs(peli["vy"]) <= PUTOAMISKIIHTYVYYS:
        alkutila()

def kasittele_raahaus(sijx=0, sijy=0, muutosx=0, muutosy=0, painike=haravasto.HIIRI_VASEN, muokkaus=haravasto.MOD_SHIFT):
    """
    Tätä funktiota kutsutaan kun käyttäjä liikuttaa hiirtä jonkin painikkeen
    ollessa painettuna. Siirtää ruudulla olevaa laatikkoa saman verran kuin kursori
    liikkui.
    """
    if not peli["lennossa"] and peli["paalla"]:
        peli["x"] += muutosx
        peli["y"] += muutosy


def laske_etaisyys(alkux, alkuy, loppux, loppuy):
    """
    Laskee kahden pisteen välisen etäisyyden ja palauttaa sen.
    """
    etaisyys = math.sqrt((alkux - loppux) ** 2 + (alkuy - loppuy) ** 2)
    return etaisyys

def rajaa_ympyraan(koordx, koordy, keskx, kesky, sade):
    """
    Siirtää pisteen ympyrän kehälle, mikäli annettu piste
    ei ole valmiiksi ympyrän sisällä.
    """
    etaisyys = laske_etaisyys(koordx, koordy, keskx, kesky)
    if etaisyys > sade:
        uusix = (koordx - keskx) / (etaisyys / sade) + keskx
        uusiy = (koordy - kesky) / (etaisyys / sade) + kesky
    else:
        uusix = koordx
        uusiy = koordy
    return uusix, uusiy

def alue(kulunut_aika):
    """
    Pitää sorsan näkymättömän ympyrän sisällä, kun se ei ole lennossa.
    """
    peli["x"], peli["y"] = rajaa_ympyraan(peli["x"], peli["y"], ALKUP_X, ALKUP_Y, 69)






#Laatikoihin liittyvät funktiot

def luo_laatikot(nlaatikot):
    """
    Luo halutun määrän laatikoita ja asettaa ne satunnaisiin kohtiin määritetyn
    alueen sisälle. Laatikot esitetään sanakirjoilla joissa on seuraavat avaimet:
    x: vasemman alakulman x-koordinaatti
    y: vasemman alakulman y-koordinaatti
    w: laatikon leveys
    h: laatikon korkeus
    vy: laatikon putoamisnopeus
    """
    for i in range(nlaatikot):
        if len(peli["laatikot"]) > 0:
            while True:
                paikka_x = ra.randint(18, 29) * 40
                paikka_y = ra.randint(0, 14) * 40
                luvallinen = True
                for i in range(len(peli["laatikot"])):    
                    sivusuunta = paikka_x == peli["laatikot"][i]["x"]
                    pystysuunta = paikka_y == peli["laatikot"][i]["y"]
                    ylapuolella = paikka_y == peli["laatikot"][i]["y"] + 40
                    alapuolella = paikka_y == peli["laatikot"][i]["y"] - 40
                    if sivusuunta and (pystysuunta or ylapuolella or alapuolella):
                        luvallinen = False
                        break
                if luvallinen:
                    break
        else:
            paikka_x = ra.randint(18, 29) * 40
            paikka_y = ra.randint(0, 14) * 40
        peli["laatikot"].append({
            "x": paikka_x,
            "y": paikka_y,
            "w": 40,
            "h": 40,
            "vy": 0
            })

def luo_esteet():
    """
    Luo halutun määrän esteitä ja asettaa ne satunnaisiin kohtiin määritetyn
    alueen sisälle. Laatikot esitetään sanakirjoilla joissa on seuraavat avaimet:
    x: vasemman alakulman x-koordinaatti
    y: vasemman alakulman y-koordinaatti
    w: laatikon leveys
    h: laatikon korkeus
    vy: laatikon putoamisnopeus
    """
    for i in range(len(peli["laatikot"])):
        paikka_x = peli["laatikot"][i]["x"] 
        paikka_y = peli["laatikot"][i]["y"] - 40
        peli["esteet"].append({
            "x": paikka_x,
            "y": paikka_y,
            "w": 40,
            "h": 40,
            })

def jarjestelya(joku):
    """
    Avain sortille pudota-funktiossa.
    """
    return joku["y"]

def jarjestelya_2(joku):
    """
    Järjestää laatikot ja esteet niiden etäisyyden perusteella sorsaan.
    """
    return laske_etaisyys(peli["x"], peli["y"], joku["x"], joku["y"])

def kosketus(sanakirja, paikka, lista, lista2):
    """
    Tarkistaa kahden laatikon tai esteen kosketuksen.
    """
    totuusarvo = False
    if paikka == 0:
        if sanakirja["y"] <= 0:
            sanakirja["y"] = 0
            totuusarvo = True    
    else:    
        for i in range(paikka):
            xkoord = lista[paikka - i - 1]["x"]
            ykoord = lista[paikka - i - 1]["y"]
            leveys = lista[paikka - i - 1]["w"]
            korkeus = lista[paikka - i - 1]["h"]
            oikea = sanakirja["x"] < xkoord + leveys
            vasen = sanakirja["x"] + sanakirja["w"] > xkoord
            yla = sanakirja["y"] <= ykoord + korkeus
            if oikea and vasen and yla:
                sanakirja["y"] = ykoord + korkeus
                totuusarvo = True
                break
            elif sanakirja["y"] <= 0:
                sanakirja["y"] = 0
                totuusarvo = True
                break

    for i in range(len(lista2)):
        xkoord = lista2[i]["x"]
        ykoord = lista2[i]["y"]
        leveys = lista2[i]["w"]
        korkeus = lista2[i]["h"]
        oikea = sanakirja["x"] < xkoord + leveys
        vasen = sanakirja["x"] + sanakirja["w"] > xkoord
        yla = sanakirja["y"] <= ykoord + korkeus
        ala = sanakirja["y"] + sanakirja["h"] > ykoord
        if oikea and vasen and yla and ala:
            sanakirja["y"] = ykoord + korkeus
            return True
    else:
        return totuusarvo
    
def pudota(lista, lista2):
    """
    Pudottaa annetussa listassa olevia neliskanttisia objekteja (määritelty
    sanakirjana jossa vasemman alakulman x, y -koordinaatit, leveys, korkeus sekä
    nopeus pystysuuntaan). Funktio pudottaa laatikoita yhtä aikayksikköä
    vastaavan matkan.
    """
    lista.sort(key=jarjestelya)
    for i, sanakirja in enumerate(lista):
        if not kosketus(sanakirja, i, lista, lista2):
            sanakirja["vy"] += PUTOAMISKIIHTYVYYS
            sanakirja["y"] -= sanakirja["vy"]

def paivita(kulunut_aika):
    """
    Pudota-funktio muodossa, jonka toistuva käsittelijä hyväksyy.
    """
    pudota(peli["laatikot"], peli["esteet"])

def vaihda_kuva(lista):
    """
    Vaihtaa sorsan kuvaketta.
    """
    if lista["kuva"] == "sorsa":
        lista["kuva"] = "sorsa_reverse"
    else:
        lista["kuva"] = "sorsa"




#Sorsan törmäys laatikoihin ja esteisiin

def tormays(lista):
    """
    Tarkistaa sorsan ja laatikon törmäyksen ja poistaa laatikon kosketuksesta.
    Sorsa kimpoaa laatikosta riippuen, mistä suunnasta se laatikkoon osui.
    Lisäksi funktio vaihtaa sorsan kuvan peilikuvaksi, mikäli sen nopeus
    x-suunnassa vaihtuu. Funktio myös käsittelee maasta pomppimisen.
    """
    lista.sort(key=jarjestelya_2)
    if len(lista) > 0:
        for i in range(1):
            sanakirja = lista[0]
            kosketus_x = peli["x"] + 40 > sanakirja["x"] and peli["x"] < sanakirja["x"] + 40
            kosketus_y = peli["y"] < sanakirja["y"] + 40 and peli["y"] + 40 > sanakirja["y"]
            tulo_vas = abs(peli["x"] + 40 - sanakirja["x"]) <= abs(peli["vx"])
            tulo_oik = abs(sanakirja["x"] + 40 - peli["x"]) <= abs(peli["vx"])
            tulo_yla = abs(sanakirja["y"] + 40 - peli["y"]) <= abs(peli["vy"])
            tulo_ala = abs(peli["y"] + 40 - sanakirja["y"]) <= abs(peli["vy"]) + abs(sanakirja["vy"])
            laatikko_nopeampi = - sanakirja["vy"] < peli["vy"]
            tulo_vas_vaihtoehtoinen = abs(peli["x"] + 40 - sanakirja["x"]) <= abs(peli["vx"]) / 0.7
            tulo_oik_vaihtoehtoinen = abs(sanakirja["x"] + 40 - peli["x"]) <= abs(peli["vx"]) / 0.7
            if kosketus_x and kosketus_y:
                if tulo_vas and peli["vx"] > 0:
                    peli["x"] = sanakirja["x"] - 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)
                elif tulo_oik and peli["vx"] < 0:
                    peli["x"] = sanakirja["x"] + 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)
                elif tulo_ala and laatikko_nopeampi and not peli["y"] <= 0:
                    peli["y"] = sanakirja["y"] - 40
                    peli["vy"] *= -1
                elif tulo_yla and peli["vy"] < 0:
                    peli["y"] = sanakirja["y"] + 40
                    peli["vy"] *= POMPPUKERROIN
                    peli["vx"] *= 0.7
            if kosketus_x and kosketus_y:
                if tulo_vas_vaihtoehtoinen and peli["vx"] > 0:
                    peli["x"] = sanakirja["x"] - 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)      
                elif tulo_oik_vaihtoehtoinen and peli["vx"] < 0:
                    peli["x"] = sanakirja["x"] + 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)            
                lista.remove(sanakirja)

def tormays_paivitys(kulunut_aika):
    """
    Törmäysfunktio muodossa, jonka toistuva käsittelijä hyväksyy.
    """
    tormays(peli["laatikot"])

def este_tormays(lista):
    """
    Tarkistaa sorsan ja esteen törmäyksen.
    Sorsa kimpoaa esteestä riippuen, mistä suunnasta se laatikkoon osui.
    Lisäksi funktio vaihtaa sorsan kuvan peilikuvaksi, mikäli sen nopeus
    x-suunnassa vaihtuu.
    """
    lista.sort(key=jarjestelya_2)
    if len(lista) > 0:
        for i in range(1):
            sanakirja = lista[0]
            kosketus_x = peli["x"] + 40 > sanakirja["x"] and peli["x"] < sanakirja["x"] + 40
            kosketus_y = peli["y"] < sanakirja["y"] + 40 and peli["y"] + 40 > sanakirja["y"]
            tulo_vas = abs(peli["x"] + 40 - sanakirja["x"]) <= abs(peli["vx"])
            tulo_oik = abs(sanakirja["x"] + 40 - peli["x"]) <= abs(peli["vx"])
            tulo_yla = abs(sanakirja["y"] + 40 - peli["y"]) <= abs(peli["vy"])
            tulo_ala = abs(peli["y"] + 40 - sanakirja["y"]) <= abs(peli["vy"])
            tulo_vas_vaihtoehtoinen = abs(peli["x"] + 40 - sanakirja["x"]) <= abs(peli["vx"]) / 0.7
            tulo_oik_vaihtoehtoinen = abs(sanakirja["x"] + 40 - peli["x"]) <= abs(peli["vx"]) / 0.7
            if kosketus_x and kosketus_y:
                if tulo_vas and peli["vx"] > 0:
                    peli["x"] = sanakirja["x"] - 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)
                elif tulo_oik and peli["vx"] < 0:
                    peli["x"] = sanakirja["x"] + 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)
                elif tulo_ala and not peli["y"] <= 0:
                    peli["y"] = sanakirja["y"] - 40
                    peli["vy"] *= -1
                elif tulo_yla and peli["vy"] < 0:
                    peli["y"] = sanakirja["y"] + 40
                    peli["vy"] *= POMPPUKERROIN
                    peli["vx"] *= 0.7
            if kosketus_x and kosketus_y:
                if tulo_vas_vaihtoehtoinen and peli["vx"] > 0:
                    peli["x"] = sanakirja["x"] - 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)      
                elif tulo_oik_vaihtoehtoinen and peli["vx"] < 0:
                    peli["x"] = sanakirja["x"] + 40
                    peli["vx"] *= -0.7
                    vaihda_kuva(peli)   

def estetormays_paivitys(kulunut_aika):
    """
    Estetörmäys-funktio muodossa, jonka toistuva käsittelijä hyväksyy.
    """
    este_tormays(peli["esteet"])






#Piirtofunktiot

def piirra_kentta():
    """
    Tämä funktio hoitaa peli-ikkunan, sorsan, laatikoiden 
    sekä pelitietojen piirtämisen.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    haravasto.lisaa_piirrettava_ruutu("{}".format(peli["kuva"]), peli["x"], peli["y"])
    haravasto.lisaa_piirrettava_ruutu("ritsa", 50, 0)
    haravasto.lisaa_piirrettava_ruutu("x", 1155, 555)
    for sanakirja in peli["laatikot"]:
        haravasto.lisaa_piirrettava_ruutu("barrel", sanakirja["x"], sanakirja["y"])
    for sanakirja in peli["esteet"]:
        haravasto.lisaa_piirrettava_ruutu("box", sanakirja["x"], sanakirja["y"])
    haravasto.piirra_ruudut()
    if peli["tila"] == "virallinen":
        haravasto.piirra_tekstia("Taso: {}".format(peli["taso"]), 10, 560, koko=20)
        haravasto.piirra_tekstia("VIRALLISET TASOT", 450, 560, koko=20)
    if peli["tila"] == "satunnainen":
        haravasto.piirra_tekstia("Tulos: {}".format(peli["tulos"]), 10, 560, koko=20)
        haravasto.piirra_tekstia("SATUNNAINEN TILA", 450, 560, koko=20)
    haravasto.piirra_tekstia("Sorsia jäljellä: {}".format(peli["n_sorsat"]), 150, 560, koko=20)

def piirra_paavalikko():
    """
    Piirtää päävalikon.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    haravasto.lisaa_piirrettava_ruutu("box", 120, 0)
    haravasto.lisaa_piirrettava_ruutu("box", 160, 0)
    haravasto.lisaa_piirrettava_ruutu("box", 200, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 160, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 200, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 240, 0)
    haravasto.lisaa_piirrettava_ruutu("barrel", 160, 40)
    haravasto.lisaa_piirrettava_ruutu("barrel", IKKUNAN_LEVEYS - 200, 40)
    haravasto.lisaa_piirrettava_ruutu("{}".format(grafiikkasorsa["kuva"]), grafiikkasorsa["x"], grafiikkasorsa["y"])
    haravasto.piirra_ruudut()
    haravasto.piirra_tekstia("MIELENSÄPAHOITTANEET SORSAT", 70, 500, koko=45)    
    haravasto.piirra_tekstia("VIRALLISET TASOT", 370, 350)
    haravasto.piirra_tekstia("SATUNNAINEN TILA", 365, 270)
    haravasto.piirra_tekstia("__________________", 355, 340)
    haravasto.piirra_tekstia("__________________", 355, 260)

def piirra_voittovalikko():
    """
    Piirtää voittovalikon.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.piirra_tekstia("TASO LÄPÄISTY", 345, 500, koko=45)
    haravasto.piirra_tekstia("SEURAAVA TASO", 410, 310)
    haravasto.piirra_tekstia("PÄÄVALIKKO", 450, 230)
    haravasto.piirra_tekstia("________________", 400, 300)
    haravasto.piirra_tekstia("____________", 440, 220)   

def piirra_haviovalikko_viral():
    """
    Piirtää häviövalikon virallisessa pelimuodossa.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.piirra_tekstia("SORSAT LOPPUIVAT", 270, 500, koko=45)
    haravasto.piirra_tekstia("YRITÄ UUDESTAAN", 370, 310)
    haravasto.piirra_tekstia("PÄÄVALIKKO", 430, 230)
    haravasto.piirra_tekstia("_________________", 370, 300)
    haravasto.piirra_tekstia("____________", 420, 220)    

def piirra_haviovalikko_satun():
    """
    Piirtää häviövalikon satunnaisessa pelitilassa.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.piirra_tekstia("HÄVISIT PELIN", 345, 500, koko=45)
    haravasto.piirra_tekstia("TULOS: {}".format(peli["tulos"]), 470, 400)
    haravasto.piirra_tekstia("ALOITA ALUSTA", 400, 310)
    haravasto.piirra_tekstia("PÄÄVALIKKO", 430, 230)
    haravasto.piirra_tekstia("_______________", 385, 300)
    haravasto.piirra_tekstia("____________", 420, 220)

def piirra_peli_lapaisty():
    """
    Piirtää valikon, joka näkyy, kun peli on läpäisty.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    haravasto.lisaa_piirrettava_ruutu("sorsa", 100, IKKUNAN_KORKEUS - 90)
    haravasto.lisaa_piirrettava_ruutu("sorsa_reverse", IKKUNAN_LEVEYS - 140, IKKUNAN_KORKEUS - 90)
    haravasto.lisaa_piirrettava_ruutu("box", 120, 0)
    haravasto.lisaa_piirrettava_ruutu("box", 160, 0)
    haravasto.lisaa_piirrettava_ruutu("box", 200, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 160, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 200, 0)
    haravasto.lisaa_piirrettava_ruutu("box", IKKUNAN_LEVEYS - 240, 0)
    haravasto.lisaa_piirrettava_ruutu("pum", 160, 40)
    haravasto.lisaa_piirrettava_ruutu("pum", IKKUNAN_LEVEYS - 200, 40)
    haravasto.piirra_ruudut()
    haravasto.piirra_tekstia("LÄPÄISIT PELIN!", 320, 500, koko=45)
    haravasto.piirra_tekstia("PÄÄVALIKKO", 430, 230)
    haravasto.piirra_tekstia("____________", 420, 220)    




#Loput funktiot

def hiiri(hiiri_x, hiiri_y, nappi=haravasto.HIIRI_VASEN, muokkausnappi=None):
    """
    Määrittää, mitä tapahtuu hiiren painalluksesta missäkin pelin tilassa.
    """
    if peli["tila"] == "paavalikko":
        if hiiri_x > 355 and hiiri_y > 345 and hiiri_x < 780 and hiiri_y < 410:
            peli["tila"] = "virallinen"
            peli["taso"] = 1
            pelitila()
        elif hiiri_x > 355 and hiiri_y > 255 and hiiri_x < 780 and hiiri_y < 320:
            peli["tila"] = "satunnainen"
            peli["tulos"] = 0        
            pelitila()

    if peli["tila"] == "voittovalikko_satunnainen":    
        if hiiri_x > 400 and hiiri_y > 300 and hiiri_x < 785 and hiiri_y < 365:
            peli["tila"] = "satunnainen"
            peli["tulos"] += 1        
            pelitila()
        elif hiiri_x > 440 and hiiri_y > 220 and hiiri_x < 740 and hiiri_y < 285:
            peli["tila"] = "paavalikko"
            peli["tulos"] = 0
            paavalikko()

    if peli["tila"] == "haviovalikko_satunnainen":
        if hiiri_x > 385 and hiiri_y > 300 and hiiri_x < 785 and hiiri_y < 365:
            peli["tila"] = "satunnainen"
            peli["tulos"] = 0
            pelitila()
        elif hiiri_x > 420 and hiiri_y > 220 and hiiri_x < 720 and hiiri_y < 285:
            peli["tila"] = "paavalikko"
            peli["tulos"] = 0
            paavalikko()  

    if peli["tila"] == "voittovalikko_virallinen":   
        if hiiri_x > 400 and hiiri_y > 300 and hiiri_x < 785 and hiiri_y < 365:
            peli["tila"] = "virallinen"
            peli["taso"] += 1        
            pelitila()
        elif hiiri_x > 440 and hiiri_y > 220 and hiiri_x < 740 and hiiri_y < 285:
            peli["tila"] = "paavalikko"
            peli["taso"] = 0
            paavalikko()

    if peli["tila"] == "haviovalikko_virallinen":         
        if hiiri_x > 370 and hiiri_y > 300 and hiiri_x < 780 and hiiri_y < 365:
            peli["tila"] = "virallinen"        
            pelitila()            
        elif hiiri_x > 420 and hiiri_y > 220 and hiiri_x < 710 and hiiri_y < 285:
            peli["tila"] = "paavalikko"
            peli["taso"] = 0
            paavalikko() 

    if peli["paalla"]:
        if hiiri_x >= 1155 and hiiri_y >= 555 and hiiri_x <= 1195 and hiiri_y <= 595:
            peli["tila"] = "paavalikko"
            peli["taso"] = 0      
            peli["tulos"] = 0
            peli["laatikot"] = []
            peli["esteet"] = []
            alkutila()
            paavalikko()
    if peli["tila"] == "peli_lapaisty":         
        if hiiri_x > 420 and hiiri_y > 220 and hiiri_x < 710 and hiiri_y < 285:        
            peli["tila"] = "paavalikko"
            peli["taso"] = 0
            paavalikko() 

def toistuvat(kulunut_aika):
    """
    Kaikki toistuvat funktiot kasattuna yhteen.
    """
    if peli["lennossa"] and peli["paalla"]:
        lento(kulunut_aika)
    if peli["tila"] == "paavalikko":
        lento_grafiikkasorsa(kulunut_aika)
    if not peli["lennossa"] and peli["paalla"]:
        alue(kulunut_aika)
    paivita(kulunut_aika)
    tormays_paivitys(kulunut_aika)
    estetormays_paivitys(kulunut_aika)
    voittotarkistin(kulunut_aika)

def paavalikko():
    """
    Aukaisee pelin päävalikon.
    """
    peli["paalla"] = False
    haravasto.aseta_piirto_kasittelija(piirra_paavalikko)

def lataa_tiedosto():
    """
    Lataa kentän tiedot json-tiedostosta ja asettaa ne sanakirjan muuttujiin.
    """
    try:
        tiedosto = "sorsapelin_tasot\\sorsapeli_taso{}.json".format(peli["taso"])
    except FileNotFoundError:
        print("Tiedostokansiota ei löytynyt.")
    try:
        with open(tiedosto) as lahde:
            kenttatiedot = json.load(lahde)
    except json.JSONDecodeError:
        print("Tiedoston aukaisu ei onnistunut!")
    else:
        peli["laatikot"] = (kenttatiedot["laatikot"])
        peli["esteet"] = (kenttatiedot["esteet"])
        peli["n_sorsat"] = (kenttatiedot["n_sorsat"])

def pelitila():
    """
    Aukaisee pelitilan.
    """
    peli["paalla"] = True
    if peli["tila"] == "satunnainen":
        luku = ra.randint(1, 3)
        peli["n_sorsat"] = luku * 2
        luo_laatikot(luku)
        luo_esteet()
    elif peli["tila"] == "virallinen":
        lataa_tiedosto()
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
  
def voittotarkistin(kulunut_aika):
    """
    Tarkistaa, onko kaikki laatikot tuhottu.
    """
    if peli["paalla"] and len(peli["laatikot"]) == 0 and not peli["lennossa"]:
        voittovalikko()
    elif peli["n_sorsat"] == 0 and peli["paalla"]:
        if len(peli["laatikot"]) == 0:
            voittovalikko()
        else:
            haviovalikko()

def voittovalikko():
    """
    Aukaisee valikon, joka näkyy, kun taso on voitettu.
    """
    peli["paalla"] = False
    peli["laatikot"] = []
    peli["esteet"] = []
    if peli["tila"] == "satunnainen":
        peli["tila"] = "voittovalikko_satunnainen"
        haravasto.aseta_piirto_kasittelija(piirra_voittovalikko)
    elif peli["tila"] == "virallinen":
        if peli["taso"] == 5:
            peli["tila"] = "peli_lapaisty"
            haravasto.aseta_piirto_kasittelija(piirra_peli_lapaisty)
        else:
            peli["tila"] = "voittovalikko_virallinen"       
            haravasto.aseta_piirto_kasittelija(piirra_voittovalikko) 

def haviovalikko():
    """
    Aukaisee valikon, joka näkyy, kun taso on hävitty.
    """
    peli["paalla"] = False
    peli["laatikot"] = []
    peli["esteet"] = []
    if peli["tila"] == "satunnainen":
        peli["tila"] = "haviovalikko_satunnainen"
        haravasto.aseta_piirto_kasittelija(piirra_haviovalikko_satun)
    elif peli["tila"] == "virallinen":
        peli["tila"] = "haviovalikko_virallinen"
        haravasto.aseta_piirto_kasittelija(piirra_haviovalikko_viral)

#Pääfunktio

if __name__ == "__main__":
    
    haravasto.lataa_kuvat("spritet")
    haravasto.lataa_sorsa("spritet")
    haravasto.luo_ikkuna(leveys=IKKUNAN_LEVEYS, korkeus=IKKUNAN_KORKEUS)
    haravasto.aseta_toistuva_kasittelija(toistuvat)
    haravasto.aseta_raahaus_kasittelija(kasittele_raahaus)
    haravasto.aseta_vapautus_kasittelija(ammu) 
    haravasto.aseta_hiiri_kasittelija(hiiri)
    paavalikko()
    haravasto.aloita()   
