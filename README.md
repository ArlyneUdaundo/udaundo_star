# MediBook Clinic Appointments — IT 424 Test III & Test IV

A server-rendered Django clinic appointment application using **Django 5.x + SQLite + HTMX 2.x + Alpine.js 3.x**.

## What is included

- Django project: `medibook/`
- Clinic application: `clinic/`
- Models: `Specialty`, `Doctor`, `Appointment`
- `DoctorForm` and `AppointmentForm`
- Server-side validation required by the exam
- Doctor directory with search, specialty filter, sorting, pagination, availability badges, and booking links
- Doctor detail tabs powered by Alpine.js
- Three-step booking wizard powered by Alpine.js
- HTMX date-based slot refresh and booking validation swaps
- Staff doctor management and appointment management
- Alpine theme and toast stores
- Responsive custom CSS
- Doctor image files under `media/doctors/` and fixture references through `MEDIA_URL`
- `requirements.txt` and `fixture.json`

## Install and run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixture.json
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Test III architecture

Django owns all server data, validation, persistence, and business rules. HTMX requests server-rendered HTML fragments instead of rebuilding server data in JavaScript.

HTMX interactions implemented:

1. Debounced directory search.
2. Specialty filter.
3. Fee/name sorting.
4. Pagination while preserving current filters.
5. Date-based available-slot refresh.
6. Booking POST validation swap and `HX-Redirect` on success.
7. Appointment confirm/cancel row swaps.
8. Doctor accepting toggle and delete row actions.
9. Loading indicator using `hx-indicator`.

## Test IV architecture

Alpine.js handles only small client-side UI state:

- `appShell` — initializes the shared theme store.
- `mobileNav` — mobile menu open/closed state and Escape handling.
- `directoryControls` — search clear and selected specialty UI state.
- `specialtyChips` — selected chip state and `$dispatch` communication.
- `quickCard` — doctor-card quick view.
- `tabs` — doctor detail tabs and keyboard arrow navigation.
- `bookingWizard` — three steps, computed getters, reason counter, `$watch`, and step restoration after an HTMX error swap.
- `statusTabs` — client-side appointment status filtering and live counts.

Shared stores:

- `theme` — persisted light/dark preference.
- `toasts` — shared notification stack.

## Alpine + HTMX integration

- `htmx:configRequest` adds the Django CSRF token to HTMX requests.
- `htmx:beforeRequest` / `htmx:afterRequest` drive loading feedback.
- `:hx-vals` sends the selected booking date into the server slot request.
- `HX-Trigger` from a successful booking dispatches a toast event.
- Alpine state remains on the booking wizard parent while HTMX swaps only the form.

## Media

The fixture loads three sample doctor images into `media/doctors/`. Django serves them during development through `MEDIA_URL` and `MEDIA_ROOT`.

## Important submission note

The project source files in this repository are the source of truth. The accompanying Word evidence document should be submitted together with this repository link. Replace the GitHub placeholder in the Word document with the URL of your actual public repository before submission.
