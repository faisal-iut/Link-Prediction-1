"""
@author: Fangshu Gao <gaofangshu@foxmail.com>
@brief: prepare data and features
"""

import csv
import random
import numpy as np
import nltk
import sys
import time
from utils import ngram_utils, dist_utils, np_utils

DIR_TRIAN = "social_train.txt"
DIR_TEST = "social_test.txt"
DIR_NODEINFO = "node_information.csv"

# nltk.download('punkt')  # for tokenization
# nltk.download('stopwords')
STPWDS = set(nltk.corpus.stopwords.words("english"))


class Data():
    def __init__(self, sample):
        assert type(sample) == bool
        self.stemmer = nltk.stem.PorterStemmer()
        # the columns of the node data frame below are:
        # (0) paper unique ID (integer)
        # (1) publication year (integer)
        # (2) paper title (string)
        # (3) authors (strings separated by ,)
        # (4) name of journal (optional) (string)
        # (5) abstract (string) - lowercased, free of punctuation except intra-word dashes

        data_train = self.load_data(DIR_TRIAN)
        data_test = self.load_data(DIR_TEST)
        data_node_info = self.load_data(DIR_NODEINFO)

        self.data_tkzd_title = []
        self.data_tkzd_title_rm_stpwds = []
        self.data_tkzd_title_rm_stpwds_stem = []
        self.data_tkzd_abstract = []
        self.data_tkzd_abstract_rm_stpwds = []
        self.data_tkzd_abstract_rm_stpwds_stem = []

        if sample:
            # to test code we select sample
            to_keep = random.sample(range(len(data_train)), k=int(round(len(data_train) * 0.01)))
            data_train_keep = [data_train[i] for i in to_keep]
            self.training_set = self.split_to_list(data_train_keep)
        else:
            self.training_set = self.split_to_list(data_train)

        # valid_ids = self.get_valid_ids(self.training_set)

        self.testing_set = self.split_to_list(data_test)
        # self.node_info_set = [element for element in data_node_info if element[0] in valid_ids]
        self.node_info_set = data_node_info
        self.node_position = self.add_position(self.node_info_set)  # {paperID : rowID in self.node_info_set}

        self.prepare_data()
        self.feature = None

    def get_features(self):
        # distance features from self.data_tkzd_title
        fea_jaccard_tkzd_title = []
        fea_dice_tkzd_title = []
        fea_jaccard_bigr_tkzd_title = []
        fea_dice_bigr_tkzd_title = []

        fea_jaccard_tkzd_title_rm_stpwds = []
        fea_dice_tkzd_title_rm_stpwds = []
        fea_jaccard_bigr_tkzd_title_rm_stpwds = []
        fea_dice_bigr_tkzd_title_rm_stpwds = []

        # distance features from self.data_tkzd_abstract
        fea_jaccard_tkzd_abstract = []
        fea_jaccard_bigr_tkzd_abstract = []
        fea_jaccard_trigr_tkzd_abstract = []
        fea_jaccard_fourgr_tkzd_abstract = []
        fea_jaccard_bitm_tkzd_abstract = []
        fea_jaccard_tritm_tkzd_abstract = []
        fea_jaccard_fourtm_tkzd_abstract = []

        fea_dice_tkzd_abstract = []
        fea_dice_bigr_tkzd_abstract = []
        fea_dice_trigr_tkzd_abstract = []
        fea_dice_fourgr_tkzd_abstract = []
        fea_dice_bitm_tkzd_abstract = []
        fea_dice_tritm_tkzd_abstract = []
        fea_dice_fourtm_tkzd_abstract = []

        # distance features from self.data_tkzd_abstract_rm_stpwds
        fea_jaccard_tkzd_abstract_rm_stpwds = []
        fea_jaccard_bigr_tkzd_abstract_rm_stpwds = []
        fea_jaccard_trigr_tkzd_abstract_rm_stpwds = []
        fea_jaccard_fourgr_tkzd_abstract_rm_stpwds = []
        fea_jaccard_bitm_tkzd_abstract_rm_stpwds = []
        fea_jaccard_tritm_tkzd_abstract_rm_stpwds = []
        fea_jaccard_fourtm_tkzd_abstract_rm_stpwds = []

        fea_dice_tkzd_abstract_rm_stpwds = []
        fea_dice_bigr_tkzd_abstract_rm_stpwds = []
        fea_dice_trigr_tkzd_abstract_rm_stpwds = []
        fea_dice_fourgr_tkzd_abstract_rm_stpwds = []
        fea_dice_bitm_tkzd_abstract_rm_stpwds = []
        fea_dice_tritm_tkzd_abstract_rm_stpwds = []
        fea_dice_fourtm_tkzd_abstract_rm_stpwds = []

        counter = 0
        size = len(self.training_set)

        for i in range(size):
            source = self.training_set[i][0]  # id of source paper
            target = self.training_set[i][1]  # id of target paper
            pos_source = self.node_position[source]
            pos_target = self.node_position[target]

            # features from self.data_tkzd_title
            obs_tkzd_title_source = self.data_tkzd_title[pos_source]
            obs_tkzd_title_target = self.data_tkzd_title[pos_target]
            bigrams_tkzd_title_source = ngram_utils._ngrams(obs_tkzd_title_source, 2)
            bigrams_tkzd_title_target = ngram_utils._ngrams(obs_tkzd_title_target, 2)

            jaccard_tkzd_title = dist_utils._jaccard_coef(obs_tkzd_title_source, obs_tkzd_title_target)
            dice_tkzd_title = dist_utils._dice_dist(obs_tkzd_title_source, obs_tkzd_title_target)
            jaccard_bigr_tkzd_title = dist_utils._jaccard_coef(bigrams_tkzd_title_source, bigrams_tkzd_title_target)
            dice_bigr_tkzd_title = dist_utils._dice_dist(bigrams_tkzd_title_source, bigrams_tkzd_title_target)

            fea_jaccard_tkzd_title.append(jaccard_tkzd_title)
            fea_dice_tkzd_title.append(dice_tkzd_title)
            fea_jaccard_bigr_tkzd_title.append(jaccard_bigr_tkzd_title)
            fea_dice_bigr_tkzd_title.append(dice_bigr_tkzd_title)

            # features from self.data_tkzd_title_rm_stpwds
            obs_tkzd_title_rm_stpwds_source = self.data_tkzd_title_rm_stpwds[pos_source]
            obs_tkzd_title_rm_stpwds_target = self.data_tkzd_title_rm_stpwds[pos_target]
            bigrams_tkzd_title_rm_stpwds_source = ngram_utils._ngrams(obs_tkzd_title_rm_stpwds_source, 2)
            bigrams_tkzd_title_rm_stpwds_target = ngram_utils._ngrams(obs_tkzd_title_rm_stpwds_target, 2)

            jaccard_tkzd_title_rm_stpwds = dist_utils._jaccard_coef(obs_tkzd_title_rm_stpwds_source,
                                                                    obs_tkzd_title_rm_stpwds_target)
            dice_tkzd_title_rm_stpwds = dist_utils._dice_dist(obs_tkzd_title_rm_stpwds_source,
                                                              obs_tkzd_title_rm_stpwds_target)
            jaccard_bigr_tkzd_title_rm_stpwds = dist_utils._jaccard_coef(bigrams_tkzd_title_rm_stpwds_source,
                                                                         bigrams_tkzd_title_rm_stpwds_target)
            dice_bigr_tkzd_title_rm_stpwds = dist_utils._dice_dist(bigrams_tkzd_title_rm_stpwds_source,
                                                                   bigrams_tkzd_title_rm_stpwds_target)

            fea_jaccard_tkzd_title_rm_stpwds.append(jaccard_tkzd_title_rm_stpwds)
            fea_dice_tkzd_title_rm_stpwds.append(dice_tkzd_title_rm_stpwds)
            fea_jaccard_bigr_tkzd_title_rm_stpwds.append(jaccard_bigr_tkzd_title_rm_stpwds)
            fea_dice_bigr_tkzd_title_rm_stpwds.append(dice_bigr_tkzd_title_rm_stpwds)

            # TODO: # features from self.data_tkzd_title_rm_stpwds

            # features from self.data_tkzd_abstract
            obs_tkzd_abstract_source = self.data_tkzd_abstract[pos_source]
            obs_tkzd_abstract_target = self.data_tkzd_abstract[pos_target]
            bigrams_tkzd_abstract_source = ngram_utils._ngrams(obs_tkzd_abstract_source, 2)
            bigrams_tkzd_abstract_target = ngram_utils._ngrams(obs_tkzd_abstract_target, 2)
            trigrams_tkzd_abstract_source = ngram_utils._ngrams(obs_tkzd_abstract_source, 3)
            trigrams_tkzd_abstract_target = ngram_utils._ngrams(obs_tkzd_abstract_target, 3)
            fourgrams_tkzd_abstract_source = ngram_utils._ngrams(obs_tkzd_abstract_source, 4)
            fourgrams_tkzd_abstract_target = ngram_utils._ngrams(obs_tkzd_abstract_target, 4)

            biterms_tkzd_abstract_source = ngram_utils._nterms(obs_tkzd_abstract_source, 2)
            biterms_tkzd_abstract_target = ngram_utils._nterms(obs_tkzd_abstract_target, 2)
            triterms_tkzd_abstract_source = ngram_utils._nterms(obs_tkzd_abstract_source, 3)
            triterms_tkzd_abstract_target = ngram_utils._nterms(obs_tkzd_abstract_target, 3)
            fourterms_tkzd_abstract_source = ngram_utils._nterms(obs_tkzd_abstract_source, 4)
            fourterms_tkzd_abstract_target = ngram_utils._nterms(obs_tkzd_abstract_target, 4)

            jaccard_tkzd_abstract = dist_utils._jaccard_coef(obs_tkzd_abstract_source, obs_tkzd_abstract_target)
            jaccard_bigr_tkzd_abstract = dist_utils._jaccard_coef(bigrams_tkzd_abstract_source,
                                                                  bigrams_tkzd_abstract_target)
            jaccard_trigr_tkzd_abstract = dist_utils._jaccard_coef(trigrams_tkzd_abstract_source,
                                                                   trigrams_tkzd_abstract_target)
            jaccard_fourgr_tkzd_abstract = dist_utils._jaccard_coef(fourgrams_tkzd_abstract_source,
                                                                    fourgrams_tkzd_abstract_target)
            jaccard_bitm_tkzd_abstract = dist_utils._jaccard_coef(biterms_tkzd_abstract_source,
                                                                  biterms_tkzd_abstract_target)
            jaccard_tritm_tkzd_abstract = dist_utils._jaccard_coef(triterms_tkzd_abstract_source,
                                                                   triterms_tkzd_abstract_target)
            jaccard_fourtm_tkzd_abstract = dist_utils._jaccard_coef(fourterms_tkzd_abstract_source,
                                                                    fourterms_tkzd_abstract_target)

            dice_tkzd_abstract = dist_utils._dice_dist(obs_tkzd_abstract_source, obs_tkzd_abstract_target)
            dice_bigr_tkzd_abstract = dist_utils._dice_dist(bigrams_tkzd_abstract_source, bigrams_tkzd_abstract_target)
            dice_trigr_tkzd_abstract = dist_utils._dice_dist(trigrams_tkzd_abstract_source,
                                                             trigrams_tkzd_abstract_target)
            dice_fourgr_tkzd_abstract = dist_utils._dice_dist(fourgrams_tkzd_abstract_source,
                                                              fourgrams_tkzd_abstract_target)
            dice_bitm_tkzd_abstract = dist_utils._dice_dist(biterms_tkzd_abstract_source, biterms_tkzd_abstract_target)
            dice_tritm_tkzd_abstract = dist_utils._dice_dist(triterms_tkzd_abstract_source,
                                                             triterms_tkzd_abstract_target)
            dice_fourtm_tkzd_abstract = dist_utils._dice_dist(fourterms_tkzd_abstract_source,
                                                              fourterms_tkzd_abstract_target)

            fea_jaccard_tkzd_abstract.append(jaccard_tkzd_abstract)
            fea_jaccard_bigr_tkzd_abstract.append(jaccard_bigr_tkzd_abstract)
            fea_jaccard_trigr_tkzd_abstract.append(jaccard_trigr_tkzd_abstract)
            fea_jaccard_fourgr_tkzd_abstract.append(jaccard_fourgr_tkzd_abstract)
            fea_jaccard_bitm_tkzd_abstract.append(jaccard_bitm_tkzd_abstract)
            fea_jaccard_tritm_tkzd_abstract.append(jaccard_tritm_tkzd_abstract)
            fea_jaccard_fourtm_tkzd_abstract.append(jaccard_fourtm_tkzd_abstract)

            fea_dice_tkzd_abstract.append(dice_tkzd_abstract)
            fea_dice_bigr_tkzd_abstract.append(dice_bigr_tkzd_abstract)
            fea_dice_trigr_tkzd_abstract.append(dice_trigr_tkzd_abstract)
            fea_dice_fourgr_tkzd_abstract.append(dice_fourgr_tkzd_abstract)
            fea_dice_bitm_tkzd_abstract.append(dice_bitm_tkzd_abstract)
            fea_dice_tritm_tkzd_abstract.append(dice_tritm_tkzd_abstract)
            fea_dice_fourtm_tkzd_abstract.append(dice_fourtm_tkzd_abstract)

            # features from self.data_tkzd_abstract_rm_stpwds
            obs_tkzd_abstract_rm_stpwds_source = self.data_tkzd_abstract[pos_source]
            obs_tkzd_abstract_rm_stpwds_target = self.data_tkzd_abstract[pos_target]
            bigrams_tkzd_abstract_rm_stpwds_source = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_source, 2)
            bigrams_tkzd_abstract_rm_stpwds_target = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_target, 2)
            trigrams_tkzd_abstract_rm_stpwds_source = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_source, 3)
            trigrams_tkzd_abstract_rm_stpwds_target = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_target, 3)
            fourgrams_tkzd_abstract_rm_stpwds_source = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_source, 4)
            fourgrams_tkzd_abstract_rm_stpwds_target = ngram_utils._ngrams(obs_tkzd_abstract_rm_stpwds_target, 4)

            biterms_tkzd_abstract_rm_stpwds_source = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_source, 2)
            biterms_tkzd_abstract_rm_stpwds_target = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_target, 2)
            triterms_tkzd_abstract_rm_stpwds_source = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_source, 3)
            triterms_tkzd_abstract_rm_stpwds_target = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_target, 3)
            fourterms_tkzd_abstract_rm_stpwds_source = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_source, 4)
            fourterms_tkzd_abstract_rm_stpwds_target = ngram_utils._nterms(obs_tkzd_abstract_rm_stpwds_target, 4)

            jaccard_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(obs_tkzd_abstract_rm_stpwds_source,
                                                                       obs_tkzd_abstract_rm_stpwds_target)
            jaccard_bigr_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(bigrams_tkzd_abstract_rm_stpwds_source,
                                                                            bigrams_tkzd_abstract_rm_stpwds_target)
            jaccard_trigr_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(trigrams_tkzd_abstract_rm_stpwds_source,
                                                                             trigrams_tkzd_abstract_rm_stpwds_target)
            jaccard_fourgr_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(fourgrams_tkzd_abstract_rm_stpwds_source,
                                                                              fourgrams_tkzd_abstract_rm_stpwds_target)
            jaccard_bitm_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(biterms_tkzd_abstract_rm_stpwds_source,
                                                                            biterms_tkzd_abstract_rm_stpwds_target)
            jaccard_tritm_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(triterms_tkzd_abstract_rm_stpwds_source,
                                                                             triterms_tkzd_abstract_rm_stpwds_target)
            jaccard_fourtm_tkzd_abstract_rm_stpwds = dist_utils._jaccard_coef(fourterms_tkzd_abstract_rm_stpwds_source,
                                                                              fourterms_tkzd_abstract_rm_stpwds_target)

            dice_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(obs_tkzd_abstract_rm_stpwds_source,
                                                                 obs_tkzd_abstract_rm_stpwds_target)
            dice_bigr_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(bigrams_tkzd_abstract_rm_stpwds_source,
                                                                      bigrams_tkzd_abstract_rm_stpwds_target)
            dice_trigr_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(trigrams_tkzd_abstract_rm_stpwds_source,
                                                                       trigrams_tkzd_abstract_rm_stpwds_target)
            dice_fourgr_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(fourgrams_tkzd_abstract_rm_stpwds_source,
                                                                        fourgrams_tkzd_abstract_rm_stpwds_target)
            dice_bitm_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(biterms_tkzd_abstract_rm_stpwds_source,
                                                                      biterms_tkzd_abstract_rm_stpwds_target)
            dice_tritm_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(triterms_tkzd_abstract_rm_stpwds_source,
                                                                       triterms_tkzd_abstract_rm_stpwds_target)
            dice_fourtm_tkzd_abstract_rm_stpwds = dist_utils._dice_dist(fourterms_tkzd_abstract_rm_stpwds_source,
                                                                        fourterms_tkzd_abstract_rm_stpwds_target)

            fea_jaccard_tkzd_abstract_rm_stpwds.append(jaccard_tkzd_abstract_rm_stpwds)
            fea_jaccard_bigr_tkzd_abstract_rm_stpwds.append(jaccard_bigr_tkzd_abstract_rm_stpwds)
            fea_jaccard_trigr_tkzd_abstract_rm_stpwds.append(jaccard_trigr_tkzd_abstract_rm_stpwds)
            fea_jaccard_fourgr_tkzd_abstract_rm_stpwds.append(jaccard_fourgr_tkzd_abstract_rm_stpwds)
            fea_jaccard_bitm_tkzd_abstract_rm_stpwds.append(jaccard_bitm_tkzd_abstract_rm_stpwds)
            fea_jaccard_tritm_tkzd_abstract_rm_stpwds.append(jaccard_tritm_tkzd_abstract_rm_stpwds)
            fea_jaccard_fourtm_tkzd_abstract_rm_stpwds.append(jaccard_fourtm_tkzd_abstract_rm_stpwds)

            fea_dice_tkzd_abstract_rm_stpwds.append(dice_tkzd_abstract_rm_stpwds)
            fea_dice_bigr_tkzd_abstract_rm_stpwds.append(dice_bigr_tkzd_abstract_rm_stpwds)
            fea_dice_trigr_tkzd_abstract_rm_stpwds.append(dice_trigr_tkzd_abstract_rm_stpwds)
            fea_dice_fourgr_tkzd_abstract_rm_stpwds.append(dice_fourgr_tkzd_abstract_rm_stpwds)
            fea_dice_bitm_tkzd_abstract_rm_stpwds.append(dice_bitm_tkzd_abstract_rm_stpwds)
            fea_dice_tritm_tkzd_abstract_rm_stpwds.append(dice_tritm_tkzd_abstract_rm_stpwds)
            fea_dice_fourtm_tkzd_abstract_rm_stpwds.append(dice_fourtm_tkzd_abstract_rm_stpwds)

            # TODO: # features from self.data_tkzd_abstract_rm_stpwds_stem

            counter += 1

            if counter % 10 == 0:
                sys.stdout.write("\rPreparing features: %.1f%%" % (100 * counter / size))
                sys.stdout.flush()

        self.feature = np.array([fea_jaccard_tkzd_title,
                                 fea_dice_tkzd_title,
                                 fea_jaccard_bigr_tkzd_title,
                                 fea_dice_bigr_tkzd_title,
                                 fea_jaccard_tkzd_title_rm_stpwds,
                                 fea_dice_tkzd_title_rm_stpwds,
                                 fea_jaccard_bigr_tkzd_title_rm_stpwds,
                                 fea_dice_bigr_tkzd_title_rm_stpwds,
                                 fea_jaccard_tkzd_abstract,
                                 fea_jaccard_bigr_tkzd_abstract,
                                 fea_jaccard_trigr_tkzd_abstract,
                                 fea_jaccard_fourgr_tkzd_abstract,
                                 fea_jaccard_bitm_tkzd_abstract,
                                 fea_jaccard_tritm_tkzd_abstract,
                                 fea_jaccard_fourtm_tkzd_abstract,
                                 fea_dice_tkzd_abstract,
                                 fea_dice_bigr_tkzd_abstract,
                                 fea_dice_trigr_tkzd_abstract,
                                 fea_dice_fourgr_tkzd_abstract,
                                 fea_dice_bitm_tkzd_abstract,
                                 fea_dice_tritm_tkzd_abstract,
                                 fea_dice_fourtm_tkzd_abstract,
                                 fea_jaccard_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_bigr_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_trigr_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_fourgr_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_bitm_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_tritm_tkzd_abstract_rm_stpwds,
                                 fea_jaccard_fourtm_tkzd_abstract_rm_stpwds,
                                 fea_dice_tkzd_abstract_rm_stpwds,
                                 fea_dice_bigr_tkzd_abstract_rm_stpwds,
                                 fea_dice_trigr_tkzd_abstract_rm_stpwds,
                                 fea_dice_fourgr_tkzd_abstract_rm_stpwds,
                                 fea_dice_bitm_tkzd_abstract_rm_stpwds,
                                 fea_dice_tritm_tkzd_abstract_rm_stpwds,
                                 fea_dice_fourtm_tkzd_abstract_rm_stpwds]).T

    def load_data(self, dir):
        assert type(dir) == str
        with open(dir, "r") as f:
            data = list(csv.reader(f))
        return data

    def get_valid_ids(self, data):
        assert type(dir) == list
        valid_ids = set()
        for element in data:
            valid_ids.add(element[0])
            valid_ids.add(element[1])
        return valid_ids

    def split_to_list(self, data, by=" "):
        assert type(data) == list
        return [element[0].split(by) for element in data]

    def add_position(self, data):
        assert type(data) == list
        ids = []
        position = {}
        for element in data:
            position[element[0]] = len(ids)
            ids.append(element[0])
        return position

    def add_feature(self, feature):
        pass

    def prepare_data(self):
        counter = 0
        size = len(self.node_info_set)
        for i in range(size):

            # title
            # convert to lowercase and tokenize
            tkzd_title = self.node_info_set[i][2].lower().split(" ")
            self.data_tkzd_title.append(tkzd_title)
            # remove stopwords
            tkzd_title_rm_stpwds = [token for token in tkzd_title if token not in STPWDS]
            self.data_tkzd_title_rm_stpwds.append(tkzd_title_rm_stpwds)
            # convert to root or original word
            tkzd_title_rm_stpwds_stem = [self.stemmer.stem(token) for token in tkzd_title_rm_stpwds]
            self.data_tkzd_title_rm_stpwds_stem.append(tkzd_title_rm_stpwds_stem)

            # authors
            authors = self.node_info_set[i][3].split(",")
            self.data_authors = authors

            # journal name
            # TODO: self.node_info_set[i][4]

            # abstract
            # convert to lowercase and tokenize
            tkzd_abstract = self.node_info_set[i][5].lower().split(" ")
            self.data_tkzd_abstract.append(tkzd_abstract)
            # remove stopwords
            tkzd_abstract_rm_stpwds = [token for token in tkzd_abstract if token not in STPWDS]
            self.data_tkzd_abstract_rm_stpwds.append(tkzd_abstract_rm_stpwds)
            # convert to root or original word
            tkzd_abstract_rm_stpwds_stem = [self.stemmer.stem(token) for token in tkzd_abstract_rm_stpwds]
            self.data_tkzd_abstract_rm_stpwds_stem.append(tkzd_abstract_rm_stpwds_stem)

            counter += 1

            if counter % 1000 == 0:
                sys.stdout.write("\rPreparing data: %.1f%%" % (100 * counter / size))
                sys.stdout.flush()

    def get_observation(self):
        # get observation from self.node_info_set
        # TODO: delete or not?
        pass


if __name__ == '__main__':
    data = Data(sample=True)
    data.get_features()
    print('')
