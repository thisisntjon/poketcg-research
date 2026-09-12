"""Exercise the exact training-side selection component with generic fixed scores.

No checkpoint, trained network, game engine, card data, GPU or network is used.
This demonstrates selection constraints, not tactical quality or the full player.
"""
import hashlib
import json
from pathlib import Path
import torch
from action_decoder import SelectionError, decode_selection

EXPECTED_SOURCE = '05917722d740c3a12ba1533ea91049acbf61e15afae9ff0c50306d6baa7bc724'

def main():
    source=Path(__file__).with_name('action_decoder.py')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==EXPECTED_SOURCE
    cases=[]
    def choose(name,scores,legal,minimum,maximum,expected):
        result=decode_selection(lambda selected:torch.tensor(scores,dtype=torch.float32),
            legal_mask=torch.tensor(legal,dtype=torch.bool),min_count=minimum,max_count=maximum)
        assert result.relative_indices==expected,(name,result)
        cases.append(dict(case=name,selected=list(result.relative_indices),passed=True))
    choose('optional empty selection',[9.,8.,100.,10.],[True,True,False],0,3,())
    choose('minimum one; illegal highest score masked',[9.,8.,100.,10.],[True,True,False],1,3,(0,))
    choose('minimum two; no repeated selection',[9.,8.,100.,10.],[True,True,False],2,3,(0,1))
    choose('maximum bound',[9.,8.,-100.],[True,True],0,1,(0,))
    choose('maximum zero',[9.,8.,-100.],[True,True],0,0,())
    selected=decode_selection(lambda prior:torch.tensor([9.,1.,0.] if not prior else [9.,1.,10.]),
        legal_mask=torch.tensor([True,True]),min_count=1,max_count=2)
    assert selected.relative_indices==(0,)
    cases.append(dict(case='context-dependent STOP',selected=[0],passed=True))
    try:
        decode_selection(lambda prior:torch.tensor([9.,8.,0.]),
            legal_mask=torch.tensor([True,False]),min_count=2,max_count=2)
    except SelectionError:
        cases.append(dict(case='unsatisfiable minimum rejected',passed=True))
    else:
        raise AssertionError('unsatisfiable minimum accepted')
    output=dict(source_sha256=EXPECTED_SOURCE,torch_version=torch.__version__,device='cpu',
                trained_models_loaded=0,games_run=0,checks=cases,
                scope='Generic deterministic checks of the training-side decoder; not a full-agent reproduction or measured game-strength result.')
    print(json.dumps(output,indent=2))

if __name__=='__main__': main()
