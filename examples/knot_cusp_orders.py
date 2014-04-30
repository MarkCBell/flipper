
import flipper
import snappy
from database import from_database

def main():
	for surface, word in from_database('knot_monodromies'):
		print(surface, word)
		S = flipper.examples.abstracttriangulation.SURFACES[surface]()
		mapping_class = S.mapping_class(word)
		splitting_sequence = mapping_class.splitting_sequence()
		lamination = splitting_sequence.laminations[0]
		cusp_stratum_orders = lamination.puncture_stratum_orders()
		corner_classes = lamination.triangulation.corner_classes
		cusp_numbers = [[triangle.corner_labels[side] for triangle, side in corner_class][0] for corner_class in corner_classes]
		real_cusp_orders = [stratum_order for number, stratum_order in zip(cusp_numbers, cusp_stratum_orders) if number == 0]
		print(real_cusp_orders)
		print(cusp_stratum_orders)
		N = snappy.twister.Surface(surface).bundle(word)
		for M in splitting_sequence.snappy_manifolds():
			print(N.volume(), M.volume())
			print(N.chern_simons(), M.chern_simons())
			for i in range(300):
				M.randomize()
				N.randomize()
				if M.is_isometric_to(N):
					print('TRUE')
					break
			else:
				print('False (probably)')

if __name__ == '__main__':
	main()

