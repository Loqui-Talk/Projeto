from github.PaginatedList import PaginatedList
from .content import GitContent

def extract_content(func):
    def wrapper(*args, **kwargs):
        data: PaginatedList = func(*args, **kwargs)
        if not isinstance(data, PaginatedList):
            return __extract(func.__name__, data)

        resultados = []
        for d in data:
            resultado_busca = __extract(func.__name__, d)
            if resultado_busca is not None:
                resultados.append(resultado_busca)

        return resultados[0] if resultados else None

    return wrapper

def __extract(func_name: str, data: PaginatedList) -> GitContent | None:
    try:
        assert isinstance(data, PaginatedList)
        if data.totalCount == 0:
            return None
        return GitContent(data[0])
    except AssertionError:
        print(f"[{func_name}] O valor retornado deve ser um PaginatedList.")
    except Exception as e:
        print(f"[{func_name}] Erro ao extrair conteúdo: {e}")
