import numpy as np

from .model import SkipAtomModel
from .trainer import Trainer
from .training_data import TrainingData
from .util import get_atoms, parse_species


class SkipAtomInducedModel:
    def __init__(self, training_data, embeddings):
        self.vectors = embeddings
        self.dictionary = training_data.atom_to_index

    @staticmethod
    def load(model_file, training_data_file, min_count, top_n):
        td = TrainingData.load(training_data_file)
        embeddings = Trainer.load_embeddings(model_file)
        elem_atoms = get_atoms()

        atoms_to_update_count = {}
        for pair in td.data:
            src = pair[0]
            if src not in atoms_to_update_count:
                atoms_to_update_count[src] = 0
            atoms_to_update_count[src] += 1

        for atom, count in atoms_to_update_count.items():
            if count < min_count:
                # update the embedding
                # find 5 most similar atoms
                atom_vector = embeddings[atom]

                elem_atom = elem_atoms[td.index_to_atom[atom]]
                repr_atom = np.array([elem_atom.group, elem_atom.row, elem_atom.X])

                similarities = []
                for i in range(len(embeddings)):
                    if i == atom:
                        continue

                    elem_other = elem_atoms[td.index_to_atom[i]]
                    repr_other = np.array(
                        [elem_other.group, elem_other.row, elem_other.X]
                    )
                    sim = np.linalg.norm(repr_atom - repr_other)

                    similarities.append((embeddings[i], sim, td.index_to_atom[i]))

                # keep the top N most similar
                most_sim = list(sorted(similarities, key=lambda item: item[1]))[:top_n]

                # print(td.index_to_atom[atom])
                # print([i[2] for i in most_sim])

                mean_sim_vector = np.mean(
                    [np.e**-i * m[0] for i, m in enumerate(most_sim)], axis=0
                )
                atom_vector = np.sum([atom_vector, mean_sim_vector], axis=0)

                embeddings[atom] = atom_vector

        return SkipAtomModel(td, embeddings)


class SkipSpeciesInducedModel:
    def __init__(self, training_data, embeddings):
        self.vectors = embeddings
        self.dictionary = training_data.atom_to_index

    @staticmethod
    def load(model_file, training_data_file, min_count, top_n):
        td = TrainingData.load(training_data_file)
        embeddings = Trainer.load_embeddings(model_file)
        elem_atoms = get_atoms()

        species_to_update_count = {}
        for pair in td.data:
            src = pair[0]
            if src not in species_to_update_count:
                species_to_update_count[src] = 0
            species_to_update_count[src] += 1

        for species, count in species_to_update_count.items():
            if count < min_count:
                # update the embedding
                # find 5 most similar atoms
                species_vector = embeddings[species]

                element, oxidation = parse_species(td.index_to_atom[species])

                elem_atom = elem_atoms[element]
                repr_atom = np.array(
                    [elem_atom.group, elem_atom.row, elem_atom.X, oxidation]
                )

                similarities = []
                for i in range(len(embeddings)):
                    if i == species:
                        continue

                    element_other, oxidation_other = parse_species(td.index_to_atom[i])
                    elem_other = elem_atoms[element_other]
                    repr_other = np.array(
                        [
                            elem_other.group,
                            elem_other.row,
                            elem_other.X,
                            oxidation_other,
                        ]
                    )
                    sim = np.linalg.norm(repr_atom - repr_other)

                    similarities.append((embeddings[i], sim, td.index_to_atom[i]))

                # keep the top N most similar
                most_sim = list(sorted(similarities, key=lambda item: item[1]))[:top_n]

                # print(td.index_to_atom[atom])
                # print([i[2] for i in most_sim])

                mean_sim_vector = np.mean(
                    [np.e**-i * m[0] for i, m in enumerate(most_sim)], axis=0
                )
                species_vector = np.sum([species_vector, mean_sim_vector], axis=0)

                embeddings[species] = species_vector

        return SkipAtomModel(td, embeddings)
