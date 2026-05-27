"""
Wumpus World Simulator - interfaccia Python/CLIPS
Uso: python3 wumpus.py -m map.json -a agent.clp [-v]

Mappa JSON:
  size        : dimensione griglia NxN
  wumpus      : [x, y] posizione wumpus (1-indexed)
  pits        : [[x,y], ...] posizioni pit
  gold        : [x, y] posizione oro
  start       : [x, y] posizione iniziale agente
  start_energy: energia iniziale

Azioni valide: up, down, left, right, grab, quit,
               pit-north, pit-south, pit-east, pit-west

Punteggio:
  grab     -> +100 oro
  pit-*    -> +25 se indovina (c'e' un pit in quella direzione), -25 altrimenti
  wall bump -> -1 energia
  wumpus   -> game over
  pit      -> game over
"""

import argparse
import json
import clips


# ---------------------------------------------------------------------------
# Mondo
# ---------------------------------------------------------------------------

class WumpusWorld:
    def __init__(self, cfg: dict):
        self.size     = cfg["size"]
        self.wumpus   = tuple(cfg["wumpus"])
        self.pits     = {tuple(p) for p in cfg["pits"]}
        self.gold_pos = tuple(cfg["gold"])
        self.start    = tuple(cfg["start"])
        self.energy   = cfg.get("start_energy", 200)

        self.pos          = list(self.start)
        self.gold         = 0
        self.steps        = 0
        self.alive        = True
        self.done         = False
        self.wumpus_alive = True
        self.gold_taken   = False

    # Perceptions at current cell
    def perceive(self) -> dict:
        x, y = self.pos
        neighbors = [(x, y+1), (x, y-1), (x+1, y), (x-1, y)]
        breeze  = any(n in self.pits for n in neighbors)
        stench  = self.wumpus_alive and any(n == self.wumpus for n in neighbors)
        glitter = (not self.gold_taken) and tuple(self.pos) == self.gold_pos
        return dict(x=x, y=y, steps=self.steps, breeze=breeze,
                    stench=stench, glitter=glitter, energy=self.energy)

    def _neighbor_in_dir(self, direction: str):
        x, y = self.pos
        return {"up": (x, y+1), "down": (x, y-1),
                "right": (x+1, y), "left": (x-1, y)}[direction]

    def apply_action(self, action: str) -> str:
        x, y = self.pos
        msg = ""

        if action in ("up", "down", "left", "right"):
            nx, ny = self._neighbor_in_dir(action)
            if 1 <= nx <= self.size and 1 <= ny <= self.size:
                self.pos = [nx, ny]
                self.steps += 1
                # Check death
                if tuple(self.pos) in self.pits:
                    self.alive = False
                    self.done  = True
                    msg = f"MORTO: sei caduto in un pozzo in ({nx},{ny})!"
                elif self.wumpus_alive and tuple(self.pos) == self.wumpus:
                    self.alive = False
                    self.done  = True
                    msg = f"MORTO: il Wumpus ti ha mangiato in ({nx},{ny})!"
                else:
                    msg = f"Mosso in ({nx},{ny})"
            else:
                self.energy -= 1
                msg = f"Sbattuto nel muro! Energia -{1} -> {self.energy}"

        elif action == "grab":
            if (not self.gold_taken) and tuple(self.pos) == self.gold_pos:
                self.gold      += 100
                self.gold_taken = True
                msg = "Oro raccolto! +100 oro"
            else:
                msg = "Nessun oro qui."

        elif action in ("pit-north", "pit-south", "pit-east", "pit-west"):
            dir_map = {"pit-north": "up", "pit-south": "down",
                       "pit-east":  "right", "pit-west": "left"}
            target = self._neighbor_in_dir(dir_map[action])
            if target in self.pits:
                self.gold += 25
                msg = f"Indovinate pit in {target}! +25 oro"
            else:
                self.gold -= 25
                msg = f"Nessun pit in {target}. -25 oro"

        elif action == "quit":
            self.done = True
            msg = "Agente uscito."

        else:
            msg = f"Azione sconosciuta: {action}"

        return msg

    def summary(self):
        status = "VIVO" if self.alive else "MORTO"
        return (f"[{status}] Passi={self.steps} Oro={self.gold} "
                f"Energia={self.energy} Pos={tuple(self.pos)}")


# ---------------------------------------------------------------------------
# Bridge CLIPS
# ---------------------------------------------------------------------------

class CLIPSAgent:
    def __init__(self, clp_file: str, verbose: bool = False, grid_size: int = 0):
        self.env     = clips.Environment()
        self.verbose = verbose
        self.env.load(clp_file)
        self.env.reset()
        # Inject grid size so the agent knows the map bounds
        if grid_size > 0:
            for name in ("MAIN::grid-size", "grid-size"):
                try:
                    tmpl = self.env.find_template(name)
                    tmpl.assert_fact(n=grid_size)
                    break
                except Exception:
                    continue
        self.env.run()  # init rules

    def decide(self, percept: dict) -> str:
        """Inietta un percept e ritorna l'azione scelta dall'agente."""
        env = self.env

        # Rimuovi eventuali action rimaste
        for tmpl_name in ("action", "MAIN::action"):
            try:
                tmpl = env.find_template(tmpl_name)
                for f in list(tmpl.facts()):
                    f.retract()
            except clips.LookupError:
                pass

        # Asserisci percept
        try:
            tmpl = env.find_template("MAIN::percept")
        except clips.LookupError:
            tmpl = env.find_template("percept")

        def sym(b): return clips.Symbol("yes") if b else clips.Symbol("no")

        tmpl.assert_fact(
            x=percept["x"],
            y=percept["y"],
            steps=percept["steps"],
            breeze=sym(percept["breeze"]),
            stench=sym(percept["stench"]),
            glitter=sym(percept["glitter"]),
            energy=percept["energy"],
        )

        env.run()

        # Leggi azione
        action = "quit"
        for tmpl_name in ("action", "MAIN::action"):
            try:
                tmpl = env.find_template(tmpl_name)
                for f in tmpl.facts():
                    action = str(f["move"])
                    break
            except clips.LookupError:
                continue

        if self.verbose:
            print(f"  [CLIPS] azione scelta: {action}")

        return action


# ---------------------------------------------------------------------------
# Simulazione principale
# ---------------------------------------------------------------------------

def run(map_file: str, agent_file: str, verbose: bool):
    with open(map_file) as f:
        cfg = json.load(f)

    world = WumpusWorld(cfg)
    agent = CLIPSAgent(agent_file, verbose=verbose, grid_size=cfg["size"])

    print(f"=== Wumpus World ({cfg['size']}x{cfg['size']}) ===")
    print(f"Wumpus: {world.wumpus}  Pit: {world.pits}  Oro: {world.gold_pos}")
    print(f"Inizio: {world.start}  Energia: {world.energy}")
    print()

    max_steps = cfg["size"] ** 2 * 4  # limite ragionevole

    while not world.done and world.steps < max_steps and world.energy > 0:
        percept = world.perceive()
        if verbose:
            print(f"Percept: {percept}")

        action = agent.decide(percept)
        msg    = world.apply_action(action)

        print(f"Step {world.steps:3d} | ({percept['x']},{percept['y']}) "
              f"| azione={action:<12} | {msg}")

        if not world.alive:
            break

    print()
    print("=== FINE PARTITA ===")
    print(world.summary())
    return world.gold if world.alive else 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wumpus World Simulator")
    parser.add_argument("-m", "--map",   required=True, help="File mappa JSON")
    parser.add_argument("-a", "--agent", required=True, help="File agente CLIPS (.clp)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Output verboso")
    args = parser.parse_args()

    score = run(args.map, args.agent, args.verbose)
    print(f"Punteggio finale: {score}")
