import unittest
import numpy as np
from quantum import H, X, Z, gate, cnot, bell_state, teleport, superdense, chsh, classical_chsh_bound


class QuantumTests(unittest.TestCase):
    def test_unitary_roundtrips(self):
        state = np.array([1, 2j, 3, 4j], complex)/np.sqrt(30)
        for op in (H, X, Z):
            for q in (0, 1):
                np.testing.assert_allclose(gate(gate(state, op, q), op, q), state, atol=1e-14)
        np.testing.assert_allclose(cnot(cnot(state, 0, 1), 0, 1), state)

    def test_bell_and_reduced_state(self):
        state = bell_state()
        np.testing.assert_allclose(abs(state)**2, [.5, 0, 0, .5], atol=1e-14)
        matrix = state.reshape(2, 2)
        np.testing.assert_allclose(matrix @ matrix.conj().T, np.eye(2)/2, atol=1e-14)

    def test_teleport_random_complex_states_all_branches(self):
        rng = np.random.default_rng(17)
        for _ in range(30):
            psi = rng.normal(size=2)+1j*rng.normal(size=2)
            psi /= np.linalg.norm(psi)
            for _, probability, bob in teleport(psi):
                self.assertAlmostEqual(probability, .25)
                self.assertAlmostEqual(abs(np.vdot(psi, bob))**2, 1)

    def test_dense_coding_all_messages(self):
        for a in (0, 1):
            for b in (0, 1):
                self.assertAlmostEqual(superdense(a, b)[2*a+b], 1)

    def test_chsh_bounds_and_noise(self):
        self.assertEqual(classical_chsh_bound(), 2)
        self.assertAlmostEqual(chsh()[0], 2*np.sqrt(2))
        self.assertAlmostEqual(chsh(0)[0], 0)
        self.assertAlmostEqual(chsh(1/np.sqrt(2))[0], 2)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            teleport([1, 1])
        with self.assertRaises(ValueError):
            chsh(1.1)


if __name__ == '__main__':
    unittest.main()
