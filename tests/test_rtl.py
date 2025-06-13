# Tests with VCS

import subprocess
import os
import sys
import pytest
# from sclibs import lib_file_list 

# vcs ../tb/cluster/tb_PE_cluster.sv ../rtl/PE_cluster.sv ../rtl/multicast_controller.sv ../rtl/PE_v2.sv ../rtl/Spad.sv -full64 -debug_pp -sverilog +neg_tchk -l vcs.log -R +lint=TFIPC-L | tee vcs.log

simulator = 'vcs' # vcs or xrun
sim_args = {'vcs':  [
                '-full64',
                '-debug_pp',
                '-debug_access',
                '-sverilog',
                '+neg_tchk',
                '-l', 'vcs.log',
                '-R', '+lint=TFIPC-L',
                '+define+SYNOPSYS'
            ],
            'xrun': [
                '+access+r'
            ]
}

def test_scaler(simulator='vcs',seed=0):

    package_list = [
        '../rtl/common.svh',
    ]

    rtl_file_list = [ 
        '../rtl/output_scaler.sv',
    ]
    tb_name = 'tb_output_scaler'
    tb_path = 'output_scaler'
    stimulus_output_path = 'tb/output_scaler/inputs'

    tb_file = f'../tb/{tb_path}/{tb_name}.sv'
    log_file = f'tests/logs/{tb_name}_{simulator}.log'
    
    logdir = os.path.dirname(log_file)
    os.makedirs(logdir,exist_ok=True)

    # Pre-simulation
    from tests.stim_lib.stimulus_gen import generate_scaler_stimulus

    generate_scaler_stimulus(
        path=stimulus_output_path,
        outBits = 8,
        inBits = 8,
        fpBits = 16
    )

    # Simulation

    with open(log_file,'w+') as f:

        sim = subprocess.Popen([
            simulator,
            *package_list,
            tb_file
        ] + sim_args[simulator] + rtl_file_list, 
        shell=False,
        cwd='./sims',
        stdout=f
        )

    assert not sim.wait(), get_log_tail(log_file,10)

    # Post-simulation

    with open(log_file,'r+') as f:
        f.seek(0)
        out = [line for line in f.readlines()]
        assert 'TEST SUCCESS\n' in out, get_log_tail(log_file,10)
    

# @pytest.mark.parametrize('mode',['random','max','min'])
def test_pe(mode, simulator='vcs',seed=0):

    rtl_file_list = [ 
        '../rtl/PE.sv',
        '../rtl/Spad.sv',
        '../rtl/saturating_multiplier.sv',
    ]
    tb_name = 'tb_PE'
    tb_path = 'PE'
    stimulus_output_path = 'tb/PE/inputs'

    tb_file = f'../tb/{tb_path}/{tb_name}.sv'
    log_file = f'tests/logs/{tb_name}_{simulator}_{mode}.log'
    
    logdir = os.path.dirname(log_file)
    os.makedirs(logdir,exist_ok=True)

    # Pre-simulation

    from tests.stim_lib.stimulus_gen import generate_tb_pe_stimulus

    generate_tb_pe_stimulus(
        actBits = 8,
        weightBits = 8,
        seed = seed,
        path = stimulus_output_path,
        mode = mode
    )

    # Simulation

    with open(log_file,'w+') as f:

        sim = subprocess.Popen([
            simulator,
            tb_file
        ] + sim_args[simulator] + rtl_file_list, 
        shell=False,
        cwd='./sims',
        stdout=f
        )

    assert not sim.wait(), get_log_tail(log_file,10)

    # Post-simulation

    with open(log_file,'r+') as f:
        f.seek(0)
        out = [line for line in f.readlines()]
        assert 'TEST SUCCESS\n' in out, get_log_tail(log_file,10)

# @pytest.mark.parametrize('mode',['random','max','min'])
def test_pe_cluster(mode, simulator='vcs', seed=0):

    rtl_file_list = [ 
        '../rtl/PE_cluster.sv',
        '../rtl/multicast_controller.sv',
        '../rtl/PE.sv',
        '../rtl/Spad.sv',
        '../rtl/saturating_multiplier.sv',
    ]
    tb_name = 'tb_PE_cluster'
    tb_path = 'cluster'
    stimulus_output_path = 'tb/cluster/inputs'

    tb_file = f'../tb/{tb_path}/{tb_name}.sv'
    log_file = f'tests/logs/{tb_name}_{simulator}_{mode}.log'
    
    logdir = os.path.dirname(log_file)
    os.makedirs(logdir,exist_ok=True)

    # Pre-simulation

    from tests.stim_lib.stimulus_gen import generate_tb_cluster_stimulus

    generate_tb_cluster_stimulus(
        actBits = 8,
        weightBits = 8,
        nActs = 16,
        nWeights = 3,
        seed = seed,
        path = stimulus_output_path,
        mode = mode
    )

    # Simulation

    with open(log_file,'w+') as f:

        sim = subprocess.Popen([
            simulator,
            tb_file
        ] + sim_args[simulator] + rtl_file_list, 
        shell=False,
        cwd='./sims',
        stdout=f
        )

    assert not sim.wait(), get_log_tail(log_file,10)

    # Post-simulation

    with open(log_file,'r+') as f:
        f.seek(0)
        out = [line for line in f.readlines()]
        assert 'TEST SUCCESS\n' in out, get_log_tail(log_file,10)

def get_log_tail(log_file,lines):
    print(f'See {log_file} for details') 
    with open(log_file,'r') as f:
        lines = f.readlines()[-lines:]
        return ''.join(lines)