"""Built-in domain catalog for text extraction schema discovery."""

from dataclasses import dataclass


@dataclass
class DomainInfo:
    """A curated knowledge domain with typical predicates."""
    name: str
    description: str
    typical_predicates: list[str]


DOMAIN_CATALOG: list[DomainInfo] = [
    DomainInfo("family", "Kinship and genealogy", ["батько/2", "мати/2", "дитина/2", "предок/2", "подружжя/2"]),
    DomainInfo("geography", "Cities, regions, spatial relations", ["місто/1", "країна/1", "знаходиться_в/2", "сусідній/2", "відстань/3"]),
    DomainInfo("biology", "Taxonomy, species, ecology", ["є/2", "має/2", "вид/1", "клас/1", "середовище/2"]),
    DomainInfo("chemistry", "Elements, compounds, reactions", ["елемент/2", "сполука/2", "реагує/3", "розчинний/2"]),
    DomainInfo("history", "Events, dates, persons", ["подія/3", "дата/2", "учасник/2", "причина/2", "наслідок/2"]),
    DomainInfo("military", "Battles, armies, strategy", ["битва/3", "армія/2", "командувач/2", "результат/2"]),
    DomainInfo("economics", "Markets, trade, finance", ["ринок/1", "ціна/3", "торгівля/3", "валюта/2"]),
    DomainInfo("medicine", "Diseases, symptoms, treatments", ["хвороба/1", "симптом/2", "лікування/2", "ліки/2"]),
    DomainInfo("literature", "Authors, works, genres", ["автор/2", "твір/2", "жанр/2", "рік/2", "персонаж/2"]),
    DomainInfo("mythology", "Gods, myths, rituals", ["бог/1", "домен/2", "міф/2", "ритуал/2"]),
    DomainInfo("programming", "Languages, paradigms, concepts", ["мова/1", "парадигма/2", "підтримує/2", "автор_мови/2"]),
    DomainInfo("physics", "Laws, quantities, experiments", ["закон/2", "величина/3", "одиниця/2", "формула/2"]),
    DomainInfo("mathematics", "Theorems, proofs, structures", ["теорема/2", "аксіома/2", "доведення/2", "структура/2"]),
    DomainInfo("linguistics", "Languages, grammar, phonetics", ["мова_природна/1", "граматика/2", "фонема/2", "морфема/2"]),
    DomainInfo("philosophy", "Ideas, schools, thinkers", ["ідея/2", "школа/2", "філософ/2", "аргумент/2"]),
    DomainInfo("law", "Statutes, rights, courts", ["закон_правовий/2", "право/2", "суд/2", "рішення/2"]),
    DomainInfo("music", "Composers, genres, instruments", ["композитор/2", "жанр_музика/2", "інструмент/1", "твір_музика/2"]),
    DomainInfo("art", "Artists, styles, works", ["художник/2", "стиль/2", "картина/2", "музей/2"]),
    DomainInfo("sport", "Athletes, competitions, records", ["спортсмен/2", "змагання/2", "рекорд/3", "команда/2"]),
    DomainInfo("cuisine", "Dishes, ingredients, traditions", ["страва/1", "інгредієнт/2", "кухня/2", "рецепт/2"]),
    DomainInfo("technology", "Inventions, companies, products", ["винахід/2", "компанія/1", "продукт/2", "рік_створення/2"]),
    DomainInfo("astronomy", "Stars, planets, phenomena", ["зірка/1", "планета/1", "орбіта/2", "відстань_астро/3"]),
    DomainInfo("ecology", "Ecosystems, conservation, pollution", ["екосистема/1", "загроза/2", "вид_під_загрозою/1", "забруднення/2"]),
    DomainInfo("psychology", "Behavior, cognition, disorders", ["поведінка/2", "теорія_психо/2", "розлад/2", "терапія/2"]),
    DomainInfo("education", "Institutions, curricula, methods", ["університет/1", "предмет/2", "метод_навчання/2", "диплом/2"]),
]


def get_domain_names() -> list[str]:
    """Return all domain names from the catalog."""
    return [d.name for d in DOMAIN_CATALOG]


def get_domain(name: str) -> DomainInfo | None:
    """Look up a domain by name."""
    for d in DOMAIN_CATALOG:
        if d.name == name:
            return d
    return None


def format_catalog_for_prompt() -> str:
    """Format the domain catalog as a string for LLM prompts."""
    lines = []
    for d in DOMAIN_CATALOG:
        preds = ", ".join(d.typical_predicates)
        lines.append(f"- **{d.name}**: {d.description}. Typical predicates: {preds}")
    return "\n".join(lines)
