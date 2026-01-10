# Kiedy/gdzie spotkanie?

Aplikacja do planowania spotkań w stylu Doodle, gdzie uczestnicy mogą oznaczać swoją dostępność dla różnych terminów i lokalizacji.

## Technologie

- **Backend**: Django 5.x z PostgreSQL
- **Frontend**: HTMX + Tailwind CSS (via CDN)
- **Serwer**: Gunicorn (produkcja) / Django dev server (development)

## Struktura projektu

```
├── kiedy_gdzie/          # Główna konfiguracja Django
│   ├── settings.py       # Ustawienia aplikacji
│   ├── urls.py           # Główne URL-e
│   └── wsgi.py           # WSGI dla produkcji
├── meetings/             # Aplikacja spotkań
│   ├── models.py         # Modele: Meeting, TimeSlot, Location, Participant, Vote
│   ├── views.py          # Widoki aplikacji
│   └── urls.py           # URL-e aplikacji
├── templates/            # Szablony HTML
│   ├── base.html         # Bazowy szablon
│   └── meetings/         # Szablony spotkań
└── static/               # Pliki statyczne
```

## Modele danych

- **Meeting**: Spotkanie z nazwą i opisem
- **TimeSlot**: Proponowany termin (data + godzina)
- **Location**: Proponowana lokalizacja
- **Participant**: Uczestnik głosowania
- **Vote**: Głos (tak/nie/może) na termin lub lokalizację

## Funkcjonalności

1. Strona główna z informacjami o aplikacji
2. Tworzenie spotkań z dynamicznym dodawaniem terminów/lokalizacji (HTMX)
3. Generowanie unikalnego linku do udostępnienia
4. Głosowanie: Tak/Nie/Może dla każdej opcji
5. Strona wyników z najlepszą opcją

## Uruchomienie

```bash
python manage.py runserver 0.0.0.0:5000
```

## Zmienne środowiskowe

- `DATABASE_URL` - URL do bazy PostgreSQL
- `SESSION_SECRET` - Klucz sesji Django
