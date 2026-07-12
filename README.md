# Anotator

Anotator is a Django project for organizing annotation batches of language-model outputs. It helps distribute answers to human annotators without exposing bias-related metadata during the review process.

## License

This project is licensed under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**. The full legal text is in [LICENSE.md](LICENSE.md); the summary below is for convenience only and is not a substitute for the license itself.

Under this license you are free to **share** (copy and redistribute the material) and **adapt** (remix, transform, and build upon the material), as long as you follow these terms:

- **Attribution** — You must give appropriate credit to the original author(s), provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may **not** use the material for commercial purposes, i.e., not primarily intended for or directed towards commercial advantage or monetary compensation.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the **same license** as the original (CC BY-NC-SA 4.0 or a compatible one).
- **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

There are no warranties given: the material is provided "as-is", and the licensor disclaims liability for any damages arising from its use. This does not affect any rights you may have under fair use, fair dealing, or applicable exceptions and limitations to copyright.

## Repository Structure

The Django project lives at the repository root for a cleaner submission layout.

```
.
├── manage.py                              # Django entry point (runserver, migrate, custom commands, etc.)
├── requirements.txt                        # Python dependencies
├── LICENSE.md                              # Full CC BY-NC-SA 4.0 license text
├── annotation/                             # Django project configuration package
│   ├── settings.py                         #   Global settings (apps, database, middleware, etc.)
│   ├── urls.py                             #   Root URL routing
│   ├── asgi.py / wsgi.py                   #   ASGI/WSGI entry points for deployment
│   └── __init__.py
└── app_projeto/                            # Main Django application ("app_projeto")
    ├── models/                             # Domain models: projects, annotators, questions, answers, batches
    │   ├── question_answer.py              #   Question and Answer models
    │   └── annotation_batches.py           #   AnnotationBatch and related models
    ├── views/                              # Request handlers
    │   ├── views.py                        #   Main application views (home, batches, answers)
    │   └── site_access.py                  #   Login / site access control views
    ├── templates/                          # HTML templates rendered by the views
    │   ├── base.html                       #   Shared layout used by other templates
    │   ├── home.html                       #   Landing page
    │   ├── batch-detail.html               #   Batch detail / annotation screen
    │   ├── avaliation.html                 #   Answer evaluation form
    │   ├── divergences.html                #   View for annotator disagreements
    │   └── site_access_login.html          #   Login page
    ├── static/                             # Static assets
    │   └── style.css                       #   Site styling
    ├── management/
    │   ├── commands/                       # Custom `python manage.py <command>` scripts
    │   │   ├── generate_sample_questions.py       #   Generates sample question+answer CSV
    │   │   ├── generate_sample_questions_only.py  #   Generates sample question-only CSV
    │   │   ├── import_answers.py                  #   Imports a CSV of answers into the database
    │   │   └── create_annotation_batch.py         #   Creates annotation batches for annotators
    │   └── data/                           # Default output folder for generated/sample CSV files
    ├── migrations/                         # Django database migration history
    ├── admin.py                            # Django admin site registration
    ├── forms.py                            # Django forms used by the views
    ├── managers.py                         # Custom model managers/querysets
    ├── middleware.py                       # Custom request/response middleware
    ├── services.py                         # Business logic shared across views/commands
    ├── context_processors.py               # Template context processors
    ├── urls.py                             # App-level URL routing
    └── tests.py                            # Automated tests
```

- [.gitignore](.gitignore) defines ignored files and folders.

## Workflow Overview

Use the project in this order:

1. Generate a question-answer CSV with [generate_sample_questions.py](app_projeto/management/commands/generate_sample_questions.py).
2. Import that CSV with [import_answers.py](app_projeto/management/commands/import_answers.py).
3. Create annotators and a batch with [create_annotation_batch.py](app_projeto/management/commands/create_annotation_batch.py).
4. Run the local server with `python manage.py runserver`.
5. Open the annotator interface in the browser and review the assigned answers.

If you only want prompt examples, use [generate_sample_questions_only.py](app_projeto/management/commands/generate_sample_questions_only.py).

## Setup

Create the virtual environment:

```bash
python -m venv .venv
```

Install the dependencies first:

```bash
pip install -r requirements.txt
```

Then run the database setup steps required by your environment:

```bash
python manage.py migrate
python manage.py createsuperuser
```

If you are using a local development server, start it with:

```bash
python manage.py runserver
```

## Available Commands

### Generate Sample Data With Answers

The command [generate_sample_questions.py](app_projeto/management/commands/generate_sample_questions.py) creates question-answer CSV files on demand.

Example:

```bash
python manage.py generate_sample_questions --count 30
```

By default, it writes the generated file into app_projeto/management/data/.

Useful options:

- `--count`: number of question-answer rows to generate.
- `--output`: output path for the main CSV file.
- `--seed`: optional random seed for reproducible output.

### Generate Questions Only

The command [generate_sample_questions_only.py](app_projeto/management/commands/generate_sample_questions_only.py) creates CSV files with questions only.

Example:

```bash
python manage.py generate_sample_questions_only --count 30
```

By default, it writes the generated file into app_projeto/management/data/.

Useful options:

- `--count`: number of questions to generate.
- `--output`: output path for the questions-only CSV file.
- `--seed`: optional random seed for reproducible output.

### Import Answers

The command [import_answers.py](app_projeto/management/commands/import_answers.py) imports CSV content into the database.

Example:

```bash
python manage.py import_answers app_projeto/management/data/sample_questions_answers.csv --project_name "My Project"
```

If you are using the default output from the generator command, the file name will be `sample_questions_answers.csv`.

The CSV should preferably include these columns:

- `Prompt`
- `Model`
- `Model Answer`

Legacy CSV files that still use `Modelo` and `Resposta do LLM` are also supported by the import command.

### Create Annotation Batches

The command [create_annotation_batch.py](app_projeto/management/commands/create_annotation_batch.py) creates annotation batches for registered annotators.

Example:

```bash
python manage.py create_annotation_batch "My Project" --annotators annotator1@example.com annotator2@example.com --num-answers 50 --limit-per-question 5
```

## Notes

- The [app_projeto/management/data/](app_projeto/management/data/) folder is the recommended place for generated test CSV files.
- No sample CSV files are committed to the repository, they are created only when you run the Python command.
- For a full local demo, run the sample generator, import the CSV, create the batch, start the server, and open the annotator page.
- If you plan to extend the evaluation protocol later, you can split inputs by project, model, or analysis focus.