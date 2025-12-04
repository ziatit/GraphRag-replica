FROM python:3.11-slim

# 1. Instalacja zależności systemowych
# build-essential i cmake są potrzebne do kompilacji niektórych bibliotek Pythonowych (np. leidenalg, c/c++ extensions)
# git przydaje się, jeśli musimy instalować pakiety bezpośrednio z repozytoriów
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Ustawienie katalogu roboczego wewnątrz kontenera
WORKDIR /app

# 3. Kopiowanie pliku requirements.txt
# Robimy to PRZED skopiowaniem reszty kodu.
# Dzięki temu Docker może wykorzystać cache warstwy ("layer caching").
# Jeśli zmienisz kod aplikacji, ale nie requirements.txt, Docker nie będzie musiał od nowa instalować pakietów.
COPY requirements.txt .

# 4. Instalacja zależności Pythonowych
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kopiowanie reszty kodu aplikacji
COPY . .

# 6. Informacja o porcie (dokumentacyjna)
EXPOSE 8000

# 7. Komenda startowa
# Uruchamia serwer uvicorn, nasłuchujący na wszystkich interfejsach (0.0.0.0) na porcie 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
