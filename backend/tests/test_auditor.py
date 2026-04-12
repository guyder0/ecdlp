from ecdlp.auditor import ECDLPAuditor

def test_auditor_anomalous(case_anomalous):
    curve = case_anomalous['curve']
    analysis = ECDLPAuditor.analyze(curve)
    assert analysis["is_anomalous"] is True
    assert analysis["recommended_solver"] == "SmartAttackSolver"

def test_auditor_smooth(case_smooth):
    curve = case_smooth['curve']
    analysis = ECDLPAuditor.analyze(curve)
    assert analysis["is_smooth"] is True
    assert analysis["recommended_solver"] == "PohligHellmanSolver"

def test_auditor_general(case_general):
    curve = case_general['curve']
    analysis = ECDLPAuditor.analyze(curve)
    assert analysis["recommended_solver"] == "PollardRhoSolver"