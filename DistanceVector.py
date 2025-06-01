#!/usr/bin/env python3
import sys
import math

INF = math.inf

def parse_input():
    nodes = []
    # Read router names until "START"
    for line in sys.stdin:
        tok = line.strip()
        if not tok: continue
        if tok == "START":
            break
        nodes.append(tok)

    edges = []
    # Read initial links until "UPDATE"
    for line in sys.stdin:
        tok = line.strip()
        if not tok: continue
        if tok == "UPDATE":
            break
        u, v, w = tok.split()
        edges.append((u, v, int(w)))

    updates = []
    # Read updates until "END"
    for line in sys.stdin:
        tok = line.strip()
        if not tok: continue
        if tok == "END":
            break
        u, v, w = tok.split()
        updates.append((u, v, int(w)))

    return nodes, edges, updates

def run_dv(nodes, edges):
    # Build adjacency map
    graph = {n: {} for n in nodes}
    for u, v, w in edges:
        graph.setdefault(u, {})[v] = w
        graph.setdefault(v, {})[u] = w

    # Initialize distance tables: dt[x][dest][via]
    dt = {}
    for x in nodes:
        dt[x] = {}
        for dest in nodes:
            if dest == x: continue
            dt[x][dest] = { via: INF for via in nodes if via != x }
        # Fill direct‐link costs
        for nbr, w in graph[x].items():
            if nbr in dt[x]:
                dt[x][nbr][nbr] = w

    # Print t=0 tables
    t = 0
    print_distance_tables(nodes, dt, t)
    t += 1

    # Synchronous rounds until convergence
    while True:
        # Each router advertises D(src, dest) = min_v dt[src][dest][v], and we define D(src, src)=0
        adv = {}
        for src in nodes:
            adv[src] = {}
            for dest in nodes:
                if dest == src:
                    adv[src][dest] = 0
                else:
                    adv[src][dest] = min(dt[src][dest].values())

        updated = False
        # For each router x and each neighbor src, try to improve via src
        for x in nodes:
            for src, cost_x_src in graph[x].items():
                for dest in dt[x]:
                    nc = cost_x_src + adv[src][dest]
                    if nc < dt[x][dest][src]:
                        dt[x][dest][src] = nc
                        updated = True

        if not updated:
            break

        print_distance_tables(nodes, dt, t)
        t += 1

    # Print final routing tables
    print_routing_tables(nodes, dt)

def print_distance_tables(nodes, dt, t):
    for x in sorted(nodes):
        print(f"Distance Table of router {x} at t={t}:")
        others = [n for n in sorted(nodes) if n != x]
        # Header
        print("   " + " ".join(others))
        # Rows
        for dest in others:
            row = [dest]
            for via in others:
                c = dt[x][dest][via]
                row.append(str(int(c)) if c != INF else "INF")
            print("   " + " ".join(row))
        print()

def print_routing_tables(nodes, dt):
    for x in sorted(nodes):
        print(f"Routing Table of router {x}:")
        for dest in sorted(nodes):
            if dest == x:
                continue
            via, cost = min(dt[x][dest].items(), key=lambda kv: kv[1])
            if cost == INF:
                print(f"{dest},INF,INF")
            else:
                print(f"{dest},{via},{int(cost)}")
        print()

def main():
    nodes, edges, updates = parse_input()

    # Run on the original topology
    run_dv(nodes, edges)

    # If there are updates, apply and run again
    if updates:
        for u, v, w in updates:
            # Remove any existing u–v link
            edges = [e for e in edges if not ((e[0]==u and e[1]==v) or (e[0]==v and e[1]==u))]
            # If w >= 0, add/update the link
            if w >= 0:
                edges.append((u, v, w))
            # Include any new nodes
            if u not in nodes:
                nodes.append(u)
            if v not in nodes:
                nodes.append(v)

        run_dv(nodes, edges)

if __name__ == "__main__":
    main()
