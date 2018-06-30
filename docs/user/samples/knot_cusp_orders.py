import flipper

for _, row in flipper.census('knots').iterrows():
    stratum = flipper.load(row.surface).mapping_class(row.monodromy).stratum()
    vertex_orders = [stratum[singularity] for singularity in stratum]
    real_vertex_orders = [stratum[singularity] for singularity in stratum if not singularity.filled]
    print('%s (%s over %s) has singularities %s with %s real singularities.' % (row.manifold, row.monodromy, row.surface, vertex_orders, real_vertex_orders))

