from services.ai.json_utils import parse_json_content


def test_parse_json_with_trailing_text():
    raw = '{"ok": true}\n\nHere is some extra commentary.'
    assert parse_json_content(raw) == {"ok": True}


def test_parse_json_with_trailing_comma():
    raw = '{"personas": [{"name": "A", "role": "Owner",},],}'
    data = parse_json_content(raw)
    assert data["personas"][0]["name"] == "A"


def test_parse_json_truncated_array():
    raw = '{"keywords": [{"keyword": "erp software", "search_volume": 1000'
    data = parse_json_content(raw)
    assert data["keywords"][0]["keyword"] == "erp software"


def test_persona_schema_accepts_gemini_shape():
    from services.ai.schemas import PersonaSchema

    persona = PersonaSchema.model_validate(
        {
            "id": "persona_01",
            "role": "Factory Owner",
            "demographics": {"age_range": "45-60", "industry": "Manufacturing"},
            "pain_points": ["Legacy systems"],
            "goals": ["Reduce downtime"],
        }
    )
    assert persona.name == "persona_01"
    assert "45-60" in persona.demographics


def test_audience_schema_accepts_gemini_shape():
    from services.ai.schemas import AudienceResearchSchema

    research = AudienceResearchSchema.model_validate(
        {
            "personas": [
                {
                    "id": "persona_01",
                    "role": "Factory Owner",
                    "demographics": {"age_range": "45-60"},
                    "pain_points": ["Legacy ERP"],
                    "goals": ["Cut waste"],
                }
            ],
            "audience_summary": {"market_opportunity": "Growing demand in Central Asia"},
        }
    )
    assert research.personas[0].name == "persona_01"
    assert "market_opportunity" in research.audience_summary


def test_keyword_schema_normalizes_db_enums():
    from services.ai.schemas import KeywordSchema

    keyword = KeywordSchema.model_validate(
        {
            "keyword": "furniture manufacturing erp",
            "search_volume": 480,
            "difficulty": 32,
            "intent": "Commercial",
            "priority": "High",
        }
    )
    assert keyword.intent == "commercial"
    assert keyword.priority == "high"
