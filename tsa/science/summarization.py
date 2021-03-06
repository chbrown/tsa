from viz import gloss, geom
import numpy as np
from sklearn import metrics, cross_validation

from tsa.science import numpy_ext as npx

from tsa import logging
logger = logging.getLogger(__name__)


def metrics_summary(y_true, y_pred, labels=None, pos_label=1, average=None):
    return ', '.join([
        'accuracy: {accuracy:.2%}',
        'P/R: {precision:.4f}/{recall:.4f}',
        'F1: {f1:.4f}',
        # '0-1 loss: {zero_one_loss:.4f}',
    ]).format(**metrics_dict(y_true, y_pred, pos_label=pos_label))


def metrics_dict(y_true, y_pred, labels=None, pos_label=1, average=None):
    prfs_values = metrics.precision_recall_fscore_support(y_true, y_pred,
                                                          labels=labels,
                                                          pos_label=pos_label,
                                                          average=average)
    prfs_keys = ('precision', 'recall', 'f1', 'support')
    accuracy = metrics.accuracy_score(y_true, y_pred)
    # hamming loss is only different from 0-1 loss in multi-label scenarios
    # hamming_loss=metrics.hamming_loss(y_true, y_pred),
    # jaccard_similarity is only different from the accuracy in multi-label scenarios
    # jaccard_similarity=metrics.jaccard_similarity_score(y_true, y_pred),
    # zero_one_loss is (1.0 - accuracy) in multi-label scenarios
    # zero_one_loss=metrics.zero_one_loss(y_true, y_pred),
    return dict(zip(prfs_keys, prfs_values), accuracy=accuracy)


def explore_mispredictions(test_X, test_y, model, test_indices, label_names, documents):
    pred_y = model.predict(test_X)
    for document_index, gold_label, pred_label in zip(test_indices, test_y, pred_y):
        if gold_label != pred_label:
            # print 'certainty: %0.4f' % certainty
            print('gold label (%s=%s) != predicted label (%s=%s)' % (
                gold_label, label_names[gold_label], pred_label, label_names[pred_label]))
            print('Document: %s' % documents[document_index])


def explore_uncertainty(test_X, test_y, model):
    if hasattr(model, 'predict_proba'):
        pred_probabilities = model.predict_proba(test_X)
        # predicts_proba returns N rows, each C-long, where C is the number of labels
        # hmean takes the harmonic mean of its arguments
        pred_probabilities_hmean = np.apply_along_axis(npx.hmean, 1, pred_probabilities)
        pred_certainty = 1 - (2 * pred_probabilities_hmean)
        # pred_certainty now ranges between 0 and 1,
        #   a pred_certainty of 1 means the prediction probabilities were extreme,
        #                       0 means they were near 0.5 each

        # with this, we can use np.array.argmax to get the class names we would have gotten with model.predict()
        # axis=0 will give us the max for each column (not very useful)
        # axis=1 will give us the max for each row (what we want)
        # find best guess (same as model.predict(...), I think)
        pred_y = pred_probabilities.argmax(axis=1)

        print('*: certainty mean=%0.5f' % np.mean(pred_certainty))
        geom.hist(pred_certainty, range=(0, 1))
        print('correct: certainty mean=%0.5f' % np.mean(pred_certainty[pred_y == test_y]))
        geom.hist(pred_certainty[pred_y == test_y], range=(0, 1))
        print('incorrect: certainty mean=%0.5f' % np.mean(pred_certainty[pred_y != test_y]))
        geom.hist(pred_certainty[pred_y != test_y], range=(0, 1))
    else:
        logger.info('predict_proba is unavailable for this model: %s', model)


def explore_topics(topic_model, tokens_per_topic=10):
    # not exactly scikit...
    for topic_i in range(topic_model.num_topics):
        topic = topic_model.show_topic(topic_i, topn=tokens_per_topic)
        ratios, tokens = zip(*topic)
        # terminal.width()
        alignments = list(zip(tokens, ['%0.3f' % ratio for ratio in ratios]))
         # (%0.4f > ratio > %0.4f):' % (, ratios[0], ratios[-1])
        # print ' ', ', '.join(tokens)
        print('Topic %d' % topic_i)
        print(gloss.gloss(alignments, toksep='  ', prefixes=['  ', '  ']))


def average_accuracy(corpus, model, test_size=0.1, n_iter=10):
    folds = cross_validation.StratifiedShuffleSplit(corpus.y, test_size=test_size, n_iter=n_iter)
    accuracies = []
    for train_indices, test_indices in folds:
        train_corpus = corpus.subset(train_indices)
        test_corpus = corpus.subset(test_indices)
        model.fit(train_corpus.X, train_corpus.y)
        pred_y = model.predict(test_corpus.X)
        # pred_proba = model.predict_proba(test_corpus.X)
        accuracy = metrics.accuracy_score(test_corpus.y, pred_y)
        accuracies += [accuracy]
    return np.mean(accuracies)
