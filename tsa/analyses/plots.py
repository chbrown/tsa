import IPython
import numpy as np

from tsa import logging
from tsa.data.sb5b.tweets import read_MulticlassCorpus as read_sb5b_MulticlassCorpus
from tsa.lib import datetime_extra
from tsa.science import numpy_ext as npx
from tsa.science import features, plot, timeseries
from tsa.science.plot import plt

logger = logging.getLogger(__name__)


def plot_hashtag_volumes(analysis_options):
    '''
    This will plot the hashtag volumes of the top 100 hashtags over the course of the corpus
    '''
    corpus = read_sb5b_MulticlassCorpus()
    logger.info('Loaded corpus: %s', corpus.X.shape)

    labeled_mask = (corpus.y == corpus.labels['Against']) | (corpus.y == corpus.labels['For'])
    labeled_indices = npx.bool_mask_to_indices(labeled_mask)
    # n_iter = 100
    # coefs = bootstrap_model(X[labeled_indices], y[labeled_indices],
    #     n_iter=n_iter, proportion=0.5)
    # coefs_means = np.mean(coefs, axis=0)
    # coefs_variances = np.var(coefs, axis=0)

    added_indices = corpus.apply_features(corpus.documents, features.hashtags)
    print('After extracting hashtags: %s' % corpus.X.shape)

    # 1. full set of data
    X = corpus.X.tocsr()
    feature_names = corpus.feature_names

    # 2. subset into just the hashtag columns
    X = X[:, added_indices]
    feature_names = feature_names[added_indices]

    # window = 7
    # alpha = .5

    labeled_edges = np.array(npx.bounds(corpus.times[labeled_indices]))
    from tsa.data.sb5b import notable_dates


    def plot_selection(X, feature_names):
        '''Just a helper function to scope better'''
        # binned_statistic doesn't play nice with sparse arrays, so fix that here
        X = X.toarray()
        #
        hashtags_bin_edges, hashtags_bins = timeseries.binned_timeseries(
            corpus.times, X, time_units_per_bin=7, time_unit='D', statistic='sum')
            # corpus.times, X, time_units_per_bin=1, time_unit='M', statistic='sum')
        #
        # hashtags_bins = hashtags_bins / hashtags_bins.sum(axis=0)  # normalize per feature
        # suited to plt.stackplot?
        hashtags_bins = hashtags_bins / hashtags_bins.sum(axis=1, keepdims=True)  # normalize per bin
        #
        # plt.scatter(totals, coefs_means, alpha=0.3)
        # selection = order[:10]
        logger.info('Top %d: %r', len(feature_names), feature_names)
        #
        # def add_lines(corpus, selection, window=7, alpha=.5, time_units_per_bin=1, time_unit='D'):
        style_iter = plots.style_loop()
        plt.cla()
        plt.stackplot(hashtags_bin_edges.astype(float), hashtags_bins.T, baseline='sym')

        # baseline : zero, sym, wiggle, weighted_wiggle
        # for feature, feature_name in enumerate(feature_names):
        #     bin_values = hashtags_bins[:, feature]
        #     # bin_values = npx.exponential_decay(bin_values, window=window, alpha=alpha)
        #     style_kwargs = style_iter.next()
        #     plt.plot(hashtags_bin_edges, bin_values, label=feature_name, **style_kwargs)
        #
        axes = plt.gca()
        axes.xaxis.set_major_formatter(plot.ticker.FuncFormatter(datetime_extra.datetime64_formatter))
        plt.legend(loc='upper left')
        #
        # plot the first and last of the labeled data
        auto_ylim = plt.ylim()
        plt.vlines(labeled_edges.astype(float), *auto_ylim, colors='c')
        plt.vlines(notable_dates.astype(float), *auto_ylim)
        plt.ylim(*auto_ylim)

    # 3. subset into just the top features
    # np.sum doesn't handle sparse arrays
    column_sums = X.sum(axis=0).A.ravel()
    most_popular_features_indices = np.argsort(-column_sums)

    selected_indices = most_popular_features_indices[np.arange(10) + 5]
    plot_selection(X[:, selected_indices], feature_names[selected_indices])
    X = X[:, selected_indices]
    feature_names = feature_names[selected_indices]

    exit(IPython.embed())

    # plt.title('Coefficient variances converging across a %d-iteration bootstrap\n(25 highest and 25 lowest variances)' % subset.shape[0])
