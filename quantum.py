"""Small exact state-vector experiments. Qubit 0 is the leftmost/MSB qubit."""
import itertools
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def gate(state, operator, target):
    state = np.asarray(state, dtype=complex)
    n = int(np.log2(state.size))
    if state.ndim != 1 or state.size != 2**n or not 0 <= target < n:
        raise ValueError('Expected a power-of-two state and a valid target')
    if operator.shape != (2, 2):
        raise ValueError('Expected a single-qubit operator')
    axes = np.moveaxis(state.reshape([2]*n), target, 0)
    result = (operator @ axes.reshape(2, -1)).reshape(axes.shape)
    return np.moveaxis(result, 0, target).reshape(-1)


def cnot(state, control, target):
    n = int(np.log2(len(state)))
    if control == target or not (0 <= control < n and 0 <= target < n):
        raise ValueError('Control and target must be distinct valid qubits')
    idx = np.arange(len(state))
    dest = idx ^ (((idx >> (n-1-control)) & 1) << (n-1-target))
    result = np.empty_like(state)
    result[dest] = state
    return result


def bell_state():
    return cnot(gate(np.array([1, 0, 0, 0], complex), H, 0), 0, 1)


def teleport(psi):
    """Return all four (classical bits, probability, corrected Bob state) branches."""
    psi = np.asarray(psi, complex)
    if psi.shape != (2,) or not np.isclose(np.vdot(psi, psi), 1):
        raise ValueError('Input must be a normalized single-qubit state')
    state = np.kron(psi, bell_state())
    state = gate(cnot(state, 0, 1), H, 0).reshape(2, 2, 2)
    branches = []
    for a, b in itertools.product(range(2), repeat=2):
        bob = state[a, b].copy()
        probability = float(np.vdot(bob, bob).real)
        bob /= np.sqrt(probability)
        if b:
            bob = X @ bob
        if a:
            bob = Z @ bob
        branches.append(((a, b), probability, bob))
    return branches


def superdense(a, b):
    if a not in (0, 1) or b not in (0, 1):
        raise ValueError('Messages must be bits')
    state = bell_state()
    if b:
        state = gate(state, X, 0)
    if a:
        state = gate(state, Z, 0)
    return np.abs(gate(cnot(state, 0, 1), H, 0))**2


def chsh(visibility=1.0):
    """CHSH S for rho = v |Phi+><Phi+| + (1-v) I/4."""
    if not 0 <= visibility <= 1:
        raise ValueError('Visibility must lie in [0,1]')
    psi = bell_state()
    rho = visibility*np.outer(psi, psi.conj()) + (1-visibility)*np.eye(4)/4
    alice = (Z, X)
    bob = ((Z+X)/np.sqrt(2), (Z-X)/np.sqrt(2))
    correlations = np.array([[np.trace(rho @ np.kron(a, b)).real
                              for b in bob] for a in alice])
    score = correlations[0, 0]+correlations[0, 1]+correlations[1, 0]-correlations[1, 1]
    return float(score), correlations


def classical_chsh_bound():
    return max(a0*b0+a0*b1+a1*b0-a1*b1
               for a0, a1, b0, b1 in itertools.product((-1, 1), repeat=4))
