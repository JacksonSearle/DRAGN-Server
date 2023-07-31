# DRAGNTown-Server
This is an implementation and expansion of Stanford's paper "Generative Agents: Interactive Simulacra of Human Behavior"(https://arxiv.org/pdf/2304.03442.pdf).
Run main.py to run the server. If there is no game frontend, run move.py to simulate a frontend moving each of the NPC's.

If you are using chatgpt, type this into your terminal so it works: "export OPENAI_API_KEY=<API_KEY>" where <API_KEY> is your actual API key. This will keep your API key seperate from the repository as it will only exist on your system.

At this point, the system does work. It is very very similar to what Stanford described in their paper linked above, with additions for quest generation from user and agent prompting. It makes a lot of API calls and takes a while, but we are working on making it more efficient in the future.
