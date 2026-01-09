ENTITIES_EXTRACTION_PROMPT_JSON = """
-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types:
- PERSON: Key characters, victims, witnesses, or suspects (e.g., Sherlock Holmes, John Watson, Enoch Drebber).
- LOCATION: Physical places, addresses, streets, cities, or rooms relevant to the plot (e.g., 221B Baker Street, Cleveland, The Brixton Road).
- ORGANIZATION: Groups, police departments, or societies (e.g., Scotland Yard, The Mormons, The Baker Street Irregulars).
- EVIDENCE: Physical objects, traces, or clues found at crime scenes or used to deduce facts (e.g., The gold ring, the pills, the word "RACHE", muddy footprints).
- CRIME: Specific illegal acts or mysteries being investigated (e.g., The Murder of Drebber, The Stangerson Case).
- TIME: Specific dates, times of day, or durations relevant to alibis or timelines (e.g., March 4th, Midnight, Tuesday morning).

- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity output as a JSON entry with the following format:

{{"name": <entity name>, "type": <type>, "description": <entity description>}}

2. **Relationship Extraction:**
   Identify interactions or logical connections between the entities found in Step 1.
   - source: Name of the source entity (must match a name from Step 1 exactly).
   - target: Name of the target entity (must match a name from Step 1 exactly).
   - relationship_type: A short, upper-case predicate (e.g., INVESTIGATES, LIVES_WITH, FOUND_AT, VICTIM_OF).
   - description: A brief sentence explaining the context of the relationship.
   - strength: Integer (1-10) indicating importance to the plot.
Format each relationship as a JSON entry with the following format:

{{"source": <source_entity>, "target": <target_entity>, "relationship": <relationship_description>, "relationship_strength": <relationship_strength>}}

IMPORTANT:
- Output MUST be valid JSON.
- Do NOT include comments (like // or #) in the JSON output.
- Do NOT use trailing commas.
- Ensure all keys and string values are enclosed in double quotes.
- Do NOT repeat the input text in your response. Only output the JSON.

-Examples-
######################
Input Text:
"Stamford introduced us. 'Dr. Watson, this is Mr. Sherlock Holmes,' he said. The detective looked up from his test tubes. 'How are you?' he asked, shaking my hand with a strength I had not expected."

JSON Output:
{
  "entities": [
    {"name": "Stamford", "type": "PERSON", "description": "A mutual acquaintance who introduces Watson to Holmes."},
    {"name": "John Watson", "type": "PERSON", "description": "The narrator and doctor being introduced."},
    {"name": "Sherlock Holmes", "type": "PERSON", "description": "The detective conducting chemical experiments."},
    {"name": "Test Tubes", "type": "OBJECT", "description": "Scientific equipment Holmes is using."}
  ],
  "relationships": [
    {"source": "Stamford", "target": "John Watson", "relationship_type": "INTRODUCES", "description": "Stamford introduces Watson to Holmes.", "strength": 5},
    {"source": "Stamford", "target": "Sherlock Holmes", "relationship_type": "INTRODUCES", "description": "Stamford introduces Holmes to Watson.", "strength": 5},
    {"source": "Sherlock Holmes", "target": "John Watson", "relationship_type": "MEETS", "description": "Holmes shakes Watson's hand.", "strength": 8},
    {"source": "Sherlock Holmes", "target": "Test Tubes", "relationship_type": "USES", "description": "Holmes is working with test tubes when introduced.", "strength": 3}
  ]
}

######################

Input Text:
"We arrived at 3 Lauriston Gardens. The body of Enoch Drebber lay upon the floor. There was no wound on his person, but there was a grim look of terror on his face. Near the body, a woman's wedding ring was rolling on the floorboards."

JSON Output:
{
  "entities": [
    {"name": "3 Lauriston Gardens", "type": "LOCATION", "description": "The address where the crime scene is located."},
    {"name": "Enoch Drebber", "type": "PERSON", "description": "The victim found dead on the floor."},
    {"name": "Wedding Ring", "type": "EVIDENCE", "description": "A woman's ring found near the body."}
  ],
  "relationships": [
    {"source": "Enoch Drebber", "target": "3 Lauriston Gardens", "relationship_type": "FOUND_AT", "description": "The body of the victim was discovered at this location.", "strength": 10},
    {"source": "Wedding Ring", "target": "Enoch Drebber", "relationship_type": "FOUND_NEAR", "description": "The ring was discovered on the floor near the victim.", "strength": 9},
    {"source": "Wedding Ring", "target": "3 Lauriston Gardens", "relationship_type": "LOCATED_AT", "description": "The ring was found at the crime scene.", "strength": 6}
  ]
}
"""