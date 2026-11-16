"""Persistent NumPy LIF state for closed-loop experiments.

The original stage-2 assay remains unchanged. This kernel preserves its update
order and accepts time-varying external rates on an explicit set of input nodes.
"""
import math
import numpy as np
from .neural import Parameters


class NeuralState:
    def __init__(self, circuit, input_indices, seed=0, params=None,
                 disconnected=False, silenced=()):
        self.circuit = circuit
        self.params = p = params or Parameters()
        self.n = len(circuit.ids)
        for group in (input_indices, silenced):
            if any(type(i) is not int or not 0 <= i < self.n for i in group):
                raise ValueError('Invalid neuron index')
        self.inputs = np.array(sorted(set(input_indices)), dtype=np.int32)
        self.input_mask = np.zeros(self.n, dtype=bool)
        self.input_mask[self.inputs] = True
        self.mute = np.zeros(self.n, dtype=bool)
        self.mute[list(silenced)] = True
        self.refractory = np.full(self.n, round(p.refractory_ms / p.dt_ms), dtype=np.int32)
        # External drive emulates the stage-2 activation assay, not natural EPSCs.
        self.refractory[self.inputs] = 0
        self.voltage = np.full(self.n, p.rest_mv)
        self.synaptic = np.zeros(self.n)
        self.next_active = np.zeros(self.n, dtype=np.int64)
        self.delay = round(p.delay_ms / p.dt_ms)
        self.pending = np.zeros((self.delay + 1, self.n))
        self.weights = circuit.signed_counts * p.weight_mv
        self.weights[self.mute[circuit.pre] | self.mute[circuit.post]] = 0
        if disconnected:
            self.weights.fill(0)
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.counts = np.zeros(self.n, dtype=np.int64)
        self.em = math.exp(-p.dt_ms / p.tau_mem_ms)
        self.es = math.exp(-p.dt_ms / p.tau_syn_ms)
        self.coupling = p.tau_syn_ms / (p.tau_syn_ms - p.tau_mem_ms) * (self.es - self.em)

    def advance(self, rates_hz, duration_ms=5.):
        """Hold rates over this interval; return per-neuron spike counts.

        Preserve RNG input slots under silencing, so an identical replay drive
        uses identical random draws in paired lesion trials.
        """
        p = self.params
        rates = np.asarray(rates_hz, dtype=float)
        if rates.shape != (self.n,) or not np.isfinite(rates).all() or (rates < 0).any():
            raise ValueError('Expected finite, nonnegative neuron rate vector')
        if (rates[~self.input_mask] != 0).any():
            raise ValueError('External drive to a non-input neuron')
        if (rates > 1000).any():
            raise ValueError('External drive exceeds 1000 Hz model guard')
        ratio = duration_ms / p.dt_ms
        if not math.isfinite(ratio) or ratio <= 0 or not math.isclose(ratio, round(ratio), abs_tol=1e-8):
            raise ValueError('Duration must be a positive integer number of neural steps')
        counts = np.zeros(self.n, dtype=np.int64)
        c = self.circuit
        for _ in range(round(ratio)):
            tick = self.tick
            slot = tick % (self.delay + 1)
            self.synaptic += self.pending[slot]
            self.pending[slot].fill(0)
            active = (tick >= self.next_active) & ~self.mute
            self.voltage[active] = (p.rest_mv + (self.voltage[active] - p.rest_mv) * self.em
                                    + self.synaptic[active] * self.coupling)
            self.synaptic[active] *= self.es
            # Always sample the same indexed input slots; mute only the injection.
            events = self.rng.poisson(rates[self.inputs] * p.dt_ms / 1000)
            self.voltage[self.inputs] += events * p.stimulus_jump_mv * ~self.mute[self.inputs]
            spikes = (self.voltage > p.threshold_mv) & active
            if spikes.any():
                ix = np.flatnonzero(spikes)
                counts[ix] += 1
                self.voltage[ix] = p.rest_mv
                self.synaptic[ix] = 0
                self.next_active[ix] = tick + 1 + self.refractory[ix]
                used = spikes[c.pre]
                arrival = (tick + 1 + self.delay) % (self.delay + 1)
                self.pending[arrival] += np.bincount(c.post[used], weights=self.weights[used], minlength=self.n)
            self.tick += 1
        self.counts += counts
        return counts
