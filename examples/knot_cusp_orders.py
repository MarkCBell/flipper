
import os

import flipper

def from_database(file_name):
	for line in open(os.path.join(os.path.dirname(__file__), file_name)):
		if line:
			yield line.strip().split('\t')

def main():
	for word, surface in from_database('knot_monodromies'):
		print(surface, word)
		S = flipper.examples.abstracttriangulation.SURFACES[surface]()
		mapping_class = S.mapping_class(word)
		splitting_sequence = mapping_class.splitting_sequence()
		lamination = splitting_sequence.laminations[0]
		cusp_stratum_orders = lamination.puncture_stratum_orders()
		corner_classes = lamination.abstract_triangulation.corner_classes
		cusp_numbers = [[triangle.corner_labels[side] for triangle, side in corner_class][0] for corner_class in corner_classes]
		real_cusp_orders = [stratum_order for number, stratum_order in zip(cusp_numbers, cusp_stratum_orders) if number == 0]
		print(real_cusp_orders)

if __name__ == '__main__':
	main()

