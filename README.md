# Anotator

Anotator is a Django project for organizing annotation batches of language-model outputs. It helps distribute answers to human annotators without exposing bias-related metadata during the review process.

## License

This project is **non-commercial**. It cannot be used for commercial purposes. See [LICENSE.md](LICENSE.md) for the full license terms.

## Repository Structure

The Django project now lives at the repository root for a cleaner submission layout.

- [manage.py](manage.py) is the main Django entry point.
- [annotation/](annotation/) contains the project settings, URL configuration, ASGI entry point, and WSGI entry point.
- [app_projeto/](app_projeto/) contains the application code.
- [app_projeto/models/](app_projeto/models/) defines the core domain models, including projects, annotators, questions, answers, batches, and methods.
- [app_projeto/views/](app_projeto/views/) contains the application views.
- [app_projeto/templates/](app_projeto/templates/) contains the HTML templates.
- [app_projeto/static/](app_projeto/static/) contains static assets such as CSS.
- [app_projeto/management/commands/](app_projeto/management/commands/) contains the custom Django management commands.
- [app_projeto/management/data/](app_projeto/management/data/) is the default output folder for generated CSV files.
- [.gitignore](.gitignore) defines ignored files and folders.
- [requirements.txt](requirements.txt) lists the Python dependencies.

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