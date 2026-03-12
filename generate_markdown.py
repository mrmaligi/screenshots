import json

def generate_markdown():
    with open('visa_schema.sql', 'r') as f:
        sql_schema = f.read()

    with open('visa_catalogue.json', 'r') as f:
        visa_catalogue = json.load(f)

    md = "# Australian Visa Tracking Application Data Architecture\n\n"

    md += "## Phase 1: The Relational Database Architecture\n\n"
    md += "Here is the absolute full SQL database schema for the application:\n\n"
    md += "```sql\n"
    md += sql_schema
    md += "```\n\n"

    md += "## Phase 2: The Complete Visa Catalogue Data\n\n"
    md += "Here is the exhaustive list of current Australian Visa Subclasses:\n\n"
    md += "```json\n"
    md += json.dumps(visa_catalogue, indent=4)
    md += "\n```\n\n"

    md += "## Phase 3 & 4 Acknowledgement\n\n"
    md += "I am ready for Phase 3 (The ANZSCO Master List) and Phase 4 (Application Lifecycles).\n\n"

    md += "---\n\n"
    md += "Are you ready for 'Phase 3: Batch 1'?\n"

    with open('visa_architecture.md', 'w') as f:
        f.write(md)

generate_markdown()
