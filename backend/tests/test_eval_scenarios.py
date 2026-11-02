from evals.scenarios import SCENARIOS


def test_scenario_ids_are_unique_and_every_step_is_checked():
    ids = [s.id for s in SCENARIOS]
    assert len(ids) == len(set(ids))
    assert all(step.checks for s in SCENARIOS for step in s.steps)


def test_the_ticket_scenarios_are_all_covered():
    ids = {s.id for s in SCENARIOS}
    assert {
        "catalog-guitars-under-1000",
        "policy-store-address",
        "pricing-takamine-gd20",
        "return-delivered-order",
        "accessory-redirect",
        "off-topic",
        "jailbreak-prompt-leak",
        "jailbreak-role-play",
        "other-customer-order",
        "complaint-confirmation",
        "complaint-visitor",
    } <= ids
