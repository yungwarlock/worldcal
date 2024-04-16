from prefect import flow

from handler import Critiquer

@flow
def critique_event(event: str):
    critiquer = Critiquer.from_env()

    res = critiquer.critique(event)
    return res

if __name__ == "__main__":
    critique_event.serve(name="critique_event")
#     res = critique_event(
#         """
# cameron vs nigeria 2 - 0

# Day: 27
# Month: 6
# Year: 0
# """
#     )
#     print("res:", res)