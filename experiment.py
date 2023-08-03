import random

config = 'random' #random, randcycle, setcycle, ordered. 
#i.e. completely random, pick each of the four states in random order, pick each of the four states in set order, and do each of the four states max_trials/4 times in a row.
i = 0
max_trials = 20
agent_coherence, use_intention = True, True
states = []
if config == 'ordered' and max_trials%4!=0: max_trials += 4-(max_trials%4) #require max_trials to be a multiple of 4

def increment_test():
    global i, max_trials, agent_coherence, use_intention, states, config
    if i>=max_trials: return True, True

    if config == 'random': agent_coherence, use_intention = random.randint(0,1),random.randint(0,1)
    elif config == 'randcycle':
        if len(states)==0: states = [(False,False), (False,True), (True,False), (True,True)]
        agent_coherence, use_intention = states[random.randint(0,len(states)-1)]
        states.remove((agent_coherence, use_intention))
    elif config == 'setcycle':
        use_intention = not use_intention
        if i%2==0: agent_coherence = not agent_coherence
    elif config == 'ordered':
        if i%(max_trials/4)==0: use_intention = not use_intention
        if i%(max_trials/2)==0: agent_coherence = not agent_coherence

    i+=1
    print(agent_coherence, use_intention)
    return agent_coherence, use_intention