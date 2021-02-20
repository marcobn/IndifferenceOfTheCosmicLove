# The Indifefrence of the Cosmic Love
# for flauto d'amore (or flute, or alto flute or piccolo), multi-channel audio, electronics and cosmic rays
# by Marco Buongiorno Nardelli for Ginevra Petrucci (2021)

# _SCORE_

import warnings
warnings.filterwarnings("ignore") 

import sys,os,glob,time
import numpy as np
import liblo
import pyo as po
import music21 as m21

from musicntwrk import musicntwrk
from musicntwrk.musicntwrk import PCSet
from musicntwrk.plotting.drawNetwork import drawNetwork
mk = musicntwrk.musicntwrk(TET=12)

from musicntwrk.harmony.harmonicDesign import harmonicDesign
from musicntwrk.harmony.networkHarmonyGen import networkHarmonyGen
from musicntwrk.harmony.rhythmicDesign import rhythmicDesign

####################### USER SETTINGS ######################

# Set number of input and output channels - recording setup - model progression
nch = 4
ich = 0
record = False
if record:
    recfil = 'perf.wav'
# choose the model for the progression
model = 'probII'
randomized = False
if randomized == False:
    # set seed to arbitrary number (for partial reproducibility of the performance)
    np.random.seed(21521)
# set dynamics for [p, mf, f, pizz, slap, jet] respectively
mul = [0.1,0.2,0.4,0.4,0.4,0.4]
# set number of octaves in mapping
octaves = [3]
# set overall gain
gain = [0.2]

#################### END USER SETTINGS ######################

# Set audio server
s = po.Server(audio='coreaudio',nchnls=nch,ichnls=ich).boot()
#s = po.Server(nchnls=nch,ichnls=ich).boot()
#s.setOutputDevice(10)  #choose audio device for routing
s.start()
if record:
    s.recordOptionstions(filename=recfil, fileformat=0, sampletype=1)
    s.recstart()

### Read the samples and create the dictionaries

def importSoundfiles(dirpath='./',filepath='./',mult=0.1,gain=1.0):
    # reading wavefiles
    try:
        obj = [None]*len(glob.glob(dirpath+filepath))
        fil = [None]*len(glob.glob(dirpath+filepath))
        n=0
        for file in glob.glob(dirpath+filepath):
            fil[n] = file
            n += 1
        for i in range(len(glob.glob(dirpath+filepath))):
            obj[i] = po.SfPlayer(fil[i],mul=mult*gain).stop()
    except:
        print('error in file reading')
        pass

    return(obj,fil,mult)

# Import sound files

p_obj,p_fil,p_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[0],gain=gain[0])
p1_obj,p_fil,p_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[0],gain=gain[0])
mf_obj,mf_fil,mf_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[1],gain=gain[0])
mf1_obj,mf_fil,mf_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[1],gain=gain[0])
f_obj,f_fil,f_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[2],gain=gain[0])
f1_obj,f_fil,f_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/FLUTE/*',mult=mul[2],gain=gain[0])

f = []
l = []
for n,file in enumerate(p_fil):
    f.append(file.split('/')[-1].split('.')[0])
    l.append(n)
p_dict = dict(zip(f,l))

f = []
l = []
for n,file in enumerate(mf_fil):
    f.append(file.split('/')[-1].split('.')[0])
    l.append(n)
mf_dict = dict(zip(f,l))

f = []
l = []
for n,file in enumerate(f_fil):
    f.append(file.split('/')[-1].split('.')[0])
    l.append(n)
f_dict = dict(zip(f,l))

pizz_obj,pizz_fil,pizz_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/PIZZ/*',
                                              mult=mul[3],gain=gain[0])
slap_obj,slap_fil,slap_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/SLAPS/*',
                                              mult=mul[4],gain=gain[0])
jet_obj,jet_fil,jet_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/JETS/*',
                                           mult=mul[5],gain=gain[0])
jet1_obj,jet_fil,jet_mul = importSoundfiles(dirpath='../SOUNDFILES',filepath='/JETS/*',
                                            mult=mul[5],gain=gain[0])


def panMove(snd0,snd1,fil,nch,mult):
    if snd0.isPlaying() == True:
        pass
    else:
        snd0.play()
        snd1.play()
        ff = float(1/po.sndinfo(fil)[1]/4)
        sin = po.Sine(freq=ff,phase=0)
        cos = po.Sine(freq=ff,phase=0.25)
        ini = np.random.randint(0,nch)
        step = np.random.randint(0,int(nch/2)+1)
        end = (ini+step)%nch
        snd0.out(ini,0).setMul(mult*cos)
        snd1.out(end,0).setMul(mult*sin)
        snd0.stop(wait=po.sndinfo(fil)[1])
        snd1.stop(wait=po.sndinfo(fil)[1])


# ### Build the harmonic progression

def noteList(pitches,octaves,TET=12):

    notes = []
    for i in range(len(pitches)):
        c = PCSet(np.random.permutation(np.asarray(pitches[i])),UNI=False,ORD=False,TET=TET)
        for i in range(c.pcs.shape[0]):
            notes.append(c.pcs[i])
    notes = np.asarray(notes)
    
    ### Assign name and octave to note list
    
    sequence = []
    for note in notes:
        p = PCSet([note])
        sequence.append(''.join(m21.chord.Chord(p.pcs.tolist()).pitchNames)+str(np.random.randint(0,octaves)+4))

    return(sequence)

### From an existing score
# __Example__: Bach's chord distribution on a scale-free network built according to the Barabasi-Albert model of preferential attachment

if model == 'score':
    # Read score from file or music21 repository
    score = m21.corpus.parse('bwv267').corpusFilepath
    seq,chords,_ = mk.dictionary(space='score',scorefil=score,music21=True,show=False)
    if randomized:
        bnodes,bedges,_,_,_,_,_ = mk.network(space='score',seq=seq,ntx=True,general=True,distance='euclidean',
                                            grphtype='directed')
        euseq,_,_ = harmonicDesign(mk,len(bnodes),bnodes,bedges,nedges=2,seed=None,reverse=True,display=False,write=False)
    else:
        euseq = seq

### From a probabilistic network distribution (I)
# __Exanple__: probabilistic chord distribution based on voice leading distances on a scale-free network built according to the Barabasi-Albert model of preferential attachment (*operator version*)

if model != 'score':
    # generate initial dictionary of tetrachords
    tetra,_ = mk.dictionary(space='pcs',Nc=4,row=False,order=1,prob=0.15)

if model == 'probI':
    names=['O(1)','O(1,1)','O(1,1,2)','O(1,2)','O(1,1,2,2)','O(1,2,2)','O(1,2,2,2)',
           'O(1,1,3)','O(1,1,1)','O(2,2)']
    probs=[0.25,0.10,0.30,0.25,0.60,0.60,0.80,0.40,0.20,0.20]
    while True:
        enodes, eedges = networkHarmonyGen(mk,descriptor='vLead',dictionary=tetra,names=names,
                                       distance='euclidean',probs=probs,pcslabel=True,write=False)
        try: 
            euseq,_,_ = harmonicDesign(mk,len(enodes),enodes,eedges,nedges=2,seed=None,reverse=True,
                                   display=False,write=False)
            break
        except:
            pass


### From a probabilistic network distribution (II)
# __Exanple__: probabilistic chord distribution based on voice leading distances on a scale-free network built 
# according to the Barabasi-Albert model of preferential attachment (*distance threshold version*)

if model == 'probII':
    while True:
        enodes, eedges = networkHarmonyGen(mk,descriptor='vLead',dictionary=tetra,thup=3.0,thdw=0.1,
                                       distance='euclidean',probs=[0.5],pcslabel=True,write=False)
        try:
            euseq,_,_ = harmonicDesign(mk,len(enodes),enodes,eedges,nedges=2,seed=None,reverse=True,
                                   display=True,write=False,verbose=True)
            break
        except:
            pass


### Assign name and octave to note list
sequence = noteList(euseq,octaves[0])

### Play

# start palyback

#### define the OSC server
# OSC server setup
server = liblo.Server(8001)
def fallback(path, args, types, src):
    global data
    data = path
# register a fallback for unhandled meessages
server.add_method(None, None, fallback)

# Play the sequence - Section I
print('Section I')
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break

# Play the sequence - Section II
print('Section II')
nsection = 6
nclk = -1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,1)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                

# Play the sequence - Section III
print('Section III')
nsection = 4
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,2)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)

# Play the sequence - Section IV
print('Section IV')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0: 
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)
            else:
                panMove(f_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f_fil[p_dict[sequence[nclk%len(sequence)]]],nch,f_mul)

# Play the sequence - Section V
print('Section V')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)
            else:
                panMove(f_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f_fil[p_dict[sequence[nclk%len(sequence)]]],nch,f_mul)

# Play the sequence - Section VI
print('Section VI')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            else:
                panMove(f_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f_fil[p_dict[sequence[nclk%len(sequence)]]],nch,f_mul)

# Play the sequence - Section VII
print('Section VII')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            else:
                panMove(f_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        f_fil[p_dict[sequence[nclk%len(sequence)]]],nch,f_mul)
                jet_obj[np.random.randint(0,len(jet_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)

# Play the sequence - Section VIII
print('Section VIII')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            elif dyn == 1:
                panMove(mf_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf1_obj[mf_dict[sequence[nclk%len(sequence)]]],
                        mf_fil[p_dict[sequence[nclk%len(sequence)]]],nch,mf_mul)
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            else:
                jetn = np.random.randint(0,len(jet_obj))
                panMove(jet_obj[jetn],jet1_obj[jetn],jet_fil[jetn],nch,jet_mul)

# Play the sequence - Section IX
print('Section IX')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                panMove(p_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p1_obj[p_dict[sequence[nclk%len(sequence)]]],
                        p_fil[p_dict[sequence[nclk%len(sequence)]]],nch,p_mul)
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch),
                   delay=np.random.rand()*3)
            elif dyn == 1:
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch))
            else:
                jetn = np.random.randint(0,len(jet_obj))
                panMove(jet_obj[jetn],jet1_obj[jetn],jet_fil[jetn],nch,jet_mul)

# Play the sequence - Section X
print('Section X')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,3)
            if dyn == 0:
                pizz_obj[np.random.randint(0,len(pizz_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch))
            elif dyn == 1:
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch))
            else:
                jetn = np.random.randint(0,len(jet_obj))
                panMove(jet_obj[jetn],jet1_obj[jetn],jet_fil[jetn],nch,jet_mul)

# Play the sequence - Section XI
print('Section XI')
nsection = 1
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,2)
            if dyn == 0:
                jetn = np.random.randint(0,len(jet_obj))
                panMove(jet_obj[jetn],jet1_obj[jetn],jet_fil[jetn],nch,jet_mul)
            elif dyn == 1:
                slap_obj[np.random.randint(0,len(slap_obj))].out(np.random.randint(0,nch),np.random.randint(0,nch))

# Play the sequence - Section XII
print('Section XII')
nsection = 2
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break
        nclk += 1
        if (nclk/nsection%1) == 0:
            dyn = np.random.randint(0,1)
            if dyn == 0:
                jetn = np.random.randint(0,len(jet_obj))
                panMove(jet_obj[jetn],jet1_obj[jetn],jet_fil[jetn],nch,jet_mul)

print('Section XIII')
while True:
    msg = server.recv(100)
    if msg:
        if data == '/stop': break

print('End run')
if record: s.recstop()
server.free()
s.stop()