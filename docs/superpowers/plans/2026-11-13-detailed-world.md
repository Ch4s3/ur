# Detailed voxel world

User correction: the initial art is too lo-fi. Deliver detailed three-dimensional
voxel buildings and environments in the running game, not a concept image.
Keep the existing simulation and controls. No approval pause (user preference).

- Replace simple building slabs with layered procedural architecture: realistic
  floor heights, pitched roofs, framed windows, balconies, entrances, cornices,
  rooftop solar, shopfronts and civic machinery. Geometry uses quarter-metre voxels.
- Decouple visible terrain from 8 m parcel terraces. Sample sub-metre contours,
  add material variation, layered rocks, denser vegetation and shoreline detail.
  Construction gets foundations and retaining edges that fit the landscape.
- Upload actual voxel occupancy to Strata lighting; enable directional shadows,
  ambient shading and material response instead of flat preview lighting.
- Add an orbiting three-quarter camera and close zoom; keep picking consistent
  with the new projection and geometry. Default to a useful neighbourhood view.
- Test geometry bounds, terrain continuity, picking, and existing simulation;
  render and inspect neighbourhood and region screenshots before completion.
