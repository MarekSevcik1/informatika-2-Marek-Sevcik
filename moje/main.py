from os.path import join, dirname, realpath
from functools import wraps
import logging

logging.basicConfig(  
    level=logging.INFO,  # Loguj vše od INFO výše (DEBUG se ignoruje)  
    level = logging.ERROR,
    filename= "log.txt",  # Ulož do souboru  
    format='%(asctime)s - %(levelname)s - %(message)s' # Přidej čas  
)

logging.info("Start programu")  
logging.warning("Pozor!")

class Polozka:
    def __init__(self, nazev, cena, mnozstvi=0):
        self.nazev = nazev
        self.cena = cena
        self.mnozstvi = mnozstvi

    def __str__(self) -> str:
        return f"{self.nazev}: {self.cena:.2f} Kč ({self.mnozstvi}ks)"

    def __repr__(self)-> str:
        return f"Polozka(({self.nazev!r}, {self.cena!r},{self.mnozstvi!r} )"

    def __eq__(self, other)->bool:
        if not isinstance(other, Polozka):
            return NotImplemented
        return self.nazev == other.nazev and self.cena == other.cena

    def __add__(self, other):
        if not isinstance(other, Polozka):
            return NotImplemented
        if self == other:
            return Polozka(self.nazev, self.cena, self.mnozstvi + other.mnozstvi)
        raise ValueError("Nelze scitat ruzne polozky")

LOG_PATH = join(dirname(realpath(__file__)), "log.txt")

def log_operace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        realne_args = args[1:]
        if kwargs:
            args_repr = f"{realne_args!r}, {kwargs!r}"
        else:
            args_repr = f"{realne_args!r}"

        log_zprava = f"[LOG] Volani '{func.__name__}' s argumenty: {args_repr}\n"
        try:
            with open(LOG_PATH, mode = "a", encoding = "utf-8") as f:
                f.write(log_zprava)
        except IOError:
                pass
        return func(*args, **kwargs)
    return wrapper


class Sklad:
    def __init__(self):
        self.polozky={}

    def __enter__(self):
        logging.info("Otviram sklad...")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.uloz_do_csv("autosave_sklad.csv")
        logging.info("Sklad uložen do autosave_sklad.csv")
        return False


    def __len__(self):
        return sum(polozka.mnozstvi for polozka in self.polozky.values())

    def __getitem__(self, index):
        return self.polozky[index]

    @log_operace
    def pridej_polozku(self, polozka):
        if polozka.nazev in self.polozky:
            self.polozky[polozka.nazev] = self.polozky[polozka.nazev] + polozka
        else:
            self.polozky[polozka.nazev] = polozka

    @log_operace
    def odeber_polozku(self, polozka):
        if polozka.nazev in self.polozky:
            self.polozky[polozka.nazev] = self.polozky[polozka.nazev] - polozka
            if polozka.mnozstvi == 0:
                del self.polozky[polozka.nazev]



    def uloz_do_csv(self, LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("nazev,cena,mnozstvi\n")
            for polozka in self.polozky.values():
                f.write(f"{polozka.nazev},{polozka.cena},{polozka.mnozstvi}\n")

    def nacti_z_csv(self, LOG_PATH):
        sklad = Sklad()
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            next(f)
            for line in f:
                nazev, cena, mnozstvi = line.strip().split(",")
                polozka = Polozka(nazev, float(cena), int(mnozstvi))
                sklad.pridej_polozku(polozka)
        return sklad




def main():
    # vytvoření položek
    jablka = Polozka("Jablko", 10, 50)
    dalsi_jablka = Polozka("Jablko", 10, 20)
    hrusky = Polozka("Hruška", 15, 30)

    # test sčítání položek
    print(jablka + dalsi_jablka)

    # práce se skladem
    sklad = Sklad()
    sklad.pridej_polozku(jablka)
    sklad.pridej_polozku(dalsi_jablka)
    sklad.pridej_polozku(hrusky)

    print(sklad["Hruška"])
    print(f"Celkem kusů na skladu: {len(sklad)}")

    # uložení do CSV
    sklad.uloz_do_csv("sklad_data.csv")
    logging.info("Sklad uložen.")

    # načtení ze CSV
    novy_sklad = Sklad()
    novy_sklad = novy_sklad.nacti_z_csv("sklad_data.csv")

    logging.info(f"Nacteno {len(novy_sklad)} kusu zbozi z noveho skladu.")


if __name__ == "__main__":
    main()