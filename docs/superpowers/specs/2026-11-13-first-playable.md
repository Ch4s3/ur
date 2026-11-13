# Ur: first playable

Priority order: (1) a fun game, (2) advance Strata, (3) improve March performance.

Ur is an approachable, serious city simulation with a cute futuristic visual direction, not a cozy decorator or a hardcore metropolitan simulator. The long-term scale is tens of thousands of residents in distinct settlements and neighbourhoods across an island region, with a denser centre. Transport and economics drive private development. Players provide infrastructure/civic buildings, zoning, density and taxes; households and businesses respond to access, income, energy prices and geography. Production emerges rather than being placed by the player. Limited terrain shaping is allowed; no voxel-by-voxel building.

## First slice (implementation decisions)

A compact two-island map, native March app rendered by Strata at 0.25 metres per voxel. Eight-metre planning parcels aggregate simulation independently of voxel detail. Start with a small harbour settlement, money, roads and power. Extend roads/bridges, zone housing or employment, increase permitted density, adjust tax and energy prices, grade vacant land, and observe private growth. Show the cause of blocked development. Pause and speed controls, a measurable population milestone, and a budget make this a game loop.

Use deterministic parcel/household aggregates initially, not tens of thousands of individual actors. A road flood fill establishes actual access to the harbour; adjacency alone is insufficient. Power requires connected capacity. Growth responds to labour/housing balance, costs and accessibility. Buildings grow without manual placement. Terrain and structures use quarter-metre coordinates; no dense allocation of empty voxels.

Deferred: full-region streaming, ferries, individual travel agents, trade chains, public services beyond power, disasters, sophisticated housing markets, final art and save games. These are not claimed complete by the first slice. Benchmark the actual simulation and rendering before modifying March. Engine changes should be reusable and small.

## Alternatives

Transport-only would underplay economics; production-chain micromanagement conflicts with emergent businesses. The selected direction blends transport and economics, with private development and player-owned infrastructure.
