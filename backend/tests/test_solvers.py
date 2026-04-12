import random
from ecdlp import solve_ecdlp

def test_smart_attack_from_dataset(case_anomalous):
    curve = case_anomalous['curve']
    P = case_anomalous['generator']
    n = case_anomalous['order']

    secret_x = random.randint(1, n - 1)
    Q = P * secret_x
    
    result = solve_ecdlp(P, Q, curve)
    assert result == secret_x

def test_pohlig_hellman_from_dataset(case_smooth):
    curve = case_smooth['curve']
    P = case_smooth['generator']
    n = case_smooth['order']
    
    secret_x = random.randint(1, n - 1)
    Q = P * secret_x
    
    result = solve_ecdlp(P, Q, curve)
    assert result == secret_x

def test_pollard_rho_from_dataset(case_general):
    curve = case_general['curve']
    P = case_general['generator']
    n = case_general['order']

    secret_x = random.randint(1, n - 1)
    Q = P * secret_x
    
    result = solve_ecdlp(P, Q, curve)
    assert result == secret_x