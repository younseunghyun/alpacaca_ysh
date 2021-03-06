import re
import random
from collections import Counter
import time
import math
import pickle 

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F

class LineGenerator():

    def __init__(self, model, data_reader, max_length=20):

        self.rnn = model
        self.data_reader = data_reader
        self.max_length = max_length

    # Sample from a category and starting letter
    def sample(self, start_letter='A'):
        input = Variable(self.data_reader.inputTensor(start_letter))
        hidden = self.rnn.initHidden()

        output_name = start_letter

        for i in range(self.max_length):
            output, hidden = self.rnn(input[0], hidden)
            topv, topi = output.data.topk(1)
            topi = topi[0][0]
            if topi == 0:
                break
            else:
                letter = self.data_reader.idx2word[topi]
                output_name += letter
            input = Variable(self.data_reader.inputTensor(letter))

        return output_name

    # Get multiple samples from one category and multiple starting letters
    def samples(self, start_letters='ABC'):
        results = []
        for start_letter in start_letters:
            results.append(self.sample(start_letter))
        return results

class LineSampleGenerator():

    def __init__(self, model, data_reader, max_length=20):

        self.rnn = model
        self.data_reader = data_reader
        self.max_length = max_length

    # Sample from a category and starting letter
    def sample(self, start_letter='A'):
        start_word = random.choice([key for key in self.data_reader.word2idx.keys() if key[0][0] == start_letter])
        input = Variable(self.data_reader.inputTensor(start_letter))
        hidden = self.rnn.initHidden()

        output_name = start_word[0]

        for i in range(self.max_length):
            output, hidden = self.rnn(input[0], hidden)
            # topv, topi = output.data.topk(1)
            # topi = topi[0][0]
            tt = output.data.topk(10)
            topi = tt[1].numpy()[0][np.random.randint(len(tt[0][0]))]
            if topi == 0:
                break
            else:
                letter = self.data_reader.idx2word[topi]
                output_name = output_name + ' ' + letter[0]
            input = Variable(self.data_reader.inputTensor(letter))

        return output_name

    # Get multiple samples from one category and multiple starting letters
    def samples(self, start_letters='ABC'):
        results = []
        for start_letter in start_letters:
            results.append(self.sample(start_letter))
        return results


class LineEmbeddingGenerator():

    def __init__(self, model, dataloader, embedding, vector_size, max_length=20):

        self.rnn = model
        self.dataloader = dataloader
        self.embedding = embedding
        self.max_length = max_length
        self.vector_size = vector_size

    # Sample from a category and starting letter
    def sample(self, start_letter='A'):
        start_word = random.choice([key for key in self.embedding.vocab.keys() if key[0] == start_letter])
        input = (self.embedding[start_word] if word in self.embedding.vocab else self.unknown)
        self.rnn.hidden = self.rnn.init_hidden()

        output_name = start_word

        for i in range(self.max_length):
            output, hidden = self.rnn(input.view(1, -1, self.vector_size), hidden)
            # topv, topi = output.data.topk(1)
            # topi = topi[0][0]
            tt = output.data.topk(10)
            topi = tt[1].numpy()[0][np.random.randint(len(tt[0][0]))]
            if topi == 0:
                break
            else:
                letter = self.dataloader.idx2word[topi]
                output_name = output_name + ' ' + letter[0]
            input = Variable(self.dataloader.inputTensor(letter))

        return output_name

    # Get multiple samples from one category and multiple starting letters
    def samples(self, start_letters='ABC'):
        results = []
        for start_letter in start_letters:
            results.append(self.sample(start_letter))
        return results



class LineLstmEmbeddingGenerator():
    def __init__(self, model, dataloader, embedding, vector_size, max_length=20):

        self.rnn = model
        self.dataloader = dataloader
        self.embedding = embedding
        self.max_length = max_length
        self.vector_size = vector_size

    # Sample from a category and starting letter
    def sample(self, start_letter='A'):
        for letter in start_letter:
            start_word = random.choice([key for key in self.embedding.vocab if key[0] == letter])
            print(self.generateLine(start_word))

    def generateLine(self, seedWord):
        inputWordVec = (self.embedding.model.wv[seedWord] if seedWord in self.embedding.vocab else self.unknown)

        output_name = seedWord

        self.rnn.hidden = self.rnn.init_hidden()
        for i in range(self.max_length):
            inputWordVec = torch.from_numpy(inputWordVec).view(-1, self.vector_size)
            inputWordVec = inputWordVec.unsqueeze(0).unsqueeze(0)
            inputWordVec = F.pad(inputWordVec, (0, 0, 0, 9)).squeeze(0)

            out = self.rnn(inputWordVec)
            out2Numpy = out[0][0].squeeze().data.numpy()
            letter = self.embedding.findSimilarWordByVector(out2Numpy)
            outputLetter = random.choice(letter)[0]
            output_name = output_name + ' ' + outputLetter

            inputWordVec = (
                self.embedding.model.wv[outputLetter] if outputLetter in self.embedding.vocab else self.unknown)

        return output_name

    # Get multiple samples from one category and multiple starting letters
    def samples(self, start_letters='ABC'):
        results = []
        for start_letter in start_letters:
            results.append(self.sample(start_letter))
        return results