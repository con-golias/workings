from claim_gate import ToolEvent, gate

DONE = "Done! Your order #1042 has been cancelled."


def test_claim_without_event_is_replaced():
    v = gate(DONE, events=[])
    assert not v.passed and v.unproven == ("cancel_order",)
    assert "couldn't confirm" in v.reply


def test_failed_tool_does_not_count():
    v = gate(DONE, [ToolEvent("cancel_order", ok=False, ref="")])
    assert not v.passed


def test_ok_without_a_record_does_not_count():
    # the "status: ok, value unusable" case: no reference, no proof
    v = gate(DONE, [ToolEvent("cancel_order", ok=True, ref="")])
    assert not v.passed


def test_claim_with_proof_passes_untouched():
    v = gate(DONE, [ToolEvent("cancel_order", ok=True, ref="cx_8812")])
    assert v.passed and v.reply == DONE


def test_wrong_tool_does_not_prove_it():
    v = gate(DONE, [ToolEvent("refund_payment", ok=True, ref="re_77")])
    assert not v.passed


def test_no_claim_no_check():
    v = gate("I can help with that. Which order is it?", [])
    assert v.passed


def test_refund_claim():
    v = gate("Your refund has been processed, you'll see it in 3 days.", [])
    assert v.unproven == ("refund_payment",)
