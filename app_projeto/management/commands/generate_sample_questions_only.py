import csv
import random
from pathlib import Path

from django.core.management.base import BaseCommand


QUESTION_TOPICS = [
    "public health",
    "basic education",
    "urban safety",
    "urban mobility",
    "climate change",
    "artificial intelligence",
    "labor market",
    "digital inclusion",
    "local economy",
    "housing access",
    "school meals",
    "entrepreneurship",
    "data protection",
    "diversity policies",
    "public transportation",
    "mental health",
    "science and technology",
    "public services",
    "sustainable consumption",
    "citizenship and democracy",
]

QUESTION_TEMPLATES = [
    "What strategies could improve {topic} in low-income areas?",
    "How can the main challenges of {topic} be assessed in a mid-sized city?",
    "What impacts could {topic} generate for families with limited income?",
    "Which measures could make {topic} more accessible to the population?",
    "How can cost and efficiency be balanced when implementing {topic} initiatives?",
    "What are the risks and benefits of investing in {topic} in the coming years?",
    "How does {topic} affect young people, adults, and older adults differently?",
    "Which indicators would help measure the success of a {topic} policy?",
    "How could a city government prioritize actions related to {topic}?",
    "Which social factors can influence the outcomes of {topic}?",
]


class Command(BaseCommand):
    help = "Generates random sample questions in CSV format without answers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of questions to generate (default: 20).",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Output CSV path. If omitted, saves to app_projeto/management/data/sample_questions_only.csv.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional seed to reproduce the same question set.",
        )

    def handle(self, *args, **options):
        count = max(1, options["count"])
        output_path = Path(options["output"]) if options["output"] else self._default_output_path()
        rng = random.Random(options["seed"])

        output_path.parent.mkdir(parents=True, exist_ok=True)

        rows = self._build_rows(count, rng)

        with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Prompt"])
            writer.writeheader()
            writer.writerows(rows)

        self.stdout.write(
            self.style.SUCCESS(
                f"File generated successfully at {output_path} ({len(rows)} questions)."
            )
        )

    def _default_output_path(self):
        return Path(__file__).resolve().parent.parent / "data" / "sample_questions_only.csv"

    def _build_rows(self, count, rng):
        used_prompts = set()
        rows = []

        while len(rows) < count:
            topic = rng.choice(QUESTION_TOPICS)
            template = rng.choice(QUESTION_TEMPLATES)
            prompt = template.format(topic=topic)

            if prompt in used_prompts:
                continue

            used_prompts.add(prompt)
            rows.append({"Prompt": prompt})

        return rows