"""Adversarial geometry, decision parity and seeded integration checks; CPU only."""
import ast
import copy
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from pipeline import e1_eval as E
from pipeline.decision_options import (DecisionOptions, filtered_probabilities, choose_slot, choose_cells,
                                      rocket_area_scores, rocket_radius_tiles, match_kwargs)
from pipeline.live_gen_v2 import GenPilot
from pipeline.tests.test_live_gen_afford import pilot, frame

torch.set_num_threads(1)


@pytest.mark.parametrize('ratio,expected', [(0.5, [.6, .4]), (0.7, [1, 0])])
def test_confident_replacement_is_measured_not_silently_blocked(ratio, expected):
    np.testing.assert_allclose(filtered_probabilities(np.log([.6, .4]), [True, True], ratio), expected)


def test_filter_before_temperature_and_affordability():
    p = filtered_probabilities(np.log([.9, .06, .04]), [False, True, True], .7, .2)
    np.testing.assert_array_equal(p, [0, 1, 0])
    np.testing.assert_array_equal(filtered_probabilities([4, 5], [False, False]), [0, 0])
    np.testing.assert_allclose(filtered_probabilities([1, 1, 0], [True]*3, 1), [.5, .5, 0])


@pytest.mark.parametrize('kwargs', [{'card_ratio': 0}, {'card_ratio': 1.1}, {'card_T': 0},
                                    {'card_T': float('nan')}, {'spell_aim': 'tower_rule'}])
def test_invalid_options_fail(kwargs):
    with pytest.raises(ValueError):
        DecisionOptions(**kwargs)


def test_only_near_ties_draw_and_stream_is_reproducible():
    rng = np.random.default_rng(123); before = copy.deepcopy(rng.bit_generator.state)
    options = DecisionOptions(card_choice='filtered')
    assert choose_slot(torch.tensor([9., 0.]), [True, True], options, rng) == 0
    assert choose_slot(torch.tensor([0., 0.]), [True, True], options, rng, playing=False) == 0
    assert choose_slot(torch.tensor([0., 0.]), [False, False], options, rng) == -1
    assert rng.bit_generator.state == before
    def draws(seed):
        stream = np.random.default_rng(seed)
        return [choose_slot(torch.zeros(2), [True, True], options, stream) for _ in range(40)]
    assert draws(7) == draws(7)
    assert set(draws(7)) == {0, 1}
    assert draws(7) != draws(8)


def cluster_logits():
    p = torch.zeros(1, 2304)
    p[0, 50*36+28] = .2  # highest individual cell, away from the learned target cluster
    for y in range(12, 15):
        for x in range(6, 9):
            p[0, y*36+x] = .8/9
    return p.log()


def test_area_mass_selects_broad_cluster_without_tower_prior():
    logits = cluster_logits()
    default = int(choose_cells(logits, ['Rocket'], DecisionOptions())[0])
    selected = int(choose_cells(logits, ['Rocket'], DecisionOptions(spell_aim='rocket_area'))[0])
    assert default == 50*36+28
    assert np.linalg.norm(np.array([selected % 36, selected // 36])/2 - [3.5, 6.5]) <= rocket_radius_tiles()
    # Same probabilities on a different card do not enable the Rocket rule.
    assert int(choose_cells(logits, ['Log'], DecisionOptions(spell_aim='rocket_area'))[0]) == default


def test_disk_uses_physical_tiles_and_cannot_wrap_edges():
    p = torch.zeros(2, 2304); p[0, 0] = 1; p[1, 20*36+20] = 1
    mass = rocket_area_scores(p)
    assert rocket_radius_tiles() == 2  # checked-in game's catalog, not the inference implementation
    assert mass[0, 4] == 1 and mass[0, 4*36] == 1
    assert mass[0, 3*36+3] == 0  # 2.12 tiles diagonally
    assert mass[0, 35] == 0 and mass[0, -1] == 0
    assert mass[0, 0] == 1  # missing board cells do not get probability renormalised
    # Independent brute-force disk sum at every board location.
    xy = np.c_[np.tile(np.arange(36)/2, 64), np.repeat(np.arange(64)/2, 36)]
    expected = np.linalg.norm(xy-[10, 10], axis=1) <= 2
    np.testing.assert_array_equal(mass[1].numpy(), expected)


def test_equal_mass_prefers_learned_local_mode():
    logits = torch.full((1, 2304), -torch.inf); logits[0, 20*36+20] = 0
    assert int(choose_cells(logits, ['Rocket'], DecisionOptions(spell_aim='rocket_area'))[0]) == 20*36+20


class Model:
    def cell_logits(self, enc, slot):
        return cluster_logits().repeat(len(slot), 1)


@pytest.fixture(scope='module')
def legacy():
    root = Path(__file__).resolve().parents[2]
    source = subprocess.check_output(['git', 'show', '4b36ab2:pipeline/e1_eval.py'], cwd=root, text=True)
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('live_decide', 'live_decide_batch')]
    scope = dict(E.__dict__)
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<frozen legacy e1>', 'exec'), scope)
    return scope


def tensors():
    heads = {'card': torch.tensor([[1., 2., 0., -1.], [0., 0., 0., 0.], [2., 2., -1., 0.],
                                   [0., 9., 3., 2.], [1., 1., 1., 1.]])}
    allowed = np.array([[1, 1, 1, 1], [0, 0, 0, 0], [1, 1, 0, 1], [1, 0, 1, 1], [1, 1, 1, 1]], bool)
    return {'g': torch.zeros(5, 2)}, heads, np.array([.9, .9, .1, .35, .1]), allowed, np.array([0, 0, 0, 0, 1], bool)


def test_default_sim_is_exact_legacy_single_and_batch(legacy):
    enc, heads, p, allowed, stalled = tensors()
    for r in range(len(p)):
        args = (Model(), {k:v[r:r+1] for k,v in enc.items()}, {k:v[r:r+1] for k,v in heads.items()},
                p[r], allowed[r])
        expected = legacy['live_decide'](*args, tau=.35, stalled=stalled[r])
        assert E.live_decide(*args, tau=.35, stalled=stalled[r]) == expected
        assert E.live_decide(*args, tau=.35, stalled=stalled[r], decision_options=DecisionOptions()) == expected
    args = (Model(), enc, heads, p, allowed, stalled)
    assert E.live_decide_batch(*args, tau=.35) == legacy['live_decide_batch'](*args, tau=.35)


def test_option_sim_batch_and_single_are_identical_and_gate_unchanged():
    enc, heads, p, allowed, stalled = tensors()
    options = DecisionOptions(card_choice='filtered', card_ratio=.5, spell_aim='rocket_area')
    names = [['Rocket', 'Knight', 'Log', 'Tesla']]*len(p)
    seeds = [7, 19, 6, 42, 123]
    batch = E.live_decide_batch(Model(), enc, heads, p, allowed, stalled, tau=.35, decision_options=options,
                                rngs=[np.random.default_rng(s) for s in seeds], card_names=names)
    single = [E.live_decide(Model(), {k:v[r:r+1] for k,v in enc.items()}, {k:v[r:r+1] for k,v in heads.items()},
                           p[r], allowed[r], tau=.35, stalled=stalled[r], decision_options=options,
                           rng=np.random.default_rng(seeds[r]), card_names=names[r]) for r in range(len(p))]
    assert batch == single
    baseline = E.live_decide_batch(Model(), enc, heads, p, allowed, stalled, tau=.35)
    assert [d['play'] for d in batch] == [d['play'] for d in baseline]
    assert [d['why'] for d in batch] == [d['why'] for d in baseline]
    for r, d in enumerate(batch):
        assert d['slot'] == -1 or allowed[r, d['slot']]


def test_streams_follow_match_not_batch_order():
    def match(tag, seed):
        return SimpleNamespace(tag=tag, k=seed, cfg={'card_choice':'filtered'}, deck=SimpleNamespace(cards=['Rocket', 'Log']))
    a, b = match('a', 2), match('b', 3)
    streams = match_kwargs([a, b])['rngs']
    first = [s.random() for s in streams]
    a2, b2 = match('a', 2), match('b', 3)
    second = [s.random() for s in match_kwargs([b2, a2])['rngs']]
    assert first == second[::-1]
    assert match_kwargs([SimpleNamespace(cfg={})]) == {}


@pytest.mark.parametrize('elixir', [1.9, 3.5, 10])
def test_candidate_live_default_is_exact_legacy(elixir):
    original = pilot([0, 9, 1, 2])
    candidate = object.__new__(GenPilot); candidate.__dict__.update(copy.deepcopy(original.__dict__))
    candidate.decision_options = DecisionOptions()
    assert candidate.decide(frame(elixir)) == original.decide(frame(elixir))


def test_candidate_live_and_sim_share_selected_rocket_aim():
    candidate = object.__new__(GenPilot)
    candidate.decision_options = DecisionOptions(spell_aim='rocket_area', card_choice='filtered')
    candidate.rng_decisions = np.random.default_rng(7)
    candidate.dev, candidate.grid, candidate.gate_tau = torch.device('cpu'), 'lattice', .35
    info = dict(hand=[(1, 0), (2, 0)], costs=[6, 3], el_int=10, bs=None,
                names=['Rocket', 'Knight'], hand_deck_indices=[0, 1])
    candidate.row = lambda frame: ({}, info)
    class LiveModel:
        def __call__(self, b, card=None, form=None):
            return {'cell':cluster_logits()} if card is not None else {'gate':torch.tensor([2.]), 'card':torch.tensor([[9., 0.]])}
    candidate.model = LiveModel()
    d = candidate.decide({})
    expected = E.live_decide(Model(), {'g':torch.zeros(1, 2)}, {'card':torch.tensor([[9., 0.]])},
                             float(torch.sigmoid(torch.tensor(2.))), np.array([True, True]), tau=.35, stalled=False,
                             decision_options=candidate.decision_options, rng=np.random.default_rng(7),
                             card_names=info['names'])
    assert d['play'] == expected['play'] and d['hand_pos'] == expected['slot']
    assert d['xy'] == (expected['cell'] % 36 / 36, expected['cell'] // 36 / 64)


def test_diagnostic_maps_checkpoint_card_ids_by_name():
    from scratchpad.gauntlet.L71.decision_options.check_sampling_v2 import remap_validation_cards
    a = np.array([[0, 2, 3]])
    sub = {k: a for k in ('hand_card', 'next_card', 'deck_card', 'y_card', 'y_wait_card')}
    sub['past'] = np.array([[[3., 0, .1, .2, 1.]]])
    result, mapping = remap_validation_cards(sub, ['pad', 'new', 'rocket', 'log'], ['pad', 'rocket', 'log'], 1)
    np.testing.assert_array_equal(result['hand_card'], [[0, 1, 2]])
    assert result['past'][0, 0, 0] == 2
    assert sub['past'][0, 0, 0] == 3  # source rows preserved
    assert mapping['identity_mapping'] is False
    with pytest.raises(ValueError, match='lacks'):
        remap_validation_cards(sub, ['pad', 'new', 'rocket', 'log'], ['pad', 'rocket'], 1)


def test_active_options_follow_real_reactive_path_and_match_batched_engine():
    from pipeline.tests.test_search_s0 import runner, HOGEQ, RoyaleSelfPlayEnv
    if RoyaleSelfPlayEnv is None:
        pytest.skip('Royale venv required')
    run = runner(tail_cap=500)
    run.lcfg.update(card_choice='filtered', card_ratio=.5, card_T=.7,
                    spell_aim='rocket_area', decision_seed=17)
    actual_match = run.setup('gen', 3, HOGEQ)
    run.play('plain', actual_match)
    actual = dict(run.last_result); actual.pop('wall_s')
    assert hasattr(actual_match.learner, 'rng_decision_options')
    assert not hasattr(actual_match.opp, 'rng_decision_options')
    opp, opp_cfg = run.opps['gen']
    spec = dict(tag='s0:gen:3', opp={'id':'gen'}, learner_deck=list(E.ICEBOW_ENGINE_DECK),
                opp_deck=list(HOGEQ), learner_side=1, seed=3)
    outputs=[]
    E.run_selfplay_batch(lambda: RoyaleSelfPlayEnv(tail_cap=500), run.learner,
                         {'gen':(opp,opp_cfg)}, [(0,spec,0)], run.lcfg, 1, on_result=outputs.append)
    expected=dict(outputs[0]); expected.pop('wall_s')
    assert actual == expected


def test_seeded_runtime_frequencies_match_checked_distribution():
    options=DecisionOptions(card_choice='filtered',card_ratio=.5,card_T=.7)
    logits=np.log([.4,.3,.2,.1]); allowed=[True]*4
    expected=filtered_probabilities(logits,allowed,.5,.7)
    rng=np.random.default_rng(982)
    samples=[choose_slot(logits,allowed,options,rng) for _ in range(6000)]
    observed=np.bincount(samples,minlength=4)/len(samples)
    assert observed[3]==0
    np.testing.assert_allclose(observed,expected,atol=.025,rtol=0)


def test_e1_cli_rejects_invalid_options_before_loading(tmp_path):
    # Exercises main(), not only --help, with no model/game connection.
    with pytest.raises(ValueError, match='card_ratio'):
        E.main(['--port','0','--out',str(tmp_path/'unused'), '--card-ratio','0'])
    with pytest.raises(ValueError, match='policy live'):
        E.main(['--port','0','--out',str(tmp_path/'unused2'), '--policy','sample', '--spell-aim','rocket_area'])


def test_reactive_cli_forwards_telemetry_and_options_to_worker(tmp_path, monkeypatch):
    from pipeline import search_s0 as S
    seen=[]
    monkeypatch.setattr(S, '_init_worker', lambda args: seen.append(args))
    monkeypatch.setattr(S, '_run_job', lambda job: dict(arm=job[0], opp=job[1], seed=job[2], skipped='test'))
    S.main(['--out',str(tmp_path/'run'),'--seeds','0:1','--opps','gen','--arms','plain',
            '--behaviour-telemetry','--card-choice','filtered','--card-ratio','.7'])
    assert seen[0]['behaviour_telemetry'] is True
    assert seen[0]['decision_options']['card_choice']=='filtered'
