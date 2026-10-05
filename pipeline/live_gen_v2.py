"""Inactive candidate pilot for filtered card choice / Rocket area aim.

The running pilot in live_gen.py is not edited. Constructor defaults delegate
to it exactly. Deploy only through an owner-approved candidate live entry point.
"""
import numpy as np
import torch

from .live_gen import GenPilot as LegacyGenPilot, FORM_PAD
from .e1_eval import allowed_slots
from .model_v3 import cell_xy
from .decision_options import DecisionOptions, choose_cells, choose_slot


class GenPilot(LegacyGenPilot):
    def __init__(self, *args, decision_options=None, decision_seed=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.decision_options = decision_options or DecisionOptions()
        self.decision_seed = int(decision_seed)
        self.match_index = -1
        self.match_seed = self.decision_seed
        self.rng_decisions = np.random.default_rng(self.match_seed)

    def reset_match(self):
        super().reset_match()
        self.match_index += 1
        self.match_seed = int(np.random.SeedSequence([self.decision_seed, self.match_index]).generate_state(1)[0])
        self.rng_decisions = np.random.default_rng(self.match_seed)

    @torch.no_grad()
    def decide(self, frame):
        options = self.decision_options
        if not options.active:
            return super().decide(frame)
        b, info = self.row(frame)
        lookahead = ({'public_lookahead_counts': info['public_lookahead_counts']}
                     if 'public_lookahead_counts' in info else {})
        out = self.model(b)
        p = float(torch.sigmoid(out['gate'][0]))
        allowed = allowed_slots(np.array([h[0] > 0 for h in info['hand']]), info['costs'], info['el_int'])
        if not allowed.any():
            return dict(play=False, no_affordable=True, p_play=p, hand_pos=-1, deck_index=-1, card=0,
                        form=FORM_PAD, bs=info['bs'], name=None, el_int=info['el_int'], **lookahead)
        pos = choose_slot(out['card'][0], allowed, options, self.rng_decisions, playing=p > self.gate_tau)
        card, form = info['hand'][pos]
        name = info['names'][info['hand_deck_indices'][pos]] if card > 0 else None
        d = dict(play=p > self.gate_tau and card > 0, p_play=p, hand_pos=pos, no_affordable=False,
                 deck_index=info['hand_deck_indices'][pos], card=card, form=form, bs=info['bs'], name=name, **lookahead)
        if card > 0:
            logits = self.model(b, card=torch.tensor([card], device=self.dev),
                                form=torch.tensor([form], device=self.dev))['cell']
            d['xy'] = cell_xy(int(choose_cells(logits, [name], options)[0]), self.grid)
        return d
