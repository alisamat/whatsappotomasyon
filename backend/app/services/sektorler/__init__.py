from app.services.sektorler.emlak import EmlakHandler

SEKTOR_HANDLER_MAP = {
    'emlak': EmlakHandler(),
}

def handler_al(sektor: str):
    return SEKTOR_HANDLER_MAP.get(sektor)
