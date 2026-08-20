"""Temporary Track 05 fixture used to prove that an uncovered REGR blocks CI."""


# SAC:REGR: on=dogfood_ci - track05Dogfood: MUST block uncovered changes; MUST verify: track05DogfoodTest
def track05Dogfood() -> bool:
    return True


def track05DogfoodTest() -> bool:
    return track05Dogfood()
