import numpy as np
from scipy.signal import convolve2d
import os
from tests.stim_lib.quant import *

def generate_scaler_stimulus(
    path,
    outBits = 8,
    inBits = 8,
    fpBits = 16,
    seed = 0
):

    np.random.seed(seed)

    out_scale = np.random.uniform(0,5,10) / (2**outBits)
    m0, shift = np.vectorize(convert_scale_to_shift_and_m0)(out_scale)
    m0bin = np.vectorize(convert_to_fixed_point)(m0,fpBits)

    m0int = np.vectorize(int)(m0bin,base=2)

    test_int = np.random.randint(-2**(inBits-1),2**(inBits-1)-1,10) * np.random.randint(-2**(inBits-1),2**(inBits-1)-1,10)
    scaled = test_int*m0int
    scaled_clipped = scaled // (2**fpBits)
    scaled_clipped_shifted = np.vectorize(int)(scaled_clipped / 2**(-shift))
    out = np.vectorize(saturating_clip)(scaled_clipped_shifted,outBits=outBits)
    
    vbin = np.vectorize(hex)

    print('m0, shift\t',m0int,shift)
    print('test_int\t',test_int)
    print('test_int x m0\t',scaled, vbin(scaled))
    print('shifted by m0 fp\t',scaled_clipped, vbin(scaled_clipped))
    print('then shifted by shift\t',scaled_clipped_shifted, vbin(scaled_clipped_shifted))
    print('saturating_clip\t',out)
    
    np.savetxt(path+'/shift.txt',-shift,'%i')
    np.savetxt(path+'/m0.txt',m0int,'%i')
    np.savetxt(path+'/ins.txt',test_int,'%i')
    np.savetxt(path+'/outs.txt',out,'%i') 

    return out

def generate_tb_cluster_stimulus(
    actBits = 3,
    weightBits = 3,
    outBits = 3,
    nActs = 16,
    nWeights = 3,
    seed = 0,
    path = 'tb_cluster',
    mode = 'random'
):

    # Check if path exists
    if not os.path.exists(path):
        raise ValueError(f'Path {path} does not exist.')

    nOuts = nActs - nWeights + 1

    np.random.seed(0)
    if mode == 'random':
        a = np.random.randint(-2**(actBits-1),2**(actBits-1)-1,size=(nActs,nActs))
        w = np.random.randint(-2**(weightBits-1),2**(weightBits-1)-1,size=(nWeights,nWeights))
        o = convolve2d(a,w[::-1].T[::-1].T,mode='valid')
    if mode == 'max':
        act_value = 2**(actBits-1) - 1
        weight_value = 2**(weightBits-1) - 1
        a = np.full((nActs, nActs), act_value)
        w = np.full((nWeights, nWeights), weight_value)
        o = convolve2d(a,w[::-1].T[::-1].T,mode='valid')
    if mode == 'min':
        act_value = -2**(actBits-1)
        weight_value = -2**(weightBits-1)
        a = np.full((nActs, nActs), act_value)
        w = np.full((nWeights, nWeights), weight_value)
        o = convolve2d(a,w[::-1].T[::-1].T,mode='valid')

    print(f'PE cluster must be {nOuts} PEs wide and {nWeights} PEs high ')

    ids_acts = np.zeros((nOuts+1,nWeights))
    for x,idx in enumerate(ids_acts):
        for y,id in enumerate(idx):
            ids_acts[x][y] = x + y
    ids_acts[-1] = [0,0,0] # Only zeros for the Y-bus for now (you only need it for multichannel convolutions)
    
    ids_weights = np.zeros((nOuts+1,nWeights))
    for x,idx in enumerate(ids_weights):
        ids_weights[x] = [i for i in range(nWeights)]
    ids_weights[-1] = [0,0,0] # Only zeros for the Y-bus for now (you only need it for multichannel convolutions)

    tag_order_acts = []
    for i in range(nActs):
        tag_order_acts.append([0,i])
    tag_order_acts = np.array(tag_order_acts)

    tag_order_weights = []
    for i in range(nWeights):
        tag_order_weights.append([0,i])
    tag_order_weights = np.array(tag_order_weights)

    print("=============== A =================")
    print(a)
    print("=============== W =================")
    print(w)
    print("=============== O =================")
    print(o)

    np.savetxt(path + '/a.txt',a,'%i')
    np.savetxt(path + '/w.txt',w,'%i')
    np.savetxt(path + '/o.txt',o,'%i')
    np.savetxt(path + '/ids_acts.txt',ids_acts,'%i')
    np.savetxt(path + '/ids_weights.txt',ids_weights,'%i')
    np.savetxt(path + '/tag_order_acts.txt',tag_order_acts,'%i')
    np.savetxt(path + '/tag_order_weights.txt',tag_order_weights,'%i')


def generate_tb_pe_stimulus(
    actBits = 8,
    weightBits = 8,
    nActs = 16,
    nWeights = 3,
    seed = 0,
    path = 'tb_PE',
    mode = 'random' # 'max', 'min', 'random'
):

    # Check if path exists
    if not os.path.exists(path):
        raise ValueError(f'Path {path} does not exist.')

    if mode == 'random':
        np.random.seed(0)    
        a = np.random.randint(-2**(actBits-1),2**(actBits-1)-1,size=nActs)
        w = np.random.randint(-2**(weightBits-1),2**(weightBits-1)-1,size=nWeights)
        o = np.convolve(a,w[::-1],'valid')
    if mode == 'max':
        act_value = 2**(actBits-1) - 1
        weight_value = 2**(weightBits-1) - 1
        a = np.full((nActs), act_value)
        w = np.full((nWeights), weight_value)
        o = np.convolve(a,w[::-1],'valid')
    if mode == 'min':
        act_value = -2**(actBits-1)
        weight_value = -2**(weightBits-1)
        a = np.full((nActs), act_value)
        w = np.full((nWeights), weight_value)
        o = np.convolve(a,w[::-1],'valid')

    np.savetxt(path + '/a.txt',a,'%i')
    np.savetxt(path + '/w.txt',w,'%i')
    np.savetxt(path + '/o.txt',o+1,'%i')