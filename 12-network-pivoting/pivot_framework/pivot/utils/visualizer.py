def print_topology(pivot_chain, active_forwards):
    """Visualize pivot chain topology"""
    print(f"\n" + "=" * 60)
    print(f"PIVOT CHAIN TOPOLOGY")
    print(f"=" * 60)

    print(f"\n[Attacker]")

    for i, pivot in enumerate(pivot_chain, 1):
        print(f"    |")
        print(f"    v")
        print(f"[{i}] {pivot.name} ({pivot.ip})")
        print(f"    Networks: {', '.join(pivot.networks)}")

    if active_forwards:
        print(f"\n" + "=" * 60)
        print(f"ACTIVE PORT FORWARDS")
        print(f"=" * 60)

        for fwd in active_forwards:
            print(f"\n  localhost:{fwd['local_port']} -> {fwd['pivot']} -> {fwd['target']}")