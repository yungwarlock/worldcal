from prefect import flow

from handler import Critiquer

@flow
def critique_event(event: str):
    critiquer = Critiquer.from_env()

    res = critiquer.critique(event)
    return res
