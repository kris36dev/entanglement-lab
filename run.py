"""Run with python run.py --seed 2023 --output results."""
import numpy as np
import matplotlib.pyplot as plt
from quantum import teleport, superdense, chsh, classical_chsh_bound
from reporting import arguments, csv_write, finish, style


def main():
    args, out = arguments('Teleportation, dense coding and CHSH experiments')
    rng = np.random.default_rng(args.seed)
    style()
    fidelities = []
    for index in range(100):
        psi = rng.normal(size=2)+1j*rng.normal(size=2)
        psi /= np.linalg.norm(psi)
        for (a, b), probability, bob in teleport(psi):
            fidelities.append({'input_state': index, 'alice_bits': f'{a}{b}',
                               'branch_probability': probability,
                               'fidelity': float(abs(np.vdot(psi, bob))**2)})
    csv_write(out/'teleportation.csv', fidelities)
    rows = []
    shots = 4096  # per setting, four settings per visibility
    for v in np.linspace(0, 1, 21):
        score, correlations = chsh(float(v))
        samples = 2*rng.binomial(shots, (1+correlations)/2)/shots-1
        sampled_score = samples[0, 0]+samples[0, 1]+samples[1, 0]-samples[1, 1]
        se = np.sqrt(np.sum(1-correlations**2)/shots)
        rows.append({'visibility': float(v), 'exact_S': score, 'sampled_S': float(sampled_score),
                     'model_standard_error': float(se), 'shots_per_setting': shots})
    csv_write(out/'chsh.csv', rows)
    dense = np.array([superdense(a, b) for a in (0, 1) for b in (0, 1)])
    csv_write(out/'superdense.csv', [{'message': f'{i:02b}', **{f'p_{j:02b}': float(p) for j, p in enumerate(row)}}
                                     for i, row in enumerate(dense)])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), layout='constrained')
    axes[0].plot([r['visibility'] for r in rows], [r['exact_S'] for r in rows], label='Exact model', color='#007f86')
    axes[0].errorbar([r['visibility'] for r in rows], [r['sampled_S'] for r in rows],
                    yerr=[1.96*r['model_standard_error'] for r in rows], fmt='.', color='#c56b26',
                    label='Sampled; approx. 95% interval', capsize=2)
    axes[0].axhline(2, color='#435267', ls='--', label='Classical bound')
    axes[0].set(xlabel='Bell-state visibility', ylabel='CHSH S', title='Entanglement advantage fades with noise', ylim=(-.2, 3.2))
    axes[0].legend(fontsize=8, loc='upper left')
    axes[1].imshow(dense, cmap='Blues', vmin=0, vmax=1)
    for i in range(4):
        for j in range(4):
            axes[1].text(j, i, f'{dense[i,j]:.0%}', ha='center', va='center',
                         color='white' if dense[i,j] > .5 else '#24344a')
    axes[1].set(xticks=range(4), yticks=range(4), xticklabels=['00', '01', '10', '11'],
                yticklabels=['00', '01', '10', '11'], xlabel='Decoded bits', ylabel='Sent bits',
                title='Superdense coding: all messages decoded')
    axes[1].grid(False)
    fig.suptitle('ENTANGLEMENT LAB  |  Exact protocols and finite measurements', fontsize=14, fontweight='bold')
    fig.savefig(out/'overview.png', dpi=180)
    plt.close(fig)
    summary = {'seed': args.seed, 'teleportation_states': 100, 'branches_checked': len(fidelities),
               'minimum_teleportation_fidelity': min(r['fidelity'] for r in fidelities),
               'ideal_chsh_S': chsh()[0], 'classical_bound': classical_chsh_bound(),
               'ideal_chsh_game_win_probability': .5+chsh()[0]/8,
               'chsh_visibility_threshold': 1/np.sqrt(2), 'hardware_execution': False}
    finish(out, summary)


if __name__ == '__main__':
    main()
