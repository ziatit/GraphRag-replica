# 🐳 Przewodnik po Dockerfile

Ten dokument wyjaśnia, jak zbudowany jest `Dockerfile` w tym projekcie, dlaczego podjęto takie decyzje oraz jak go używać i utrzymywać.

## 1. Analiza Dockerfile (Co i Dlaczego?)

```dockerfile
FROM python:3.11-slim
```
*   **Co:** Używamy oficjalnego obrazu Pythona w wersji 3.11 w wariancie `slim`.
*   **Dlaczego:** Wersja `slim` jest znacznie lżejsza (mniejszy rozmiar obrazu) niż pełna wersja, ale zawiera wszystko, co potrzebne do uruchomienia Pythona. Python 3.11 jest szybki i nowoczesny.

```dockerfile
RUN apt-get update && apt-get install -y build-essential cmake git ...
```
*   **Co:** Instalujemy systemowe narzędzia kompilacji (`gcc`, `g++`, `make` itp.) oraz `cmake`.
*   **Dlaczego:** Niektóre biblioteki Pythonowe do obliczeń grafowych (jak `leidenalg` czy `igraph`, używane przez `graspologic`) mają komponenty napisane w C/C++. Muszą one zostać skompilowane podczas instalacji (`pip install`). Bez tych narzędzi instalacja by się nie powiodła.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
*   **Co:** Najpierw kopiujemy TYLKO plik z zależnościami i je instalujemy.
*   **Dlaczego:** To kluczowa optymalizacja (Docker Layer Caching). Docker buduje obraz warstwami. Jeśli zmienisz kod w `app/main.py`, ale nie zmienisz `requirements.txt`, Docker **użyje gotowej warstwy z zainstalowanymi pakietami** i nie będzie ich pobierał od nowa. Przyspiesza to budowanie obrazu z kilku minut do kilku sekund.

```dockerfile
COPY . .
```
*   **Co:** Dopiero teraz kopiujemy resztę kodu.
*   **Dlaczego:** Ponieważ kod zmienia się najczęściej, ta operacja powinna być jak najpóźniej w procesie budowania.

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
*   **Co:** Domyślna komenda startowa.
*   **Dlaczego:** Uruchamia serwer FastAPI. Opcja `--reload` jest przydatna w developmencie (restartuje serwer po zmianie kodu), ale w produkcji warto ją usunąć.

---

## 2. Jak używać? (How-to)

### Budowanie obrazu
Aby stworzyć obraz (czyli "paczkę" z Twoją aplikacją), wykonaj w terminalu:

```bash
docker build -t graphrag-app .
```
*   `-t graphrag-app`: Nadaje nazwę (tag) twojemu obrazowi.
*   `.`: Wskazuje, że Dockerfile jest w obecnym katalogu.

### Uruchamianie kontenera
Aby uruchomić zbudowaną aplikację:

```bash
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data graphrag-app
```
*   `-p 8000:8000`: Przekierowuje port 8000 z kontenera na port 8000 Twojego komputera.
*   `--env-file .env`: Wczytuje zmienne środowiskowe (np. klucz OpenAI) z pliku `.env`.
*   `-v $(pwd)/data:/app/data`: Mapuje katalog `data` z Twojego komputera do kontenera. Dzięki temu pliki indeksu stworzone przez aplikację **nie znikną** po wyłączeniu kontenera.

---

## 3. Utrzymanie (Maintenance)

1.  **Dodawanie nowych bibliotek:**
    *   Dopisz bibliotekę do `requirements.txt`.
    *   Uruchom `docker build ...` ponownie. Docker wykryje zmianę w pliku i doinstaluje pakiety.

2.  **Aktualizacja wersji Pythona:**
    *   Zmień pierwszą linię `FROM python:3.11-slim` na nowszą wersję (np. `3.12-slim`), gdy będzie stabilna i wspierana przez Twoje biblioteki.

3.  **Czyszczenie:**
    *   Z czasem możesz mieć dużo starych obrazów. Użyj `docker system prune`, aby zwolnić miejsce na dysku.

4.  **Produkcja:**
    *   W wersji produkcyjnej usuń flagę `--reload` z komendy `CMD` w Dockerfile, aby zwiększyć wydajność i stabilność.
